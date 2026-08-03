"""Base agent shared by every LangGraph agent node."""

from abc import ABC, abstractmethod
from typing import Any, Optional, TypedDict

from app.ai.model_router import ModelCall, ModelProviderError, router
from app.ai.prompts import build_system_prompt
from app.core.logging import get_logger
from app.services.logging_service import LoggingService

logger = get_logger("agents.base")

EMERGENCY_KEYWORDS = [
    "chest pain",
    "chest pressure",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "shortness of breath",
    "stroke",
    "face drooping",
    "slurred speech",
    "arm weakness",
    "severe bleeding",
    "uncontrolled bleeding",
    "unconscious",
    "loss of consciousness",
    "fainted",
    "not responding",
    "choking",
    "seizure",
    "suicidal",
    "killing myself",
    "severe allergic reaction",
    "swelling of throat",
]


class AgentState(TypedDict, total=False):
    """State dictionary shared across LangGraph nodes.

    Must be a TypedDict so LangGraph can configure its channels. All keys are
    optional; use :func:`new_agent_state` to build a defaulted state.
    """

    user_message: str
    user_id: Optional[int]
    history: list
    profile: dict
    intent: str
    agent_name: str
    response: str
    model: str
    data: dict
    errors: list
    db: Any


def new_agent_state(**kwargs: Any) -> AgentState:
    """Create a state dict with sensible defaults for every channel."""
    state: AgentState = {
        "user_message": "",
        "user_id": None,
        "history": [],
        "profile": {},
        "intent": "general",
        "agent_name": "general",
        "response": "",
        "model": "",
        "data": {},
        "errors": [],
        "db": None,
    }
    state.update(kwargs)
    return state


class BaseAgent(ABC):
    """Base class for all AI agents."""

    name: str = "base"
    prompt_template: str = "system_base"
    requires_json: bool = False

    def __init__(self) -> None:
        self.system_prompt = build_system_prompt(self.prompt_template)

    # ------------------------------------------------------------------ core
    def _record_usage(
        self,
        state: AgentState,
        call: ModelCall,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        db = state.get("db")
        if db is None:
            return
        try:
            LoggingService.log_model_usage(
                db,
                user_id=state.get("user_id"),
                agent=self.name,
                model=call.model,
                tier=call.tier,
                prompt_tokens=call.prompt_tokens,
                completion_tokens=call.completion_tokens,
                cost_usd=call.cost_usd,
                latency_ms=call.latency_ms,
                success=success,
                error=error,
            )
        except Exception:  # pragma: no cover
            logger.exception("Failed to persist model usage")

    def _record_prompt(
        self,
        state: AgentState,
        messages: list[dict[str, str]],
        response: Optional[str],
        model: str,
    ) -> None:
        db = state.get("db")
        if db is None:
            return
        try:
            LoggingService.log_prompt(
                db,
                agent=self.name,
                prompt="\n".join(m["content"] for m in messages),
                response=response,
                model=model,
                user_id=state.get("user_id"),
            )
        except Exception:  # pragma: no cover
            logger.exception("Failed to persist prompt history")

    def _build_messages(self, state: AgentState, user_message: str) -> list[dict[str, str]]:
        profile = state.get("profile") or {}
        context_bits = []
        if profile.get("age"):
            context_bits.append(f"age: {profile['age']}")
        if profile.get("gender"):
            context_bits.append(f"gender: {profile['gender']}")
        if profile.get("medical_history"):
            context_bits.append(f"medical history: {profile['medical_history']}")
        if profile.get("allergies"):
            context_bits.append(f"allergies: {profile['allergies']}")
        if profile.get("current_medications"):
            context_bits.append(f"current medications: {profile['current_medications']}")

        content = user_message
        if context_bits:
            content = f"User health profile: {'; '.join(context_bits)}.\n\nUser message: {user_message}"

        return router.build_messages(
            self.system_prompt,
            history=state.get("history") or [],
            user_message=content,
        )

    def _call_model(self, state: AgentState, messages: list[dict[str, str]]) -> ModelCall:
        call = router.chat(messages)
        self._record_usage(state, call)
        self._record_prompt(state, messages, call.content, call.model)
        return call

    @abstractmethod
    def run(self, state: AgentState) -> AgentState:
        """Execute the agent node and return the updated state."""

    # ------------------------------------------------------------------ util
    def extract_json_or_fallback(
        self, raw: str, fallback_text: str
    ) -> tuple[dict[str, Any], str]:
        """Parse JSON from the model output; return ``(parsed, display_text)``.

        When parsing fails the raw text is used as the display text and the
        parsed data is an empty dict.
        """
        from app.ai.json_utils import extract_json

        parsed = extract_json(raw)
        if parsed is not None:
            return parsed, raw
        return {}, fallback_text
