"""Persistence layer for structured logs (system_logs, prompt_history, model_usage)."""

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models import ModelUsage, PromptHistory, SystemLog


class LoggingService:
    """Writes operational telemetry rows to the SQLite database."""

    @staticmethod
    def log_system_event(
        db: Session,
        level: str,
        event: str,
        message: Optional[str] = None,
        user_id: Optional[int] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        status_code: Optional[int] = None,
        response_time_ms: Optional[float] = None,
    ) -> SystemLog:
        row = SystemLog(
            level=level,
            event=event,
            message=message,
            user_id=user_id,
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=response_time_ms,
        )
        db.add(row)
        db.commit()
        return row

    @staticmethod
    def log_prompt(
        db: Session,
        agent: str,
        prompt: str,
        response: Optional[str] = None,
        model: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> PromptHistory:
        row = PromptHistory(
            user_id=user_id,
            agent=agent,
            model=model,
            prompt=prompt,
            response=response,
        )
        db.add(row)
        db.commit()
        return row

    @staticmethod
    def log_model_usage(
        db: Session,
        *,
        user_id: Optional[int],
        agent: str,
        model: str,
        tier: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        latency_ms: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> ModelUsage:
        total = prompt_tokens + completion_tokens
        row = ModelUsage(
            user_id=user_id,
            agent=agent,
            model=model,
            tier=tier,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            cost_usd=round(cost_usd, 6),
            latency_ms=latency_ms,
            success=1 if success else 0,
            error=error,
        )
        db.add(row)
        db.commit()
        return row
