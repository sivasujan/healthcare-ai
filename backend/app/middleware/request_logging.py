"""Request logging middleware.

Records every HTTP request into the ``system_logs`` table and logs to stdout.
"""

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import client_ip, get_logger
from app.database import SessionLocal

logger = get_logger("middleware.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Persists request metadata (method, path, status, latency) to the DB."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            db = SessionLocal()
            try:
                from app.models import SystemLog

                db.add(
                    SystemLog(
                        level="error",
                        event="request",
                        method=request.method,
                        path=request.url.path,
                        status_code=500,
                        response_time_ms=round((time.perf_counter() - start) * 1000, 2),
                        message="Unhandled exception in middleware chain",
                    )
                )
                db.commit()
            finally:
                db.close()
            raise

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "%s %s -> %s (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        if request.url.path.startswith("/api"):
            try:
                db = SessionLocal()
                try:
                    from app.models import SystemLog

                    db.add(
                        SystemLog(
                            level="info",
                            event="request",
                            method=request.method,
                            path=request.url.path,
                            status_code=response.status_code,
                            response_time_ms=elapsed_ms,
                            message=f"request from {client_ip(request)}",
                        )
                    )
                    db.commit()
                finally:
                    db.close()
            except Exception:  # pragma: no cover - logging must never break requests
                logger.exception("Failed to persist request log")

        return response
