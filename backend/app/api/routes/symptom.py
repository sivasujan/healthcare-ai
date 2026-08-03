"""Symptom analysis API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.symptom import run_symptom_analysis
from app.api.deps import enforce_rate_limit
from app.auth import get_current_user
from app.core.logging import get_logger
from app.database import get_db
from app.middleware.prompt_injection import assert_prompt_safe
from app.models import SavedSearch, User
from app.schemas.common import ApiResponse
from app.schemas.symptom import SymptomAnalyzeRequest, SymptomAnalysisResult
from app.services.user_service import UserService

router = APIRouter(prefix="/symptom", tags=["Symptom Analysis"])

logger = get_logger("api.symptom")


@router.post(
    "/analyze",
    response_model=ApiResponse[SymptomAnalysisResult],
    dependencies=[Depends(enforce_rate_limit)],
)
def analyze(
    payload: SymptomAnalyzeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[SymptomAnalysisResult]:
    """Analyze symptoms and return conditions, severity and recommendations."""
    assert_prompt_safe(payload.symptoms)

    profile = UserService.profile_dict(user)
    profile.update(
        {
            "age": payload.age if payload.age is not None else profile.get("age"),
            "gender": payload.gender or profile.get("gender"),
            "medical_history": payload.medical_history or profile.get("medical_history"),
            "allergies": payload.allergies or profile.get("allergies"),
            "current_medications": payload.current_medications
            or profile.get("current_medications"),
        }
    )

    context_parts = [
        payload.symptoms,
        f"age: {payload.age}" if payload.age is not None else "",
        f"gender: {payload.gender}" if payload.gender else "",
        f"duration: {payload.duration}" if payload.duration else "",
        f"medical history: {payload.medical_history}" if payload.medical_history else "",
        f"medications: {payload.current_medications}" if payload.current_medications else "",
        f"allergies: {payload.allergies}" if payload.allergies else "",
        f"lifestyle: {payload.lifestyle}" if payload.lifestyle else "",
        f"smoking: {payload.smoking}" if payload.smoking else "",
        f"alcohol: {payload.alcohol}" if payload.alcohol else "",
        f"exercise: {payload.exercise}" if payload.exercise else "",
    ]
    full_message = "\n".join(part for part in context_parts if part)

    _, data, model = run_symptom_analysis(db, user.id, full_message, profile)

    db.add(
        SavedSearch(
            user_id=user.id,
            search_type="symptom",
            query=payload.symptoms[:500],
            result_summary=str(data.get("overall_severity", ""))[:500],
        )
    )
    db.commit()

    return ApiResponse(success=True, data=SymptomAnalysisResult(**data))
