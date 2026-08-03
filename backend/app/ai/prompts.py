"""Prompt template loader.

Reads prompt templates from ``app/prompts/*.md`` once and caches them.
"""

from functools import lru_cache
from pathlib import Path

from app.config import BASE_DIR

PROMPTS_DIR = Path(BASE_DIR) / "app" / "prompts"


@lru_cache(maxsize=32)
def load_prompt(name: str) -> str:
    """Load a prompt template by file stem (e.g. ``"symptom_analysis"``)."""
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def build_system_prompt(name: str) -> str:
    """Combine the shared system base prompt with an agent-specific prompt."""
    base = load_prompt("system_base")
    specific = load_prompt(name)
    return f"{base}\n\n---\n\n{specific}"
