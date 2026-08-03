"""Medicine Information agent node (LangGraph)."""

from app.agents.base import AgentState, BaseAgent, new_agent_state
from app.ai.json_utils import get_text_field
from app.core.logging import get_logger

logger = get_logger("agents.medicine")

DISCLAIMER = (
    "This information is for educational purposes only and is not a substitute "
    "for professional medical advice. Never start, stop, or change a medication "
    "without consulting your doctor or pharmacist."
)


class MedicineAgent(BaseAgent):
    """Provides educational medicine information; never prescribes."""

    name = "medicine"
    prompt_template = "medicine_info"
    requires_json = True

    def run(self, state: AgentState) -> AgentState:
        messages = self._build_messages(state, state.get("user_message", ""))
        call = self._call_model(state, messages)
        parsed, raw = self.extract_json_or_fallback(call.content, call.content)

        fields = parsed.get("fields", {}) if parsed else {}
        if not isinstance(fields, dict):
            fields = {}

        state["model"] = call.model
        state["data"] = {
            "summary": get_text_field(parsed, "summary", raw),
            "fields": {
                key: get_text_field(fields, key)
                for key in (
                    "purpose",
                    "uses",
                    "dosage",
                    "warnings",
                    "side_effects",
                    "interactions",
                    "storage",
                    "notes",
                )
            },
            "disclaimer": get_text_field(parsed, "disclaimer", DISCLAIMER),
        }
        state["response"] = raw
        return state


def run_medicine_info(db, user_id, query: str, profile: dict) -> tuple[str, dict, str]:
    agent = MedicineAgent()
    state = new_agent_state(
        user_message=query, user_id=user_id, profile=profile, db=db
    )
    agent.run(state)
    return state["response"], state["data"], state["model"]
