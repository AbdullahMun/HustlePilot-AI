"""Agent 5b: Client-Specific Sample (an AI-generated idea, never a delivered asset)."""
from typing import Optional

from models.schemas import ClientSample, Offer, ProspectQualification, UserProfileInput
from prompts import agent_prompts as P
from services import demo_data
from agents.base import AgentResult, run_agent


def generate_sample(profile: UserProfileInput, prospect: dict, offer: Offer, qualification: Optional[ProspectQualification]) -> AgentResult[ClientSample]:
    return run_agent(P.client_sample(profile, _safe(prospect), offer, qualification), ClientSample, lambda: demo_data.client_sample(prospect, offer))


def _safe(prospect: dict) -> dict:
    return {k: v for k, v in prospect.items() if k != "contact_email"}
