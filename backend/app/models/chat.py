"""Chat and Message ORM models (conversation history)."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.user import utcnow


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title = Column(String(255), default="New Chat", nullable=False)
    agent = Column(String(50), default="general", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    user = relationship("User", back_populates="chats")
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.id",
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(
        Integer, ForeignKey("chats.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    agent = Column(String(50), nullable=True)  # agent that produced the reply
    model = Column(String(100), nullable=True)  # model used
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    chat = relationship("Chat", back_populates="messages")
