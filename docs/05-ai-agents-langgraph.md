# 05 — AI Agents & LangGraph

## The agent graph

All structured AI features are LangGraph nodes connected in a router graph (`backend/app/agents/graph.py`):

```
                    ┌──────────────────────────┐
   user message ──▶ │     IntentDetector       │
                    └────────────┬─────────────┘
                                 │ intent (or force_intent)
          ┌──────────┬───────────┼───────────┬───────────┬──────────┐
          ▼          ▼           ▼           ▼           ▼          ▼
      symptom    medicine    doctor     emergency   appointment  general
      agent      agent       agent      agent       agent        chat
          └──────────┬───────────┴───────────┴───────────┴──────────┘
                     ▼
               persist + respond
```

## Files

| File | Responsibility |
| --- | --- |
| `agents/base.py` | `AgentState` TypedDict, `new_agent_state()`, `EMERGENCY_KEYWORDS`, shared prompt helpers |
| `agents/intent.py` | `IntentDetector` — intent classification (regex first, model fallback with JSON parsing) |
| `agents/symptom.py` | `run_symptom_analysis` — conditions, confidence, severity, recommendations, doctor advice |
| `agents/medicine.py` | `run_medicine_info` — medicine facts (summary fields) |
| `agents/doctor.py` | `run_doctor_recommendation` — specialty, urgency, prep tips, nearby hospitals |
| `agents/emergency.py` | `run_emergency_check` — red-flag detection, immediate actions, emergency number |
| `agents/appointment.py` | `run_appointment_agent` — books an appointment from natural language (date/time parsing) |
| `agents/general.py` | general conversation with history |
| `agents/graph.py` | `build_agent_graph()` — compiled LangGraph, `run_agent_graph(state, force_intent=...)` |

## Agent contract

Every agent function follows the same signature:

```python
def run_<agent>(db, user_id, user_message, profile) -> tuple[str, dict, str]:
    # 1. build system prompt (healthcare-tuned, JSON schema for structured agents)
    # 2. router.chat(messages)  → ModelCall
    # 3. parse/validate JSON (fallback to regex extraction)
    # 4. persist ModelUsage row
    # 5. return (human_response, data_dict, model_used)
```

Structured agents instruct the model to return strict JSON matching their Pydantic schema; parsing failures fall back to regex extraction so the feature degrades gracefully instead of erroring.

## Important

- `AgentState` **must** be a `TypedDict` — LangGraph validates channel types at runtime.
- The chat route passes `force_intent` to `run_agent_graph` so structured intents never re-classify (faster + cheaper).
- Emergency keywords are matched **before** the model call for instant safety responses.
