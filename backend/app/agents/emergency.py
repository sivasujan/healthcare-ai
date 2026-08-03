"""Emergency Detection agent node (LangGraph)."""

from app.agents.base import AgentState, BaseAgent, new_agent_state, EMERGENCY_KEYWORDS
from app.ai.json_utils import get_list_field, get_text_field
from app.core.logging import get_logger

logger = get_logger("agents.emergency")

DISCLAIMER = (
    "This is an automated screening, not a medical diagnosis. Call emergency "
    "services immediately if you or someone else experiences severe symptoms."
)

EMERGENCY_NUMBER = "911 (or your local emergency number)"

_DEFAULT_INSTRUCTIONS = [
    "Call emergency services immediately (911 or your local emergency number).",
    "Stay with the person and keep them calm and still.",
    "Do not give food, drink, or medication unless instructed by a professional.",
    "Follow any first-aid training you have; keep the airway clear if the person is unconscious.",
    "Tell the emergency operator the person's symptoms, age, and current medications.",
]


class EmergencyAgent(BaseAgent):
    """Detects emergency symptoms and provides immediate advice."""

    name = "emergency"
    prompt_template = "emergency_detection"
    requires_json = True

    def run(self, state: AgentState) -> AgentState:
        text = state.get("user_message", "").lower()
        keyword_hit = any(kw in text for kw in EMERGENCY_KEYWORDS)

        messages = self._build_messages(state, state.get("user_message", ""))
        call = self._call_model(state, messages)
        parsed, raw = self.extract_json_or_fallback(call.content, call.content)

        detected = bool(parsed.get("emergency_detected", keyword_hit)) if parsed else keyword_hit

        state["model"] = call.model
        state["data"] = {
            "model": call.model,
            "emergency_detected": detected,
            "severity": get_text_field(parsed, "severity", "high" if detected else "none"),
            "conditions": get_list_field(parsed, "conditions"),
            "instructions": get_list_field(parsed, "instructions")
            or (_DEFAULT_INSTRUCTIONS if detected else []),
            "immediate_actions": get_list_field(parsed, "immediate_actions"),
            "nearby_hospitals": get_list_field(parsed, "nearby_hospitals"),
            "emergency_number": get_text_field(parsed, "emergency_number", EMERGENCY_NUMBER),
            "disclaimer": get_text_field(parsed, "disclaimer", DISCLAIMER),
        }
        state["response"] = raw
        return state


def run_emergency_check(db, user_id, symptoms: str, profile: dict) -> tuple[str, dict, str]:
    agent = EmergencyAgent()
    state = new_agent_state(user_message=symptoms, user_id=user_id, profile=profile, db=db)
    agent.run(state)
    return state["response"], state["data"], state["model"]
