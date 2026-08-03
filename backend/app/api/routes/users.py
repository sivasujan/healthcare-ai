"""User profile API routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models import MedicalHistory, User
from app.schemas.common import ApiResponse
from app.schemas.user import (
    ChangePasswordRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/profile", tags=["Profile"])


class MedicalHistoryCreate(BaseModel):
    condition: str = Field(min_length=2, max_length=255)
    diagnosed_year: int | None = Field(default=None, ge=1900, le=2100)
    notes: str | None = None


@router.get("", response_model=ApiResponse[ProfileResponse])
def get_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[ProfileResponse]:
    """Return the authenticated user's profile."""
    return ApiResponse(success=True, data=ProfileResponse.model_validate(user))


@router.put("", response_model=ApiResponse[ProfileResponse])
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[ProfileResponse]:
    """Update personal information and health profile."""
    updated = UserService.update_profile(db, user, payload)
    return ApiResponse(
        success=True, message="Profile updated", data=ProfileResponse.model_validate(updated)
    )


@router.post("/change-password", response_model=ApiResponse[None])
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Change the current user's password."""
    AuthService.change_password(db, user, payload.current_password, payload.new_password)
    return ApiResponse(success=True, message="Password changed successfully")


@router.get("/medical-history", response_model=ApiResponse[list[MedicalHistory]])
def list_medical_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[list[MedicalHistory]]:
    """List the user's medical history entries."""
    rows = (
        db.query(MedicalHistory)
        .filter(MedicalHistory.user_id == user.id)
        .order_by(MedicalHistory.created_at.desc())
        .all()
    )
    return ApiResponse(success=True, data=rows)


@router.post("/medical-history", response_model=ApiResponse[MedicalHistory], status_code=201)
def add_medical_history(
    payload: MedicalHistoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[MedicalHistory]:
    """Add a medical history entry."""
    row = UserService.add_medical_history(
        db, user.id, payload.condition, payload.diagnosed_year, payload.notes
    )
    return ApiResponse(success=True, message="Entry added", data=row)


@router.delete("/medical-history/{entry_id}", response_model=ApiResponse[None])
def delete_medical_history(
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Delete a medical history entry."""
    try:
        UserService.delete_medical_history(db, user.id, entry_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    return ApiResponse(success=True, message="Entry deleted")
