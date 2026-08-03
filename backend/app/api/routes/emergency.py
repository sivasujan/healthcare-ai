"""Emergency detection API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.emergency import run_emergency_check
from app.api.deps import enforce_rate_limit
from app.auth import get_current_user
from app.core.logging import get_logger
from app.database import get_db
from app.middleware.prompt_injection import assert_prompt_safe
from app.models import SavedSearch, User
from app.schemas.common import ApiResponse
from app.schemas.emergency import EmergencyCheckRequest, EmergencyCheckResult
from app.services.user_service import UserService

router = APIRouter(prefix="/emergency", tags=["Emergency"])

logger = get_logger("api.emergency")


@router.post(
    "/check",
    response_model=ApiResponse[EmergencyCheckResult],
    dependencies=[Depends(enforce_rate_limit)],
)
def check(
    payload: EmergencyCheckRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[EmergencyCheckResult]:
    """Check symptoms for emergency red flags and give immediate advice."""
    assert_prompt_safe(payload.symptoms)

    profile = UserService.profile_dict(user)
    profile.update(
        {
            "age": payload.age if payload.age is not None else profile.get("age"),
            "medical_history": payload.medical_history or profile.get("medical_history"),
            "current_medications": payload.current_medications
            or profile.get("current_medications"),
        }
    )

    context_parts = [
        payload.symptoms,
        f"age: {payload.age}" if payload.age is not None else "",
        f"medical history: {payload.medical_history}" if payload.medical_history else "",
        f"medications: {payload.current_medications}" if payload.current_medications else "",
    ]
    full_message = "\n".join(part for part in context_parts if part)

    _, data, model = run_emergency_check(db, user.id, full_message, profile)

    db.add(
        SavedSearch(
            user_id=user.id,
            search_type="emergency",
            query=payload.symptoms[:500],
            result_summary="emergency" if data.get("emergency_detected") else "no-emergency",
        )
    )
    db.commit()

    return ApiResponse(success=True, data=EmergencyCheckResult(**data))
