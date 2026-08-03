"""Medicine and SavedMedicine ORM models."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.user import utcnow


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    generic_name = Column(String(255), nullable=True)
    category = Column(String(120), nullable=True)
    purpose = Column(Text, nullable=True)
    uses = Column(Text, nullable=True)
    dosage = Column(Text, nullable=True)
    warnings = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    interactions = Column(Text, nullable=True)
    storage = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String(50), default="knowledge-base", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    saved_by = relationship(
        "SavedMedicine", back_populates="medicine", cascade="all, delete-orphan"
    )


class SavedMedicine(Base):
    __tablename__ = "saved_medicines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    medicine_id = Column(
        Integer, ForeignKey("medicines.id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="saved_medicines")
    medicine = relationship("Medicine", back_populates="saved_by")
