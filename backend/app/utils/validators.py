"""Input validation utilities (SQL injection, common unsafe payloads)."""

import re

_SQL_PATTERNS = [
    re.compile(r"('|%27)\s*(or|union|select|insert|update|delete|drop|alter)\b", re.I),
    re.compile(r"\b(union|select)\s+(all|distinct)?\s*\*?\s+from\b", re.I),
    re.compile(r"(/\*|--\s|\;|\#)\s*(drop|truncate|insert|update|delete)", re.I),
    re.compile(r"\b(sleep|benchmark)\s*\(", re.I),
    re.compile(r"(information_schema|pg_catalog|sqlite_master)", re.I),
]


def is_sql_injection_risk(text: str) -> bool:
    """Heuristic SQL-injection scan; returns True when suspicious."""
    return any(pattern.search(text) for pattern in _SQL_PATTERNS)


def sanitize_text(text: str, max_length: int = 8000) -> str:
    """Trim and collapse whitespace in user-provided text."""
    return " ".join(text.split())[:max_length]
