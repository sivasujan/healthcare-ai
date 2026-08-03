"""Admin panel API routes (protected: admin role required)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit
from app.auth import get_current_admin
from app.core.logging import get_logger
from app.database import get_db
from app.models import ModelUsage, PromptHistory, SystemLog, User
from app.schemas.admin import (
    AdminDashboardStats,
    ChatLogRow,
    ModelUsageRow,
    PromptLogRow,
    SystemHealth,
)
from app.schemas.auth import UserPublic
from app.schemas.common import ApiResponse
from app.services.admin_service import AdminService
from app.services.chat_service import ChatService
from app.ai.model_router import router as ai_router

router = APIRouter(prefix="/admin", tags=["Admin"])

logger = get_logger("api.admin")


@router.get("/dashboard", response_model=ApiResponse[AdminDashboardStats])
def dashboard(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> ApiResponse[AdminDashboardStats]:
    """Aggregated statistics for the admin dashboard."""
    return ApiResponse(success=True, data=AdminDashboardStats(**AdminService.dashboard_stats(db)))


@router.get("/users", response_model=ApiResponse[list[UserPublic]])
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> ApiResponse[list[UserPublic]]:
    """List all registered users."""
    users = AdminService.list_users(db)
    return ApiResponse(success=True, data=[UserPublic.model_validate(u) for u in users])


@router.post("/users/{user_id}/toggle", response_model=ApiResponse[UserPublic])
def toggle_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> ApiResponse[UserPublic]:
    """Activate or deactivate a user account."""
    target = db.query(User).filter(User.id == user_id).first()
    if target is None:
        return ApiResponse(success=False, message="User not found")
    if target.id == admin.id:
        return ApiResponse(success=False, message="You cannot deactivate your own account")
    updated = AdminService.set_user_active(db, user_id, not target.is_active)
    return ApiResponse(
        success=True,
        message="User status updated",
        data=UserPublic.model_validate(updated),
    )


@router.get("/chat-logs", response_model=ApiResponse[list[ChatLogRow]])
def chat_logs(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> ApiResponse[list[ChatLogRow]]:
    """Browse all chats across users."""
    rows = AdminService.chat_logs(db)
    data = []
    for chat in rows:
        data.append(
            ChatLogRow(
                id=chat.id,
                user_id=chat.user_id,
                user_email=chat.user.email if chat.user else None,
                title=chat.title,
                agent=chat.agent,
                message_count=ChatService.count_messages(db, chat.id),
                created_at=chat.created_at,
            )
        )
    return ApiResponse(success=True, data=data)


@router.get("/system-logs", response_model=ApiResponse[list[SystemLog]])
def system_logs(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> ApiResponse[list[SystemLog]]:
    """Browse system logs."""
    return ApiResponse(success=True, data=AdminService.system_logs(db))


@router.get("/model-usage", response_model=ApiResponse[list[ModelUsageRow]])
def model_usage(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> ApiResponse[list[ModelUsageRow]]:
    """Browse per-call model usage."""
    rows = AdminService.model_usage(db)
    return ApiResponse(
        success=True,
        data=[
            ModelUsageRow(
                id=r.id,
                model=r.model,
                tier=r.tier,
                agent=r.agent,
                total_tokens=r.total_tokens,
                cost_usd=r.cost_usd,
                success=r.success,
                created_at=r.created_at,
            )
            for r in rows
        ],
    )


@router.get("/model-usage/summary", response_model=ApiResponse[list[dict]])
def model_usage_summary(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> ApiResponse[list[dict]]:
    """Aggregated model usage summary (grouped by model)."""
    return ApiResponse(success=True, data=AdminService.model_usage_summary(db))


@router.get("/prompt-logs", response_model=ApiResponse[list[PromptLogRow]])
def prompt_logs(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> ApiResponse[list[PromptLogRow]]:
    """Browse prompt history."""
    rows = AdminService.prompt_history(db)
    return ApiResponse(
        success=True,
        data=[
            PromptLogRow(
                id=r.id,
                agent=r.agent,
                model=r.model,
                prompt=(r.prompt[:2000] + "...") if len(r.prompt or "") > 2000 else r.prompt,
                created_at=r.created_at,
            )
            for r in rows
        ],
    )


@router.get("/health", response_model=ApiResponse[SystemHealth])
def system_health(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> ApiResponse[SystemHealth]:
    """System health check."""
    return ApiResponse(
        success=True,
        data=SystemHealth(
            status="healthy",
            database="ok",
            ai_configured=ai_router.configured,
            version="1.0.0",
        ),
    )
