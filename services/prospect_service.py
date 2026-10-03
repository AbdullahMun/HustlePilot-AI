"""Loads and validates the DEMO prospect dataset (no scraping, no live lookups)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from config import settings

REQUIRED_COLUMNS = [
    "company_name", "industry", "country", "city", "website", "social_platform",
    "business_description", "online_activity", "contact_role", "contact_email",
    "fit_signals", "potential_problem",
]
DEMO_LABEL = "SAMPLE DATA - fictional business, not a verified lead"


class ProspectDataError(Exception):
    """Raised with a message that is safe to show to the user."""


def load_prospects(path: Optional[Path] = None) -> pd.DataFrame:
    path = Path(path or settings.PROSPECTS_CSV)
    if not path.exists():
        raise ProspectDataError(f"Prospect file not found: {path.name}. Make sure data/sample_prospects.csv exists.")
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception as exc:
        raise ProspectDataError("The prospect CSV could not be read. Check that it is a valid CSV file.") from exc
    if df.empty:
        raise ProspectDataError("The prospect CSV is empty.")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ProspectDataError("The prospect CSV is missing columns: " + ", ".join(missing))
    df = df.copy()
    if "prospect_id" not in df.columns:
        df.insert(0, "prospect_id", [f"P{i:03d}" for i in range(1, len(df) + 1)])
    if "data_label" not in df.columns:
        df["data_label"] = DEMO_LABEL
    df["prospect_id"] = df["prospect_id"].str.strip()
    return df.reset_index(drop=True)


def prospect_dict(df: pd.DataFrame, prospect_id: str) -> dict:
    rows = df[df["prospect_id"] == prospect_id]
    return rows.iloc[0].to_dict() if not rows.empty else {}


def prospects_for_prompt(df: pd.DataFrame) -> list:
    """Compact records (no contact emails) sent to the model."""
    keep = ["prospect_id", "company_name", "industry", "country", "city", "social_platform",
            "business_description", "online_activity", "contact_role", "fit_signals", "potential_problem"]
    return df[keep].to_dict(orient="records")
