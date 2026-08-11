# 07 — API Reference

Base URL: `http://localhost:8000/api`. All endpoints (except auth/health) require `Authorization: Bearer <access_token>`. Responses use the `ApiResponse` envelope. Interactive docs: `/docs`.

## Auth

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| POST | `/auth/register` | `{full_name, email, password, phone?}` | Register + tokens |
| POST | `/auth/login` | `{email, password}` | Login + tokens |
| POST | `/auth/refresh` | `{refresh_token}` | New access/refresh pair |
| POST | `/auth/forgot-password` | `{email}` | Request reset (dev: prints token) |
| POST | `/auth/reset-password` | `{email, reset_token, new_password}` | Reset password |

Login response `data`: `{access_token, refresh_token, token_type, expires_in, user}`.

## Chat

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| GET | `/chat` | — | List my chats |
| POST | `/chat` | `{title}` | Create empty chat |
| GET | `/chat/{id}` | — | Chat detail with messages |
| POST | `/chat/send` | `{message, chat_id?}` | Non-streaming reply (agent + data + response) |
| POST | `/chat/stream` | `{message, chat_id?}` | **SSE streaming** reply (token/done/emergency/error events) |
| GET | `/chat/history/{id}` | — | Chat with messages |
| DELETE | `/chat/{id}` | — | Delete chat |

## Symptom

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| POST | `/symptom/analyze` | `{symptoms, age?, gender?, height_cm?, weight_kg?, duration?, medical_history?, current_medications?, allergies?, lifestyle?, smoking?, alcohol?, exercise?}` | Full analysis |

`data`: `{possible_conditions:[{name,confidence,severity}], overall_severity, recommendations:[{title,detail}], precautions[], doctor_specialty, doctor_reason, emergency_detected, emergency_instructions?, disclaimer, model}`

## Medicine

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| GET | `/medicine/search?q=` | — | Local knowledge base (fast, no AI) |
| POST | `/medicine/search` | `{query}` | Local first, AI fallback |
| GET | `/medicine/saved/list` | — | Saved medicines |
| GET | `/medicine/{id}` | — | Medicine by id |
| POST | `/medicine/{id}/save` | — | Save medicine |
| DELETE | `/medicine/{id}/save` | — | Unsave |

## Doctor

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| POST | `/doctor/recommend` | `{symptoms, age?, gender?, medical_history?, current_medications?}` | Specialty recommendation |

`data`: `{specialty, reason, consultation_type, urgency, preparation_tips[], nearby_hospitals[], disclaimer, model}`

## Emergency

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| POST | `/emergency/check` | `{symptoms, age?, medical_history?, current_medications?}` | Red-flag check |

`data`: `{emergency_detected, severity, conditions[], instructions[], immediate_actions[], nearby_hospitals[], emergency_number, disclaimer, model}`

## Appointments

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| GET | `/appointments?status=` | — | List (optional status filter) |
| POST | `/appointments` | `{title, doctor_name, specialty, hospital?, appointment_date, appointment_time, notes?}` | Book |
| GET | `/appointments/upcoming` | — | Upcoming only |
| PUT | `/appointments/{id}` | `{appointment_date?, appointment_time?, status?, notes?}` | Reschedule/update |
| POST | `/appointments/{id}/cancel` | — | Cancel |
| DELETE | `/appointments/{id}` | — | Delete |

## Profile

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| GET | `/profile` | — | My profile |
| PUT | `/profile` | `{full_name?, phone?, preferred_language?, profile:{...health fields}}` | Update profile |
| POST | `/profile/change-password` | `{current_password, new_password}` | Change password |
| GET | `/profile/medical-history` | — | List entries |
| POST | `/profile/medical-history` | `{condition, diagnosed_year?, notes?}` | Add entry |
| DELETE | `/profile/medical-history/{id}` | — | Delete entry |

## Admin (admin role)

| Method | Path | Description |
| --- | --- | --- |
| GET | `/admin/dashboard` | Platform stats |
| GET | `/admin/users` | All users |
| POST | `/admin/users/{id}/toggle` | Activate/deactivate |
| GET | `/admin/chat-logs` | All chats |
| GET | `/admin/system-logs` | System logs |
| GET | `/admin/model-usage` | Per-call AI usage |
| GET | `/admin/model-usage/summary` | Aggregated by model |
| GET | `/admin/prompt-logs` | Prompt history |
| GET | `/admin/health` | System health |

## Misc

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Public health check |
