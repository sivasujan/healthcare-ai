"""Appointment service: booking, rescheduling, cancellation, listing."""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Appointment
from app.schemas.appointment import AppointmentBookRequest, AppointmentUpdateRequest

VALID_STATUSES = {"scheduled", "confirmed", "cancelled", "completed"}


class AppointmentService:
    """Business logic for the appointment module."""

    @staticmethod
    def book(db: Session, user_id: int, request: AppointmentBookRequest) -> Appointment:
        appointment = Appointment(
            user_id=user_id,
            title=request.title,
            doctor_name=request.doctor_name,
            specialty=request.specialty,
            hospital=request.hospital,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            notes=request.notes,
            status="scheduled",
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def _get(db: Session, user_id: int, appointment_id: int) -> Appointment:
        appointment = (
            db.query(Appointment)
            .filter(
                Appointment.id == appointment_id,
                Appointment.user_id == user_id,
            )
            .first()
        )
        if appointment is None:
            raise NotFoundError("Appointment not found")
        return appointment

    @staticmethod
    def update(
        db: Session,
        user_id: int,
        appointment_id: int,
        request: AppointmentUpdateRequest,
    ) -> Appointment:
        appointment = AppointmentService._get(db, user_id, appointment_id)
        if request.appointment_date is not None:
            appointment.appointment_date = request.appointment_date
        if request.appointment_time is not None:
            appointment.appointment_time = request.appointment_time
        if request.status is not None:
            if request.status not in VALID_STATUSES:
                raise ValueError(f"Invalid status: {request.status}")
            appointment.status = request.status
        if request.notes is not None:
            appointment.notes = request.notes
        appointment.updated_at = datetime.now(timezone.utc)
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def cancel(db: Session, user_id: int, appointment_id: int) -> Appointment:
        return AppointmentService.update(
            db, user_id, appointment_id, AppointmentUpdateRequest(status="cancelled")
        )

    @staticmethod
    def delete(db: Session, user_id: int, appointment_id: int) -> None:
        appointment = AppointmentService._get(db, user_id, appointment_id)
        db.delete(appointment)
        db.commit()

    @staticmethod
    def list(
        db: Session,
        user_id: int,
        *,
        status: str | None = None,
        limit: int = 100,
    ) -> list[Appointment]:
        query = db.query(Appointment).filter(Appointment.user_id == user_id)
        if status:
            query = query.filter(Appointment.status == status)
        return query.order_by(Appointment.appointment_date.desc()).limit(limit).all()

    @staticmethod
    def upcoming(db: Session, user_id: int) -> list[Appointment]:
        today = date.today()
        return (
            db.query(Appointment)
            .filter(
                Appointment.user_id == user_id,
                Appointment.appointment_date >= today,
                Appointment.status.in_(["scheduled", "confirmed"]),
            )
            .order_by(Appointment.appointment_date.asc())
            .all()
        )

    @staticmethod
    def reminder_text(appointment: Appointment) -> str:
        """Generate a human readable reminder for an appointment."""
        return (
            f"Reminder: You have an appointment with {appointment.doctor_name} "
            f"({appointment.specialty}) on {appointment.appointment_date.isoformat()} "
            f"at {appointment.appointment_time.isoformat()}. "
            f"Please arrive 15 minutes early."
        )
