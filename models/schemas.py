"""Pydantic models for every structured AI output (and the user's profile input).

AI-facing models are deliberately forgiving: every field has a default and
common LLM quirks (a list where a string is expected, nulls, numbers as text)
are normalised before validation. `REQUIRED` lists the fields that must be
non-empty for an output to be considered usable.
"""
from __future__ import annotations

import typing
from typing import Any, ClassVar, List, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------- coercion ---
def to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return "; ".join(t for t in (to_text(v) for v in value) if t)
    if isinstance(value, dict):
        return "; ".join(f"{k}: {to_text(v)}" for k, v in value.items())
    return str(value)


def to_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [p.strip(" -•\t") for p in value.splitlines() if p.strip(" -•\t")]
    if isinstance(value, (list, tuple)):
        return [t for t in (to_text(v) for v in value) if t]
    text = to_text(value)
    return [text] if text else []


def _is_str_list(annotation: Any) -> bool:
    return typing.get_origin(annotation) is list and typing.get_args(annotation) == (str,)


class AIModel(BaseModel):
    """Base class for all AI outputs."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)
    REQUIRED: ClassVar[Tuple[str, ...]] = ()

    @model_validator(mode="before")
    @classmethod
    def _normalise(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        cleaned: dict = {}
        for name, field in cls.model_fields.items():
            if name not in data or data[name] is None:
                continue
            value = data[name]
            if field.annotation is str:
                value = to_text(value)
            elif _is_str_list(field.annotation):
                value = to_list(value)
            cleaned[name] = value
        return cleaned

    def missing_required(self) -> List[str]:
        return [f for f in self.REQUIRED if not getattr(self, f)]


# ------------------------------------------------------------ user profile ---
class UserProfileInput(BaseModel):
    """What the user types in (not an AI output)."""

    name: str = ""
    skills: str
    experience: str = ""
    hours_per_day: float = 2.0
    work_type: str = "Project-based freelance"
    tools: str = ""
    currency: str = "USD"
    strengths: str = ""
    limitations: str = ""
    portfolio_level: str = "Just starting (no portfolio)"


# ------------------------------------------------------------------ agents ---
class ProfileAnalysis(AIModel):
    REQUIRED = ("summary", "core_skills")
    summary: str = ""
    core_skills: List[str] = Field(default_factory=list)
    marketable_strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    time_assessment: str = ""
    portfolio_assessment: str = ""
    recommended_work_style: str = ""
    next_steps: List[str] = Field(default_factory=list)


class NicheOption(AIModel):
    REQUIRED = ("name", "target_customer", "suggested_service")
    name: str = ""
    target_market: str = ""
    target_customer: str = ""
    customer_problem: str = ""
    suggested_service: str = ""
    skill_match_reason: str = ""
    difficulty: str = ""
    client_accessibility: str = ""
    recurring_revenue_potential: str = ""
    portfolio_difficulty: str = ""
    buyer_type: str = ""
    risks: str = ""


class NicheList(AIModel):
    REQUIRED = ("niches",)
    niches: List[NicheOption] = Field(default_factory=list)


class NicheValidation(AIModel):
    REQUIRED = ("who_buys", "problem_customers_pay_for")
    niche_name: str = ""
    who_buys: str = ""
    problem_customers_pay_for: str = ""
    why_it_matters: str = ""
    alternatives: List[str] = Field(default_factory=list)
    acquisition_difficulty: str = ""
    portfolio_difficulty: str = ""
    remote_delivery_feasibility: str = ""
    recurring_potential: str = ""
    risks: List[str] = Field(default_factory=list)
    ai_assumptions: List[str] = Field(default_factory=list)
    how_to_verify: List[str] = Field(default_factory=list)
    summary: str = ""


class PackageTier(AIModel):
    name: str = ""
    suggested_example_price_usd: str = ""
    includes: List[str] = Field(default_factory=list)
    best_for: str = ""


class Offer(AIModel):
    REQUIRED = ("offer_name", "deliverables", "packages")
    offer_name: str = ""
    target_customer: str = ""
    customer_problem: str = ""
    description: str = ""
    deliverables: List[str] = Field(default_factory=list)
    packages: List[PackageTier] = Field(default_factory=list)
    delivery_time: str = ""
    revision_policy: str = ""
    value_proposition: str = ""
    unique_angle: str = ""
    portfolio_requirements: List[str] = Field(default_factory=list)
    example_outcome: str = ""
    pricing_note: str = ""


class ICP(AIModel):
    REQUIRED = ("industry", "business_type", "typical_problem")
    country: str = ""
    industry: str = ""
    business_type: str = ""
    business_size: str = ""
    decision_maker: str = ""
    typical_problem: str = ""
    buying_trigger: str = ""
    fit_signals: List[str] = Field(default_factory=list)
    where_to_find: List[str] = Field(default_factory=list)
    why_relevant: str = ""


class ProspectQualification(AIModel):
    REQUIRED = ("prospect_id",)
    prospect_id: str = ""
    company_name: str = ""
    fit_score: int = 0
    fit_level: str = "Weak"
    qualified: bool = False
    why_fit: str = ""
    fit_signals_found: List[str] = Field(default_factory=list)
    potential_problems: List[str] = Field(default_factory=list)
    recommended_angle: str = ""

    @field_validator("fit_score", mode="before")
    @classmethod
    def _score(cls, v: Any) -> int:
        try:
            return max(0, min(100, int(round(float(v)))))
        except (TypeError, ValueError):
            return 0

    @field_validator("fit_level", mode="before")
    @classmethod
    def _level(cls, v: Any) -> str:
        text = to_text(v).lower()
        for label in ("Strong", "Moderate", "Weak"):
            if label.lower() in text:
                return label
        return "Weak"


class QualificationList(AIModel):
    REQUIRED = ("qualifications",)
    qualifications: List[ProspectQualification] = Field(default_factory=list)


class ClientSample(AIModel):
    REQUIRED = ("sample_post",)
    company_name: str = ""
    sample_post: str = ""
    reel_idea: str = ""
    caption: str = ""
    cta: str = ""
    design_direction: str = ""
    why_it_works: str = ""


class FollowUp(AIModel):
    day_offset: int = 3
    subject: str = ""
    body: str = ""

    @field_validator("day_offset", mode="before")
    @classmethod
    def _offset(cls, v: Any) -> int:
        try:
            return max(1, int(float(v)))
        except (TypeError, ValueError):
            return 3


class OutreachCampaign(AIModel):
    REQUIRED = ("subject", "initial_email")
    company_name: str = ""
    subject: str = ""
    initial_email: str = ""
    followups: List[FollowUp] = Field(default_factory=list)
    cta: str = ""
    personalization_notes: str = ""
    suggested_interval: str = ""
