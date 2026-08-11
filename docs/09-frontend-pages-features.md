# 09 — Frontend Pages & Features

All dashboard pages are protected (`RequireAuth` in `app/dashboard/layout.tsx`) and wrapped in the dashboard shell (sidebar + header + theme toggle).

| Route | Page | Description |
| --- | --- | --- |
| `/` | Landing | Hero, features, how-it-works, agents, stats, testimonials, FAQ |
| `/login` | Login | Email/password, demo credentials hint |
| `/register` | Register | Full name, email, password, phone (optional) |
| `/forgot-password` | Reset | Request + confirm reset token |
| `/dashboard` | Home | Greeting, health stat cards, quick actions to each tool, recent chats, appointments, saved searches |
| `/dashboard/chat` | AI Chat | New chat: streaming, voice input, suggestion chips, stop/regenerate, clear |
| `/dashboard/chat/[id]` | Chat detail | Loads chat history, continues streaming in the same conversation |
| `/dashboard/symptom` | Symptom Analyzer | Multi-field form → conditions/severity/recommendations cards |
| `/dashboard/medicine` | Medicine | Instant local search + AI fallback, save/unsave list |
| `/dashboard/doctor` | Doctor | Symptom form → specialty, urgency, prep tips, hospitals |
| `/dashboard/emergency` | Emergency | Red-flag check → instructions, immediate actions, emergency number |
| `/dashboard/appointments` | Appointments | Book dialog, upcoming vs past/cancelled lists, cancel |
| `/dashboard/profile` | Profile | Personal info, health profile, change password, medical history entries |
| `/dashboard/admin` | Admin | Stats grid, user management, tabs for chats/usage/prompts/logs (admin only) |

## Chat flow detail

1. User sends a message → optimistic user bubble + streaming placeholder.
2. `POST /chat/stream` streams tokens into the assistant bubble.
3. Structured intents (symptom/doctor/emergency) additionally render the `data` payload as cards inside the message.
4. On `done`, the chat list refreshes; on `emergency`, a red banner appears with dismiss.
5. **Regenerate** re-sends the last user message; **Stop** aborts the fetch; **Clear** deletes the chat.

## Voice input

`chat-input.tsx` uses the Web Speech API (`SpeechRecognition`/`webkitSpeechRecognition`) for dictation — works in Chrome/Edge; shows a toast in unsupported browsers.

## Theme

`theme-toggle.tsx` + `next-themes`: light/dark/system with class-based dark mode. The dashboard shell, landing and all cards adapt via CSS variables.

## Empty & error states

Every page shows skeleton/empty states (dashed cards with icons), loading spinners during AI calls, and toast errors via `errorMessage()` so failures are actionable ("Cannot reach the server. Is the backend running?").
