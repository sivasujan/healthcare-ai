"""Admin panel Pydantic schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.schemas.auth import UserPublic
from app.schemas.chat import ChatOut


class AdminDashboardStats(BaseModel):
    total_users: int
    total_chats: int
    total_messages: int
    total_appointments: int
    active_appointments: int
    total_searches: int
    total_prompts: int


class UserRow(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class ChatLogRow(BaseModel):
    id: int
    user_id: int
    user_email: Optional[str] = None
    title: str
    agent: str
    message_count: int
    created_at: datetime


class ModelUsageRow(BaseModel):
    id: int
    model: str
    tier: Optional[str] = None
    agent: Optional[str] = None
    total_tokens: int
    cost_usd: float
    success: int
    created_at: datetime


class PromptLogRow(BaseModel):
    id: int
    agent: Optional[str] = None
    model: Optional[str] = None
    prompt: str
    created_at: datetime


class SystemHealth(BaseModel):
    status: str
    database: str
    ai_configured: bool
    version: str
