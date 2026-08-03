"""Prompt injection protection.

Scans user-supplied text for common prompt-injection patterns and system
override attempts before the text reaches any AI agent. Suspicious input is
rejected with a 400 response rather than being forwarded to the model.
"""

import re
from typing import Optional

from app.core.exceptions import AppError

_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("system_override", re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.I)),
    ("system_override", re.compile(r"disregard\s+(your\s+)?(previous|prior)\s+(instructions|prompt)", re.I)),
    ("system_override", re.compile(r"forget\s+everything", re.I)),
    ("system_override", re.compile(r"you\s+are\s+now\s+(an?\s+)?\w+\s+(without\s+)?(restrictions|guardrails|safety|limits)", re.I)),
    ("prompt_leak", re.compile(r"(print|reveal|show|display|repeat).{0,40}(system\s+prompt|instructions|prompt\b)", re.I)),
    ("prompt_leak", re.compile(r"what\s+(is|are|were)\s+your\s+(system\s+)?prompt", re.I)),
    ("delimiter_break", re.compile(r"(\[?system|\[?user)\s*:\s*\]?", re.I)),
    ("delimiter_break", re.compile(r"\]\]\s*to\s*\w+", re.I)),
]

_BLOCKLIST_WORDS = {
    "ignore all instructions",
    "disregard instructions",
    "forget your instructions",
    "reveal your prompt",
    "reveal the system prompt",
    "act as a non-medical",
    "no medical disclaimer",
    "don't include a disclaimer",
    "without disclaimer",
}


class PromptInjectionError(AppError):
    """Raised when user input looks like a prompt injection attempt.

    Inherits from :class:`AppError` so it is returned as an HTTP 400 by the
    global exception handler.
    """

    status_code = 400

    def __init__(self, message: str = "Input rejected as a potential prompt injection"):
        super().__init__(message, status_code=400)


def validate_prompt_safety(text: str) -> Optional[str]:
    """Return a human readable reason if ``text`` is unsafe, else ``None``."""
    lowered = re.sub(r"\s+", " ", text.lower()).strip()
    for phrase in _BLOCKLIST_WORDS:
        if phrase in lowered:
            return f"Input contains a blocked phrase: '{phrase}'"

    for label, pattern in _PATTERNS:
        if pattern.search(text):
            return f"Input matches a {label} pattern"

    return None


def assert_prompt_safe(text: str) -> None:
    """Raise :class:`PromptInjectionError` when the input is unsafe."""
    reason = validate_prompt_safety(text)
    if reason:
        raise PromptInjectionError(f"Input rejected: {reason}")
