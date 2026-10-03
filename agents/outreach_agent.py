"""Agent 6: Outreach Campaign. Drafts only; nothing is ever sent automatically."""
from typing import Optional

from models.schemas import ClientSample, Offer, OutreachCampaign, ProspectQualification, UserProfileInput
from prompts import agent_prompts as P
from services import demo_data
from agents.base import AgentResult, run_agent


def generate_campaign(
    profile: UserProfileInput, prospect: dict, offer: Offer,
    qualification: Optional[ProspectQualification], sample: Optional[ClientSample],
) -> AgentResult[OutreachCampaign]:
    safe = {k: v for k, v in prospect.items() if k != "contact_email"}
    prompt = P.outreach(profile, safe, offer, qualification, sample)
    return run_agent(prompt, OutreachCampaign, lambda: demo_data.campaign(profile, prospect, qualification, offer, sample is not None), temperature=0.8)
