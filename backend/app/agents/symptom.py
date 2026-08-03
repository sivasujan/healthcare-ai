"""Symptom Analysis agent node (LangGraph)."""

from typing import Any

from app.agents.base import AgentState, BaseAgent, new_agent_state
from app.ai.json_utils import get_list_field, get_text_field
from app.core.logging import get_logger

logger = get_logger("agents.symptom")

DISCLAIMER = (
    "This analysis is for educational purposes only and is not a substitute for "
    "professional medical advice, diagnosis, or treatment. Always consult a "
    "qualified healthcare provider about your symptoms."
)


class SymptomAnalysisAgent(BaseAgent):
    """Analyzes symptoms, estimates severity, and flags emergencies."""

    name = "symptom_analysis"
    prompt_template = "symptom_analysis"
    requires_json = True

    def run(self, state: AgentState) -> AgentState:
        messages = self._build_messages(state, state.get("user_message", ""))
        call = self._call_model(state, messages)
        parsed, raw = self.extract_json_or_fallback(call.content, call.content)

        conditions: list[dict[str, Any]] = []
        for item in parsed.get("possible_conditions", []) if parsed else []:
            if isinstance(item, dict):
                conditions.append(
                    {
                        "name": str(item.get("name", "Unknown")),
                        "confidence": float(item.get("confidence", 0.0) or 0.0),
                        "severity": str(item.get("severity", "low")),
                    }
                )

        emergency = bool(parsed.get("emergency_detected", False)) if parsed else False

        state["model"] = call.model
        state["data"] = {
            "model": call.model,
            "possible_conditions": conditions,
            "overall_severity": get_text_field(parsed, "overall_severity", "low"),
            "recommendations": [
                {"title": str(r.get("title", "")), "detail": str(r.get("detail", ""))}
                for r in parsed.get("recommendations", [])
                if isinstance(r, dict)
            ]
            if parsed
            else [],
            "precautions": get_list_field(parsed, "precautions"),
            "doctor_specialty": get_text_field(parsed, "doctor_specialty", "General Physician"),
            "doctor_reason": get_text_field(parsed, "doctor_reason", "Evaluation by a physician is recommended."),
            "emergency_detected": emergency,
            "emergency_instructions": get_list_field(parsed, "emergency_instructions")
            if emergency
            else None,
            "disclaimer": get_text_field(parsed, "disclaimer", DISCLAIMER),
        }
        state["response"] = raw
        return state


def run_symptom_analysis(
    db, user_id, user_message: str, profile: dict, history: list | None = None
) -> tuple[str, dict, str]:
    """Synchronous entry point used by the REST API."""
    agent = SymptomAnalysisAgent()
    state = new_agent_state(
        user_message=user_message,
        user_id=user_id,
        profile=profile,
        history=history or [],
        db=db,
    )
    agent.run(state)
    return state["response"], state["data"], state["model"]
