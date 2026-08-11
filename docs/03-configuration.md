# 03 — Configuration

All backend configuration lives in `backend/app/config.py` (pydantic-settings). Values are read from `backend/.env` or the process environment. Frontend config lives in `frontend/lib/api.ts`.

## Backend `.env`

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEBUG` | `false` | FastAPI debug mode |
| `SECRET_KEY` | demo value | JWT signing secret — **change in production** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Access token lifetime (24 h) |
| `DATABASE_URL` | `sqlite:///backend/healthcare.db` | SQLite only |
| `CORS_ORIGINS` | localhost:3000 | Allowed browser origins (JSON list) |
| `RATE_LIMIT_REQUESTS` | `60` | Requests per window per user |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate-limit window |
| `AI_PROVIDER` | `auto` | `auto` (Gemini first), `gemini` or `openrouter` |
| `GEMINI_API_KEY` | — | **Required for fast AI responses** |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Fast primary model |
| `OPENROUTER_API_KEY` | — | Fallback provider key |
| `PRIMARY_MODEL` | `google/gemma-4-26b-a4b-it:free` | OpenRouter tier 1 |
| `SECONDARY_MODEL` | `openai/gpt-oss-20b:free` | OpenRouter tier 2 |
| `FALLBACK_MODEL` | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter tier 3 |
| `AI_TIMEOUT_SECONDS` | `60` | Per-request timeout |
| `AI_MAX_RETRIES` | `2` | Retries per tier |
| `AI_TEMPERATURE` | `0.4` | Model temperature |
| `AI_MAX_TOKENS` | `2048` | Max output tokens |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | demo admin | Seeded admin credentials |

## Frontend

| Variable | Default | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api` | Backend base URL for the API client |

Set it in `frontend/.env.local` (or `.env`) when the backend runs elsewhere.

## Provider selection (`AI_PROVIDER`)

- **`auto`** — uses Gemini when `GEMINI_API_KEY` is set, with automatic fallback to OpenRouter tiers on any failure. Recommended.
- **`gemini`** — Gemini only (errors if the key is missing/invalid).
- **`openrouter`** — OpenRouter tiers only.

## Notes

- `.env` is gitignored; commit changes to `.env.example` instead.
- The OpenRouter keys shown in the repo are placeholders — never commit real keys.
- Changing `SECRET_KEY` invalidates existing tokens (harmless in dev).
