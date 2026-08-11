# 11 — Database & Migrations

## Models (11)

Defined in `backend/app/models/` (SQLAlchemy 2):

| Model | Purpose |
| --- | --- |
| `User` | Auth, role, health profile fields (age, gender, height, weight, blood group, history, allergies, medications, preferences) |
| `MedicalHistory` | Per-user chronic condition entries (condition, diagnosed year, notes) |
| `Chat` | Conversation (title, agent, timestamps) |
| `ChatMessage` | Messages in a chat (role, content, agent, model) |
| `Appointment` | Appointments (title, doctor, specialty, hospital, date, time, status, notes) |
| `SavedSearch` | Search log (type: symptom/medicine/doctor/emergency, query, summary) |
| `Medicine` | Local drug knowledge base (generic name, uses, dosage, warnings, side effects, interactions…) |
| `SavedMedicine` | User ↔ medicine saved link |
| `PromptHistory` | AI prompt audit (agent, model, prompt) |
| `ModelUsage` | Per-call AI usage (model, tier, agent, tokens, cost, success) |
| `SystemLog` | Request/system logs (level, event, method, path, status, latency) |

## SQLite + Alembic

- Default DB: `backend/healthcare.db` (`DATABASE_URL` in `.env`).
- Migrations live in `backend/alembic/versions/`; current head: **`448bb5599d92` (initial_schema)**.

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head    # apply
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "desc"   # new migration
```

## Seeding

Seeding is **automatic on backend startup** (`app/main.py` lifespan):

- **Admin user** from `ADMIN_EMAIL`/`ADMIN_PASSWORD` settings (idempotent).
- **10 medicines** into the knowledge base (paracetamol, ibuprofen, amoxicillin, metformin, omeprazole, cetirizine, amlodipine, atorvastatin, salbutamol, ondansetron) with full usage/dosage/warning data — used by the instant local lookup.

Implemented in `app/services/auth_service.py` (admin) and `app/services/medicine_service.py::seed_medicines`. To force-reseed medicines, delete the `Medicine` rows (or the DB file) and restart.

## Test database

Tests use an in-memory SQLite (`StaticPool`, `Base.metadata.create_all`) with a fresh transaction rolled back per test — no migration dependency.

## Conventions

- All models use `id` PK, `created_at`/`updated_at` timestamps where relevant.
- API responses validate models via `model_config = {"from_attributes": True}`.
- Foreign keys are indexed for the chat-history and saved-list queries.
