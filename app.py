"""HustlePilot AI - From Skills to Your First Client.

Run locally:  streamlit run app.py
"""
import logging

import streamlit as st

# set_page_config must be the first Streamlit call.
st.set_page_config(page_title="HustlePilot AI", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

from config import settings  # noqa: E402
from agents import followup_agent  # noqa: E402
from ui import pages, styles  # noqa: E402
from utils.helpers import init_state  # noqa: E402
from workflows import hustle_workflow as wf  # noqa: E402

ROUTES = {
    "dashboard": pages.page_dashboard,
    "profile": pages.page_profile,
    "niches": pages.page_niches,
    "validate": pages.page_validate,
    "offer": pages.page_offer,
    "icp": pages.page_icp,
    "prospects": pages.page_prospects,
    "sample": pages.page_sample,
    "outreach": pages.page_outreach,
    "followups": pages.page_followups,
}


def _reset_all() -> None:
    st.session_state.clear()


def _sidebar(state) -> None:
    with st.sidebar:
        st.markdown(
            f'<div class="hp-brand"><b>{settings.APP_NAME}</b><span>{settings.TAGLINE}</span></div>',
            unsafe_allow_html=True,
        )
        labels = {s.key: s.label for s in wf.STEPS}

        def fmt(key: str) -> str:
            return ("✓  " if wf.is_done(key, state) else "     ") + labels[key]

        st.radio("Navigate", list(ROUTES), format_func=fmt, key="nav", label_visibility="collapsed")
        # done = sum(wf.is_done(s.key, state) for s in wf.FLOW_STEPS)
        # st.progress(wf.progress(state))
        # st.caption(f"{done} of {len(wf.FLOW_STEPS)} steps complete")
        done = sum(wf.is_done(s.key, state) for s in wf.FLOW_STEPS)

        # Follow-ups is the final workflow step.
        # Once the user reaches it, the workflow is considered complete.
        if st.session_state.get("nav") == "followups":
            done = len(wf.FLOW_STEPS)

        st.progress(done / len(wf.FLOW_STEPS))
        st.caption(f"{done} of {len(wf.FLOW_STEPS)} steps complete")

        with st.expander("AI settings"):
            if state["force_demo"]:
                st.caption("Demo mode is on: no Gemini calls are made.")
            elif settings.has_api_key():
                st.caption(f"Gemini key found. Model: {settings.get_model_name()}")
            else:
                st.caption("No Gemini key found. The app runs in Demo / Fallback Mode.")
            st.checkbox("Demo mode (no API calls)", key="force_demo")
            st.text_input("Use my own Gemini key (this session only)", type="password", key="user_api_key",
                          help="Kept in memory for this browser session. Never saved or logged.")
        st.button("Reset everything", on_click=_reset_all)
        st.caption("Drafts only. HustlePilot never sends messages for you.")


def main() -> None:
    styles.inject_css()
    state = st.session_state
    init_state(state)
    if "goto" in state:
        state["nav"] = state.pop("goto")
    followup_agent.refresh_due(state["leads"])
    _sidebar(state)
    try:
        ROUTES[state["nav"]](state)
    except Exception:
        logging.getLogger(__name__).exception("Page render failed")
        st.error("Something went wrong on this page. Your other progress is safe. Try again, or pick another step.")


main()
