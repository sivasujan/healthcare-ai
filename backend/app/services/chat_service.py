"""Chat service: conversation history and chat CRUD."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Chat, Message


class ChatService:
    """Business logic for chats and messages."""

    @staticmethod
    def create_chat(db: Session, user_id: int, title: str = "New Chat", agent: str = "general") -> Chat:
        chat = Chat(user_id=user_id, title=title[:255] or "New Chat", agent=agent)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    @staticmethod
    def get_chat(db: Session, user_id: int, chat_id: int) -> Chat:
        chat = (
            db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
        )
        if chat is None:
            raise NotFoundError("Chat not found")
        return chat

    @staticmethod
    def list_chats(db: Session, user_id: int, limit: int = 50) -> list[Chat]:
        return (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def rename_chat(db: Session, user_id: int, chat_id: int, title: str) -> Chat:
        chat = ChatService.get_chat(db, user_id, chat_id)
        chat.title = title.strip()[:255]
        chat.updated_at = datetime.now(timezone.utc)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    @staticmethod
    def delete_chat(db: Session, user_id: int, chat_id: int) -> None:
        chat = ChatService.get_chat(db, user_id, chat_id)
        db.delete(chat)
        db.commit()

    @staticmethod
    def add_message(
        db: Session,
        chat: Chat,
        *,
        role: str,
        content: str,
        agent: str | None = None,
        model: str | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> Message:
        message = Message(
            chat_id=chat.id,
            role=role,
            content=content,
            agent=agent,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        db.add(message)
        chat.updated_at = datetime.now(timezone.utc)
        db.add(chat)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def history_messages(db: Session, chat_id: int) -> list[dict[str, str]]:
        """Return the raw ``(role, content)`` pairs used for model memory."""
        rows = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.id)
            .limit(40)
            .all()
        )
        return [{"role": m.role, "content": m.content} for m in rows]

    @staticmethod
    def count_messages(db: Session, chat_id: int) -> int:
        return db.query(Message).filter(Message.chat_id == chat_id).count()
