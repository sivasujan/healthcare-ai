"""Structured logging for the application.

Logs go to stdout via Python's logging module, and API/prompt/model events are
additionally persisted to the ``system_logs`` table through
:func:`app.services.logging_service`.
"""

import logging
import sys
from typing import Optional

from fastapi import Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger instance."""
    return logging.getLogger(name)


def client_ip(request: Request) -> str:
    """Extract the client IP from a request, honoring X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
