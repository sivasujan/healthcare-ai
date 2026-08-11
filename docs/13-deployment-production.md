# 13 — Deployment & Production

## Build the frontend

```powershell
cd frontend
npm run build     # Next.js production build (Turbopack)
npm run start     # serves on :3000
```

Set `NEXT_PUBLIC_API_URL` to the production API URL in `frontend/.env.production`.

## Run the backend in production

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

Add `--reload` only in development.

## Security hardening checklist

- [ ] Generate a strong `SECRET_KEY` (`python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Change `ADMIN_EMAIL`/`ADMIN_PASSWORD` to real admin credentials (or disable seeding)
- [ ] Put both API keys in a secret manager; never commit `.env`
- [ ] Add your domain(s) to `CORS_ORIGINS` (JSON list)
- [ ] Serve over **HTTPS** (reverse proxy: nginx/Caddy/Cloudflare)
- [ ] Replace the in-memory rate limiter with a Redis-backed limiter if multi-worker
- [ ] Consider PostgreSQL: set `DATABASE_URL=postgresql+psycopg://user:pass@host/db` and run `alembic upgrade head`
- [ ] Keep `DEBUG=false`

## Reverse proxy example (nginx)

```nginx
server {
    listen 443 ssl;
    server_name assist.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

> Note: the chat SSE stream is `fetch`-based (POST), so standard proxy buffering is fine, but disable response buffering for `/api/chat/stream` if tokens feel delayed.

## Process management

Use a process manager to keep both services alive (Windows: NSSM/WinSW; Linux: systemd). Example systemd units:

```ini
# /etc/systemd/system/mediback.service
[Service]
WorkingDirectory=/opt/health-care-project/backend
ExecStart=/opt/health-care-project/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
```

```ini
# /etc/systemd/system/medifront.service
[Service]
WorkingDirectory=/opt/health-care-project/frontend
ExecStart=/usr/bin/npm run start
Restart=always
```

## Logs

- Development logs: `%TEMP%\hc_backend.log`, `%TEMP%\hc_frontend.log` (via `run.ps1`).
- App-level logs also persist to the `system_logs` table → Admin panel → System logs.
- Enable request logging middleware in production to audit traffic.

## Known production considerations

- Free OpenRouter models share rate pools — the tier chain handles 429s, but consider BYOK or paid models for sustained load.
- Gemini model names change over time; monitor provider deprecation notices and update `GEMINI_MODEL`.
- Token usage/cost accumulate in `model_usage` — prune or archive periodically.
