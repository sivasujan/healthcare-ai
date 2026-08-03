"""ModelUsage ORM model (token & cost tracking for the AI Model Router)."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base
from app.models.user import utcnow


class ModelUsage(Base):
    __tablename__ = "model_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    agent = Column(String(50), nullable=True)
    model = Column(String(100), nullable=False)
    tier = Column(String(20), nullable=True)  # primary | secondary | fallback
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Float, nullable=True)
    success = Column(Integer, default=1)  # 1 = success, 0 = failure
    error = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
