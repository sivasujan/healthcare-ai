# 01 — Project Overview

**MediAssist** is a production-grade, locally runnable AI healthcare assistant built with a modern multi-agent architecture. It combines a FastAPI backend with a Next.js frontend and routes every AI call through a central **Model Router** with provider failover.

## What it does

| Feature | Description |
| --- | --- |
| AI Chat | Multi-turn chat with live SSE token streaming, voice input, history, regenerate and stop |
| Symptom Analysis | Structured analysis with possible conditions, confidence, severity, recommendations |
| Medicine Info | Instant local knowledge-base lookup with AI fallback; save medicines to a personal list |
| Doctor Recommendation | Specialty, consultation type, urgency and preparation tips |
| Emergency Check | Red-flag symptom detection with immediate actions and emergency numbers |
| Appointments | Book, list, reschedule and cancel appointments |
| Health Profile | Personal details, health profile (age, blood group, history…), change password, medical history entries |
| Admin Panel | Platform stats, user activation/deactivation, chat logs, model usage, prompt and system logs |

## Architecture at a glance

```
Browser (Next.js 15)
   │  REST + SSE
   ▼
FastAPI (Python 3.10)
   │
   ├── Auth (JWT access/refresh + bcrypt)
   ├── Multi-Agent Graph (LangGraph)
   │     intent → symptom | medicine | doctor | emergency | appointment | general
   ├── Model Router (provider failover)
   │     Gemini (fast) ──fallback──▶ OpenRouter tiers
   ├── SQLAlchemy + SQLite
   └── Middleware (rate limit, prompt injection, logging)
```

## Tech stack

- **Frontend:** Next.js 15 (App Router, Turbopack), React 19, TypeScript, Tailwind CSS v4, shadcn-style UI, TanStack Query, react-hook-form + zod, framer-motion
- **Backend:** FastAPI, SQLAlchemy 2, SQLite, Alembic, LangGraph, httpx, Pydantic v2, JWT
- **AI:** Google Gemini (primary, fast) with OpenRouter free-model tiers as fallback

## Repo layout

```
health-care-project/
├── backend/     # FastAPI app, agents, model router, alembic, tests (46)
├── frontend/    # Next.js app (17 routes)
├── docs/        # This documentation set (01-13)
├── run.ps1      # One-command launcher (backend + frontend)
└── README.md    # Quick start
```

## Reading order

1. [02 — Quick Start](02-quick-start.md)
2. [03 — Configuration](03-configuration.md)
3. [04 — Backend Architecture](04-backend-architecture.md)
4. [05 — AI Agents & LangGraph](05-ai-agents-langgraph.md)
5. [06 — Model Router](06-model-router.md)
6. [07 — API Reference](07-api-reference.md)
7. [08 — Frontend Architecture](08-frontend-architecture.md)
8. [09 — Frontend Pages & Features](09-frontend-pages-features.md)
9. [10 — Authentication & Security](10-authentication-security.md)
10. [11 — Database & Migrations](11-database-migrations.md)
11. [12 — Testing](12-testing.md)
12. [13 — Deployment & Production](13-deployment-production.md)
