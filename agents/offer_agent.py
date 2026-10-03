"""Agent 3: Offer / Product Builder."""
from typing import Optional

from models.schemas import NicheOption, NicheValidation, Offer, UserProfileInput
from prompts import agent_prompts as P
from services import demo_data
from agents.base import AgentResult, run_agent


def build_offer(profile: UserProfileInput, niche: NicheOption, validation: Optional[NicheValidation]) -> AgentResult[Offer]:
    return run_agent(P.offer_builder(profile, niche, validation), Offer, lambda: demo_data.offer(profile, niche))
