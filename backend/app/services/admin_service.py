"""Admin service: aggregate stats and log browsing."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    Appointment,
    Chat,
    Message,
    ModelUsage,
    PromptHistory,
    SavedSearch,
    SystemLog,
    User,
)


class AdminService:
    """Business logic for the admin panel."""

    @staticmethod
    def dashboard_stats(db: Session) -> dict:
        return {
            "total_users": db.query(User).count(),
            "total_chats": db.query(Chat).count(),
            "total_messages": db.query(Message).count(),
            "total_appointments": db.query(Appointment).count(),
            "active_appointments": db.query(Appointment)
            .filter(Appointment.status.in_(["scheduled", "confirmed"]))
            .count(),
            "total_searches": db.query(SavedSearch).count(),
            "total_prompts": db.query(PromptHistory).count(),
            "total_model_usage_rows": db.query(ModelUsage).count(),
            "total_tokens": db.query(func.coalesce(func.sum(ModelUsage.total_tokens), 0))
            .scalar()
            or 0,
            "total_cost_usd": round(
                db.query(func.coalesce(func.sum(ModelUsage.cost_usd), 0)).scalar() or 0,
                4,
            ),
        }

    @staticmethod
    def list_users(db: Session, limit: int = 100) -> list[User]:
        return db.query(User).order_by(User.created_at.desc()).limit(limit).all()

    @staticmethod
    def set_user_active(db: Session, user_id: int, is_active: bool) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise LookupError("User not found")
        user.is_active = is_active
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def chat_logs(db: Session, limit: int = 200) -> list[Chat]:
        return (
            db.query(Chat)
            .order_by(Chat.updated_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def system_logs(db: Session, limit: int = 200) -> list[SystemLog]:
        return (
            db.query(SystemLog)
            .order_by(SystemLog.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def model_usage(db: Session, limit: int = 200) -> list[ModelUsage]:
        return (
            db.query(ModelUsage)
            .order_by(ModelUsage.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def prompt_history(db: Session, limit: int = 200) -> list[PromptHistory]:
        return (
            db.query(PromptHistory)
            .order_by(PromptHistory.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def model_usage_summary(db: Session) -> list[dict]:
        rows = (
            db.query(
                ModelUsage.model,
                func.count(ModelUsage.id),
                func.sum(ModelUsage.total_tokens),
                func.sum(ModelUsage.cost_usd),
                func.sum(ModelUsage.prompt_tokens),
                func.sum(ModelUsage.completion_tokens),
            )
            .group_by(ModelUsage.model)
            .all()
        )
        return [
            {
                "model": model,
                "calls": count,
                "total_tokens": int(tokens or 0),
                "cost_usd": round(cost or 0, 4),
                "prompt_tokens": int(prompt or 0),
                "completion_tokens": int(completion or 0),
            }
            for model, count, tokens, cost, prompt, completion in rows
        ]
