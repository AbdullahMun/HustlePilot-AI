"""Page renderers. Each takes the Streamlit session state and draws one screen."""
from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from agents import followup_agent
from config import settings
from services.prospect_service import ProspectDataError, prospect_dict
from ui import styles
from ui.styles import badge, kv, level_badge, metric_card, page_header, source_note, status_badge
from utils import helpers
from utils.validation import scan_risky_phrases, validate_profile
from workflows import hustle_workflow as wf


# ------------------------------------------------------------------ shared ---
def _goto(key: str) -> None:
    st.session_state["goto"] = key


def go_button(label: str, target: str, key: str, primary: bool = False) -> None:
    st.button(label, key=key, on_click=_goto, args=(target,),
              type="primary" if primary else "secondary")


def gate(state, step_key: str) -> bool:
    missing = wf.missing_prerequisite(step_key, state)
    if missing is None:
        return True
    st.warning(wf.STEP_BY_KEY[step_key].needs_message)
    go_button(f"Go to {missing.label}", missing.key,
              f"gate_{step_key}", primary=True)
    return False


def _bullets(items) -> None:
    st.markdown(helpers.bullets(items) or "_Nothing listed._")


def _load_prospects_or_stop(state):
    try:
        return wf.load_prospects(state)
    except ProspectDataError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Something went wrong while loading the prospect data.")
    return None


def _qualified_ids(state) -> list:
    q = state["qualifications"]
    ids = [pid for pid, item in q.items() if item.qualified]
    return sorted(ids, key=lambda pid: q[pid].fit_score, reverse=True)


def _pick_prospect(state, key: str):
    ids = _qualified_ids(state)
    if not ids:
        st.info("No qualified prospects yet. Qualify prospects first, or lower the bar by reviewing the Prospects page.")
        go_button("Go to Prospects", "prospects", f"nopros_{key}")
        return None
    q = state["qualifications"]
    labels = {
        pid: f"{q[pid].company_name or pid}  (fit {q[pid].fit_score})" for pid in ids}
    return st.selectbox("Prospect", ids, format_func=lambda pid: labels[pid], key=key)


def _run(label: str, fn, *args):
    """Run an agent step with a spinner; the agent layer already handles failures."""
    try:
        with st.spinner(label):
            return fn(*args)
    except Exception:
        st.error(
            "Something unexpected went wrong. Please try again, or switch on Demo mode in the sidebar.")
        return None


# --------------------------------------------------------------- dashboard ---
def page_dashboard(state) -> None:
    page_header(settings.APP_NAME, settings.TAGLINE)
    done_map = {s.key: wf.is_done(s.key, state) for s in wf.FLOW_STEPS}
    st.markdown(styles.flight_track(wf.FLOW_STEPS,
                "dashboard", done_map), unsafe_allow_html=True)

    # # df = _load_prospects_or_stop(state)
    # metrics = followup_agent.dashboard_metrics(state["leads"])
    # # if df is not None else {})
    
    df = state.get("prospects_df")
    metrics = followup_agent.dashboard_metrics(state["leads"])
    
    names = list(metrics)
    for row in (names[:4], names[4:]):
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            col.markdown(metric_card(
                name, metrics[name]), unsafe_allow_html=True)
    st.write("")

    nxt = wf.next_step(state)
    left, right = st.columns([3, 2])
    with left:
        with st.container(border=True):
            if nxt is None:
                st.markdown(
                    "**Every step has been completed.** Review your leads below and keep following up manually.")
            else:
                st.markdown(f"**Next step: {nxt.label}**")
                st.caption(
                    "Work through the steps in order. Nothing is ever sent for you; you review and send outreach yourself.")
                go_button(f"Open {nxt.label}", nxt.key,
                          "dash_next", primary=True)
    with right:
        with st.container(border=True):
            st.markdown("**How this works**")
            st.caption("Skills, niche, offer, ideal client, prospects, a personal sample, outreach, follow-ups. "
                       "Suggestions are AI-generated and unverified. No income or client results are promised.")

    # st.subheader("Lead pipeline")
    # # if df is None or not state["qualifications"]:
    # if not state["qualifications"]:
    #     st.info("Your pipeline fills in after you qualify prospects. Start with My Profile.")
    #     if not wf.is_done("profile", state):
    #         go_button("Start with My Profile", "profile", "dash_start", primary=True)
    # else:
    #     table = followup_agent.leads_dataframe(state["leads"], df, state["qualifications"])
    #     st.dataframe(table, hide_index=True, column_config={
    #         "Fit score": st.column_config.ProgressColumn("Fit score", min_value=0, max_value=100, format="%d")})
    # # if df is not None:
    # #     styles.demo_data_banner()

    st.subheader("Lead pipeline")

    df = state.get("prospects_df")

    if not state["qualifications"]:
        st.info("Your pipeline fills in after you qualify prospects. Start with My Profile.")

        if not wf.is_done("profile", state):
            go_button("Start with My Profile", "profile",
                    "dash_start", primary=True)

    else:
        if df is not None:
            table = followup_agent.leads_dataframe(
                state["leads"],
                df,
                state["qualifications"]
            )

            st.dataframe(
                table,
                hide_index=True,
                column_config={
                    "Fit score": st.column_config.ProgressColumn(
                        "Fit score",
                        min_value=0,
                        max_value=100,
                        format="%d"
                    )
                }
            )


# ----------------------------------------------------------------- profile ---
def _load_demo_profile() -> None:
    for key, value in helpers.DEMO_PROFILE.items():
        st.session_state[key] = value


def page_profile(state) -> None:
    page_header(
        "My Profile", "Tell us what you can do and how much time you have. This is the starting point for everything else.")
    st.button("Load the demo example", on_click=_load_demo_profile,
              help="Fills the form with: Canva + AI tools, 2-3 hours/day, earning in USD")
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input(
                "Your name (optional, used to sign drafts)", key="pf_name")
            st.text_area("Skills", key="pf_skills", height=90,
                         placeholder="e.g. Canva, AI tools, copywriting, video editing")
            st.text_area("Experience", key="pf_experience", height=90,
                         placeholder="What have you made or done so far?")
            st.text_input("Tools you use", key="pf_tools",
                          placeholder="e.g. Canva, CapCut, ChatGPT")
        with c2:
            st.slider("Hours available per day", 0.5,
                      8.0, step=0.5, key="pf_hours")
            st.selectbox("Preferred work type",
                         helpers.WORK_TYPES, key="pf_worktype")
            st.selectbox("Currency you want to earn in",
                         helpers.CURRENCIES, key="pf_currency")
            st.selectbox("Portfolio level",
                         helpers.PORTFOLIO_LEVELS, key="pf_portfolio")
            st.text_input("Strengths", key="pf_strengths",
                          placeholder="What are you good at?")
            st.text_input("Limitations", key="pf_limits",
                          placeholder="Anything holding you back?")
        submitted = st.form_submit_button("Analyze profile", type="primary")

    if submitted:
        s = st.session_state
        profile, errors = validate_profile({
            "name": s["pf_name"], "skills": s["pf_skills"], "experience": s["pf_experience"],
            "hours_per_day": float(s["pf_hours"]), "work_type": s["pf_worktype"], "tools": s["pf_tools"],
            "currency": s["pf_currency"], "strengths": s["pf_strengths"], "limitations": s["pf_limits"],
            "portfolio_level": s["pf_portfolio"],
        })
        if errors:
            for e in errors:
                st.error(e)
        else:
            state["profile"] = profile
            _run("Analyzing your profile...", wf.run_profile_analysis, state)

    a = state["analysis"]
    if a is None:
        st.info(
            "Fill in the form (or load the demo example) and select Analyze profile.")
        return
    st.subheader("Profile analysis")
    source_note(state, "analysis")
    st.markdown(a.summary)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Core skills**")
        _bullets(a.core_skills)
        st.markdown("**Marketable strengths**")
        _bullets(a.marketable_strengths)
    with c2:
        st.markdown("**Limitations to plan around**")
        _bullets(a.limitations)
        st.markdown("**Suggested next steps**")
        _bullets(a.next_steps)
    with st.expander("Time, portfolio and work style"):
        kv("Time", a.time_assessment)
        kv("Portfolio", a.portfolio_assessment)
        kv("Work style", a.recommended_work_style)
    go_button("Continue to Discover Niches",
              "niches", "prof_next", primary=True)


# ------------------------------------------------------------------ niches ---
def page_niches(state) -> None:
    page_header("Discover Niches",
                "Several options that fit your skills. Pick the one you want to explore; none is declared the best.")
    if not gate(state, "niches"):
        return
    if st.button("Generate niche options" if not state["niches"] else "Regenerate niche options", type="primary"):
        _run("Looking for niches that fit your profile...",
             wf.run_niche_discovery, state)
        st.rerun()
    if not state["niches"]:
        st.info("Select Generate niche options to see suggestions.")
        return
    source_note(state, "niches")
    chosen = state["selected_niche"]
    for i, n in enumerate(state["niches"]):
        is_sel = chosen is not None and chosen.name == n.name
        with st.container(border=True):
            st.markdown(f"### {n.name}")
            st.markdown(
                " ".join([badge(f"Difficulty: {n.difficulty}" if n.difficulty else "Difficulty: n/a", "amber"),
                          badge(f"Market: {n.target_market}",
                                "blue") if n.target_market else "",
                          badge("Selected", "green") if is_sel else ""]),
                unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                kv("Target customer", n.target_customer)
                kv("Buyer type", n.buyer_type)
                kv("Customer problem", n.customer_problem)
                kv("Suggested service", n.suggested_service)
            with c2:
                kv("Why it matches you", n.skill_match_reason)
                kv("Client accessibility", n.client_accessibility)
                kv("Recurring revenue potential", n.recurring_revenue_potential)
                kv("Portfolio difficulty", n.portfolio_difficulty)
            kv("Risks and limitations", n.risks)
            if not is_sel and st.button("Select this niche", key=f"sel_{i}"):
                wf.select_niche(state, i)
                st.rerun()
    if chosen is not None:
        st.success(f"Selected niche: {chosen.name}")
        c1, c2 = st.columns(2)
        with c1:
            go_button("Validate this niche", "validate",
                      "niche_val", primary=True)
        with c2:
            go_button("Skip to Build Offer", "offer", "niche_offer")


# ---------------------------------------------------------------- validate ---
def page_validate(state) -> None:
    page_header("Validate Niche",
                "Stress-test the niche before you build an offer around it.")
    if not gate(state, "validate"):
        return
    n = state["selected_niche"]
    st.markdown(f"**Selected niche:** {n.name}")
    st.markdown('<div class="hp-note">This validation is AI reasoning, not market research. Nothing here has been verified against real data.</div>', unsafe_allow_html=True)
    if st.button("Validate niche" if state["validation"] is None else "Re-run validation", type="primary"):
        _run("Validating the niche...", wf.run_niche_validation, state)
    v = state["validation"]
    if v is None:
        return
    source_note(state, "validation")
    if v.summary:
        st.markdown(v.summary)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="hp-assume"><h4>AI-generated assumptions (unverified)</h4><ul>'
                    + "".join(f"<li>{helpers.esc(a)}</li>" for a in v.ai_assumptions) + "</ul></div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="hp-verify"><h4>Verify these yourself</h4><ul>'
                    + "".join(f"<li>{helpers.esc(a)}</li>" for a in v.how_to_verify) + "</ul></div>", unsafe_allow_html=True)
    st.caption("The app does not retrieve live market data, so there are no verified facts here. Use the checks on the right to confirm the assumptions.")
    t1, t2, t3 = st.tabs(
        ["Buyers and problem", "Difficulty and delivery", "Risks and alternatives"])
    with t1:
        kv("Who buys", v.who_buys)
        kv("Problem customers pay to solve", v.problem_customers_pay_for)
        kv("Why it matters", v.why_it_matters)
    with t2:
        kv("Acquisition difficulty", v.acquisition_difficulty)
        kv("Portfolio difficulty", v.portfolio_difficulty)
        kv("Remote delivery feasibility", v.remote_delivery_feasibility)
        kv("Recurring potential", v.recurring_potential)
    with t3:
        st.markdown("**Risks**")
        _bullets(v.risks)
        st.markdown("**Alternatives customers use today**")
        _bullets(v.alternatives)
    go_button("Continue to Build Offer", "offer", "val_next", primary=True)


# ------------------------------------------------------------------- offer ---
def page_offer(state) -> None:
    page_header(
        "Build Offer", "Turn the niche into a clear, productised service with three packages.")
    if not gate(state, "offer"):
        return
    st.markdown(f"**Niche:** {state['selected_niche'].name}")
    if st.button("Build offer" if state["offer"] is None else "Rebuild offer", type="primary"):
        _run("Designing your offer...", wf.run_offer, state)
    o = state["offer"]
    if o is None:
        return
    source_note(state, "offer")
    st.subheader(o.offer_name)
    st.markdown(o.description)
    t1, t2, t3 = st.tabs(["Overview", "Packages", "Portfolio and outcome"])
    with t1:
        kv("Target customer", o.target_customer)
        kv("Customer problem", o.customer_problem)
        kv("Value proposition", o.value_proposition)
        kv("Unique angle", o.unique_angle)
        kv("Delivery time", o.delivery_time)
        kv("Revision policy", o.revision_policy)
        st.markdown("**Deliverables**")
        _bullets(o.deliverables)
    with t2:
        st.markdown(
            '<span class="hp-label">Suggested Example Pricing (USD)</span>', unsafe_allow_html=True)
        cols = st.columns(max(1, len(o.packages)))
        for col, pkg in zip(cols, o.packages):
            with col, st.container(border=True):
                st.markdown(f"**{pkg.name}**")
                st.markdown(
                    f'<div class="hp-price">{helpers.esc(pkg.suggested_example_price_usd)}</div>', unsafe_allow_html=True)
                _bullets(pkg.includes)
                if pkg.best_for:
                    st.caption(f"Best for: {pkg.best_for}")
        st.caption(
            o.pricing_note or "Illustrative example prices only. They are not verified market rates and not guaranteed income.")
    with t3:
        st.markdown("**Build this before pitching**")
        _bullets(o.portfolio_requirements)
        kv("Example outcome (illustrative, not guaranteed)", o.example_outcome)
    go_button("Continue to Ideal Client", "icp", "offer_next", primary=True)


# --------------------------------------------------------------------- icp ---
def page_icp(state) -> None:
    page_header("Ideal Client",
                "Describe who your offer is for, so prospects can be compared against it.")
    if not gate(state, "icp"):
        return
    if st.button("Generate ideal client profile" if state["icp"] is None else "Regenerate profile", type="primary"):
        _run("Building your ideal client profile...", wf.run_icp, state)
    i = state["icp"]
    if i is None:
        return
    source_note(state, "icp")
    c1, c2 = st.columns(2)
    with c1:
        kv("Country / market", i.country)
        kv("Industry", i.industry)
        kv("Business type", i.business_type)
        kv("Business size", i.business_size)
        kv("Decision maker (role)", i.decision_maker)
    with c2:
        kv("Typical problem", i.typical_problem)
        kv("Buying trigger", i.buying_trigger)
        kv("Why relevant", i.why_relevant)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Fit signals to look for**")
        _bullets(i.fit_signals)
    with c4:
        st.markdown("**Where to find them**")
        _bullets(i.where_to_find)
    go_button("Continue to Prospects", "prospects", "icp_next", primary=True)


# --------------------------------------------------------------- prospects ---
def page_prospects(state) -> None:
    page_header(
        "Prospects", "Demo businesses compared against your ideal client profile.")
    if not gate(state, "prospects"):
        return
    df = _load_prospects_or_stop(state)
    if df is None:
        return
    styles.demo_data_banner()
    if st.button("Qualify prospects" if not state["qualifications"] else "Re-qualify prospects", type="primary"):
        _run("Comparing prospects with your ideal client profile...",
             wf.run_qualification, state)
    q = state["qualifications"]

    f1, f2, f3 = st.columns(3)
    industries = f1.multiselect("Industry", sorted(df["industry"].unique()))
    countries = f2.multiselect("Country", sorted(df["country"].unique()))
    search = f3.text_input("Search company or description")
    view = df.copy()
    if industries:
        view = view[view["industry"].isin(industries)]
    if countries:
        view = view[view["country"].isin(countries)]
    if search.strip():
        mask = view["company_name"].str.contains(
            search, case=False, regex=False) | view["business_description"].str.contains(search, case=False, regex=False)
        view = view[mask]

    if not q:
        st.dataframe(view[["prospect_id", "company_name", "industry", "country",
                     "city", "social_platform", "contact_role"]], hide_index=True)
        st.info(
            "Select Qualify prospects to score each one against your ideal client profile.")
        return

    source_note(state, "qualifications")
    view = view.assign(
        fit_score=view["prospect_id"].map(
            lambda p: q[p].fit_score if p in q else 0),
        fit_level=view["prospect_id"].map(
            lambda p: q[p].fit_level if p in q else ""),
        qualified=view["prospect_id"].map(
            lambda p: bool(q[p].qualified) if p in q else False),
    ).sort_values("fit_score", ascending=False)
    cols = ["prospect_id", "company_name", "industry",
            "country", "fit_score", "fit_level", "qualified"]
    cfg = {"fit_score": st.column_config.ProgressColumn(
        "Fit score", min_value=0, max_value=100, format="%d")}
    tab_all, tab_q = st.tabs(
        [f"All ({len(view)})", f"Qualified ({int(view['qualified'].sum())})"])
    with tab_all:
        st.dataframe(view[cols], hide_index=True, column_config=cfg)
    with tab_q:
        st.dataframe(view[view["qualified"]][cols],
                     hide_index=True, column_config=cfg)

    st.subheader("Inspect a prospect")
    ids = list(view["prospect_id"])
    if not ids:
        st.info("No prospects match the current filters.")
        return
    pid = st.selectbox(
        "Prospect", ids, format_func=lambda p: f"{q[p].company_name or p} (fit {q[p].fit_score})" if p in q else p, key="inspect_pid")
    row, item = prospect_dict(df, pid), q.get(pid)
    with st.container(border=True):
        st.markdown(f"### {row.get('company_name')}  " +
                    (level_badge(item.fit_level) if item else ""), unsafe_allow_html=True)
        st.caption(
            f"{row.get('industry')} | {row.get('city')}, {row.get('country')} | {row.get('social_platform')} | {row.get('website')}")
        kv("About", row.get("business_description"))
        kv("Online activity", row.get("online_activity"))
        kv("Contact role", row.get("contact_role"))
        if item:
            st.markdown("---")
            kv("Why this may fit", item.why_fit)
            kv("Recommended angle", item.recommended_angle)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Fit signals found**")
                _bullets(item.fit_signals_found)
            with c2:
                st.markdown("**Potential problems to help with**")
                _bullets(item.potential_problems)
        st.caption(
            "Sample record. Find and verify a real, appropriate contact yourself before reaching out to any real business.")
    go_button("Continue to Client Sample", "sample", "pros_next", primary=True)


# ------------------------------------------------------------------ sample ---
def page_sample(state) -> None:
    page_header("Client Sample",
                "A small, personalised idea you can prepare to show value before you reach out.")
    if not gate(state, "sample"):
        return
    pid = _pick_prospect(state, "sample_pid")
    if pid is None:
        return
    row = prospect_dict(state["prospects_df"], pid)
    st.caption(
        f"{row.get('industry')} | {row.get('city')}, {row.get('country')} | {row.get('potential_problem')}")
    if st.button("Generate sample idea" if pid not in state["samples"] else "Regenerate sample idea", type="primary"):
        _run("Creating a personalised sample idea...", wf.run_sample, state, pid)
    s = state["samples"].get(pid)
    if s is None:
        return
    source_note(state, f"sample:{pid}")
    st.markdown('<span class="hp-label">AI-generated sample idea</span>',
                unsafe_allow_html=True)
    st.caption(
        "This is an idea for you to build and review. It has not been created for or sent to this business.")
    with st.container(border=True):
        st.markdown("**Sample post**")
        st.markdown(s.sample_post)
        st.markdown("**Reel idea**")
        st.markdown(s.reel_idea)
        st.markdown("**Caption**")
        st.markdown(s.caption)
        kv("Call to action", s.cta)
        kv("Design direction", s.design_direction)
        kv("Why it works", s.why_it_works)
    go_button("Continue to Outreach", "outreach", "sample_next", primary=True)


# ---------------------------------------------------------------- outreach ---
def _seed(key: str, value: str) -> None:
    if key not in st.session_state:
        st.session_state[key] = value


def _set_campaign_widgets(pid: str, c) -> None:
    st.session_state[f"subj_{pid}"] = c.subject
    st.session_state[f"mail_{pid}"] = c.initial_email
    for j, fu in enumerate(c.followups[:2]):
        st.session_state[f"fu{j}_subj_{pid}"] = fu.subject
        st.session_state[f"fu{j}_body_{pid}"] = fu.body


def _generate_campaign(state, pid: str) -> None:
    c = _run("Drafting outreach...", wf.run_campaign, state, pid)
    if c is not None:
        _set_campaign_widgets(pid, c)


def _bulk_campaigns(state, ids: list) -> None:
    bar = st.progress(0.0)
    for n, pid in enumerate(ids, 1):
        _generate_campaign(state, pid)
        bar.progress(n / len(ids))
    bar.empty()


def page_outreach(state) -> None:
    page_header(
        "Outreach", "Review and edit each draft. Nothing is sent for you: you copy it and send it yourself.")
    if not gate(state, "outreach"):
        return
    st.markdown('<div class="hp-note">Human-in-the-loop: HustlePilot never sends emails or social messages. Approve a draft to unlock copy and email actions.</div>', unsafe_allow_html=True)
    ids = _qualified_ids(state)
    pid = _pick_prospect(state, "outreach_pid")
    if pid is None:
        return
    c1, c2 = st.columns(2)
    if c1.button("Generate campaign" if pid not in state["campaigns"] else "Regenerate campaign", type="primary"):
        _generate_campaign(state, pid)
    missing = [p for p in ids if p not in state["campaigns"]
               ][: settings.MAX_BULK_CAMPAIGNS]
    if missing and c2.button(f"Generate for next {len(missing)} qualified prospects"):
        _bulk_campaigns(state, missing)

    camp = state["campaigns"].get(pid)
    if camp is None:
        st.info("Generate a campaign to review the drafts.")
        return
    source_note(state, f"campaign:{pid}")
    lead = state["leads"].setdefault(pid, followup_agent.new_lead())
    st.markdown("Status: " + status_badge(lead["status"]) + ("  " + badge(
        "Approved by you", "green") if lead["approved"] else ""), unsafe_allow_html=True)

    _seed(f"subj_{pid}", camp.subject)
    _seed(f"mail_{pid}", camp.initial_email)
    st.text_input("Subject", key=f"subj_{pid}")
    st.text_area("Initial email", key=f"mail_{pid}", height=230)
    fu_values = []
    for j, fu in enumerate(camp.followups[:2]):
        _seed(f"fu{j}_subj_{pid}", fu.subject)
        _seed(f"fu{j}_body_{pid}", fu.body)
        with st.expander(f"Follow-up #{j + 1} (suggested after {fu.day_offset} days)"):
            st.text_input("Subject", key=f"fu{j}_subj_{pid}")
            st.text_area("Message", key=f"fu{j}_body_{pid}", height=170)
        fu_values.append(
            (st.session_state[f"fu{j}_subj_{pid}"], st.session_state[f"fu{j}_body_{pid}"], fu.day_offset))

    flagged = scan_risky_phrases(
        st.session_state[f"mail_{pid}"] + " " + " ".join(b for _, b, _ in fu_values))
    if flagged:
        st.warning(
            "Review these phrases before sending, they can sound spammy or make claims: " + ", ".join(flagged))
    with st.expander("Personalization notes and timing"):
        kv("Call to action", camp.cta)
        kv("Personalization notes", camp.personalization_notes)
        kv("Suggested interval", camp.suggested_interval)
        st.caption(
            "Check every claim against reality. Do not mention work or results you have not actually done.")

    if st.button("Approve this campaign"):
        updated = camp.model_copy(update={
            "subject": st.session_state[f"subj_{pid}"], "initial_email": st.session_state[f"mail_{pid}"],
            "followups": [f.model_copy(update={"subject": s, "body": b}) for f, (s, b, _) in zip(camp.followups, fu_values)] + camp.followups[len(fu_values):],
        })
        state["campaigns"][pid] = updated
        followup_agent.approve_campaign(state["leads"], pid)
        st.rerun()

    if not lead["approved"]:
        return
    st.markdown("#### Send it yourself")
    subj, body = st.session_state[f"subj_{pid}"], st.session_state[f"mail_{pid}"]
    st.caption("Copy the text (hover over the box and use the copy icon), or open it in your email app. The email opens with no recipient: add a verified address yourself.")
    st.code(f"Subject: {subj}\n\n{body}", language=None, wrap_lines=True)
    st.link_button("Open in my email app", helpers.mailto_link(subj, body))
    first_gap = fu_values[0][2] if fu_values else 3
    if lead["status"] in {"New", "Qualified", "Campaign Ready"}:
        if st.button("Mark as contacted (after you have sent it)"):
            followup_agent.mark_contacted(state["leads"], pid, first_gap)
            st.success(
                f"Marked as contacted. First follow-up suggested in {first_gap} days.")
            st.rerun()
    else:
        d = st.date_input("Next follow-up date", value=date.fromisoformat(
            lead["next_followup"]) if lead["next_followup"] else date.today() + timedelta(days=first_gap), key=f"fud_{pid}")
        if st.button("Schedule follow-up"):
            followup_agent.schedule_followup(state["leads"], pid, d)
            st.success(f"Follow-up scheduled for {d.isoformat()}.")
    go_button("Go to Follow-ups", "followups", "out_next")


# --------------------------------------------------------------- follow-ups ---
def page_followups(state) -> None:
    page_header(
        "Follow-ups", "Track every lead, see who is due, and change statuses as conversations move.")
    df = _load_prospects_or_stop(state)
    if df is None:
        return
    followup_agent.refresh_due(state["leads"])
    metrics = followup_agent.dashboard_metrics(state["leads"])
    cols = st.columns(len(metrics))
    for col, (k, v) in zip(cols, metrics.items()):
        col.markdown(metric_card(k, v), unsafe_allow_html=True)
    st.write("")

    due = [pid for pid, lead in state["leads"].items() if lead["status"]
           == "Follow-up Due"]
    st.subheader(f"Due now ({len(due)})")
    if not due:
        st.caption(
            "Nothing is due. Leads you mark as contacted show up here when their follow-up date arrives.")
    for pid in due:
        row = prospect_dict(df, pid)
        camp = state["campaigns"].get(pid)
        with st.expander(f"{row.get('company_name')} - follow-up due"):
            if camp and camp.followups:
                for j, fu in enumerate(camp.followups[:2], 1):
                    st.markdown(
                        f"**Follow-up #{j}** (suggested after {fu.day_offset} days)")
                    st.code(f"Subject: {fu.subject}\n\n{fu.body}",
                            language=None, wrap_lines=True)
            else:
                st.caption(
                    "No saved follow-up drafts. Generate a campaign on the Outreach page.")
            c1, c2 = st.columns(2)
            if c1.button("Snooze 3 days", key=f"snooze_{pid}"):
                followup_agent.schedule_followup(
                    state["leads"], pid, date.today() + timedelta(days=3))
                state["leads"][pid]["status"] = "Contacted"
                st.rerun()
            if c2.button("Mark interested", key=f"int_{pid}"):
                followup_agent.set_status(state["leads"], pid, "Interested")
                st.rerun()

    st.subheader("All leads")
    table = followup_agent.leads_dataframe(
        state["leads"], df, state["qualifications"])
    status_filter = st.multiselect("Filter by status", followup_agent.STATUSES)
    if status_filter:
        table = table[table["Status"].isin(status_filter)]
    st.dataframe(table, hide_index=True, column_config={
        "Fit score": st.column_config.ProgressColumn("Fit score", min_value=0, max_value=100, format="%d")})

    st.subheader("Update a lead")
    pid = st.selectbox("Lead", list(df["prospect_id"]), format_func=lambda p: prospect_dict(
        df, p).get("company_name", p), key="lead_pid")
    lead = state["leads"].setdefault(pid, followup_agent.new_lead())
    st.markdown("Current status: " +
                status_badge(lead["status"]), unsafe_allow_html=True)
    new_status = st.selectbox("Change status", followup_agent.STATUSES,
                              index=followup_agent.STATUSES.index(lead["status"]), key=f"status_{pid}")
    note = st.text_input("Notes", value=lead.get(
        "notes", ""), key=f"note_{pid}")
    c1, c2 = st.columns(2)
    if c1.button("Save changes", type="primary"):
        followup_agent.set_status(state["leads"], pid, new_status)
        lead["notes"] = note
        st.success("Lead updated.")
        st.rerun()
    when = c2.date_input("Schedule follow-up", value=date.today() +
                         timedelta(days=3), min_value=date.today(), key=f"when_{pid}")
    if c2.button("Schedule follow-up date"):
        followup_agent.schedule_followup(state["leads"], pid, when)
        st.success(f"Follow-up scheduled for {when.isoformat()}.")
        st.rerun()
    if lead["history"]:
        with st.expander("Activity history"):
            _bullets(reversed(lead["history"]))
