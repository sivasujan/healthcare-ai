"""Doctor Recommendation agent node (LangGraph)."""

from app.agents.base import AgentState, BaseAgent, new_agent_state
from app.ai.json_utils import get_list_field, get_text_field
from app.core.logging import get_logger

logger = get_logger("agents.doctor")

DISCLAIMER = (
    "This recommendation is for guidance only and is not a substitute for "
    "professional medical evaluation. Always consult a qualified healthcare provider."
)


class DoctorRecommendationAgent(BaseAgent):
    """Recommends the appropriate medical specialty for the user."""

    name = "doctor"
    prompt_template = "doctor_recommendation"
    requires_json = True

    def run(self, state: AgentState) -> AgentState:
        messages = self._build_messages(state, state.get("user_message", ""))
        call = self._call_model(state, messages)
        parsed, raw = self.extract_json_or_fallback(call.content, call.content)

        state["model"] = call.model
        state["data"] = {
            "model": call.model,
            "specialty": get_text_field(parsed, "specialty", "General Physician"),
            "reason": get_text_field(parsed, "reason", ""),
            "consultation_type": get_text_field(parsed, "consultation_type", "in-person"),
            "urgency": get_text_field(parsed, "urgency", "routine"),
            "preparation_tips": get_list_field(parsed, "preparation_tips"),
            "nearby_hospitals": get_list_field(parsed, "nearby_hospitals"),
            "disclaimer": get_text_field(parsed, "disclaimer", DISCLAIMER),
        }
        state["response"] = raw
        return state


def run_doctor_recommendation(
    db, user_id, symptoms: str, profile: dict
) -> tuple[str, dict, str]:
    agent = DoctorRecommendationAgent()
    state = new_agent_state(user_message=symptoms, user_id=user_id, profile=profile, db=db)
    agent.run(state)
    return state["response"], state["data"], state["model"]
