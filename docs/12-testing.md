# 12 — Testing

## Backend — pytest (46 tests)

Run from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pytest app\tests -q
```

Coverage areas:

| File | What it covers |
| --- | --- |
| `test_auth.py` | Register/login/refresh, password policy, wrong credentials, token expiry |
| `test_chat.py` | Chat CRUD, `/send` routing (symptom + general), history persistence, delete, **SSE stream** (`done` event via mocked router) |
| `test_features.py` | Symptom analysis, emergency detection, doctor recommendation, saved-search recording, rate limiting |
| `test_health.py` | Health endpoint |

**Mocking:** `conftest.py` replaces the singleton `router.chat` / `router.chat_stream` with canned per-intent responses (e.g. `{"symptom_analysis": '<json>'}`), so tests never hit the network. `mock_router.chat_stream` is an async generator yielding tokens + a `done` event.

**Isolation:** in-memory SQLite, per-test transaction rollback, dependency-overridden `get_db`.

## Frontend

No unit-test runner is configured yet; verification is:

```powershell
cd frontend
npx tsc --noEmit      # type safety
npm run lint          # ESLint (zero errors)
npm run build         # production build incl. static generation of all 17 routes
```

## Manual smoke test

1. Start with `run.ps1`.
2. Login as `test@example.com / Test@12345`.
3. Chat: send *"Tell me 3 tips for better sleep"* → tokens stream, model badge shows `gemini-3.6-flash`.
4. Chat: *"I have chest pain and shortness of breath"* → emergency banner appears.
5. Symptom Analyzer: submit → conditions with confidence bars.
6. Medicine: search *paracetamol* → instant knowledge-base card; save it.
7. Doctor: submit symptoms → specialty recommendation.
8. Appointments: book, then cancel.
9. Profile: change phone, add a medical-history entry.
10. Admin (`admin@healthcare.ai`): stats, deactivate a user, browse usage/prompts/logs.
