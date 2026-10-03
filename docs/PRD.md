# HustlePilot AI: Product Requirements Document

**Version:** 1.0 (Hackathon MVP) | **Tagline:** From Skills to Your First Client

## 1. Executive Overview
HustlePilot AI is an agentic web app that turns a person's existing skills into a practical plan to approach international clients paying in USD. It connects ten steps in one guided workflow: profile, niche, validation, offer, ideal client, prospects, a personal sample, outreach, follow-ups and lead tracking. A human reviews and approves every outreach message; the system sends nothing.

## 2. Problem Statement
Aspiring freelancers often have a marketable skill but no clear niche, offer, target client or message. Generic side-hustle lists don't connect these decisions, and untargeted mass outreach is ineffective and reputationally risky. Many people stop before sending their first well-targeted message.

## 3. Background
Entry-level freelancers, especially those in markets where earning in a stronger currency is attractive, compete on large marketplaces where differentiation is difficult. Direct, well-researched outreach to a narrow type of business is an alternative path, but it requires several skills at once (positioning, pricing, research, writing). HustlePilot scaffolds those decisions. *The product makes no claims about market size, rates or conversion; any such claim would have to be verified separately.*

## 4. Target Users
Beginners and side-hustlers with at least one digital skill (design, writing, editing, AI tooling, etc.), 1-4 hours a day, wanting international clients.

## 5. Personas
- **Ayesha, the Canva + AI beginner.** Makes good designs for friends; no portfolio; 2-3 h/day; wants USD clients. Needs a niche and a first message.
- **Daniel, the career-switcher.** Copywriter by day, wants a weekend retainer client. Needs a realistic offer and a follow-up routine.
- **Mei, the student editor.** Edits short video; unsure whom to approach. Needs an ICP and qualification help.

## 6. Goals
1. Take a user from a one-line skill description to a reviewed outreach draft in one sitting.
2. Make every AI output honest: labelled assumptions, labelled example pricing, labelled demo data.
3. Keep the user in control (no automatic sending).
4. Work reliably in a live demo, even if the AI service is unavailable.

## 7. Non-goals
Guaranteeing clients or income; auto-sending email/LinkedIn/Instagram messages; marketplace (Fiverr/Upwork) integration; scraping; payments; authentication; mobile app; ML training; large-scale lead databases.

## 8. User Stories
- As a beginner, I enter my skills and get an honest analysis so I know my strengths and gaps.
- As a user, I see several niches with trade-offs and choose one myself.
- As a user, I see which claims about a niche are assumptions and how to verify them.
- As a user, I get an offer with three packages and example USD pricing I can adjust.
- As a user, I get an ICP so I know whom to look for.
- As a user, I can filter prospects and see why each fits.
- As a user, I get a small personalised sample idea to show value first.
- As a user, I can edit and approve outreach before anything leaves my hands.
- As a user, I track status and see who is due for a follow-up.

## 9. Functional Requirements
| ID | Requirement |
|----|-------------|
| F1 | Capture profile (skills, experience, hours, work type, tools, currency, strengths, limitations, portfolio level) with validation |
| F2 | Profile Analysis agent returns structured `ProfileAnalysis` |
| F3 | Niche agent returns 4 `NicheOption`s with the specified fields; user selects one |
| F4 | Niche validation returns `NicheValidation` separating assumptions from verification steps |
| F5 | Offer agent returns `Offer` with 3 packages labelled Suggested Example Pricing |
| F6 | ICP agent returns `ICP` |
| F7 | Load `data/sample_prospects.csv`, validate columns, show filters (industry, country, search) |
| F8 | Qualify prospects against the ICP with score, level, reasons, signals and problems; filter qualified |
| F9 | Generate a client-specific sample labelled "AI-generated sample idea" |
| F10 | Generate outreach (subject, email, 2 follow-ups, CTA, notes, interval) |
| F11 | Approve, copy, mailto (no recipient), mark contacted, schedule follow-up, change status |
| F12 | Lead statuses: New, Qualified, Campaign Ready, Contacted, Follow-up Due, Interested, Not Interested, Closed |
| F13 | Dashboard metrics: Total, Qualified, Campaign Ready, Contacted, Follow-ups Due, Interested, Closed |
| F14 | Demo/Fallback Mode for every AI step, with a visible banner |

## 10. Non-functional Requirements
- **Reliability:** no uncaught exceptions in normal use; every Gemini failure maps to a friendly message plus fallback.
- **Performance:** one AI call per step (qualification is one batched call); 90 s request timeout; one retry on transient errors.
- **Portability:** runs locally and on Streamlit Community Cloud; minimal dependencies.
- **Maintainability:** modular agents, central prompts, central settings.
- **Security:** no hardcoded secrets (see 17-18).

## 11. Agent Architecture
Seven logical agents (profile, niche discovery and validation, offer, ICP, prospect qualification, outreach, follow-up) plus a client-sample agent. All AI agents share one runner with schema validation and fallback. See `ARCHITECTURE.md`.

## 12. User Flow
Profile -> Analysis -> Niche options -> **user selects** -> Validation -> Offer -> ICP -> Prospects -> Qualification -> **user selects prospect** -> Sample -> Outreach draft -> **user edits and approves** -> **user sends manually** -> Mark contacted -> Follow-ups -> Dashboard.

## 13. Data Flow
User input -> `UserProfileInput` -> prompts (user text wrapped as data) -> Gemini JSON -> Pydantic validation -> session state -> UI. The prospect CSV is read locally; contact emails are excluded from prompts. Nothing is persisted outside the browser session.

## 14. UI Requirements
Sidebar navigation with completion markers and progress; dashboard with a step track and metric cards; tabs, expanders, tables with progress bars, status badges; consistent typography; clear primary actions; gated steps with a "go to the missing step" button.

## 15. AI Requirements
Current official `google-genai` SDK; JSON output validated by Pydantic; configurable model; handle malformed, empty, partial and failed responses (one corrective retry); prompts forbid fabricated statistics, guarantees, invented contacts and false claims of past work.

## 16. Human-in-the-loop
No send capability exists in the product. Users edit drafts, press Approve, copy/open the draft themselves, send manually, and then record "contacted". The mailto link has no recipient by design.

## 17. Safety
Phrase check for spammy or claim-like wording; honest labelling of assumptions, example pricing, demo data and AI-generated samples; instructions to avoid deceptive claims; no impersonation of real people.

## 18. Privacy
Minimal data: the profile typed by the user, kept in session memory. No database, no analytics beyond Streamlit defaults (disabled in config), no personal contact data in the repo. The optional API key typed in the sidebar is kept in memory only. Users should avoid entering sensitive personal details.

## 19. Success Metrics (hackathon MVP)
- Completes the 16-step demo without errors, with and without an API key.
- Time from profile to first approved draft under 10 minutes.
- 100% of AI outputs schema-validated or replaced by a labelled fallback.
- Zero hardcoded secrets in the repository.
- Qualitative: judges can explain the workflow after the demo.

## 20. Limitations
Demo dataset only; AI reasoning is unverified; example prices are illustrative; session-only state; fixed fallback content; no outcome guarantees.

## 21. Future Roadmap
1. Upload your own prospect CSV; export leads.
2. Persistent storage and accounts.
3. Grounded research (Gemini with Google Search) with visible sources.
4. Calendar reminders for follow-ups.
5. Multi-language outreach; additional copy-only channels.
6. Outcome tracking to learn which messages get replies.
