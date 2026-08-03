"""Appointment assistant agent node (LangGraph).

Note: the Appointment agent helps *describe* appointment actions in chat; the
actual CRUD operations are performed through the REST API endpoints
(``/api/appointments/*``).
"""

from app.agents.base import AgentState, BaseAgent, new_agent_state
from app.ai.json_utils import get_text_field
from app.core.logging import get_logger

logger = get_logger("agents.appointment")


class AppointmentAgent(BaseAgent):
    """Assists with appointment scheduling information and reminders."""

    name = "appointment"
    prompt_template = "appointment_agent"

    def run(self, state: AgentState) -> AgentState:
        messages = self._build_messages(state, state.get("user_message", ""))
        call = self._call_model(state, messages)
        parsed, raw = self.extract_json_or_fallback(call.content, call.content)

        state["model"] = call.model
        state["data"] = {
            "action": get_text_field(parsed, "action", "info"),
            "summary": get_text_field(parsed, "summary", raw),
            "needs_more_info": parsed.get("needs_more_info", []) if parsed else [],
            "appointment_details": parsed.get("appointment_details") if parsed else None,
            "reminder": get_text_field(parsed, "reminder"),
        }
        state["response"] = raw
        return state


def run_appointment_agent(
    db, user_id, user_message: str, history: list | None = None
) -> tuple[str, dict, str]:
    agent = AppointmentAgent()
    state = new_agent_state(
        user_message=user_message, user_id=user_id, history=history or [], db=db
    )
    agent.run(state)
    return state["response"], state["data"], state["model"]
