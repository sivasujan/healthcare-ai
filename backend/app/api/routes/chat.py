"""Chat API routes, including server-sent-event (SSE) streaming."""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.general import GeneralAgent
from app.agents.graph import run_agent_graph
from app.agents.intent import IntentDetector
from app.ai.model_router import ModelProviderError, router as ai_router
from app.api.deps import enforce_rate_limit
from app.auth import get_current_user
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.database import get_db
from app.middleware.prompt_injection import assert_prompt_safe
from app.models import Chat, User
from app.schemas.chat import (
    ChatCreateRequest,
    ChatDetailOut,
    ChatOut,
    ChatRenameRequest,
    ChatRequest,
)
from app.schemas.common import ApiResponse
from app.services.chat_service import ChatService
from app.services.user_service import UserService

router = APIRouter(prefix="/chat", tags=["Chat"])

logger = get_logger("api.chat")


def _chat_out(chat: Chat) -> ChatOut:
    return ChatOut(
        id=chat.id,
        title=chat.title,
        agent=chat.agent,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
    )


@router.post(
    "",
    response_model=ApiResponse[ChatOut],
    status_code=201,
    dependencies=[Depends(enforce_rate_limit)],
)
def create_chat(
    payload: ChatCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[ChatOut]:
    """Create a new empty conversation."""
    chat = ChatService.create_chat(
        db, user.id, title=payload.title or "New Chat", agent=payload.agent or "general"
    )
    return ApiResponse(success=True, message="Chat created", data=_chat_out(chat))


@router.get("", response_model=ApiResponse[list[ChatOut]])
def list_chats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[list[ChatOut]]:
    """List the user's chats, most recent first."""
    chats = ChatService.list_chats(db, user.id)
    return ApiResponse(success=True, data=[_chat_out(c) for c in chats])


@router.get("/history/{chat_id}", response_model=ApiResponse[ChatDetailOut])
def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[ChatDetailOut]:
    """Return a chat with all its messages."""
    chat = ChatService.get_chat(db, user.id, chat_id)
    detail = ChatDetailOut(
        id=chat.id,
        title=chat.title,
        agent=chat.agent,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=chat.messages,
    )
    return ApiResponse(success=True, data=detail)


@router.put("/{chat_id}", response_model=ApiResponse[ChatOut])
def rename_chat(
    chat_id: int,
    payload: ChatRenameRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[ChatOut]:
    """Rename a chat."""
    chat = ChatService.rename_chat(db, user.id, chat_id, payload.title)
    return ApiResponse(success=True, message="Chat renamed", data=_chat_out(chat))


@router.delete("/{chat_id}", response_model=ApiResponse[None])
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Delete a chat and all its messages."""
    ChatService.delete_chat(db, user.id, chat_id)
    return ApiResponse(success=True, message="Chat deleted")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _stream_chat(
    db: Session,
    user: User,
    payload: ChatRequest,
) -> AsyncGenerator[str, None]:
    """Execute the agent graph and stream the response to the client.

    Streaming behavior:
    * ``general`` intents stream real tokens from the Model Router.
    * Structured agents (symptom, medicine, doctor, emergency) emit their
      structured ``data`` plus the full text in the ``done`` event.
    * ``emergency`` events are emitted before ``done`` when red flags fire.
    """
    assert_prompt_safe(payload.message)

    chat_id = payload.chat_id
    chat = None
    if chat_id is not None:
        try:
            chat = ChatService.get_chat(db, user.id, chat_id)
        except NotFoundError:
            yield _sse("error", {"message": "Chat not found"})
            return

    if chat is None:
        chat = ChatService.create_chat(db, user.id, agent="general")

    ChatService.add_message(db, chat, role="user", content=payload.message)

    profile = UserService.profile_dict(user)
    history = ChatService.history_messages(db, chat.id)
    if len(history) > 1:
        history = history[:-1]

    # 1. Intent detection (cheap, always via the router)
    intent_state = IntentDetector().run(
        {
            "user_message": payload.message,
            "user_id": user.id,
            "db": db,
        }
    )
    intent = intent_state.get("intent", "general")

    # 2. Stream tokens directly for general conversations
    if intent == "general":
        general = GeneralAgent()
        messages = general._build_messages(
            {"user_message": payload.message, "history": history, "profile": profile, "db": db},
            payload.message,
        )
        streamed_parts: list[str] = []
        model_used = ""
        try:
            async for event in ai_router.chat_stream(messages):
                if event["type"] == "token":
                    streamed_parts.append(event["token"])
                    yield _sse("token", {"token": event["token"]})
                elif event["type"] == "done":
                    model_used = event.get("model", "")
        except Exception as exc:  # noqa: BLE001 - fall back to non-streaming
            logger.warning("Streaming failed, falling back to full response: %s", exc)
            call = ai_router.chat(messages)
            streamed_parts = [call.content]
            model_used = call.model

        response_text = "".join(streamed_parts).strip()
        if not response_text:
            yield _sse("error", {"message": "The model returned an empty response. Please try again."})
            return

        from app.services.logging_service import LoggingService

        LoggingService.log_prompt(
            db,
            agent="general_chat",
            prompt="\n".join(m["content"] for m in messages),
            response=response_text,
            model=model_used,
            user_id=user.id,
        )

        saved = ChatService.add_message(
            db, chat, role="assistant", content=response_text, agent="general_chat", model=model_used
        )
    else:
        # 3. Structured agents run through the LangGraph pipeline
        state = run_agent_graph(
            payload.message,
            db=db,
            user_id=user.id,
            profile=profile,
            history=history,
            force_intent=intent,
        )

        response_text = state.get("response", "")
        agent = state.get("agent_name", "general")
        model = state.get("model", "")
        data = state.get("data") or {}

        if agent == "emergency" and data.get("emergency_detected"):
            yield _sse("emergency", data)
        elif agent == "symptom_analysis" and data.get("emergency_detected"):
            yield _sse("emergency", data)

        saved = ChatService.add_message(
            db, chat, role="assistant", content=response_text, agent=agent, model=model
        )

    if chat.title == "New Chat":
        chat.title = payload.message.strip().split("\n")[0][:60] or "New Chat"
        db.add(chat)
        db.commit()

    yield _sse(
        "done",
        {
            "chat_id": chat.id,
            "message_id": saved.id,
            "agent": saved.agent or "general_chat",
            "model": saved.model or "",
            "title": chat.title,
            "data": state.get("data") if intent != "general" else {},
        },
    )


@router.post("/stream")
async def stream_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    """Stream an AI response as Server-Sent Events.

    Emits ``emergency`` events for emergency detection, then a final ``done``
    event carrying the full response.
    """
    return StreamingResponse(
        _stream_chat(db, user, payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/send",
    response_model=ApiResponse[dict],
    dependencies=[Depends(enforce_rate_limit)],
)
def send_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[dict]:
    """Send a message and return the (non-streamed) agent response."""
    chat_id = payload.chat_id
    chat = None
    if chat_id is not None:
        try:
            chat = ChatService.get_chat(db, user.id, chat_id)
        except NotFoundError:
            chat = None
    if chat is None:
        chat = ChatService.create_chat(db, user.id, agent="general")

    ChatService.add_message(db, chat, role="user", content=payload.message)
    profile = UserService.profile_dict(user)
    history = ChatService.history_messages(db, chat.id)
    if len(history) > 1:
        history = history[:-1]

    state = run_agent_graph(
        payload.message,
        db=db,
        user_id=user.id,
        profile=profile,
        history=history,
    )

    agent = state.get("agent_name", "general")
    model = state.get("model", "")
    saved = ChatService.add_message(
        db, chat, role="assistant", content=state.get("response", ""), agent=agent, model=model
    )
    if chat.title == "New Chat":
        chat.title = payload.message.strip().split("\n")[0][:60] or "New Chat"
        db.add(chat)
        db.commit()

    return ApiResponse(
        success=True,
        data={
            "chat_id": chat.id,
            "message_id": saved.id,
            "agent": agent,
            "model": model,
            "response": state.get("response", ""),
            "data": state.get("data"),
            "title": chat.title,
        },
    )
