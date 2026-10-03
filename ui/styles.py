# """Visual layer: CSS plus small HTML components. All dynamic text is HTML-escaped."""
# from __future__ import annotations

# import streamlit as st

# from utils.helpers import esc

# CSS = """
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
# :root{--ink:#17212B;--muted:#5B6773;--line:#E1E6EC;--surface:#FFFFFF;--teal:#0F6E6E;--teal-soft:#E3F1F0;--amber:#E8A317;--amber-soft:#FBF1D9;--red-soft:#F8E4E1;--red:#A5372B;--green:#1E7F52;--green-soft:#E2F2EA;--blue:#2A5DA8;--blue-soft:#E4ECF8;}
# .block-container{padding-top:2.2rem;padding-bottom:4rem;max-width:1180px;}
# h1,h2,h3,h4,.stMarkdown p,.stMarkdown li,.stButton button,label{font-family:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif;}
# h1{font-weight:800;letter-spacing:-0.02em;}
# h2,h3{font-weight:700;letter-spacing:-0.01em;}
# [data-testid="stSidebar"]{background:var(--surface);border-right:1px solid var(--line);}
# [data-testid="stMetric"]{background:var(--surface);}
# .hp-brand{padding:.2rem 0 1rem 0;border-bottom:1px solid var(--line);margin-bottom:1rem;}
# .hp-brand b{font-family:'Manrope',sans-serif;font-size:1.25rem;font-weight:800;color:var(--ink);}
# .hp-brand span{display:block;color:var(--muted);font-size:.82rem;margin-top:.15rem;}
# .hp-header{margin-bottom:1.1rem;}
# .hp-header h1{margin:0 0 .25rem 0;font-size:2rem;}
# .hp-header p{margin:0;color:var(--muted);font-size:1rem;max-width:70ch;}
# .hp-card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:1rem 1.15rem;}
# .hp-metric{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:.85rem 1rem;}
# .hp-metric .v{font-family:'Manrope',sans-serif;font-size:1.75rem;font-weight:800;color:var(--ink);line-height:1.1;}
# .hp-metric .l{color:var(--muted);font-size:.82rem;margin-top:.25rem;}
# .hp-badge{display:inline-block;padding:.12rem .55rem;border-radius:999px;font-size:.78rem;font-weight:600;white-space:nowrap;}
# .hp-b-gray{background:#EDF0F3;color:#46515C;}.hp-b-teal{background:var(--teal-soft);color:var(--teal);}
# .hp-b-blue{background:var(--blue-soft);color:var(--blue);}.hp-b-amber{background:var(--amber-soft);color:#8A5F00;}
# .hp-b-green{background:var(--green-soft);color:var(--green);}.hp-b-red{background:var(--red-soft);color:var(--red);}
# .hp-b-slate{background:#DDE3EA;color:#26323D;}.hp-b-indigo{background:#E8E6F7;color:#4338A0;}
# .hp-track{display:flex;gap:0;margin:.4rem 0 1.4rem 0;overflow-x:auto;padding-bottom:.4rem;}
# .hp-node{flex:1 0 92px;position:relative;text-align:center;padding-top:26px;font-size:.76rem;color:var(--muted);font-weight:500;}
# .hp-node:before{content:"";position:absolute;top:8px;left:-50%;width:100%;height:3px;background:var(--line);}
# .hp-node:first-child:before{display:none;}
# .hp-node:after{content:"";position:absolute;top:1px;left:calc(50% - 8px);width:14px;height:14px;border-radius:50%;background:var(--surface);border:2px solid var(--line);}
# .hp-node.done{color:var(--ink);}.hp-node.done:before{background:var(--teal);}
# .hp-node.done:after{background:var(--teal);border-color:var(--teal);}
# .hp-node.now{color:var(--ink);font-weight:700;}.hp-node.now:before{background:var(--teal);}
# .hp-node.now:after{border-color:var(--amber);background:var(--amber);box-shadow:0 0 0 4px var(--amber-soft);}
# .hp-note{font-size:.84rem;color:var(--muted);margin:.2rem 0 .8rem 0;}
# .hp-demo{background:var(--amber-soft);border:1px solid #EACD8A;border-radius:8px;padding:.6rem .85rem;color:#6B4A00;font-size:.9rem;margin:.2rem 0 .9rem 0;}
# .hp-live{background:var(--green-soft);border:1px solid #B9DEC9;border-radius:8px;padding:.45rem .85rem;color:var(--green);font-size:.84rem;margin:.2rem 0 .9rem 0;}
# .hp-assume{background:var(--amber-soft);border-left:4px solid var(--amber);padding:.7rem 1rem;border-radius:6px;}
# .hp-verify{background:var(--blue-soft);border-left:4px solid var(--blue);padding:.7rem 1rem;border-radius:6px;}
# .hp-assume h4,.hp-verify h4{margin:0 0 .4rem 0;font-size:1rem;}
# .hp-assume ul,.hp-verify ul{margin:0;padding-left:1.1rem;}
# .hp-kv{margin:.15rem 0;font-size:.93rem;}.hp-kv b{color:var(--ink);}
# .hp-price{font-family:'Manrope',sans-serif;font-size:1.25rem;font-weight:800;color:var(--teal);}
# .hp-label{display:inline-block;background:var(--teal-soft);color:var(--teal);font-weight:700;font-size:.8rem;padding:.2rem .6rem;border-radius:6px;margin-bottom:.5rem;}
# </style>
# """

# STATUS_CLASS = {
#     "New": "gray", "Qualified": "teal", "Campaign Ready": "indigo", "Contacted": "blue",
#     "Follow-up Due": "amber", "Interested": "green", "Not Interested": "red", "Closed": "slate",
# }
# LEVEL_CLASS = {"Strong": "green", "Moderate": "amber", "Weak": "gray"}


# def inject_css() -> None:
#     st.markdown(CSS, unsafe_allow_html=True)


# def badge(text: str, kind: str = "gray") -> str:
#     return f'<span class="hp-badge hp-b-{kind}">{esc(text)}</span>'


# def status_badge(status: str) -> str:
#     return badge(status, STATUS_CLASS.get(status, "gray"))


# def level_badge(level: str) -> str:
#     return badge(level, LEVEL_CLASS.get(level, "gray"))


# def page_header(title: str, subtitle: str) -> None:
#     st.markdown(f'<div class="hp-header"><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div>', unsafe_allow_html=True)


# def metric_card(label: str, value) -> str:
#     return f'<div class="hp-metric"><div class="v">{esc(value)}</div><div class="l">{esc(label)}</div></div>'


# def kv(label: str, value: str) -> None:
#     if value:
#         st.markdown(f'<div class="hp-kv"><b>{esc(label)}:</b> {esc(value)}</div>', unsafe_allow_html=True)


# def flight_track(steps, current_key: str, done_map: dict) -> str:
#     """Horizontal progress track; the first not-done step is highlighted."""
#     first_open = next((s.key for s in steps if not done_map[s.key]), None)
#     nodes = []
#     for s in steps:
#         cls = "done" if done_map[s.key] else ("now" if s.key == first_open else "")
#         nodes.append(f'<div class="hp-node {cls}">{esc(s.label)}</div>')
#     return '<div class="hp-track">' + "".join(nodes) + "</div>"


# def source_note(state, key: str) -> None:
#     """Show 'Demo / Fallback Mode' or a live-generation note for a stored result."""
#     info = state["sources"].get(key)
#     if not info:
#         return
#     if info["source"] == "demo":
#         st.markdown(
#             '<div class="hp-demo"><b>Demo / Fallback Mode.</b> This is example data, not live Gemini output and '
#             f'not verified market research. {esc(info.get("notice") or "")}</div>',
#             unsafe_allow_html=True,
#         )
#     else:
#         st.markdown('<div class="hp-live">Generated live by Gemini. Treat it as AI-generated suggestions, not verified facts.</div>', unsafe_allow_html=True)


# def demo_data_banner() -> None:
#     st.markdown(
#         '<div class="hp-demo"><b>Sample data.</b> These prospects are fictional demo records for the hackathon MVP. '
#         'They are not live, verified leads and the contact emails are placeholders on the reserved ".example" domain.</div>',
#         unsafe_allow_html=True,
#     )

"""Visual layer: CSS plus small HTML components. All dynamic text is HTML-escaped."""
from __future__ import annotations

import streamlit as st

from utils.helpers import esc


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

:root{
    --ink:#172033;
    --ink-soft:#344054;
    --muted:#667085;
    --line:#E4E7EC;
    --surface:#FFFFFF;
    --surface-soft:#F8FAFC;
    --bg:#F6F8FB;

    --primary:#0F6E6E;
    --primary-dark:#0B5A5A;
    --primary-soft:#E8F5F4;

    --teal:#087F7A;
    --teal-soft:#E7F7F5;

    --amber:#B7791F;
    --amber-soft:#FFF7E6;

    --red:#B42318;
    --red-soft:#FEECEB;

    --green:#16835B;
    --green-soft:#E8F7F0;

    --blue:#2563EB;
    --blue-soft:#EAF1FF;

    --slate:#475467;
    --slate-soft:#EEF1F5;

    --indigo:#4E647A;
    --indigo-soft:#EDF2F5;
}

html, body, [class*="css"]{
    font-family:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif;
}

.stApp{
    background:
        radial-gradient(circle at 85% 8%, rgba(15,110,110,.045), transparent 28%),
        radial-gradient(circle at 10% 90%, rgba(37,99,235,.025), transparent 25%),
        var(--bg);
}

.block-container{
    padding-top:2.25rem;
    padding-bottom:4rem;
    max-width:1200px;
}

h1,h2,h3,h4,.stMarkdown p,.stMarkdown li,.stButton button,label{
    font-family:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif;
}

h1{font-weight:800;letter-spacing:-0.035em;color:var(--ink);}
h2{font-weight:750;letter-spacing:-0.025em;color:var(--ink);}
h3{font-weight:700;letter-spacing:-0.02em;color:var(--ink);}
h4{font-weight:700;color:var(--ink);}


/* =========================
   SIDEBAR
   ========================= */

[data-testid="stSidebar"]{
    background:#FFFFFF;
    border-right:1px solid var(--line);
}

[data-testid="stSidebar"] > div:first-child{
    padding-top:1.35rem;
}

/* Brand */
.hp-brand{
    padding:.2rem .15rem .9rem .15rem;
    border-bottom:1px solid var(--line);
    margin-bottom:.75rem;
}

.hp-brand b{
    font-family:'Manrope',sans-serif;
    font-size:1.25rem;
    font-weight:800;
    letter-spacing:-0.025em;
    color:var(--ink);
}

.hp-brand span{
    display:block;
    color:var(--muted);
    font-size:.78rem;
    line-height:1.4;
    margin-top:.2rem;
}

/*
   Sidebar workflow:
   No white cards/background blocks around individual steps.
   Tight vertical spacing keeps the navigation compact.
*/
[data-testid="stSidebar"] [data-testid="stRadio"]{
    margin-top:0 !important;
    padding-top:0 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"]{
    gap:0 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label{
    position:relative;
    display:flex;
    align-items:center;
    width:100%;
    min-height:34px;
    box-sizing:border-box;

    background:transparent !important;
    border:0 !important;
    border-radius:7px;

    color:#667085 !important;
    padding:.32rem .55rem !important;
    margin:0 !important;

    transition:
        color .15s ease,
        background .15s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{
    background:#F5F7F8 !important;
    color:#344054 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){
    background:#EEF7F6 !important;
    border:0 !important;
    color:var(--primary-dark) !important;
    font-weight:700;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked)::before{
    content:"";
    position:absolute;
    left:0;
    top:5px;
    bottom:5px;
    width:3px;
    border-radius:3px;
    background:var(--primary);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label p{
    color:inherit !important;
    font-weight:600;
    margin:0 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p{
    font-weight:750;
}

/* Make the actual radio indicator subtle */
[data-testid="stSidebar"] [data-testid="stRadio"] label div[role="radio"]{
    border-color:#C7CED8 !important;
    width:14px !important;
    height:14px !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) div[role="radio"]{
    border-color:var(--primary) !important;
    background:var(--primary) !important;
}

/* Progress bar + caption */
[data-testid="stSidebar"] [data-testid="stProgress"]{
    margin-top:.5rem;
    margin-bottom:.15rem;
}

[data-testid="stSidebar"] .stCaption{
    color:#7A8594;
}


/* =========================
   PAGE HEADER
   ========================= */

.hp-header{
    margin-bottom:1.35rem;
}

.hp-header h1{
    margin:0 0 .3rem 0;
    font-size:2.05rem;
    line-height:1.15;
}

.hp-header p{
    margin:0;
    color:var(--muted);
    font-size:.96rem;
    line-height:1.6;
    max-width:72ch;
}


/* =========================
   CARDS
   ========================= */

.hp-card{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:14px;
    padding:1.15rem 1.25rem;
    box-shadow:
        0 1px 2px rgba(16,24,40,.03),
        0 5px 18px rgba(16,24,40,.025);
}

.hp-card:hover{
    border-color:#D7DBE5;
    box-shadow:
        0 2px 4px rgba(16,24,40,.04),
        0 10px 28px rgba(16,24,40,.045);
}


/* =========================
   METRICS
   ========================= */

[data-testid="stMetric"]{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:14px;
    padding:1rem 1.05rem;
    box-shadow:0 2px 8px rgba(16,24,40,.025);
}

.hp-metric{
    position:relative;
    background:#FFFFFF;
    border:1px solid var(--line);
    border-radius:14px;
    padding:1rem 1.05rem;
    min-height:82px;
    box-shadow:0 2px 8px rgba(16,24,40,.025);
    overflow:hidden;
}

.hp-metric:before{
    content:"";
    position:absolute;
    left:0;
    top:0;
    bottom:0;
    width:3px;
    background:var(--primary);
}

.hp-metric .v{
    font-size:1.75rem;
    font-weight:800;
    color:var(--ink);
    line-height:1.1;
    letter-spacing:-0.03em;
}

.hp-metric .l{
    color:var(--muted);
    font-size:.78rem;
    font-weight:600;
    margin-top:.32rem;
}


/* =========================
   BUTTONS
   ========================= */

.stButton > button{
    border-radius:9px;
    border:1px solid #D0D5DD;
    background:#FFFFFF;
    color:var(--ink-soft);
    font-weight:700;
    min-height:2.45rem;
    transition:background .15s ease,border-color .15s ease,box-shadow .15s ease;
}

.stButton > button:hover{
    border-color:#B8BEC9;
    background:#F9FAFB;
    box-shadow:0 3px 10px rgba(16,24,40,.07);
}

.stButton > button[kind="primary"]{
    background:linear-gradient(135deg,#0F6E6E 0%,#0B5A5A 100%);
    border-color:#0F6E6E;
    color:#FFFFFF;
    box-shadow:0 4px 12px rgba(15,110,110,.18);
}

.stButton > button[kind="primary"]:hover{
    background:linear-gradient(135deg,#148080 0%,#0F6E6E 100%);
    border-color:#148080;
    box-shadow:0 6px 16px rgba(15,110,110,.24);
}


/* =========================
   BADGES
   ========================= */

.hp-badge{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    padding:.22rem .62rem;
    border-radius:999px;
    font-size:.73rem;
    font-weight:700;
    line-height:1.25;
    white-space:nowrap;
    border:1px solid transparent;
}

.hp-b-gray{background:#F2F4F7;color:#475467;border-color:#EAECF0;}
.hp-b-teal{background:var(--teal-soft);color:var(--teal);border-color:#CBEAE7;}
.hp-b-blue{background:var(--blue-soft);color:var(--blue);border-color:#D4E1FF;}
.hp-b-amber{background:var(--amber-soft);color:#9A6700;border-color:#F5DFA8;}
.hp-b-green{background:var(--green-soft);color:var(--green);border-color:#C9EAD9;}
.hp-b-red{background:var(--red-soft);color:var(--red);border-color:#F4CCC8;}
.hp-b-slate{background:var(--slate-soft);color:var(--slate);border-color:#DDE2E8;}
.hp-b-indigo{background:var(--indigo-soft);color:var(--indigo);border-color:#D9E2F3;}


/* =========================
   WORKFLOW TRACKER
   ========================= */

.hp-track{
    display:flex;
    gap:0;
    margin:.65rem 0 1.6rem 0;
    overflow-x:auto;
    padding:.25rem .1rem .55rem .1rem;
    scrollbar-width:thin;
}

.hp-node{
    flex:1 0 92px;
    position:relative;
    text-align:center;
    padding-top:29px;
    font-size:.72rem;
    color:#98A2B3;
    font-weight:600;
    line-height:1.3;
}

.hp-node:before{
    content:"";
    position:absolute;
    top:9px;
    left:-50%;
    width:100%;
    height:2px;
    background:#E4E7EC;
}

.hp-node:first-child:before{display:none;}

.hp-node:after{
    content:"";
    position:absolute;
    top:2px;
    left:calc(50% - 8px);
    width:14px;
    height:14px;
    border-radius:50%;
    background:#FFFFFF;
    border:2px solid #D0D5DD;
    z-index:2;
}

.hp-node.done{color:var(--ink-soft);}
.hp-node.done:before{background:var(--primary);}
.hp-node.done:after{
    background:var(--primary);
    border-color:var(--primary);
    box-shadow:0 0 0 4px var(--primary-soft);
}

.hp-node.now{
    color:var(--ink);
    font-weight:800;
}

.hp-node.now:before{background:var(--primary);}

.hp-node.now:after{
    border-color:var(--primary);
    background:#FFFFFF;
    box-shadow:0 0 0 4px var(--primary-soft);
}


/* =========================
   NOTES / AI
   ========================= */

.hp-note{
    font-size:.82rem;
    color:var(--muted);
    line-height:1.55;
    margin:.2rem 0 .8rem 0;
}

.hp-demo{
    background:linear-gradient(135deg,#FFF9EA 0%,#FFF5D9 100%);
    border:1px solid #F0D58E;
    border-radius:10px;
    padding:.72rem .9rem;
    color:#704F00;
    font-size:.83rem;
    line-height:1.5;
    margin:.25rem 0 .95rem 0;
}

.hp-live{
    background:linear-gradient(135deg,#ECFAF4 0%,#E4F6EE 100%);
    border:1px solid #BFE5D0;
    border-radius:10px;
    padding:.62rem .9rem;
    color:var(--green);
    font-size:.82rem;
    line-height:1.5;
    margin:.25rem 0 .95rem 0;
}

.hp-assume{
    background:linear-gradient(135deg,#FFF9EA 0%,#FFF5DD 100%);
    border:1px solid #F1D99A;
    border-left:4px solid var(--amber);
    padding:.8rem 1rem;
    border-radius:9px;
}

.hp-verify{
    background:linear-gradient(135deg,#F0F5FF 0%,#EAF1FF 100%);
    border:1px solid #D2DFFF;
    border-left:4px solid var(--blue);
    padding:.8rem 1rem;
    border-radius:9px;
}

.hp-assume h4,.hp-verify h4{
    margin:0 0 .45rem 0;
    font-size:.92rem;
}

.hp-assume ul,.hp-verify ul{
    margin:0;
    padding-left:1.15rem;
}

.hp-assume li,.hp-verify li{margin:.2rem 0;}


/* =========================
   KEY / VALUE
   ========================= */

.hp-kv{
    margin:.2rem 0;
    font-size:.88rem;
    color:var(--muted);
    line-height:1.5;
}

.hp-kv b{
    color:var(--ink);
    font-weight:700;
}


/* =========================
   PRICE / LABEL
   ========================= */

.hp-price{
    font-size:1.3rem;
    font-weight:800;
    color:var(--primary);
    letter-spacing:-0.02em;
}

.hp-label{
    display:inline-flex;
    align-items:center;
    background:var(--primary-soft);
    color:var(--primary-dark);
    font-weight:800;
    font-size:.72rem;
    padding:.25rem .62rem;
    border-radius:6px;
    margin-bottom:.55rem;
}


/* =========================
   STREAMLIT INPUTS
   ========================= */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"]{
    border-radius:9px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus{
    border-color:var(--primary) !important;
    box-shadow:0 0 0 1px var(--primary) !important;
}

[data-baseweb="select"]{border-radius:9px !important;}

label{
    color:var(--ink-soft) !important;
    font-weight:650 !important;
    font-size:.83rem !important;
}


/* =========================
   TABLES / EXPANDERS / TABS
   ========================= */

[data-testid="stDataFrame"]{
    border:1px solid var(--line);
    border-radius:12px;
    overflow:hidden;
}

[data-testid="stExpander"]{
    border:1px solid var(--line);
    border-radius:11px;
    background:var(--surface);
    overflow:hidden;
}

[data-testid="stExpander"] summary{
    font-weight:700;
    color:var(--ink);
}

.stTabs [data-baseweb="tab-list"]{
    gap:.25rem;
    border-bottom:1px solid var(--line);
}

.stTabs [data-baseweb="tab"]{
    padding:.65rem .85rem;
    color:var(--muted);
    font-weight:650;
}

.stTabs [aria-selected="true"]{
    color:var(--primary) !important;
}

hr{border-color:var(--line) !important;}

[data-testid="stAlert"]{border-radius:10px;}


/* =========================
   MOBILE
   ========================= */

@media (max-width:768px){
    .block-container{
        padding-top:1.25rem;
        padding-left:1rem;
        padding-right:1rem;
    }

    .hp-header h1{font-size:1.65rem;}
    .hp-header p{font-size:.9rem;}
    .hp-card{padding:1rem;border-radius:12px;}
    .hp-metric{border-radius:12px;}
    .hp-node{flex-basis:82px;font-size:.68rem;}
}
</style>
"""


STATUS_CLASS = {
    "New": "gray",
    "Qualified": "teal",
    "Campaign Ready": "indigo",
    "Contacted": "blue",
    "Follow-up Due": "amber",
    "Interested": "green",
    "Not Interested": "red",
    "Closed": "slate",
}

LEVEL_CLASS = {
    "Strong": "green",
    "Moderate": "amber",
    "Weak": "gray",
}


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def badge(text: str, kind: str = "gray") -> str:
    return f'<span class="hp-badge hp-b-{kind}">{esc(text)}</span>'


def status_badge(status: str) -> str:
    return badge(status, STATUS_CLASS.get(status, "gray"))


def level_badge(level: str) -> str:
    return badge(level, LEVEL_CLASS.get(level, "gray"))


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hp-header">'
        f'<h1>{esc(title)}</h1>'
        f'<p>{esc(subtitle)}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value) -> str:
    return (
        f'<div class="hp-metric">'
        f'<div class="v">{esc(value)}</div>'
        f'<div class="l">{esc(label)}</div>'
        f'</div>'
    )


def kv(label: str, value: str) -> None:
    if value:
        st.markdown(
            f'<div class="hp-kv">'
            f'<b>{esc(label)}:</b> {esc(value)}'
            f'</div>',
            unsafe_allow_html=True,
        )


def flight_track(steps, current_key: str, done_map: dict) -> str:
    """Horizontal progress track; the first not-done step is highlighted."""
    first_open = next(
        (s.key for s in steps if not done_map[s.key]),
        None,
    )

    nodes = []

    for s in steps:
        cls = (
            "done"
            if done_map[s.key]
            else ("now" if s.key == first_open else "")
        )

        nodes.append(
            f'<div class="hp-node {cls}">'
            f'{esc(s.label)}'
            f'</div>'
        )

    return '<div class="hp-track">' + "".join(nodes) + '</div>'


def source_note(state, key: str) -> None:
    """Show demo/fallback or live-generation note for a stored result."""
    info = state["sources"].get(key)

    if not info:
        return

    if info["source"] == "demo":
        st.markdown(
            '<div class="hp-demo">'
            '<b>Demo / Fallback Mode.</b> '
            'This is example data, not live Gemini output and '
            'not verified market research. '
            f'{esc(info.get("notice") or "")}'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="hp-live">'
            '<b>Live AI Generation.</b> '
            'Generated by Gemini. Treat it as AI-generated '
            'suggestions, not verified facts.'
            '</div>',
            unsafe_allow_html=True,
        )


def demo_data_banner() -> None:
    st.markdown(
        '<div class="hp-demo">'
        '<b>Sample data.</b> '
        'These prospects are fictional demo records for the hackathon MVP. '
        'They are not live, verified leads and the contact emails are '
        'placeholders on the reserved ".example" domain.'
        '</div>',
        unsafe_allow_html=True,
    )

