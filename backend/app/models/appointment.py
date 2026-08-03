"""Appointment ORM model."""

from datetime import date, datetime, time, timezone

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.user import utcnow

APPOINTMENT_STATUSES = ("scheduled", "confirmed", "cancelled", "completed")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title = Column(String(255), nullable=False)
    doctor_name = Column(String(120), nullable=False)
    specialty = Column(String(120), nullable=False)
    hospital = Column(String(255), nullable=True)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(String(20), default="scheduled", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    user = relationship("User", back_populates="appointments")
