"""Agent 5: Prospect Research & Qualification (over the local DEMO dataset)."""
from __future__ import annotations

from typing import Dict

import pandas as pd

from models.schemas import ICP, Offer, ProspectQualification, QualificationList
from prompts import agent_prompts as P
from services import demo_data
from services.prospect_service import prospects_for_prompt
from agents.base import DEMO, AgentResult, run_agent


def qualify_prospects(df: pd.DataFrame, icp: ICP, offer: Offer) -> AgentResult[Dict[str, ProspectQualification]]:
    rows = {r["prospect_id"]: r for r in df.to_dict(orient="records")}

    def fallback() -> QualificationList:
        return QualificationList(qualifications=[demo_data.qualification_heuristic(r, icp) for r in rows.values()])

    result = run_agent(P.prospect_qualification(prospects_for_prompt(df), icp, offer), QualificationList, fallback, temperature=0.3)

    by_id: Dict[str, ProspectQualification] = {}
    for q in result.data.qualifications:
        if q.prospect_id in rows:
            if not q.company_name:
                q.company_name = rows[q.prospect_id].get("company_name", "")
            by_id[q.prospect_id] = q
    # Any prospect the model skipped gets a transparent heuristic assessment.
    skipped = [pid for pid in rows if pid not in by_id]
    for pid in skipped:
        by_id[pid] = demo_data.qualification_heuristic(rows[pid], icp)
    notice = result.notice
    if skipped and result.source != DEMO:
        notice = f"{len(skipped)} prospect(s) were missing from the AI reply and were scored with the simple keyword fallback."
    return AgentResult(by_id, result.source, notice)
