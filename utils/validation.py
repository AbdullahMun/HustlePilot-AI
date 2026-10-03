"""Input validation and light safety checks for generated text."""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from pydantic import ValidationError

from models.schemas import UserProfileInput

MAX_FIELD_CHARS = 1500

RISKY_PHRASES = [
    "guarantee", "guaranteed", "100%", "risk-free", "risk free", "act now", "last chance",
    "limited time", "dear sir", "dear madam", "to whom it may concern", "double your",
    "make money fast", "we have helped", "our clients saw", "trusted by",
]


def clean_text(value: Optional[str], max_chars: int = MAX_FIELD_CHARS) -> str:
    text = re.sub(r"\s+", " ", (value or "")).strip()
    return text[:max_chars]


def validate_profile(values: dict) -> Tuple[Optional[UserProfileInput], List[str]]:
    errors: List[str] = []
    cleaned = {
        k: (clean_text(v) if isinstance(v, str) else v) for k, v in values.items()
    }
    if len(cleaned.get("skills", "")) < 3:
        errors.append("Add at least one skill (for example: Canva, copywriting, video editing).")
    hours = cleaned.get("hours_per_day", 0)
    if not isinstance(hours, (int, float)) or not 0.5 <= float(hours) <= 16:
        errors.append("Available hours per day must be between 0.5 and 16.")
    if not cleaned.get("currency"):
        errors.append("Choose the currency you want to earn in.")
    if errors:
        return None, errors
    try:
        return UserProfileInput(**cleaned), []
    except ValidationError:
        return None, ["Some profile fields look invalid. Please check them and try again."]


def scan_risky_phrases(text: str) -> List[str]:
    """Return phrases in an outreach draft that may sound spammy or make claims."""
    lowered = (text or "").lower()
    return sorted({p for p in RISKY_PHRASES if p in lowered})
