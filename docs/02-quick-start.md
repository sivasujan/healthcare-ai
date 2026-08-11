# 02 — Quick Start

## Prerequisites

- **Python** 3.10+ (tested on 3.10.11)
- **Node.js** 18.18+ (tested on 24.x) with npm
- A **Gemini API key** (free): https://aistudio.google.com/apikey
- *(Optional)* an **OpenRouter API key** for the fallback tiers: https://openrouter.ai/keys

## Option A — One command

From the project root:

```powershell
.\run.ps1
```

This creates the backend venv, installs dependencies, copies `.env.example` to `.env` (first run), starts the FastAPI backend on **:8000** and the Next.js dev server on **:3000**. Ctrl+C stops both.

> **Important:** add your `GEMINI_API_KEY` to `backend\.env` before the first AI call.

## Option B — Manual

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then edit: GEMINI_API_KEY=...
alembic upgrade head        # create schema
# (medicines + admin seed automatically on first backend start)
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Log in

| Role | Email | Password |
| --- | --- | --- |
| Demo user | `test@example.com` | `Test@12345` |
| Admin | `admin@healthcare.ai` | `Admin@12345` |

(Or register a new account from the login page.)

## URLs

| Service | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api |
| Swagger UI | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/health |

## Verify it works

1. Open http://localhost:3000 and log in.
2. Go to **AI Chat** and send *"Tell me 3 tips for better sleep"* — the reply should stream token-by-token.
3. Go to **Symptom Analyzer** and submit symptoms — structured results appear.
4. Go to **Medicine** and search *paracetamol* — instant local knowledge-base result.
