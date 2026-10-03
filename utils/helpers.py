"""Session-state defaults and small UI-independent helpers."""
from __future__ import annotations

import html
from urllib.parse import quote

PORTFOLIO_LEVELS = [
    "Just starting (no portfolio)",
    "A few practice samples",
    "Some real projects",
    "Established portfolio",
]
WORK_TYPES = [
    "Project-based freelance",
    "Monthly retainer clients",
    "Either / open to both",
    "Quick one-off gigs",
]
CURRENCIES = ["USD", "EUR", "GBP", "AED", "CAD", "AUD"]

DEMO_PROFILE = {
    "pf_name": "",
    "pf_skills": "Canva + AI tools (ChatGPT / Gemini for ideas and copy)",
    "pf_experience": "Beginner. Made designs for friends and personal projects, no paid international clients yet.",
    "pf_hours": 2.5,
    "pf_worktype": "Monthly retainer clients",
    "pf_tools": "Canva, ChatGPT, Gemini, CapCut",
    "pf_currency": "USD",
    "pf_strengths": "Strong visual sense, learns fast, consistent",
    "pf_limits": "No formal portfolio yet; limited experience writing to overseas clients",
    "pf_portfolio": PORTFOLIO_LEVELS[0],
}

STATE_DEFAULTS = {
    "nav": "dashboard",
    "profile": None,
    "analysis": None,
    "niches": [],
    "selected_niche": None,
    "validation": None,
    "offer": None,
    "icp": None,
    "prospects_df": None,
    "qualifications": {},
    "samples": {},
    "campaigns": {},
    "leads": {},
    "sources": {},
    "force_demo": False,
    "user_api_key": "",
    "pf_name": "",
    "pf_skills": "",
    "pf_experience": "",
    "pf_hours": 2.5,
    "pf_worktype": WORK_TYPES[0],
    "pf_tools": "",
    "pf_currency": "USD",
    "pf_strengths": "",
    "pf_limits": "",
    "pf_portfolio": PORTFOLIO_LEVELS[0],
}

_MUTABLE = (list, dict)


def init_state(state) -> None:
    """Populate missing keys (copying mutable defaults so sessions never share them)."""
    for key, default in STATE_DEFAULTS.items():
        if key not in state:
            state[key] = type(default)() if isinstance(default, _MUTABLE) else default


def mailto_link(subject: str, body: str) -> str:
    """mailto link with NO recipient: the user must add a verified address themselves."""
    return f"mailto:?subject={quote(subject or '')}&body={quote(body or '')}"


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def bullets(items) -> str:
    return "\n".join(f"- {i}" for i in items if i)
