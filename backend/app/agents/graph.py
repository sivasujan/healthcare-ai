"""LangGraph orchestration for the AI multi-agent system.

Flow::

    START
      |
      v
    intent_node (IntentDetector)
      |
      v
    route (conditional edge on intent)
      |----> symptom_node
      |----> medicine_node
      |----> doctor_node
      |----> emergency_node
      |----> appointment_node
      |----> general_node
      |
      v
    END

Every agent node calls the central Model Router; the router calls OpenRouter.
"""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.appointment import AppointmentAgent
from app.agents.base import AgentState, new_agent_state
from app.agents.doctor import DoctorRecommendationAgent
from app.agents.emergency import EmergencyAgent
from app.agents.general import GeneralAgent
from app.agents.intent import IntentDetector
from app.agents.medicine import MedicineAgent
from app.agents.symptom import SymptomAnalysisAgent

AGENT_MAP = {
    "symptom_analysis": "symptom_node",
    "medicine": "medicine_node",
    "doctor": "doctor_node",
    "emergency": "emergency_node",
    "appointment": "appointment_node",
    "general": "general_node",
}


def _build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("intent_node", IntentDetector().run)
    graph.add_node("symptom_node", SymptomAnalysisAgent().run)
    graph.add_node("medicine_node", MedicineAgent().run)
    graph.add_node("doctor_node", DoctorRecommendationAgent().run)
    graph.add_node("emergency_node", EmergencyAgent().run)
    graph.add_node("appointment_node", AppointmentAgent().run)
    graph.add_node("general_node", GeneralAgent().run)

    def route(state: AgentState) -> Literal[
        "symptom_node", "medicine_node", "doctor_node",
        "emergency_node", "appointment_node", "general_node",
    ]:
        return AGENT_MAP.get(state.get("intent", "general"), "general_node")

    graph.add_edge(START, "intent_node")
    graph.add_conditional_edges("intent_node", route, list(AGENT_MAP.values()))
    for node in AGENT_MAP.values():
        graph.add_edge(node, END)

    return graph


compiled_graph = _build_graph().compile()


def run_agent_graph(
    user_message: str,
    *,
    db=None,
    user_id=None,
    profile: dict | None = None,
    history: list | None = None,
    force_intent: str | None = None,
) -> AgentState:
    """Execute the full agent pipeline for a user message.

    ``force_intent`` lets callers skip intent detection (e.g. dedicated
    endpoints such as ``/api/symptom/analyze`` that already know the intent).
    """
    state = new_agent_state(
        user_message=user_message,
        user_id=user_id,
        profile=profile or {},
        history=history or [],
        db=db,
        intent=force_intent or "",
    )
    if force_intent:
        state["agent_name"] = AGENT_MAP.get(force_intent, "general_node")
        return compiled_graph.invoke(state)
    return compiled_graph.invoke(state)
