"""Robust JSON extraction from model responses.

Models sometimes wrap JSON in markdown code fences or append explanatory text;
these helpers extract the first valid JSON object defensively.
"""

import json
import re
from typing import Any, Optional

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)
_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(text: str) -> Optional[dict[str, Any]]:
    """Return the first valid JSON object found in ``text``, else ``None``."""
    candidates: list[str] = []

    fenced = _JSON_FENCE_RE.findall(text)
    candidates.extend(fenced)

    obj_match = _OBJECT_RE.search(text)
    if obj_match:
        candidates.append(obj_match.group(0))

    candidates.append(text)

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    return None


def get_text_field(data: Optional[dict], key: str, default: str = "") -> str:
    """Extract a string field safely from a parsed JSON dict."""
    if not data:
        return default
    value = data.get(key, default)
    return value if isinstance(value, str) else default


def get_list_field(data: Optional[dict], key: str) -> list[str]:
    """Extract a list-of-strings field safely."""
    if not data:
        return []
    value = data.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str) and value.strip():
        return [value]
    return []
