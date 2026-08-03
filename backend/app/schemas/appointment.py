"""Appointment Pydantic schemas."""

from datetime import date, datetime, time
from typing import Literal, Optional

from pydantic import BaseModel, Field

AppointmentStatus = Literal["scheduled", "confirmed", "cancelled", "completed"]


class AppointmentBookRequest(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    doctor_name: str = Field(min_length=2, max_length=120)
    specialty: str = Field(min_length=2, max_length=120)
    hospital: Optional[str] = Field(default=None, max_length=255)
    appointment_date: date
    appointment_time: time
    notes: Optional[str] = None


class AppointmentUpdateRequest(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    title: str
    doctor_name: str
    specialty: str
    hospital: Optional[str] = None
    appointment_date: date
    appointment_time: time
    status: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
