"""Medicine information API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.medicine import run_medicine_info
from app.api.deps import enforce_rate_limit
from app.auth import get_current_user
from app.core.logging import get_logger
from app.database import get_db
from app.middleware.prompt_injection import assert_prompt_safe
from app.models import SavedMedicine, SavedSearch, User
from app.schemas.common import ApiResponse
from app.schemas.medicine import (
    MedicineOut,
    MedicineSearchRequest,
    MedicineSearchResult,
    SavedMedicineOut,
)
from app.services.medicine_service import (
    DISCLAIMER as MEDICINE_DISCLAIMER,
    search_knowledge_base,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/medicine", tags=["Medicine"])

logger = get_logger("api.medicine")


@router.post(
    "/search",
    response_model=ApiResponse[MedicineSearchResult],
    dependencies=[Depends(enforce_rate_limit)],
)
def search_medicine(
    payload: MedicineSearchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[MedicineSearchResult]:
    """Search for medicine information.

    Checks the local knowledge base first; falls back to the AI agent.
    """
    assert_prompt_safe(payload.query)
    results = search_knowledge_base(db, payload.query, limit=1)

    db.add(
        SavedSearch(
            user_id=user.id,
            search_type="medicine",
            query=payload.query[:500],
            result_summary="found" if results else "ai-fallback",
        )
    )
    db.commit()

    if results:
        medicine = results[0]
        return ApiResponse(
            success=True,
            data=MedicineSearchResult(
                medicine=MedicineOut.model_validate(medicine),
                summary=None,
                disclaimer=MEDICINE_DISCLAIMER,
                model="local-knowledge-base",
            ),
        )

    profile = UserService.profile_dict(user)
    _, data, model = run_medicine_info(db, user.id, payload.query, profile)
    return ApiResponse(
        success=True,
        data=MedicineSearchResult(
            medicine=None,
            summary=data.get("summary"),
            disclaimer=data.get("disclaimer", MEDICINE_DISCLAIMER),
            model=model,
        ),
    )


@router.get("/search", response_model=ApiResponse[list[MedicineOut]])
def search_medicine_get(
    q: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> ApiResponse[list[MedicineOut]]:
    """Local-only medicine lookup (fast, no AI call)."""
    results = search_knowledge_base(db, q)
    return ApiResponse(
        success=True, data=[MedicineOut.model_validate(m) for m in results]
    )


@router.get("/saved/list", response_model=ApiResponse[list[SavedMedicineOut]])
def list_saved_medicines(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[list[SavedMedicineOut]]:
    """List the user's saved medicines."""
    rows = (
        db.query(SavedMedicine)
        .join(SavedMedicine.medicine)
        .filter(SavedMedicine.user_id == user.id)
        .order_by(SavedMedicine.created_at.desc())
        .all()
    )
    return ApiResponse(
        success=True,
        data=[
            SavedMedicineOut(
                id=row.id,
                medicine_id=row.medicine.id,
                name=row.medicine.name,
                category=row.medicine.category,
                purpose=row.medicine.purpose,
                saved_at=row.created_at,
            )
            for row in rows
        ],
    )


@router.get("/{medicine_id}", response_model=ApiResponse[MedicineOut])
def get_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> ApiResponse[MedicineOut]:
    """Return a single medicine by id."""
    from app.models import Medicine

    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return ApiResponse(success=True, data=MedicineOut.model_validate(medicine))


@router.post("/{medicine_id}/save", response_model=ApiResponse[SavedMedicineOut])
def save_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[SavedMedicineOut]:
    """Save a medicine to the user's saved list."""
    from app.models import Medicine

    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")

    existing = (
        db.query(SavedMedicine)
        .filter(
            SavedMedicine.user_id == user.id,
            SavedMedicine.medicine_id == medicine_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Medicine already saved")

    row = SavedMedicine(user_id=user.id, medicine_id=medicine_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ApiResponse(
        success=True,
        message="Medicine saved",
        data=SavedMedicineOut(
            id=row.id,
            medicine_id=medicine.id,
            name=medicine.name,
            category=medicine.category,
            purpose=medicine.purpose,
            saved_at=row.created_at,
        ),
    )


@router.delete("/{medicine_id}/save", response_model=ApiResponse[None])
def unsave_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Remove a medicine from the user's saved list."""
    row = (
        db.query(SavedMedicine)
        .filter(
            SavedMedicine.user_id == user.id,
            SavedMedicine.medicine_id == medicine_id,
        )
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Saved medicine not found")
    db.delete(row)
    db.commit()
    return ApiResponse(success=True, message="Medicine removed from saved list")


@router.get("/saved/list", response_model=ApiResponse[list[SavedMedicineOut]])
def list_saved_medicines(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[list[SavedMedicineOut]]:
    """List the user's saved medicines."""
    rows = (
        db.query(SavedMedicine)
        .join(SavedMedicine.medicine)
        .filter(SavedMedicine.user_id == user.id)
        .order_by(SavedMedicine.created_at.desc())
        .all()
    )
    return ApiResponse(
        success=True,
        data=[
            SavedMedicineOut(
                id=row.id,
                medicine_id=row.medicine.id,
                name=row.medicine.name,
                category=row.medicine.category,
                purpose=row.medicine.purpose,
                saved_at=row.created_at,
            )
            for row in rows
        ],
    )
