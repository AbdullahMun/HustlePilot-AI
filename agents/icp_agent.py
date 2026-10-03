"""Agent 4: Ideal Client Profile."""
from models.schemas import ICP, NicheOption, Offer, UserProfileInput
from prompts import agent_prompts as P
from services import demo_data
from agents.base import AgentResult, run_agent


def build_icp(profile: UserProfileInput, niche: NicheOption, offer: Offer) -> AgentResult[ICP]:
    return run_agent(P.icp_builder(profile, niche, offer), ICP, lambda: demo_data.icp(niche, offer), temperature=0.5)
