"""Agent 7: Follow-up & Lead Management (deterministic, no AI needed).

Leads live in `st.session_state["leads"]` as plain dicts, keyed by prospect_id.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, Optional

import pandas as pd

STATUSES = ["New", "Qualified", "Campaign Ready", "Contacted", "Follow-up Due", "Interested", "Not Interested", "Closed"]
CONTACTED_STATES = {"Contacted", "Follow-up Due", "Interested", "Not Interested", "Closed"}


def new_lead() -> dict:
    return {"status": "New", "qualified": False, "approved": False, "contacted_at": None,
            "next_followup": None, "notes": "", "history": []}


def _log(lead: dict, event: str) -> None:
    lead["history"].append(f"{datetime.now():%Y-%m-%d %H:%M} - {event}")


def ensure_leads(leads: Dict[str, dict], prospect_ids) -> None:
    for pid in prospect_ids:
        leads.setdefault(pid, new_lead())


def apply_qualifications(leads: Dict[str, dict], qualifications: dict) -> None:
    for pid, q in qualifications.items():
        lead = leads.setdefault(pid, new_lead())
        lead["qualified"] = bool(q.qualified)
        if q.qualified and lead["status"] == "New":
            lead["status"] = "Qualified"
            _log(lead, "Qualified against the ICP")


def approve_campaign(leads: Dict[str, dict], pid: str) -> None:
    lead = leads.setdefault(pid, new_lead())
    lead["approved"] = True
    if lead["status"] in {"New", "Qualified"}:
        lead["status"] = "Campaign Ready"
    _log(lead, "Outreach reviewed and approved by you")


def mark_contacted(leads: Dict[str, dict], pid: str, followup_days: int = 3, today: Optional[date] = None) -> None:
    today = today or date.today()
    lead = leads.setdefault(pid, new_lead())
    lead["status"] = "Contacted"
    lead["contacted_at"] = today.isoformat()
    lead["next_followup"] = (today + timedelta(days=max(1, followup_days))).isoformat()
    _log(lead, "Marked as contacted (sent manually by you)")


def schedule_followup(leads: Dict[str, dict], pid: str, when: date) -> None:
    lead = leads.setdefault(pid, new_lead())
    lead["next_followup"] = when.isoformat()
    if lead["status"] == "Follow-up Due" and when > date.today():
        lead["status"] = "Contacted"
    _log(lead, f"Follow-up scheduled for {when.isoformat()}")


def set_status(leads: Dict[str, dict], pid: str, status: str) -> None:
    if status not in STATUSES:
        return
    lead = leads.setdefault(pid, new_lead())
    if lead["status"] != status:
        lead["status"] = status
        _log(lead, f"Status changed to {status}")


def refresh_due(leads: Dict[str, dict], today: Optional[date] = None) -> int:
    """Move 'Contacted' leads whose follow-up date has arrived to 'Follow-up Due'."""
    today = today or date.today()
    moved = 0
    for lead in leads.values():
        if lead["status"] == "Contacted" and lead.get("next_followup"):
            if date.fromisoformat(lead["next_followup"]) <= today:
                lead["status"] = "Follow-up Due"
                _log(lead, "Follow-up is due")
                moved += 1
    return moved


def dashboard_metrics(leads: Dict[str, dict]) -> Dict[str, int]:
    vals = list(leads.values())
    count = lambda s: sum(1 for v in vals if v["status"] == s)  # noqa: E731
    return {
        "Total Prospects": len(vals),
        "Qualified": sum(1 for v in vals if v.get("qualified")),
        "Campaign Ready": count("Campaign Ready"),
        "Contacted": sum(1 for v in vals if v["status"] in CONTACTED_STATES),
        "Follow-ups Due": count("Follow-up Due"),
        "Interested": count("Interested"),
        "Closed": count("Closed"),
    }


def leads_dataframe(leads: Dict[str, dict], prospects: pd.DataFrame, qualifications: dict) -> pd.DataFrame:
    rows = []
    for _, r in prospects.iterrows():
        pid = r["prospect_id"]
        lead = leads.get(pid) or new_lead()
        q = qualifications.get(pid)
        rows.append({
            "ID": pid, "Company": r["company_name"], "Industry": r["industry"], "Country": r["country"],
            "Fit score": q.fit_score if q else None, "Status": lead["status"],
            "Contacted on": lead["contacted_at"] or "", "Next follow-up": lead["next_followup"] or "",
        })
    return pd.DataFrame(rows)
