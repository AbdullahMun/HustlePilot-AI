# HustlePilot AI

**From Skills to Your First Client**

HustlePilot AI is an agentic planning app that helps aspiring freelancers and side-hustlers turn the skills they already have into a practical plan for approaching international, USD-paying clients. It walks the user from *skills* all the way to *reviewed, personalised outreach and follow-up tracking*, with a human approving every step.

> It is **not** a chatbot, a Fiverr clone, or an auto-emailer. It does not promise clients or income.

---

## Overview

| | |
|---|---|
| **Stack** | Python, Streamlit, Google Gemini (`google-genai` SDK), Pydantic, Pandas |
| **Agents** | 7 logical agents (see below) |
| **Data** | Local **demo** prospect dataset (`data/sample_prospects.csv`), fictional businesses |
| **State** | Streamlit session state (no database, nothing stored on disk) |
| **Outreach** | Drafts only. The user reviews, approves, copies and sends manually |

## Problem

New freelancers usually know *a skill* but not *who to sell it to*. Generic side-hustle idea lists don't tell them which niche fits them, what to offer, which businesses to approach, or what to actually say. Many give up before the first message is sent, or fall back to mass, generic outreach that gets ignored.

## Solution

One connected workflow instead of disconnected tips:

```
Skills -> Profile Analysis -> Niche Discovery -> Niche Validation -> Offer
      -> Ideal Client Profile -> Prospect Qualification -> Client-Specific Sample
      -> Personalised Outreach -> Follow-ups -> Lead Tracking
```

## Key features

- **Profile analysis** of skills, time, tools, strengths, limitations and portfolio level.
- **Niche discovery** with 4 options and honest trade-offs (the user picks; no "universal best").
- **Niche validation** that clearly separates *AI-generated assumptions* from *things to verify yourself*. The app retrieves no live market data and shows no market statistics.
- **Offer builder** with 3 packages, clearly labelled **Suggested Example Pricing**.
- **Ideal Client Profile (ICP)** to compare prospects against.
- **Prospect qualification** over a demo CSV: fit score, level, why it fits, fit signals, potential problems, filtering.
- **Client-specific sample idea** (post, reel, caption, CTA, design direction), labelled *AI-generated sample idea*.
- **Outreach campaigns**: subject, first email, 2 follow-ups, CTA, personalization notes, timing. Editable, with a spam/claims phrase check.
- **Lead tracking** with 8 statuses and a dashboard (Total, Qualified, Campaign Ready, Contacted, Follow-ups Due, Interested, Closed).
- **Demo / Fallback Mode** if Gemini is unavailable, with a clear banner.
- **Friendly errors** instead of tracebacks.

## Agent architecture

| # | Agent | File | Output schema |
|---|-------|------|---------------|
| 1 | Profile Analysis | `agents/profile_agent.py` | `ProfileAnalysis` |
| 2 | Niche Discovery & Validation | `agents/niche_agent.py` | `NicheList` / `NicheValidation` |
| 3 | Offer Builder | `agents/offer_agent.py` | `Offer` |
| 4 | Ideal Client Profile | `agents/icp_agent.py` | `ICP` |
| 5 | Prospect Research & Qualification | `agents/prospect_agent.py` | `QualificationList` |
| 5b | Client Sample | `agents/sample_agent.py` | `ClientSample` |
| 6 | Outreach Campaign | `agents/outreach_agent.py` | `OutreachCampaign` |
| 7 | Follow-up / Lead Management | `agents/followup_agent.py` | deterministic (no AI call) |

Every AI agent runs through `agents/base.py::run_agent`, which: calls Gemini, validates the JSON against its Pydantic schema, and on **any** failure returns structured demo data tagged as "demo". LangGraph is intentionally not used: the flow is linear and gated by human choices, so a small Python orchestrator (`workflows/hustle_workflow.py`) is simpler and more reliable. See `docs/ARCHITECTURE.md`.

## Workflow

See the diagram in `docs/ARCHITECTURE.md`. In the app: **Dashboard, My Profile, Discover Niches, Validate Niche, Build Offer, Ideal Client, Prospects, Client Sample, Outreach, Follow-ups**. Steps are gated: you are guided to the missing prerequisite instead of seeing an error.

## Tech stack

Python 3.10+, Streamlit, `google-genai` (official Google GenAI SDK, `from google import genai`), Pydantic v2, Pandas, python-dotenv.

## Project structure

```
HustlePilot-AI/
├── app.py                      # Streamlit entry point, navigation, sidebar
├── requirements.txt
├── README.md
├── .env.example                # copy to .env (git-ignored)
├── .gitignore
├── LICENSE
├── .streamlit/
│   ├── config.toml             # theme
│   └── secrets.toml.example    # template for Streamlit secrets
├── config/settings.py          # keys, model name, constants (single place)
├── agents/                     # one module per agent + base runner
├── workflows/hustle_workflow.py# step order, prerequisites, result storage
├── models/schemas.py           # Pydantic schemas
├── services/
│   ├── gemini_service.py       # Gemini client, JSON parsing, error mapping
│   ├── prospect_service.py     # CSV loading + validation
│   └── demo_data.py            # demo/fallback outputs + heuristic scoring
├── prompts/agent_prompts.py    # all prompts and guardrails
├── ui/                         # CSS/components and page renderers
├── utils/                      # helpers, input validation
├── data/sample_prospects.csv   # 19 FICTIONAL demo prospects
└── docs/                       # PRD, ARCHITECTURE, DEMO_GUIDE
```

## Installation

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Gemini API setup

1. Create a free key at <https://aistudio.google.com/apikey>.
2. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
3. (Optional) set `GEMINI_MODEL`. The default is the alias `gemini-flash-latest`, which follows Google's current Flash model so the app survives model retirements. Model names change over time; if you see a "model not found" message, check the current list in Google's docs and set `GEMINI_MODEL`.

## Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `GEMINI_API_KEY` | For live AI | Your Gemini key. Without it the app runs in Demo / Fallback Mode |
| `GEMINI_MODEL` | No | Override the model (default `gemini-flash-latest`) |
| `HUSTLEPILOT_DEMO_MODE` | No | `1` forces Demo mode (no API calls) |

Lookup order: sidebar key (session only) -> Streamlit secrets -> environment / `.env`.

## Local run

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually <http://localhost:8501>). No key? You can still click through the whole flow in Demo / Fallback Mode.

## Streamlit Community Cloud deployment

1. Push the project to a GitHub repository (do **not** commit `.env`; `.gitignore` already excludes it).
2. In Streamlit Community Cloud choose **New app**, select the repo, branch, and main file `app.py`.
3. Open **Advanced settings -> Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your_real_key"
   # GEMINI_MODEL = "gemini-flash-latest"
   ```
4. Deploy. Rotate the key if it is ever exposed.

## Demo workflow

Follow `docs/DEMO_GUIDE.md` (3-5 minutes). Use the **Load the demo example** button on My Profile, which fills in: *"I know Canva + AI tools, have 2-3 hours/day and want to earn in USD."*

## Human-in-the-loop

- The app has **no code path that sends email or social messages**.
- Outreach drafts are editable. Copy and "Open in my email app" unlock only after you press **Approve**.
- The email link opens with **no recipient**, so you add a verified address yourself.
- "Mark as contacted" is something *you* press after sending manually.
- Phrases that can sound spammy or make claims ("guarantee", "Dear Sir", "100%", ...) are flagged for review.

## Limitations

- Prospects are a small **fictional demo dataset**, not live or verified leads. There is no scraping and no live company lookup.
- AI niche validation is reasoning, **not market research**. No statistics are produced or verified.
- Suggested prices are illustrative examples, not market rates or income guarantees.
- State lives in the browser session; refreshing the page or a Streamlit Cloud restart clears it.
- Demo/fallback content is a fixed example set and is not tailored to every skill set.
- No guarantee of clients, replies or income.

## Future improvements

CSV upload of the user's own prospects, persistent storage, export to CSV, Gemini grounding with Google Search for sourced research, more outreach channels as copy-only drafts, multi-language drafts, optional LangGraph for parallel research once the flow branches.

## Security notes

- No API keys in code. `.env` and `.streamlit/secrets.toml` are git-ignored.
- Error messages are fixed, friendly strings; keys are never logged or displayed.
- The optional sidebar key is held in session memory only.
- Prospect contact emails in the CSV are placeholders on the reserved `.example` domain, and are never sent to the model.
- User input is wrapped in `<user_input>` tags and treated as data by the prompts.
- All dynamic text rendered as HTML is escaped.
