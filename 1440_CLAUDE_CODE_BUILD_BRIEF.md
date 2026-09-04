1440 Intelligence Platform — Claude Code Build Brief
Owner: Trushil Jani, 1440Sports (London). MD and primary reader: Ricky Paugh.
Date: 4 September 2026
Status: Greenlit. Replaces the n8n workflow (deactivated) with a code pipeline + web app.
---
0. How to work on this (read before anything else)
Copy the spec files listed in §2 into `spec/` in the repo before writing code. They are the source of truth for scoring, brand and audit rules. Do not reinvent them.
Read `spec/SKILL.md`, `spec/v21_prompt.md`, `spec/pdf_brief_template.md`, `spec/n8n_v21_prompts.md` and `spec/builder.py` in full before designing anything.
Build in the milestone order in §10. Do not start the web app before the pipeline passes the regression suite in §9.
Never invent company facts, people, funding figures, sponsorships or races anywhere in code, fixtures or tests. Where a test needs data, use the real historical cases in §9.
Ask before: changing any scoring weight or gate, changing the 2-page brief layout, changing what gets emailed to the MD, or adding a paid service.
Commit small, with tests. Every PR must pass CI. No secrets in the repo, ever.
---
1. Mission and context
1440Sports runs a daily engine that finds F1 / Formula E sponsorship targets, scores them (V2.1 six gates, five dimensions /20 = /100; V2.2 alumni boost), and sends the MD a 2-page brand-formatted PDF brief each morning.
The engine's intelligence logic is sound and MD-approved. The delivery layer failed: it lived in n8n, which over four months produced parse failures from stray brackets, five separate duplicate-guard bugs (Primer duplicate, Lime vs "Lime (Neutron Holdings)" mismatch, wrong `execution_mode`), stale signals resurfacing as fresh (Strava Jan 2026, 1Komma5° Jul 2025), and, most seriously, fabricated facts reaching the MD: a 1Komma5° brief with a wrong revenue figure and an investor not on the cap table, and a Ramp brief (N° 025) citing an "F1 London race in August 2026" that does not exist.
The existing engine audits structure (13 rules) but cannot audit substance. That gap is the reason for this rebuild.
Goal: a trustworthy, code-based pipeline with a claim-level verification pass, a database that makes duplicates structurally impossible, a 06:00 Europe/London Outlook delivery, and a premium web app where the MD scrolls day by day, searches, and opens every brief with its verification record.
---
2. Spec files to place in `spec/` (from the 1440 skill / project)
File	What it governs
`SKILL.md`	Architecture overview, critical rules 1–12, 13-rule audit, digest format
`v21_prompt.md`	Track 1 scoring: gates, dimensions, output schema
`v22_alumni.md`	Track 2 alumni tiers and boost maths
`alumni_database.md`	Current alumni entries
`active_sponsor_db.md`	Canonical F1/FE sponsor + activation database (pre-flight sponsor check)
`team_needs_taxonomy.md`	Operational Fit dimension
`blocklist.md`	Active pursuits and cooling-off list
`scoring_calibration.md`	Scored precedents
`brand_voice.md`	Copy rules
`pdf_brief_template.md`	2-page layout, typography, production checklist
`builder.py` / `build_brief_template.py`	Working reportlab PDF builders (navy + gold, Lora + Poppins)
`n8n_v21_prompts.md`	Canonical record of the prompts and audit code currently in production; port the logic, not the n8n wrapper
`1440_logo.png`	Transparent RGBA logo
`1440_Intelligence_Brief_Datadog.pdf`	Phase 2.1 reference brief (secondary). Primary layout target is the June-2026 format, e.g. Ramp N° 008 from Outlook
---
3. Non-negotiables
No unverified load-bearing claim reaches the MD. Every brief carries a claim ledger (§6). Briefs with an unverified or contradicted load-bearing claim go to the operator only, never to the MD, and are labelled in the app.
Duplicates are structurally impossible. Dedup is a database rule on normalised company + trigger, not a prompt instruction.
Stale signals are rejected by date arithmetic, not by asking the model. Any trigger older than the freshness window is discarded before scoring.
The 2-page brief format, brand and 13-rule audit are preserved exactly. The layout target is the format in production from June 2026 (Ramp N° 008 and later: proof-points grid, GRID FIT category-whitespace table, BOTTOM LINE box, signal tags, RISKS & COUNTERS, SOURCES list, VERIFIED decision-maker tag, five /20 score cells). Locate the builder that produced those PDFs in the repo and use it as `render.py`. `spec/pdf_brief_template.md` and the Datadog PDF are the earlier Phase 2.1 format and are superseded where they differ. Do not regress to the older layout.
The PROOF POINTS header "EVERY FIGURE VERIFIED TO A PRIMARY SOURCE", the decision-maker "VERIFIED" tag and the SOURCES list must be rendered from the claims ledger (§6), never as static text. If a figure is not verified, the header must say so and the brief is not MD-eligible.
GRID FIT rows (OPEN / CROWDED per team) must be computed from the `sponsors` table, not written by the model.
06:00 Europe/London, every day, with a defined behaviour on a no-signal day (§7).
Everything is stored: every candidate, score, dedup decision, verification result, audit result, PDF and email send, queryable in the app.
Code lives in GitHub, with CI, tests, and no secrets in the repo.
---
4. Architecture
Monorepo, three deployable parts sharing one Postgres database.
```
1440-intel/
├── spec/                     # the files in §2 (read-only reference)
├── pipeline/                 # Python 3.12 — scan, score, dedup, verify, audit, render, send
│   ├── intel/
│   │   ├── scan.py           # Claude + web search → candidate list (V2.1 prompt from spec)
│   │   ├── parse.py          # strict pydantic schemas; bracket-balanced JSON extraction
│   │   ├── freshness.py      # date-window rejection (deterministic)
│   │   ├── dedup.py          # DB-backed, parens-aware normaliser
│   │   ├── score.py          # gate + dimension bookkeeping, alumni boost, team grid match
│   │   ├── verify.py         # claim extraction + per-claim source verification (§6)
│   │   ├── brief.py          # BRIEF_DATA generation (writer prompt from spec)
│   │   ├── audit.py          # the 13 rules, ported from n8n_v21_prompts.md, + retry loop
│   │   ├── render.py         # reportlab builder (from spec/builder.py)
│   │   ├── send.py           # Microsoft Graph sendMail with PDF attachment
│   │   └── run_daily.py      # orchestrator, idempotent per date
│   ├── tests/                # regression suite (§9)
│   └── pyproject.toml
├── api/                      # FastAPI — read/write access for the web app
├── web/                      # Next.js 15 (App Router) + Tailwind — the MD-facing app
├── db/                       # Alembic migrations
├── .github/workflows/        # CI (lint, tests) + scheduled daily run (or Railway cron)
└── README.md
```
Hosting (default, change only with approval): Railway for pipeline cron job, API and Postgres (Railway already hosts the current PDF builder); Vercel for `web/`. PDFs in object storage (Cloudflare R2 or S3-compatible), path stored in DB.
Models: `claude-sonnet-5` for scan and brief writing; `claude-opus-5` for the verification pass (accuracy matters most there). Both configurable by env var. Use the Anthropic web search tool for scanning and web fetch for verification. Check current API docs for exact tool names before coding.
Scheduling: run pipeline at 05:30 Europe/London, send at 06:00. Handle BST/GMT correctly (schedule in Europe/London, not UTC). Retry the run once on failure. Idempotent per date: a second run on the same date must not re-send.
---
5. Data model (Postgres)
```
runs            id, run_date, started_at, finished_at, status, model_versions, error
candidates      id, run_id, company_raw, company_norm, track (1|2), series (F1|FE),
                trigger_reason_norm, trigger_date, source_url, source_tier, raw_json,
                gate_results jsonb, score_total, score_breakdown jsonb, alumni_boost,
                tier, recommended_team, decision (selected|dedup_suppressed|stale|blocklisted|
                                                  gate_failed|below_threshold)
briefs          id, candidate_id, brief_number (auto-increment, never reused), brief_data jsonb,
                audit_status (pass|pass_after_retry|failed), audit_violations jsonb,
                verification_status (verified|needs_review|blocked), pdf_path, created_at
claims          id, brief_id, text, section, load_bearing bool, claim_type
                (funding|person_role|sponsorship|event|revenue|date|other)
verifications   id, claim_id, status (verified|unverified|contradicted), evidence_url,
                evidence_excerpt, checked_at, model
sends           id, brief_id, recipient, channel (outlook|app_only), sent_at, message_id, status
surfaced_log    company_norm, trigger_reason_norm, first_surfaced_at, last_surfaced_at, brief_id
alumni          (mirror of alumni_database.md; editable in app)
blocklist       company_norm, reason, added_at, cooling_until (mirror of blocklist.md; editable)
sponsors        (mirror of active_sponsor_db.md; editable in app)
brief_actions   brief_id, action (pursuing|snoozed|killed|contacted), by, at, note
contacts        id, person_name, title, company_norm, linkedin_url, email, phone,
                source_provider, provider_record_id, retrieved_at, role_verified_at,
                role_verification_id, consent_basis (b2b_legitimate_interest), opted_out bool
outreach_drafts id, brief_id, contact_id, subject, body, created_at, outlook_draft_id
highlights      brief_id, text, generated_at, claim_ids (must reference verified claims only)
```
Normaliser (`company_norm`): lowercase → strip parenthetical content first → strip suffixes (inc, ltd, llc, plc, corp, holdings, technologies, technology, the) → strip non-alphanumerics. Must map "Lime" and "Lime (Neutron Holdings)" to the same key. Unit-test this.
---
6. Pipeline stages
Scan. Run the V2.1 scanner prompt (from `spec/n8n_v21_prompts.md`, current production version) asking for a ranked candidate array (8–12). Parse with bracket-balanced extraction into pydantic models. Malformed output → one retry with the parse error fed back → then fail the run with an operator alert.
Freshness. Reject any candidate whose `trigger_date` is older than the window (default 14 days for Track 1 triggers; alumni moves 90 days). Date arithmetic only.
Blocklist + dedup. Reject if `company_norm` is in `blocklist` (active or cooling). Reject if (`company_norm`, `trigger_reason_norm`) appears in `surfaced_log` within 30 days. Same company with a different trigger passes and is tagged RESURFACED.
Gates and score. Record all six gate results and the five /20 dimensions + alumni boost. Apply FE rotation rule (Tue/Fri) and full-grid team matching from `active_sponsor_db.md`. Select the top eligible candidate. Threshold to produce a brief: score ≥ 70 (confirm with MD; store as config).
Verify (new).
Extract every factual claim from the selected candidate's key facts and, after writing, from the BRIEF_DATA text: funding amounts, valuations, dates, investor names, revenue, person + role, any sponsorship or event claim (races, partnerships, team categories).
Mark each claim `load_bearing` (anything in the deck, THE CASE, WHY NOW, decision-maker, deal architecture, score cells is load-bearing).
For each claim, fetch the cited source and up to two independent sources; classify `verified` (supported by a Tier 1 source), `unverified` (no source found), `contradicted` (source says otherwise). Store evidence URL + excerpt.
Sponsorship and event claims are additionally checked against `spec/active_sponsor_db.md` and a fixed F1/FE calendar table for the current season. A race or partnership not in those tables is `contradicted`.
Decision: any `contradicted` load-bearing claim → `blocked` (brief not sent to MD; operator alerted with the claim). Any `unverified` load-bearing claim → `needs_review` (sent to operator only, footer reads "VERIFY BEFORE CIRCULATION"). All load-bearing claims `verified` → `verified` (eligible for MD).
If blocked, the pipeline tries the next eligible candidate (max 3 attempts) before declaring a no-signal day.
Write brief. Generate BRIEF_DATA with the writer prompt from spec. Enforce the field contract with pydantic.
Audit. Port the 13 rules from `n8n_v21_prompts.md` exactly. One retry with violations fed back. Fail → operator review.
Render. Port `spec/builder.py`. Assert page count == 2 in a test. Store PDF.
Send. See §7.
Log. Everything from steps 1–9 is written to the DB regardless of outcome.
---
7. Distribution rules
MD (Ricky) receives an email at 06:00 only when a brief is `verified` and `audit_status` is pass or pass_after_retry. Subject: `1440 Intelligence Brief N° {n} — {Company} — {score}/100`. Body: three-line executive take + link to the brief in the app. PDF attached.
Operator (Trushil) receives everything: verified briefs (cc), `needs_review` briefs, `blocked` notices with the failing claim, run failures, and a "no verified signal today" note when nothing clears the bar. The MD never receives a padded or flagged brief.
Send via Microsoft Graph (`POST /users/{sender}/sendMail`) using an Entra app registration with `Mail.Send` application permission. Needs tenant admin consent. If IT will not grant it, fall back to delegated auth with a stored refresh token. Confirm which before building `send.py`.
Record `message_id` on every send; never send twice for the same brief.
---
8. Web app (`web/`) — the 1440 Intelligence app
Feel: installed on the phone as a PWA (home-screen icon with the 1440 logo, full-screen, no browser chrome, works offline for already-loaded briefs). Desktop is the same app at wider breakpoints. Premium and restrained: navy + gold, Lora for display, Poppins for UI, generous whitespace, no dashboard chrome.
Sign-in: once, then invisible. Passkey (Face ID / Touch ID via WebAuthn) is the primary method. Magic link is used only to enrol a first device and for recovery. Allowlist exactly two addresses (Trushil, Ricky); anyone else gets a silent no-op. 90-day session, refreshed silently. No passwords anywhere.
Layout
Top bar: 1440 logo (gold on navy), today's date, search icon, menu.
Home ("Today"): today's brief as a hero card: company, score with tier badge, series and team, decision-maker name + title, one-line executive take, verification badge (Verified / Review / Blocked), Alumni Intelligence tag where Track 2. Beneath it a Recent & insightful block: two or three sentences, generated at brief time from verified claims only, on what changed in the last 14 days and why it matters. Three buttons: Open brief · Draft outreach · Pursuing.
Left panel (drawer on mobile, persistent on desktop): history day by day, grouped by month, newest first. Each row: date, company, score, badge. Tap loads that day's brief in the main pane. Search field at the top of the panel: company, person, team, series, tier, date range, verification state, track. Infinite scroll.
Brief view: the stored 2-page PDF rendered inline (pdf.js) with download and share; then the Verification panel ("9 of 10 load-bearing claims verified", each claim with status, source link, excerpt); score composition; audit result; Action bar: Pursuing / Snooze 30d / Kill / Mark contacted, each logged to `brief_actions`. Snooze and Kill write to the cooling list so the pipeline respects them.
People panel (inside the brief and as its own tab): decision-maker card with name, title, company, current position with "verified on [date]" and source, LinkedIn URL, email and phone only where the licensed provider returns them (provider name + retrieved date shown), co-decision-makers, Alumni tag with the prior deal where Track 2. "Re-verify" button re-runs the role check. If the role check fails after the brief was issued, the card shows a warning and the outreach button is disabled until re-verified.
Outreach: "Draft outreach" generates a subject and email body in brand voice (`spec/brand_voice.md`), built from the opening angle and verified claims only, ending with the 25-minute ask. Actions: Copy · Create Outlook draft (Graph: creates a Draft in the sender's mailbox; never sends) · Mark contacted. Stored in `outreach_drafts`.
Ops (`/ops`, Trushil only): run history, today's full candidate list with the reason each was not chosen, blocked / needs-review queue, editable blocklist, alumni and sponsor tables, contact-provider usage and cost, model and version config.
Performance: Home loads in under 1s on mobile; PDFs lazy-loaded; history panel paginated.
9. Regression suite (must pass before any MD send)
Use the real cases from production history as fixtures. Do not invent alternatives.
Ramp N° 025 phantom race. A brief citing an "F1 London race in August 2026" must be `blocked` by the event check against the F1 calendar table.
1Komma5° fabricated figures. A brief with a revenue figure and an investor not supported by any fetched source must land in `needs_review` (unverified) or `blocked` (contradicted), never `verified`.
Lime / "Lime (Neutron Holdings)". Both normalise to the same key; the second is `dedup_suppressed` within 30 days.
Primer duplicate. Same company, same trigger, next day → suppressed; same company, new trigger → passes, tagged RESURFACED.
Strava January 2026 / 1Komma5° July 2025 stale triggers. Rejected at the freshness stage by date arithmetic, before scoring.
Stray-bracket output. Scanner output containing an unbalanced bracket inside a string still parses (bracket-depth-balanced scanner).
Layout reference brief. Rendered PDF is exactly 2 pages and matches the June-2026 production format (use Ramp N° 008 or the most recent brief in Outlook as the reference; compare page images at low resolution, tolerance for font antialiasing). The Datadog PDF is a secondary check only.
Idempotent day. Running the pipeline twice for the same date produces one brief and one send.
No-signal day. With all candidates suppressed, the MD receives nothing and the operator receives the no-signal note.
All 13 audit rules have at least one passing and one failing fixture each.
Role drift. A stored contact whose title no longer matches the fetched source is marked `contradicted`; the People card shows the warning and "Draft outreach" is disabled until re-verified.
Outreach draft safety. A generated draft contains no claim absent from the brief's verified claims list, and "Create Outlook draft" never calls sendMail.
---
10. Milestones
#	Deliverable	Done when
M1	Repo, CI, DB schema, migrations, spec files in place	`pytest` green on an empty suite; migrations apply on Railway Postgres
M2	Scan → parse → freshness → dedup → score, writing to DB	§9 tests 3, 4, 5, 6, 8 pass on fixtures; a live run stores 8–12 candidates
M3	Verification pass	§9 tests 1 and 2 pass; a live run produces a claim ledger for the selected candidate
M4	Brief writer + 13-rule audit + render	§9 tests 7 and 10 pass; a live run produces a 2-page PDF matching brand
M5	Outlook send + scheduler + operator alerts	Test send lands in Trushil's inbox at 06:00 for three consecutive days (shadow mode: MD not yet on distribution)
M6	Backfill history	All prior briefs (from Sheets audit log + Railway PDFs) imported so day one of the app has the full backlog, each marked "historical, unverified" unless re-verified
M7	Web app: feed, search, brief page with verification panel, actions, auth	MD can open the link on a phone and scroll every brief
M8	Cut-over	MD added to distribution; n8n workflow deleted; ops page live
Shadow mode (M5–M7) is mandatory before M8. Minimum three clean days.
---
11. Decisions needed from Trushil before M1
GitHub org/repo name and who has access.
Microsoft Graph: can IT grant `Mail.Send` application permission, or do we use delegated auth? Sender address (Trushil's mailbox or a shared `intel@1440sports.com`)?
Hosting confirmation: Railway (pipeline, API, DB) + Vercel (web), or all on Railway.
Brief threshold for MD circulation: 70 (HOT) or 85 (HOT TOP TIER)?
Weekend behaviour: run Sat/Sun with score-only selection, or weekdays only.
App login: PWA + passkey (Face ID) with magic-link enrolment only. Confirm.
Contact data provider (paid; needs approval under §0.5). Default: Apollo.io API (trial on free tier); alternative Cognism if UK/EU coverage matters more. Rules regardless of provider: never scrape LinkedIn, never guess email patterns, display only what the provider returns, store provider + date on every record, honour opt-outs, keep a UK GDPR legitimate-interest record in `/ops`.
---
12. Definition of done
Ricky opens the 1440 app icon on his phone at 06:05, Face ID lets him in, today's brief is the hero card with a "Verified" badge, he reads the two pages, sees every claim with its source, checks the decision-maker's verified role and contact details, taps Draft outreach, and the email is waiting in his Outlook drafts. Trushil sees why the other nine candidates were not chosen. Nobody ever has to explain a phantom race again.
