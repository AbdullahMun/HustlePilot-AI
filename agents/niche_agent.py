"""Agent 2: Niche Discovery & Validation."""
from models.schemas import NicheList, NicheOption, NicheValidation, ProfileAnalysis, UserProfileInput
from prompts import agent_prompts as P
from services import demo_data
from agents.base import AgentResult, run_agent


def discover_niches(profile: UserProfileInput, analysis: ProfileAnalysis) -> AgentResult[NicheList]:
    return run_agent(P.niche_discovery(profile, analysis), NicheList, lambda: demo_data.niches(profile))


def validate_niche(profile: UserProfileInput, niche: NicheOption) -> AgentResult[NicheValidation]:
    return run_agent(P.niche_validation(profile, niche), NicheValidation, lambda: demo_data.validation(niche), temperature=0.5)
