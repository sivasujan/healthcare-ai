"""SystemLog ORM model (request + error logging)."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base
from app.models.user import utcnow


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), default="info", nullable=False)  # info | warning | error
    event = Column(String(120), nullable=False)  # request | prompt | model | error
    method = Column(String(10), nullable=True)
    path = Column(String(255), nullable=True)
    user_id = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
