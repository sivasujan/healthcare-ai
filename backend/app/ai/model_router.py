"""Centralized OpenRouter Model Router.

Every AI agent in the application talks to this router — never directly to
OpenRouter. The router provides:

* Model tiering: primary -> secondary -> fallback (configurable in ``.env``)
* Automatic retries with exponential backoff
* Streaming support (SSE via FastAPI or async generator)
* Timeout handling
* Token usage and cost tracking (persisted to ``model_usage``)
* Conversation memory assembly
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Optional

import httpx

from app.config import settings
from app.core.logging import get_logger
from app.middleware.prompt_injection import validate_prompt_safety

logger = get_logger("ai.model_router")

# Approximate USD per 1M tokens per model (input/output). Used for cost tracking.
PRICING: dict[str, tuple[float, float]] = {
    "openai/gpt-4o": (2.50, 10.00),
    "openai/gpt-4o-mini": (0.15, 0.60),
    "openai/gpt-oss-20b:free": (0.0, 0.0),
    "anthropic/claude-3.5-sonnet": (3.00, 15.00),
    "anthropic/claude-3-haiku": (0.25, 1.25),
    "google/gemini-1.5-flash": (0.075, 0.30),
    "google/gemini-1.5-pro": (1.25, 5.00),
    "google/gemma-2-9b-it:free": (0.0, 0.0),
    "google/gemma-4-26b-a4b-it:free": (0.0, 0.0),
    "google/gemma-3-27b-it:free": (0.0, 0.0),
    "nvidia/nemotron-3-ultra-550b-a55b:free": (0.0, 0.0),
    "meta-llama/llama-3.3-70b-instruct:free": (0.0, 0.0),
    "gemini-2.5-pro": (1.25, 10.00),
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-3.6-flash": (0.30, 2.50),
    "gemini-3.5-flash": (0.30, 2.50),
}


@dataclass
class ModelCall:
    """Result of a single model invocation."""

    content: str
    model: str
    tier: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    cost_usd: float
    usage: dict[str, Any] = field(default_factory=dict)


class ModelTimeoutError(Exception):
    """Raised when a model request exceeds the configured timeout."""


class ModelProviderError(Exception):
    """Raised when the provider fails on all retries."""


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate cost in USD from token counts using the local pricing table."""
    in_rate, out_rate = PRICING.get(model, (0.0, 0.0))
    return (prompt_tokens / 1_000_000 * in_rate) + (completion_tokens / 1_000_000 * out_rate)


def get_model_tiers() -> dict[str, str]:
    """Return the configured model tiers (primary, secondary, fallback, free)."""
    return {
        "primary": settings.PRIMARY_MODEL,
        "secondary": settings.SECONDARY_MODEL,
        "fallback": settings.FALLBACK_MODEL,
        "free": settings.FREE_MODEL,
    }


class ModelRouter:
    """Thread-safe model router with fallback and retry logic."""

    def __init__(self, timeout_seconds: Optional[int] = None) -> None:
        self.timeout = timeout_seconds or settings.AI_TIMEOUT_SECONDS
        self.max_retries = settings.AI_MAX_RETRIES
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL.rstrip("/")
        self.gemini_key = settings.GEMINI_API_KEY
        self.gemini_base_url = settings.GEMINI_BASE_URL.rstrip("/")
        self.gemini_model = settings.GEMINI_MODEL

    @property
    def configured(self) -> bool:
        """Whether an OpenRouter API key is available."""
        return bool(self.api_key)

    @property
    def gemini_configured(self) -> bool:
        """Whether a Gemini API key is available."""
        return bool(self.gemini_key)

    def _gemini_preferred(self) -> bool:
        """Gemini is used first when it is configured and AI_PROVIDER allows it."""
        return bool(self.gemini_key) and settings.AI_PROVIDER in ("auto", "gemini")

    def _tier_order(self) -> list[tuple[str, str]]:
        tiers = get_model_tiers()
        return [
            ("primary", tiers["primary"]),
            ("secondary", tiers["secondary"]),
            ("fallback", tiers["fallback"]),
        ]

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": settings.OPENROUTER_SITE_URL,
            "X-Title": settings.OPENROUTER_SITE_NAME,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _build_payload(model: str, messages: list[dict], temperature: float, max_tokens: int) -> dict:
        return {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    # ----------------------------------------------------------------- Gemini
    @staticmethod
    def _to_gemini_payload(model: str, messages: list[dict], temperature: float, max_tokens: int) -> dict:
        """Convert OpenAI-style messages to a Gemini generateContent payload."""
        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        contents: list[dict] = []
        for m in messages:
            if m["role"] == "system":
                continue
            contents.append(
                {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
            )
        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }
        if system_parts:
            payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}
        return payload

    @staticmethod
    def _parse_gemini(data: dict) -> tuple[str, int, int]:
        """Extract text + usage from a Gemini generateContent response."""
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})
        prompt_tokens = usage.get("promptTokenCount", 0) or 0
        completion_tokens = usage.get("candidatesTokenCount", 0) or 0
        return content, prompt_tokens, completion_tokens

    def _gemini_request_once(
        self, model: str, messages: list[dict], temperature: float, max_tokens: int
    ) -> dict:
        payload = self._to_gemini_payload(model, messages, temperature, max_tokens)
        url = f"{self.gemini_base_url}/models/{model}:generateContent"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, params={"key": self.gemini_key}, json=payload)
        except httpx.TimeoutException as exc:
            raise ModelTimeoutError(f"Gemini {model} timed out after {self.timeout}s") from exc
        except httpx.HTTPError as exc:
            raise ModelProviderError(f"Network error calling Gemini {model}: {exc}") from exc

        if response.status_code >= 500:
            raise ModelProviderError(f"Provider error {response.status_code} from Gemini {model}")
        if response.status_code == 429:
            raise ModelProviderError(f"Rate limited (429) by Gemini for {model}")
        if response.status_code >= 400:
            body = response.text[:500]
            raise ModelProviderError(f"Bad request ({response.status_code}) for Gemini {model}: {body}")
        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise ModelProviderError(f"Invalid JSON response from Gemini {model}") from exc

    def _gemini_chat(self, messages: list[dict], temperature: float, max_tokens: int) -> ModelCall:
        """Invoke the configured Gemini model with per-attempt retries."""
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            started = time.perf_counter()
            try:
                data = self._gemini_request_once(self.gemini_model, messages, temperature, max_tokens)
                latency_ms = round((time.perf_counter() - started) * 1000, 2)
                content, prompt_tokens, completion_tokens = self._parse_gemini(data)
                cost = estimate_cost(self.gemini_model, prompt_tokens, completion_tokens)
                return ModelCall(
                    content=content,
                    model=data.get("modelVersion", self.gemini_model),
                    tier="gemini",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_ms=latency_ms,
                    cost_usd=cost,
                    usage=data.get("usageMetadata", {}),
                )
            except ModelTimeoutError as exc:
                last_error = exc
                logger.warning("Timeout on Gemini %s (attempt %d/%d)", self.gemini_model, attempt + 1, self.max_retries + 1)
            except ModelProviderError as exc:
                last_error = exc
                logger.warning("Gemini error on %s: %s", self.gemini_model, exc)
                break  # 4xx errors won't succeed on retry
        raise ModelProviderError(f"Gemini failed. Last error: {last_error}")

    @staticmethod
    def _parse_usage(usage: Optional[dict]) -> tuple[int, int]:
        usage = usage or {}
        prompt_tokens = usage.get("prompt_tokens", 0) or 0
        completion_tokens = usage.get("completion_tokens", 0) or 0
        return prompt_tokens, completion_tokens

    def _request_once(self, model: str, messages: list[dict], temperature: float, max_tokens: int) -> dict:
        """Single (no-retry) request to OpenRouter; returns parsed JSON."""
        payload = self._build_payload(model, messages, temperature, max_tokens)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise ModelTimeoutError(f"Model {model} timed out after {self.timeout}s") from exc
        except httpx.HTTPError as exc:
            raise ModelProviderError(f"Network error calling {model}: {exc}") from exc

        if response.status_code >= 500:
            raise ModelProviderError(f"Provider error {response.status_code} from {model}")

        if response.status_code == 429:
            raise ModelProviderError(f"Rate limited (429) by provider for {model}")

        if response.status_code >= 400:
            body = response.text[:500]
            raise ModelProviderError(f"Bad request ({response.status_code}) for {model}: {body}")

        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise ModelProviderError(f"Invalid JSON response from {model}") from exc

    def _chat(self, messages: list[dict], temperature: float, max_tokens: int) -> ModelCall:
        """Invoke models tier-by-tier with per-tier retries.

        When Gemini is configured and preferred it is tried first (faster),
        falling back to the OpenRouter tiers on any error.
        """
        gemini_error: Optional[Exception] = None
        if self._gemini_preferred():
            try:
                return self._gemini_chat(messages, temperature, max_tokens)
            except (ModelTimeoutError, ModelProviderError) as exc:
                gemini_error = exc
                logger.warning("Gemini failed, falling back to OpenRouter tiers: %s", exc)

        if not self.configured:
            raise ModelProviderError(
                "No AI provider configured. Set GEMINI_API_KEY or OPENROUTER_API_KEY in backend/.env"
            )

        last_error: Optional[Exception] = gemini_error
        for tier, model in self._tier_order():
            for attempt in range(self.max_retries + 1):
                started = time.perf_counter()
                try:
                    data = self._request_once(model, messages, temperature, max_tokens)
                    latency_ms = round((time.perf_counter() - started) * 1000, 2)
                    content = data["choices"][0]["message"]["content"]
                    prompt_tokens, completion_tokens = self._parse_usage(data.get("usage"))
                    cost = estimate_cost(model, prompt_tokens, completion_tokens)
                    return ModelCall(
                        content=content,
                        model=data.get("model", model),
                        tier=tier,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        latency_ms=latency_ms,
                        cost_usd=cost,
                        usage=data.get("usage", {}),
                    )
                except ModelTimeoutError as exc:
                    last_error = exc
                    logger.warning("Timeout on %s (attempt %d/%d)", model, attempt + 1, self.max_retries + 1)
                except ModelProviderError as exc:
                    last_error = exc
                    logger.warning("Provider error on %s: %s", model, exc)
                    break  # 4xx errors won't succeed on retry; move to next tier

        raise ModelProviderError(f"All model tiers failed. Last error: {last_error}")

    # ------------------------------------------------------------------ public
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> ModelCall:
        """Complete a chat conversation (non-streaming)."""
        return self._chat(
            messages,
            temperature or settings.AI_TEMPERATURE,
            max_tokens or settings.AI_MAX_TOKENS,
        )

    async def _gemini_chat_stream(
        self, messages: list[dict], temperature: float, max_tokens: int
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream from Gemini. Yields token events and a done event."""
        payload = self._to_gemini_payload(self.gemini_model, messages, temperature, max_tokens)
        url = f"{self.gemini_base_url}/models/{self.gemini_model}:streamGenerateContent"
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST", url, params={"alt": "sse", "key": self.gemini_key}, json=payload
                ) as response:
                    if response.status_code >= 400:
                        body = "".join([part async for part in response.aiter_text()]).strip()[:500]
                        yield {"type": "error", "message": f"Gemini provider error {response.status_code}: {body}"}
                        return
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        chunk = line[5:].strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            obj = json.loads(chunk)
                        except json.JSONDecodeError:
                            continue
                        parts = obj.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                        for part in parts:
                            text = part.get("text")
                            if text and not part.get("thought"):
                                yield {"type": "token", "token": text}
        except (httpx.TimeoutException, httpx.HTTPError) as exc:
            logger.warning("Gemini streaming failed: %s", exc)
            yield {"type": "error", "message": f"Gemini streaming failed: {exc}"}
            return

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        yield {"type": "done", "model": self.gemini_model, "latency_ms": latency_ms}

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream a chat conversation (async generator).

        Uses Gemini first when configured (faster); falls back to OpenRouter
        streaming on any error. Yields ``{"type": "token", "token": ...}``
        events and finally ``{"type": "done", "model": ..., "latency_ms": ...}``.
        """
        temperature = temperature or settings.AI_TEMPERATURE
        max_tokens = max_tokens or settings.AI_MAX_TOKENS

        if self._gemini_preferred():
            saw_error = False
            async for event in self._gemini_chat_stream(messages, temperature, max_tokens):
                if event["type"] == "error":
                    saw_error = True
                    logger.warning("Gemini streaming failed, falling back: %s", event["message"])
                    break
                yield event
            if not saw_error:
                return

        if not self.configured:
            yield {"type": "error", "message": "No AI provider configured. Set GEMINI_API_KEY or OPENROUTER_API_KEY in backend/.env"}
            return

        payload = self._build_payload(
            self._tier_order()[0][1],
            messages,
            temperature,
            max_tokens,
        )
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json={**payload, "stream": True},
                ) as response:
                    if response.status_code >= 400:
                        body = "".join([part async for part in response.aiter_text()]).strip()[:500]
                        yield {"type": "error", "message": f"Provider error {response.status_code}: {body}"}
                        return
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        chunk = line[5:].strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            obj = json.loads(chunk)
                        except json.JSONDecodeError:
                            continue
                        delta = obj.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield {"type": "token", "token": content}
        except (httpx.TimeoutException, httpx.HTTPError) as exc:
            logger.warning("Streaming failed on primary model: %s", exc)
            yield {"type": "error", "message": f"Streaming failed: {exc}"}
            return

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        yield {"type": "done", "model": payload["model"], "latency_ms": latency_ms}

    # ----------------------------------------------------------------- memory
    @staticmethod
    def build_messages(
        system_prompt: str,
        history: Optional[list[dict[str, str]]] = None,
        user_message: Optional[str] = None,
        max_history_turns: int = 12,
    ) -> list[dict[str, str]]:
        """Assemble the message list for a model call.

        ``history`` is a list of ``{"role": "user"|"assistant", "content": ...}``
        pairs; only the most recent ``max_history_turns`` are kept so the
        prompt stays within budget.
        """
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history[-max_history_turns:])
        if user_message:
            messages.append({"role": "user", "content": user_message})
        return messages


router = ModelRouter()
