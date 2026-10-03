"""Structured demo/fallback outputs used when Gemini is unavailable (or Demo Mode is on).

This is a FIXED example set, not live research. The UI always labels it as
"Demo / Fallback Mode".
"""
from __future__ import annotations

import re
from typing import Optional

from models.schemas import (
    ICP, ClientSample, FollowUp, NicheList, NicheOption, NicheValidation, Offer,
    OutreachCampaign, PackageTier, ProfileAnalysis, ProspectQualification, QualificationList,
    UserProfileInput,
)

_STOP = {"with", "that", "this", "from", "have", "their", "small", "business", "businesses", "local",
         "independent", "owner", "owners", "team", "teams", "country", "countries", "service", "services"}


def _tokens(text: str) -> set:
    out = set()
    for w in re.findall(r"[a-z]+", (text or "").lower()):
        if len(w) > 3 and w not in _STOP:
            out.add(w[:-1] if w.endswith("s") else w)
    return out


# ------------------------------------------------------------------ agents ---
def profile_analysis(p: UserProfileInput) -> ProfileAnalysis:
    skills = [s.strip() for s in re.split(r"[,+;/]| and ", p.skills) if s.strip()][:5] or [p.skills]
    return ProfileAnalysis(
        summary=(
            f"You bring {p.skills} and about {p.hours_per_day:g} hours a day. That is enough to run a small "
            "number of retainer or project clients if you keep the offer narrow and repeatable."
        ),
        core_skills=skills,
        marketable_strengths=[s for s in re.split(r"[,;]", p.strengths) if s.strip()] or ["Willingness to learn quickly"],
        limitations=[s for s in re.split(r"[;]", p.limitations) if s.strip()] or ["Portfolio still to be built"],
        time_assessment=f"{p.hours_per_day:g} h/day supports roughly 2-4 small recurring clients once your workflow is repeatable (assumption).",
        portfolio_assessment=f"Portfolio level: {p.portfolio_level}. Build 3-5 realistic sample pieces before pitching.",
        recommended_work_style="Productised, repeatable deliverables with a monthly rhythm.",
        next_steps=[
            "Pick one niche and one audience instead of offering everything.",
            "Create 3-5 sample pieces in that niche to act as a portfolio.",
            "Write a one-sentence offer and three simple packages.",
            "Prepare a short, honest outreach message and send a few per day yourself.",
        ],
    )


def niches(p: UserProfileInput) -> NicheList:
    common = dict(difficulty="Medium", portfolio_difficulty="Low-Medium (a handful of sample posts is enough to start)")
    return NicheList(niches=[
        NicheOption(
            name="Social media content for dental & aesthetic clinics", target_market="United States, United Kingdom",
            target_customer="Independent dental and aesthetic clinics", buyer_type="Practice owner or clinic manager",
            customer_problem="Clinics want a steady online presence but have no time or in-house designer.",
            suggested_service="Monthly pack of branded posts, captions and short-video concepts",
            skill_match_reason="Uses design and AI-assisted copywriting directly.", client_accessibility="Medium: clinics are easy to find on Instagram and Google Maps.",
            recurring_revenue_potential="High: content is needed every month.", risks="Health-related claims need care; some clinics have agencies already.", **common),
        NicheOption(
            name="Promo content for local fitness & wellness studios", target_market="United Kingdom, Canada, Australia",
            target_customer="Boutique gyms, yoga and fitness studios", buyer_type="Studio owner or manager",
            customer_problem="Class schedules and challenges are announced with inconsistent, hard-to-notice graphics.",
            suggested_service="Template-based weekly promo graphics and challenge campaign kits",
            skill_match_reason="Template design in Canva fits the repeatable weekly workload.", client_accessibility="High: studios are very active and visible on Instagram.",
            recurring_revenue_potential="High: weekly schedule and promo cycles.", risks="Small budgets; price-sensitive buyers.", **common),
        NicheOption(
            name="Listing & social creatives for real estate agents", target_market="Canada, Australia, United Kingdom",
            target_customer="Independent real estate and letting agencies", buyer_type="Principal agent or director",
            customer_problem="Listings look like everyone else's and agents have little time to design visuals.",
            suggested_service="Branded listing graphics, market-update posts and short listing videos",
            skill_match_reason="Graphic templates plus AI copy for listing descriptions.", client_accessibility="Medium: agents are easy to find but often receive many pitches.",
            recurring_revenue_potential="Medium-High: new listings appear constantly.", risks="Agents get many cold pitches; brokerage branding rules may limit design freedom.", **common),
        NicheOption(
            name="Brand content kits for small e-commerce boutiques", target_market="United States, United Kingdom",
            target_customer="Small online shops run by founders", buyer_type="Founder",
            customer_problem="Founders handle marketing alone and miss seasonal campaign windows.",
            suggested_service="Seasonal campaign kit: social graphics, email banners and caption set",
            skill_match_reason="Canva kits and AI-generated captions map directly to the deliverables.", client_accessibility="Medium: founders are reachable but time-poor.",
            recurring_revenue_potential="Medium: seasonal spikes, some monthly retainers.", risks="Revenue can be seasonal; some shops rely on platforms' built-in tools.", **common),
    ])


def validation(n: NicheOption) -> NicheValidation:
    return NicheValidation(
        niche_name=n.name,
        who_buys=f"{n.buyer_type or 'The business owner or manager'} at {n.target_customer.lower() or 'small businesses'}.",
        problem_customers_pay_for=n.customer_problem or "Consistent, professional content without hiring in-house.",
        why_it_matters="Regular, professional-looking content helps a business stay visible while the owner focuses on core work (assumption).",
        alternatives=["Doing it in-house with free templates", "Local marketing agencies", "Freelance marketplaces", "Doing nothing / posting irregularly"],
        acquisition_difficulty=f"{n.difficulty or 'Medium'}: you must stand out from other freelancers and agencies pitching the same businesses (assumption).",
        portfolio_difficulty=n.portfolio_difficulty or "Low-Medium",
        remote_delivery_feasibility="High: deliverables are digital files and can be shared over email or a shared folder.",
        recurring_potential=n.recurring_revenue_potential or "Medium",
        risks=[n.risks or "Competition from other freelancers", "Clients may churn if results are not visible quickly", "Scope creep without clear revisions policy"],
        ai_assumptions=["Businesses in this niche post regularly and care about their look.", "Owners are open to outsourcing content at small monthly budgets.", "Remote delivery is acceptable to these buyers."],
        how_to_verify=["Browse 15-20 businesses in this niche and note how consistent their content is.", "Check whether competing freelancers publish prices or packages.", "Ask 3-5 people in this niche what they currently use and spend (informal conversations)."],
        summary="Demo validation built from the niche description. None of it has been verified against real market data.",
    )


def offer(p: UserProfileInput, n: NicheOption) -> Offer:
    return Offer(
        offer_name=f"{n.suggested_service or n.name}",
        target_customer=n.target_customer, customer_problem=n.customer_problem,
        description=f"A simple, repeatable service for {n.target_customer.lower()}: {n.suggested_service.lower()}.",
        deliverables=["Branded template set in the client's colours and fonts", "Ready-to-post graphics with captions", "Short-video concept notes (script outline + visual direction)", "A simple monthly content calendar"],
        packages=[
            PackageTier(name="Starter", suggested_example_price_usd="$120-$200 / month", includes=["8 branded posts", "Captions for each post", "1 round of revisions"], best_for="Trying the service with a small budget"),
            PackageTier(name="Growth", suggested_example_price_usd="$250-$400 / month", includes=["12 posts + 4 stories", "2 short-video concepts", "Content calendar", "2 rounds of revisions"], best_for="Businesses that want steady weekly content"),
            PackageTier(name="Premium", suggested_example_price_usd="$450-$700 / month", includes=["16 posts + stories", "4 short-video concepts", "Monthly campaign idea", "Priority turnaround"], best_for="Businesses running regular promotions"),
        ],
        delivery_time="First batch within 5-7 working days; monthly batches afterwards.",
        revision_policy="1-2 revision rounds per batch; extra rounds quoted separately.",
        value_proposition="Consistent, on-brand content without the client needing a designer or extra hires.",
        unique_angle="A narrow focus on one type of business, with templates built around their typical promotions.",
        portfolio_requirements=["3-5 sample posts made for a fictional business in this niche", "One sample monthly calendar", "A short before/after of a real public post (redesigned as a practice piece, labelled as such)"],
        example_outcome="Illustrative only: a clinic that currently posts once a month could move to a steady weekly rhythm. Results vary and are not guaranteed.",
        pricing_note="Suggested Example Pricing in USD. These are illustrative starting points, not verified market rates or guaranteed income.",
    )


def icp(n: NicheOption, o: Offer) -> ICP:
    market = (n.target_market or "United States").split(",")[0].strip()
    return ICP(
        country=n.target_market or market,
        industry=n.target_customer or n.name,
        business_type=f"Independent / owner-run: {n.target_customer or n.name}",
        business_size="1-15 people, no dedicated in-house designer",
        decision_maker=n.buyer_type or "Owner or manager",
        typical_problem=n.customer_problem or o.customer_problem,
        buying_trigger="A new promotion, season, opening or rebrand; or visibly inconsistent social media.",
        fit_signals=["posts irregularly", "no in-house designer", "seasonal or recurring promotions", "small team", "stock photos or plain screenshots"],
        where_to_find=["Instagram and Facebook business profiles in the target city", "Google Maps listings for the niche", "Local business directories", "Industry association member lists (public)"],
        why_relevant="These businesses have an ongoing need for content and typically decide quickly without long procurement (assumption).",
    )


def qualification_heuristic(row: dict, i: ICP) -> ProspectQualification:
    """Transparent keyword-overlap scoring used for the demo/fallback path."""
    haystack_industry = _tokens(f"{row.get('industry','')} {row.get('business_description','')}")
    haystack_signals = _tokens(f"{row.get('fit_signals','')} {row.get('online_activity','')}")
    icp_industry = _tokens(f"{i.industry} {i.business_type}")
    icp_signals = _tokens(" ".join(i.fit_signals))
    icp_role = _tokens(i.decision_maker)
    score, why, found = 5, [], []

    if icp_industry & haystack_industry:
        score += 40
        why.append("industry matches the ICP")
    country = (row.get("country") or "").lower()
    if country and (country in (i.country or "").lower() or "any" in (i.country or "").lower()):
        score += 20
        why.append(f"located in a target market ({row.get('country')})")
    overlap = icp_signals & haystack_signals
    if overlap:
        score += min(30, 10 * len(overlap))
        found = sorted(overlap)
        why.append("shows ICP fit signals: " + ", ".join(found))
    if icp_role & _tokens(row.get("contact_role", "")):
        score += 5
        why.append("contact role matches the ICP decision maker")
    score = min(score, 100)
    level = "Strong" if score >= 70 else "Moderate" if score >= 50 else "Weak"
    return ProspectQualification(
        prospect_id=row.get("prospect_id", ""), company_name=row.get("company_name", ""),
        fit_score=score, fit_level=level, qualified=score >= 50,
        why_fit=("Keyword-based demo assessment: " + "; ".join(why)) if why else "Keyword-based demo assessment: little overlap with the ICP.",
        fit_signals_found=found or ([row.get("fit_signals", "")] if row.get("fit_signals") else []),
        potential_problems=[row.get("potential_problem", "")] if row.get("potential_problem") else [],
        recommended_angle=f"Lead with the visible gap: {row.get('potential_problem', 'inconsistent content').rstrip('.').lower()}.",
    )


def client_sample(row: dict, o: Offer) -> ClientSample:
    name, ind, plat = row.get("company_name", "the business"), row.get("industry", "business"), row.get("social_platform", "Instagram")
    problem = row.get("potential_problem", "").rstrip(".")
    return ClientSample(
        company_name=name,
        sample_post=f"Branded {plat} post for {name}: one clear headline about a current offer or tip for their customers, a clean photo area, and the business logo placeholder.",
        reel_idea="15-second reel: (1) hook with a question customers ask, (2) 2 quick visual tips, (3) a friendly team moment, (4) a simple call to action.",
        caption=f"Short, friendly caption for {plat} that answers one common customer question, ends with one clear next step.",
        cta="Message us / book / visit this week (adapt to the business).",
        design_direction=f"Consistent colours and fonts for {ind.lower()}; large readable text; one repeatable template so posts feel like a set.",
        why_it_works=f"Addresses the visible gap: {problem or 'inconsistent content'}. AI-generated sample idea for demonstration only.",
    )


def campaign(p: UserProfileInput, row: dict, q: Optional[ProspectQualification], o: Offer, has_sample: bool) -> OutreachCampaign:
    sender = p.name or "[Your Name]"
    name = row.get("company_name", "your business")
    role = row.get("contact_role", "team")
    sample_line = "I sketched a quick content idea for you and would be happy to send it over if useful.\n\n" if has_sample else ""
    industry = (row.get("industry") or "small business").lower()
    return OutreachCampaign(
        company_name=name,
        subject=f"A quick content idea for {name}",
        initial_email=(
            f"Hi {name} team,\n\n"
            f"I came across your {row.get('social_platform', 'social')} page and had a small idea for making your posts easier to notice.\n\n"
            f"I'm a freelance designer who helps businesses in the {industry} space keep their content consistent with "
            f"simple branded templates. {sample_line}"
            f"Would it be useful if I shared a short idea tailored to {name}?\n\nBest,\n{sender}"
        ),
        followups=[
            FollowUp(day_offset=3, subject=f"Re: A quick content idea for {name}",
                     body=f"Hi {name} team,\n\nJust a gentle follow-up on my note. Happy to send a short content idea if that's helpful, and no worries if the timing isn't right.\n\nBest,\n{sender}"),
            FollowUp(day_offset=7, subject=f"Closing the loop, {name}",
                     body=f"Hi {name} team,\n\nLast note from me. If content support ever becomes a priority, I'd be glad to help. Wishing you a great month.\n\nBest,\n{sender}"),
        ],
        cta="Would it be useful if I shared a short idea?",
        personalization_notes=f"Mentions the {row.get('social_platform','social')} page and the visible gap. Check the business's page yourself before sending; demo data is fictional. Add the real contact (a {role}) after verifying it.",
        suggested_interval="Follow-up 1 after 3 days, follow-up 2 after 7 days.",
    )
