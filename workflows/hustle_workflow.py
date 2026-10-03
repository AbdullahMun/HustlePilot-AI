"""Lightweight orchestration of the HustlePilot agent pipeline.

The flow is linear and gated by a human at every step (select niche, review
outreach, send manually), so a plain-Python orchestrator is simpler and more
reliable than a graph framework. Each `run_*` function calls one agent and
stores its result (plus whether it came from Gemini or demo data) in the
Streamlit session state passed in as `state`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from agents import (  # noqa: F401  (imported for clarity of the pipeline)
    followup_agent, icp_agent, niche_agent, offer_agent, outreach_agent,
    profile_agent, prospect_agent, sample_agent,
)
from agents.base import AgentResult
from services import prospect_service


@dataclass(frozen=True)
class Step:
    key: str
    label: str
    done: Callable[[dict], bool]
    needs: Optional[str] = None       # key of the step that must be done first
    needs_message: str = ""


STEPS: List[Step] = [
    Step("dashboard", "Dashboard", lambda s: False),
    Step("profile", "My Profile", lambda s: s["analysis"] is not None),
    Step("niches", "Discover Niches", lambda s: s["selected_niche"] is not None, "profile",
         "Analyze your profile first so niche ideas fit your skills."),
    Step("validate", "Validate Niche", lambda s: s["validation"] is not None, "niches",
         "Select a niche first."),
    Step("offer", "Build Offer", lambda s: s["offer"] is not None, "niches",
         "Select a niche first."),
    Step("icp", "Ideal Client", lambda s: s["icp"] is not None, "offer",
         "Build your offer first."),
    Step("prospects", "Prospects", lambda s: bool(s["qualifications"]), "icp",
         "Generate your ideal client profile first. Prospects are compared against it."),
    Step("sample", "Client Sample", lambda s: bool(s["samples"]), "prospects",
         "Qualify prospects first."),
    Step("outreach", "Outreach", lambda s: bool(s["campaigns"]), "prospects",
         "Qualify prospects first."),
    Step("followups", "Follow-ups", lambda s: any(l.get("contacted_at") for l in s["leads"].values())),
]
STEP_BY_KEY: Dict[str, Step] = {s.key: s for s in STEPS}
FLOW_STEPS = [s for s in STEPS if s.key != "dashboard"]


def is_done(key: str, state) -> bool:
    return STEP_BY_KEY[key].done(state)


def missing_prerequisite(key: str, state) -> Optional[Step]:
    need = STEP_BY_KEY[key].needs
    if need and not is_done(need, state):
        return STEP_BY_KEY[need]
    return None


def next_step(state) -> Optional[Step]:
    for step in FLOW_STEPS:
        if not is_done(step.key, state):
            return step
    return None


def progress(state) -> float:
    return sum(is_done(s.key, state) for s in FLOW_STEPS) / len(FLOW_STEPS)


# ----------------------------------------------------------------- storing ---
def _store(state, key: str, result: AgentResult):
    state[key] = result.data
    state["sources"][key] = {"source": result.source, "notice": result.notice}
    return result.data


def _mark(state, key: str, result: AgentResult) -> None:
    state["sources"][key] = {"source": result.source, "notice": result.notice}


def clear_downstream_of_niche(state) -> None:
    for key in ("validation", "offer", "icp", "prospects_df"):
        state[key] = None
    for key in ("qualifications", "samples", "campaigns", "leads", "sources"):
        keep = {k: v for k, v in state["sources"].items() if k in ("analysis", "niches")} if key == "sources" else {}
        state[key] = keep


# ------------------------------------------------------------------- steps ---
def run_profile_analysis(state):
    return _store(state, "analysis", profile_agent.analyze_profile(state["profile"]))


def run_niche_discovery(state):
    result = niche_agent.discover_niches(state["profile"], state["analysis"])
    state["selected_niche"] = None
    clear_downstream_of_niche(state)
    state["niches"] = list(result.data.niches)
    _mark(state, "niches", result)
    return state["niches"]


def select_niche(state, index: int) -> None:
    chosen = state["niches"][index]
    if state["selected_niche"] is None or state["selected_niche"].name != chosen.name:
        clear_downstream_of_niche(state)
    state["selected_niche"] = chosen


def run_niche_validation(state):
    return _store(state, "validation", niche_agent.validate_niche(state["profile"], state["selected_niche"]))


def run_offer(state):
    return _store(state, "offer", offer_agent.build_offer(state["profile"], state["selected_niche"], state["validation"]))


def run_icp(state):
    return _store(state, "icp", icp_agent.build_icp(state["profile"], state["selected_niche"], state["offer"]))


def load_prospects(state):
    """Load the demo CSV once; raises ProspectDataError with a friendly message."""
    if state["prospects_df"] is None:
        state["prospects_df"] = prospect_service.load_prospects()
        followup_agent.ensure_leads(state["leads"], state["prospects_df"]["prospect_id"])
    return state["prospects_df"]


def run_qualification(state):
    df = load_prospects(state)
    result = prospect_agent.qualify_prospects(df, state["icp"], state["offer"])
    state["qualifications"] = result.data
    _mark(state, "qualifications", result)
    followup_agent.apply_qualifications(state["leads"], result.data)
    return result.data


def run_sample(state, prospect_id: str):
    prospect = prospect_service.prospect_dict(state["prospects_df"], prospect_id)
    result = sample_agent.generate_sample(state["profile"], prospect, state["offer"], state["qualifications"].get(prospect_id))
    state["samples"][prospect_id] = result.data
    state["sources"][f"sample:{prospect_id}"] = {"source": result.source, "notice": result.notice}
    return result.data


def run_campaign(state, prospect_id: str):
    prospect = prospect_service.prospect_dict(state["prospects_df"], prospect_id)
    result = outreach_agent.generate_campaign(
        state["profile"], prospect, state["offer"],
        state["qualifications"].get(prospect_id), state["samples"].get(prospect_id),
    )
    state["campaigns"][prospect_id] = result.data
    state["leads"].setdefault(prospect_id, followup_agent.new_lead())["approved"] = False
    state["sources"][f"campaign:{prospect_id}"] = {"source": result.source, "notice": result.notice}
    return result.data
