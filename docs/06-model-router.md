# 06 — Model Router

Every AI call in the app goes through `backend/app/ai/model_router.py` — never directly to a provider.

## Providers

| Provider | Purpose | Auth |
| --- | --- | --- |
| **Gemini** (default, fast) | Primary. `gemini-3.6-flash` via the GenerateContent API | `GEMINI_API_KEY` (bearer query param `key`) |
| **OpenRouter** (fallback) | 3-tier model chain with per-tier retries | `OPENROUTER_API_KEY` |

## Routing logic

- `AI_PROVIDER=auto` (default): **Gemini first**; on any error (timeout, 4xx, 5xx, 429) fall back to the OpenRouter tier chain.
- `AI_PROVIDER=gemini`: Gemini only.
- `AI_PROVIDER=openrouter`: OpenRouter only.

```
chat(messages)
 └─ Gemini preferred?
     ├─ yes → Gemini (retries on 429/5xx) ──success──▶ ModelCall
     └─ no / failure ────────────────────────────────▶ OpenRouter tiers
                                                       primary → secondary → fallback
                                                       (per-tier retries, 4xx = skip tier)
```

## Key components

| Piece | Description |
| --- | --- |
| `ModelCall` | Result dataclass: content, model, tier, tokens, latency, cost |
| `PRICING` | USD per 1M tokens table for cost tracking |
| `estimate_cost()` | Cost from token counts |
| `get_model_tiers()` | Reads `PRIMARY/SECONDARY/FALLBACK_MODEL` settings |
| `ModelRouter.chat()` | Non-streaming completion |
| `ModelRouter.chat_stream()` | Async SSE generator (`token` + `done` events) — Gemini streaming first, OpenRouter fallback |
| `build_messages()` | Assembles system + history (last N turns) + user message |

## Message conversion (Gemini)

OpenAI-style messages are converted to the Gemini GenerateContent payload:

- `system` → `systemInstruction.parts[].text`
- `user` → `contents[] { role: "user" }`
- `assistant` → `contents[] { role: "model" }`
- Token counts read from `usageMetadata` (`promptTokenCount`, `candidatesTokenCount`).

## Streaming

- `chat_stream` is an **async** generator (httpx `AsyncClient`).
- Gemini: `POST /v1beta/models/{model}:streamGenerateContent?alt=sse` — thinking chunks are skipped (`part.thought`), only visible text yields tokens.
- OpenRouter: OpenAI-style `data:` SSE lines, `[DONE]` terminator.
- Both emit a final `done` event with model + latency; errors emit `error` events instead of raising.

## Cost tracking

Each successful call is persisted to `model_usage` (model, tier, agent, tokens, cost) — visible in the Admin panel. Gemini usage is estimated from `usageMetadata`; OpenRouter usage comes from `usage` in the response.

## Caveats

- Model availability changes: if `GEMINI_MODEL` is retired for your account, the router logs a warning and falls back to OpenRouter (visible in the backend log). Pick a current model from `GET /v1beta/models?key=...`.
- Free OpenRouter models are shared pools and may 429 — the tier chain handles it.
