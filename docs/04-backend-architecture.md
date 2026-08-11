# 04 — Backend Architecture

## Overview

The backend (`backend/app`) is a modular FastAPI application:

```
backend/app/
├── main.py                 # FastAPI app factory, middleware, router registration
├── config.py               # pydantic-settings configuration
├── database.py             # SQLAlchemy engine/session, Base
├── models/                 # 11 ORM models
├── schemas/                # Pydantic request/response schemas
├── api/
│   ├── routes/             # auth, chat, symptom, medicine, doctor, emergency,
│   │                       #   appointments, profile, admin, health
│   └── deps.py             # rate limiting dependency
├── agents/                 # LangGraph agents + intent detection + graph
├── ai/
│   └── model_router.py     # Gemini + OpenRouter provider router
├── auth.py                 # JWT create/verify, current-user/admin deps
├── middleware/             # request logging, prompt injection guard
├── services/               # business logic (user, chat, medicine, appointment, admin)
├── core/                   # exceptions, logging
└── tests/                  # 46 pytest tests
```

## Request flow

1. Request hits the FastAPI app (`app/main.py`).
2. Middleware runs: request logging → prompt-injection safety (on AI endpoints).
3. Router dependency (`get_current_user`) verifies the JWT.
4. `enforce_rate_limit` allows max 60 AI calls/minute/user.
5. Route handler calls an agent or service:
   - **AI features** → agent functions in `app/agents/`
   - **Data features** (appointments, profile, saved medicines) → services in `app/services/`
6. Every AI call goes through `app/ai/model_router.py` (see doc 06).
7. Responses are wrapped in the `ApiResponse` envelope.

## API envelope

```json
{
  "success": true,
  "message": "optional message",
  "data": { ... },
  "errors": null,
  "status_code": 200
}
```

## Agent routing (chat)

`POST /api/chat/send` and `/api/chat/stream`:

1. `IntentDetector` classifies the message (regex keywords + model call with JSON fallback).
2. **general** intent → direct model response (streamed token-by-token over SSE).
3. **structured** intents (symptom, medicine, doctor, emergency, appointment) → run the LangGraph agent graph with `force_intent` for deterministic routing (bypasses a second classification call).
4. Emergency keywords are pre-checked before the model call and short-circuit to the emergency agent.
5. Chat history, message records and model usage are persisted; the first message becomes the chat title.

## SSE streaming format

```
event: token
data: {"token": "Hello"}

event: done
data: {"chat_id": 18, "message_id": 28, "agent": "general_chat", "model": "gemini-3.6-flash", "title": "...", "data": {}}
```

Events: `token`, `emergency` (optional), `done`, `error`.

## Conventions

- `AgentState` is a `TypedDict` (LangGraph requirement) — build it with `new_agent_state(**kwargs)`, never `AgentState(...)`.
- Route handlers stay thin; logic lives in agents/services.
- Every AI call is rate-limited and prompt-injection checked.
