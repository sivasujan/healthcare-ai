# Intelligent Multi-Agent AI Healthcare Assistant

Production-quality, fully local AI healthcare assistant.

- **Frontend:** Next.js 15, TypeScript, TailwindCSS, shadcn/ui, Framer Motion
- **Backend:** FastAPI, SQLAlchemy, Alembic, LangGraph, JWT, SQLite
- **AI:** OpenRouter via a centralized Model Router (free models by default)

See the [documentation](../docs/01_Project_Overview.md) for the full picture.

## Quick start

```bash
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env          # add your OPENROUTER_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend
cd ../frontend
npm install
npm run dev                     # http://localhost:3000
```

Default admin: `admin@healthcare.local` / `Admin@12345`

## Tests

```bash
cd backend
pytest
```
