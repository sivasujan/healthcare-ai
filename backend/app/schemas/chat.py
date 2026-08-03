"""Chat related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatCreateRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    agent: Optional[str] = "general"


class ChatRenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    agent: Optional[str] = None
    model: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatOut(BaseModel):
    id: int
    title: str
    agent: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatDetailOut(ChatOut):
    messages: list[MessageOut] = []


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    chat_id: Optional[int] = None
    agent: Optional[str] = None


class StreamChunk(BaseModel):
    token: str


class ChatStreamEnd(BaseModel):
    chat_id: int
    message_id: int
    agent: str
    model: str
