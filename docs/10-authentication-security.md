# 10 — Authentication & Security

## How auth works

- Passwords are hashed with **bcrypt** (`app/auth.py`).
- Login/register return a JWT pair: **access** (24 h, HS256, signed with `SECRET_KEY`) and **refresh** (7 days).
- The access token is stored in `localStorage` by the frontend and attached as `Authorization: Bearer …` by the axios interceptor (`lib/api.ts`).
- On a 401 response, the interceptor automatically calls `/auth/refresh` once and retries the original request; if refresh fails it clears tokens (→ user is redirected to login).
- Admin routes additionally require `get_current_admin` (checks `is_admin`).

## Security layers

| Layer | Where | What it does |
| --- | --- | --- |
| Password policy | `AuthService` | Min 8 chars, must contain letter + number |
| JWT validation | `app/auth.py` | Signature + expiry verification, user still active |
| Rate limiting | `app/api/deps.py` | 60 AI requests / minute / user (in-memory sliding window) |
| Prompt injection guard | `app/middleware/prompt_injection.py` | `assert_prompt_safe()` blocks known jailbreak patterns before any AI call |
| Input validation | Pydantic v2 | Strict schemas, length/range limits on every field |
| CORS | `app/config.py` | Only localhost:3000 origins allowed by default |
| Secrets | `.env` (gitignored) | API keys and `SECRET_KEY` never committed; `.env.example` has placeholders |
| Logging | middleware + core/logging | Request logs (method, path, status, latency) + system log table |

## Frontend guard

- `components/shared/require-auth.tsx` redirects to `/login` when no valid session exists.
- The admin page renders an "Admins only" screen for non-admin users.
- `errorMessage()` never leaks raw server details beyond what the API returns.

## Password reset flow

1. `POST /auth/forgot-password` generates a reset token (stored hashed) with a 30-minute expiry.
2. In development the token is logged/returned so the flow is testable without email.
3. `POST /auth/reset-password` verifies token + expiry, then sets the new password.

## Production checklist (see doc 13)

- Generate a strong random `SECRET_KEY` (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
- Replace demo admin credentials
- Serve the frontend over HTTPS; add the domain to `CORS_ORIGINS`
- Persist rate limits (current limiter is in-memory → resets on restart)
- Rotate API keys in a secret manager
