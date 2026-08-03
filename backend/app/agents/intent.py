"""Intent Detection agent node.

Classifies a user message into one of: symptom_analysis, medicine, doctor,
emergency, appointment, general. A keyword pre-check catches emergencies
without any model call (cheap and reliable); the model performs the
classification otherwise, with a regex fallback for resilience.
"""

import re
from typing import Optional

from app.agents.base import AgentState, BaseAgent, new_agent_state, EMERGENCY_KEYWORDS
from app.ai.json_utils import extract_json
from app.ai.model_router import ModelProviderError, router
from app.core.logging import get_logger

logger = get_logger("agents.intent")

_SYMPTOM_RE = re.compile(
    r"\b(symptom|pain|ache|hurt|fever|nausea|vomit|dizzy|dizziness|headache|cough|"
    r"rash|fatigue|sore|swelling|bleed|infection|feel(ing)?\s+(bad|sick|unwell|ill))\b",
    re.I,
)
_MEDICINE_RE = re.compile(
    r"\b(medicine|medication|tablet|drug|dosage|dose|pill|antibiotic|paracetamol|"
    r"ibuprofen|side\s?effects?|interaction|prescription)\b",
    re.I,
)
_DOCTOR_RE = re.compile(
    r"\b(doctor|specialist|physician|consult|cardio\w*|derma\w*|ortho\w*|neuro\w*|"
    r"pediatr\w*|gynec\w*|ophthalm\w*|see\s+a|visit\s+a)\b",
    re.I,
)
_APPOINTMENT_RE = re.compile(
    r"\b(appointment|book|schedule|reschedule|cancel\s+appointment|booking)\b",
    re.I,
)

SIMPLE_AGENT_PROMPTS: dict[str, str] = {
    "symptom_analysis": "symptom_analysis",
    "medicine": "medicine_info",
    "doctor": "doctor_recommendation",
    "emergency": "emergency_detection",
    "appointment": "appointment_agent",
    "general": "general_chat",
}


class IntentDetector(BaseAgent):
    """Detects the user's intent and routes to the right agent."""

    name = "intent_detector"
    prompt_template = "intent_detection"

    def _keyword_emergency(self, text: str) -> bool:
        lowered = text.lower()
        return any(kw in lowered for kw in EMERGENCY_KEYWORDS)

    def _regex_intent(self, text: str) -> str:
        scores = {
            "symptom_analysis": len(_SYMPTOM_RE.findall(text)),
            "medicine": len(_MEDICINE_RE.findall(text)),
            "doctor": len(_DOCTOR_RE.findall(text)),
            "appointment": len(_APPOINTMENT_RE.findall(text)),
        }
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "general"

    def _classify_with_model(self, state: AgentState) -> str:
        messages = router.build_messages(
            self.system_prompt,
            history=[],
            user_message=state.get("user_message", ""),
        )
        try:
            call = router.chat(messages, temperature=0.0, max_tokens=64)
            self._record_usage(state, call)
        except ModelProviderError as exc:
            logger.warning("Intent model unavailable, using regex: %s", exc)
            return self._regex_intent(state.get("user_message", ""))
        parsed = extract_json(call.content)
        if parsed and parsed.get("intent") in SIMPLE_AGENT_PROMPTS:
            return parsed["intent"]
        return self._regex_intent(state.get("user_message", ""))

    def run(self, state: AgentState) -> AgentState:
        text = state.get("user_message", "")
        if self._keyword_emergency(text):
            state["intent"] = "emergency"
            state["agent_name"] = "emergency"
            return state
        intent = self._classify_with_model(state)
        state["intent"] = intent
        state["agent_name"] = SIMPLE_AGENT_PROMPTS.get(intent, "general")
        return state


def detect_intent(text: str, db=None, user_id=None, profile=None) -> tuple[str, str]:
    """Convenience helper: returns ``(intent, agent_name)`` synchronously."""
    detector = IntentDetector()
    state = new_agent_state(
        user_message=text, db=db, user_id=user_id, profile=profile or {}
    )
    detector.run(state)
    return state["intent"], state["agent_name"]
