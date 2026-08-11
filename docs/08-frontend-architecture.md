# 08 — Frontend Architecture

## Overview

The frontend is a Next.js 15 App Router application (Turbopack) with TypeScript strict mode and Tailwind CSS v4.

```
frontend/
├── app/
│   ├── layout.tsx            # Root layout (Geist fonts, Providers, navbar/footer)
│   ├── globals.css           # Design tokens (shadcn-style), dark mode, animations
│   ├── page.tsx              # Landing page
│   ├── login | register | forgot-password/
│   └── dashboard/
│       ├── layout.tsx        # RequireAuth + DashboardShell (sidebar/header)
│       ├── page.tsx          # Home: greeting, stats, quick actions
│       ├── chat/ [id]/       # AI chat (SSE streaming)
│       ├── symptom/ medicine/ doctor/ emergency/
│       ├── appointments/ profile/ admin/
├── components/
│   ├── ui/                   # Primitive components (button, card, dialog, select, tabs…)
│   ├── layout/               # navbar, sidebar, footer, dashboard-shell, theme-toggle
│   ├── chat/                 # chat-interface, chat-message, chat-input, agent-results
│   ├── landing/              # landing-sections, animated-background
│   └── shared/               # markdown, require-auth
├── lib/
│   ├── api.ts                # Axios client + JWT refresh interceptor + SSE base
│   ├── auth.tsx              # AuthProvider / useAuth context
│   └── utils.ts              # cn(), initials()
├── providers/providers.tsx   # QueryClient + ThemeProvider + AuthProvider + Toaster
└── types/index.ts            # API types (mirror backend schemas)
```

## Key patterns

- **Data fetching:** TanStack Query (`useQuery`/`useMutation`) for all API data; server state invalidated after mutations.
- **Forms:** react-hook-form + zod for validation on form-heavy pages (login, symptom, doctor, emergency).
- **Auth:** `AuthProvider` loads the profile on mount, exposes `login/register/logout/refreshProfile`; `RequireAuth` redirects unauthenticated users to `/login`; the dashboard layout wraps every page.
- **API client:** `lib/api.ts` — base URL from `NEXT_PUBLIC_API_URL` (default `http://localhost:8000/api`), attaches JWT, transparently refreshes on 401 (one retry), `errorMessage()` helper normalizes errors.
- **Styling:** Tailwind tokens via CSS variables (`--primary`, `--muted`…) with a class-based dark mode (`next-themes`), animations in `globals.css` (typing dots, gradients).

## SSE chat client

`components/chat/chat-interface.tsx` uses `fetch` + `ReadableStream` (not EventSource, so POST works) with:

- `AbortController` for **Stop** during streaming
- incremental `token` event appends
- `done` event finalizes the message (agent/model/data), invalidates the chat list, and navigates to the created chat (`/dashboard/chat/{id}`)
- `emergency` event shows a persistent banner
- one-shot JWT refresh on 401 before reconnecting the stream

## Agent result rendering

Structured agent payloads render as rich cards (`components/chat/agent-results.tsx` and each feature page):

- **conditions** → name, confidence progress bar, severity badge
- **medicine** → labeled sections (uses, dosage, warnings, interactions…)
- **doctor** → specialty, consultation type, urgency, prep tips
- **emergency** → red alert card with immediate actions
