# MediAssist — AI Healthcare Assistant

A production-grade, locally runnable AI healthcare assistant: multi-agent AI chat (symptom analysis, medicine info, doctor recommendations, emergency detection), appointments, health profile and an admin panel — built with **Next.js 15 + FastAPI + LangGraph** and a **Gemini-first Model Router** with OpenRouter failover.

## Features

- **AI Chat** — token-by-token SSE streaming, voice input, chat history, regenerate/stop, emergency alerts
- **Symptom Analyzer** — conditions with confidence + severity, recommendations, doctor advice
- **Medicine Info** — instant local knowledge base (10 drugs) + AI fallback, save list
- **Doctor Recommendation** — specialty, urgency, prep tips, nearby hospitals
- **Emergency Check** — red-flag detection with immediate actions
- **Appointments** — book / list / cancel with status tracking
- **Health Profile** — personal + health details, change password, medical history entries
- **Admin Panel** — platform stats, user management, model usage/cost, prompt + system logs

## Quick start

**Prerequisites:** Python 3.10+, Node 18.18+, and a free Gemini API key from https://aistudio.google.com/apikey

```powershell
.\run.ps1
```

One command starts the backend (FastAPI on :8000) and frontend (Next.js on :3000). Add your `GEMINI_API_KEY` to `backend\.env` first.

| Role | Email | Password |
| --- | --- | --- |
| Demo user | `test@example.com` | `Test@12345` |
| Admin | `admin@healthcare.ai` | `Admin@12345` |

## Tech stack

- **Frontend:** Next.js 15 (Turbopack), React 19, TypeScript, Tailwind v4, TanStack Query, react-hook-form + zod, framer-motion
- **Backend:** FastAPI, SQLAlchemy 2, SQLite, Alembic, LangGraph, JWT + bcrypt, rate limiting, prompt-injection guard
- **AI:** Google Gemini (fast primary) → OpenRouter free-model tiers (fallback), cost/token tracking

## Repository layout

```
backend/     FastAPI app, LangGraph agents, model router, Alembic, 46 tests
frontend/    Next.js app, 17 routes
docs/        Full documentation set (01-13)
run.ps1      One-command launcher
```

## Documentation

| Doc | Topic |
| --- | --- |
| [01](docs/01-project-overview.md) | Project overview |
| [02](docs/02-quick-start.md) | Quick start |
| [03](docs/03-configuration.md) | Configuration |
| [04](docs/04-backend-architecture.md) | Backend architecture |
| [05](docs/05-ai-agents-langgraph.md) | AI agents & LangGraph |
| [06](docs/06-model-router.md) | Model router (Gemini + OpenRouter) |
| [07](docs/07-api-reference.md) | API reference |
| [08](docs/08-frontend-architecture.md) | Frontend architecture |
| [09](docs/09-frontend-pages-features.md) | Pages & features |
| [10](docs/10-authentication-security.md) | Auth & security |
| [11](docs/11-database-migrations.md) | Database & migrations |
| [12](docs/12-testing.md) | Testing |
| [13](docs/13-deployment-production.md) | Deployment & production |

## Verification

```powershell
# Backend tests (46)
cd backend; .\.venv\Scripts\python.exe -m pytest app\tests -q

# Frontend checks
cd frontend; npx tsc --noEmit; npm run lint; npm run build
```

## Disclaimer

AI-generated health information is **educational only** and is not a substitute for professional medical advice, diagnosis or treatment.
