"""Central configuration: secrets, model name and app constants.

Secrets are read (in order) from:
1. the optional session-only key typed into the sidebar,
2. Streamlit secrets (Streamlit Cloud / .streamlit/secrets.toml),
3. environment variables (including a local .env file).
Nothing is ever hardcoded or written to disk.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # silently does nothing if the file is missing

APP_NAME = "HustlePilot AI"
TAGLINE = "From Skills to Your First Client"

# ---- Gemini -----------------------------------------------------------------
# "gemini-flash-latest" is an alias that follows Google's current Flash model, so
# the app keeps working when individual model versions are retired.
# Override with GEMINI_MODEL (env var or Streamlit secret) to pin a version.
DEFAULT_MODEL = "gemini-flash-latest"
REQUEST_TIMEOUT_SECONDS = 90
MAX_RETRIES = 2

# ---- Data -------------------------------------------------------------------
PROSPECTS_CSV = BASE_DIR / "data" / "sample_prospects.csv"
MAX_BULK_CAMPAIGNS = 8

_PLACEHOLDER_KEYS = {"", "your_api_key_here", "your-api-key", "changeme"}


def _streamlit_secret(name: str) -> Optional[str]:
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:  # no secrets file, or not running inside Streamlit
        return None
    return None


def _session_value(name: str):
    try:
        import streamlit as st

        return st.session_state.get(name)
    except Exception:
        return None


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    value = _streamlit_secret(name) or os.getenv(name)
    if value and value.strip():
        return value.strip()
    return default


def get_api_key() -> Optional[str]:
    key = _session_value("user_api_key") or get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")
    if not key:
        return None
    key = key.strip()
    return None if key.lower() in _PLACEHOLDER_KEYS else key


def get_model_name() -> str:
    return get_secret("GEMINI_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL


def force_demo_mode() -> bool:
    if _session_value("force_demo"):
        return True
    return (os.getenv("HUSTLEPILOT_DEMO_MODE", "0").strip().lower() in {"1", "true", "yes"})


def has_api_key() -> bool:
    return get_api_key() is not None
