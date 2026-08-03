"""Appointment API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit
from app.auth import get_current_user
from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models import User
from app.schemas.appointment import (
    AppointmentBookRequest,
    AppointmentOut,
    AppointmentUpdateRequest,
)
from app.schemas.common import ApiResponse
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post(
    "",
    response_model=ApiResponse[AppointmentOut],
    status_code=201,
    dependencies=[Depends(enforce_rate_limit)],
)
def book_appointment(
    payload: AppointmentBookRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[AppointmentOut]:
    """Book a new appointment."""
    appointment = AppointmentService.book(db, user.id, payload)
    return ApiResponse(
        success=True,
        message="Appointment booked successfully",
        data=AppointmentOut.model_validate(appointment),
    )


@router.get("", response_model=ApiResponse[list[AppointmentOut]])
def list_appointments(
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[list[AppointmentOut]]:
    """List the user's appointments, optionally filtered by status."""
    rows = AppointmentService.list(db, user.id, status=status)
    return ApiResponse(
        success=True, data=[AppointmentOut.model_validate(a) for a in rows]
    )


@router.get("/upcoming", response_model=ApiResponse[list[AppointmentOut]])
def upcoming_appointments(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[list[AppointmentOut]]:
    """List upcoming (not cancelled/completed) appointments."""
    rows = AppointmentService.upcoming(db, user.id)
    return ApiResponse(
        success=True, data=[AppointmentOut.model_validate(a) for a in rows]
    )


@router.put("/{appointment_id}", response_model=ApiResponse[AppointmentOut])
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[AppointmentOut]:
    """Update (reschedule or change status of) an appointment."""
    appointment = AppointmentService.update(db, user.id, appointment_id, payload)
    return ApiResponse(
        success=True,
        message="Appointment updated",
        data=AppointmentOut.model_validate(appointment),
    )


@router.post("/{appointment_id}/cancel", response_model=ApiResponse[AppointmentOut])
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[AppointmentOut]:
    """Cancel an appointment."""
    appointment = AppointmentService.cancel(db, user.id, appointment_id)
    return ApiResponse(
        success=True,
        message="Appointment cancelled",
        data=AppointmentOut.model_validate(appointment),
    )


@router.delete("/{appointment_id}", response_model=ApiResponse[None])
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Delete an appointment permanently."""
    try:
        AppointmentService.delete(db, user.id, appointment_id)
    except NotFoundError:
        return ApiResponse(success=False, message="Appointment not found")
    return ApiResponse(success=True, message="Appointment deleted")
