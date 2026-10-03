"""Agent 1: Profile Analysis."""
from models.schemas import ProfileAnalysis, UserProfileInput
from prompts import agent_prompts as P
from services import demo_data
from agents.base import AgentResult, run_agent


def analyze_profile(profile: UserProfileInput) -> AgentResult[ProfileAnalysis]:
    return run_agent(P.profile_analysis(profile), ProfileAnalysis, lambda: demo_data.profile_analysis(profile), temperature=0.4)
