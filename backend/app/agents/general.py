"""General chat agent node (LangGraph)."""

from app.agents.base import AgentState, BaseAgent, new_agent_state
from app.core.logging import get_logger

logger = get_logger("agents.general")


class GeneralAgent(BaseAgent):
    """Handles general questions and fallback conversations."""

    name = "general"
    prompt_template = "general_chat"

    def run(self, state: AgentState) -> AgentState:
        messages = self._build_messages(state, state.get("user_message", ""))
        call = self._call_model(state, messages)
        state["model"] = call.model
        state["data"] = {}
        state["response"] = call.content
        return state


def run_general_chat(
    db, user_id, user_message: str, history: list | None = None, profile: dict | None = None
) -> tuple[str, str]:
    agent = GeneralAgent()
    state = new_agent_state(
        user_message=user_message,
        user_id=user_id,
        history=history or [],
        profile=profile or {},
        db=db,
    )
    agent.run(state)
    return state["response"], state["model"]
