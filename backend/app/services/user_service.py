"""User profile service."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import MedicalHistory, User
from app.schemas.user import ProfileUpdateRequest


class UserService:
    """Business logic for profile and medical history management."""

    @staticmethod
    def get_profile(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise NotFoundError("User not found")
        return user

    @staticmethod
    def update_profile(db: Session, user: User, request: ProfileUpdateRequest) -> User:
        if request.full_name is not None:
            user.full_name = request.full_name.strip()
        if request.phone is not None:
            user.phone = request.phone
        if request.preferred_language is not None:
            user.preferred_language = request.preferred_language
        if request.dark_mode is not None:
            user.dark_mode = request.dark_mode

        if request.profile is not None:
            p = request.profile
            if p.age is not None:
                user.age = p.age
            if p.gender is not None:
                user.gender = p.gender
            if p.height_cm is not None:
                user.height_cm = p.height_cm
            if p.weight_kg is not None:
                user.weight_kg = p.weight_kg
            if p.blood_group is not None:
                user.blood_group = p.blood_group
            if p.medical_history is not None:
                user.medical_history = p.medical_history
            if p.allergies is not None:
                user.allergies = p.allergies
            if p.current_medications is not None:
                user.current_medications = p.current_medications

        user.updated_at = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def add_medical_history(db: Session, user_id: int, condition: str, year: int | None, notes: str | None) -> MedicalHistory:
        row = MedicalHistory(
            user_id=user_id, condition=condition.strip(), diagnosed_year=year, notes=notes
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def delete_medical_history(db: Session, user_id: int, entry_id: int) -> None:
        row = db.query(MedicalHistory).filter(
            MedicalHistory.id == entry_id, MedicalHistory.user_id == user_id
        ).first()
        if row is None:
            raise NotFoundError("Medical history entry not found")
        db.delete(row)
        db.commit()

    @staticmethod
    def profile_dict(user: User) -> dict:
        """Build the health-profile dict passed to AI agents."""
        return {
            "age": user.age,
            "gender": user.gender,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "medical_history": user.medical_history,
            "allergies": user.allergies,
            "current_medications": user.current_medications,
            "blood_group": user.blood_group,
        }
