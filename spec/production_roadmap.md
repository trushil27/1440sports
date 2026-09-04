# Production Roadmap

The build path: where the engine has been, where it is now, and where it's going. Captured because conversations cross sessions and the next chat needs to know what state to pick up from.

## Current State *(22 May 2026)*

### Phase 0 — MVP Design (Apr 2026) ✅ Complete

- V2.1 Track 1 prompt — 24 cold signals scored, calibration validated
- V2.2 Track 2 alumni layer — 5 strict-tier alumni surfaced
- 5 hot-signal-class briefs approved by MD *(JFrog, Luminary, Databricks, Mistral, Factory)*
- PDF brief format — 3 physical briefs built *(Mistral, Factory, Luminary)*
- Brand voice, scoring thresholds, blocklist concept
- MD signoff for full MVP build

### Phase 0.5 — Production Infrastructure (Apr-May 2026) ✅ Deployed

- n8n workflow live, daily run at 06:00 GMT weekdays (now also weekends, see Phase 2.1.8 notes)
- Railway-hosted Flask service rendering PDFs from the engine
- Brief auto-numbering via n8n workflow static data
- Company-name-only dedup logic in place
- Production webhook restored

### Phase 1 — Anti-Hallucination Spine (May 2026) ✅ Deployed

- `active_sponsor_db.md` — canonical sponsor + activation database for F1 and FE
- Step 0 Track Determination — F1/FE/Dual commitment before scoring
- FE-parallel archetype set added (SUSTAINABILITY MANDATE, FLEET INFLECTION, REGULATORY URGENCY, SHOWROOM PLAY, CITY-STATE/SOVEREIGN, NARRATIVE-CLEAN)
- Pre-Flight Sponsor Check (5-step protocol against database)
- Citation Enforcement Gate at output time
- Confidence Card on every V2.1 output (gates downstream brief generation)
- FE-specific search query templates
- Daily Top 3 FE quota (at least 3 of 10 candidates must be FE-track)
- Navy + gold rebrand applied to all brief outputs

### Phase 2.0 — Tech-into-Operations Layer (May 2026) ✅ Deployed, then superseded

- `team_needs_taxonomy.md` — 8-category map of F1/FE team operational needs
- Operational Fit added as 5th scoring dimension
- "WHAT COULD RUN ON THE CAR" brief section (later renamed in Phase 2.1.8)
- Builder.py + build_brief_template.py updated with 5-cell score grid, HOT TOP TIER eyebrow tag, MEDIUM-confidence footer warning
- 7th field in Confidence Card (Operational fit claims)

### Phase 2.1 — Recalibration (May 2026) ✅ Deployed

MD directed scoring revert to /100. Phase 2.0's other architectural changes retained.

- **Score cap restored to /100** — 5 dimensions × /20 each, OF retained as first-class 5th dimension (rebalanced /25 → /20).
- **Tier thresholds restored to original anchors:** 85+ HOT TOP TIER · 70-84 HOT · 55-69 WARM · 40-54 VERIFY · 25-39 PLANT · 0-24 DISCARD.
- **Brief hero label restored to "OPP / 100".** Score cells render "/ 20" per dim.
- **HOT TOP TIER eyebrow tag triggers at score ≥ 85.**
- **PDF spacing tightened** — gap between score panel and THE CASE reduced.
- **Logo file replaced** — transparent RGBA 4000×700 PNG, navy + gold strokes only.
- **Confidence Card unchanged** — 7 fields, HIGH = 6/7 ✅, MEDIUM = 4-5/7 with no ❌.

### Phase 2.1.3 — Anti-Duplication + Date Hygiene (21 May 2026) ✅ Deployed

- Anti-duplication self-check in brief writer (deck, the_case_p1, the_case_p2, why_now_callout must not contain the team-specific narrative claim — that lives in WHY [TEAM] only).
- Anti-hallucination rules hardened (£100 test, dated figures, anchored percentages, named investors verbatim, no hollow adjectives, quantified reach, venue specificity).
- Date hygiene fix: footer_date always uses TODAY's date in 'D MMM YYYY' UPPERCASE; industry_meta strips trailing date suffix.
- FE quota enforced at scanner level (≥3 of 10 candidates must be FE-track).

### Phase 2.1.4 — Dedup Visibility (21 May 2026) ✅ Deployed

- Parse Signal Data node: revisit fallback rewritten in three tiers — prefer non-cooling non-blocked candidate; fall back to cooling non-blocked (sets `_revisit: true` + `_revisit_reason: re_surfaced_cooling_company_no_fresh_alternative`); last resort `candidates[0]`.
- Cooling list now mirrored to Google Sheets "Cooling List" tab (`Format Cooling Snapshot` + `Google Sheets — Cooling List Mirror` nodes added in parallel branch).
- Each daily run upserts one row per cooling entry, keyed on `normalised_name`.

### Phase 2.1.5 — FE Rotation + Three Modes (Drafted) → Superseded by 2.1.8

Initial attempt at broadening WHERE THE TECH FITS section. Final form landed in 2.1.8.

### Phase 2.1.6 — Full-Grid Team Matching (21 May 2026) ✅ Deployed

- Scanner body (`Anthropic — Run Signals`) rewritten to walk the full 11-team F1 grid + all current FE teams for every candidate; explicit prohibition on default reasoning patterns ("Williams = engineering heritage", "Aston Martin = data-infrastructure team", "McLaren = technology team", "Mercedes = enterprise SaaS").
- No per-team cap; diversity emerges from genuine matching against documented open categories in active_sponsor_db.md.
- Audi, Cadillac, Haas, Alpine, Racing Bulls explicitly named with their documented open category gaps.
- Verified live: Jaguar TCS Racing, BWT Alpine, NEOM McLaren, Audi all surfaced in recent runs — no Williams/Aston Martin clustering.

### Phase 2.1.7 — Autonomous Audit + Retry Loop (22 May 2026) ✅ Deployed

- New nodes added to n8n: `Audit Brief` (Code, JS), `Audit Route` (Switch, 3 routes: pass/retry/manual_review), `Format Audit Log Rows` (Code), `Retry Prep` (Code), `Google Sheets — Audit Log`, `Outlook — Operator Manual Review Alert`.
- Wiring: Parse Claude Response → Audit Brief → Audit Route → {pass → Render PDF | retry → Retry Prep → Anthropic - Write Brief loop | manual_review → Operator Alert}.
- Retry budget: 1 retry. If retry fails, brief routes to operator manual review and does NOT reach MD.
- Audit logs to "Audit Log" tab in same workbook as Daily Signals.

### Phase 2.1.8 — VALUE TO [TEAM] + Audit Rule Refinement (22 May 2026) ✅ Deployed

- **Renamed WHERE THE TECH FITS → VALUE TO [TEAM]** (dynamic label).
- **Three content modes by company archetype:**
  - MODE A — operational (on-car/factory/broadcast) for ops_fit ≥ 14. Datadog/Cerebras/Nscale archetype.
  - MODE B — commercial back-office (paddock settlements, treasury, partner-onboarding) for ops_fit 11-13 or fintech/payments/insurance. Mercury/Brex/Primer archetype.
  - MODE C — audience/brand-pipeline (user base demographics, race-weekend activation, customer-acquisition framing) for ops_fit ≤ 10 + consumer/lifestyle/media/B2C. Strava/Farther archetype.
- **Section renders for every brief at score ≥ 70.** Below 70 the brief drops to "VERIFY/PLANT" tier and the section is suppressed.
- **Deal architecture minimum: THREE YEARS.** Default THREE YEARS entry/associate, FOUR YEARS major partner, FIVE YEARS title/category-defining.
- **Deck rule hardened.** Three explicit prohibitions: no team-vacancy claims in deck; team may be named only as destination, never explained; if unsure, do not mention team at all. The Strava-style "[TEAM] HAS NO X" failure mode now structurally prevented.
- **FE rotation in Parse Signal Data:** Tuesdays and Fridays force-select top-scored FE candidate if any eligible FE exists in pool. Mon/Wed/Thu pick highest score regardless of series. Sat/Sun fall into the Mon/Wed/Thu path (no FE force) — see "Pending decisions" below.
- **13-rule audit** in Audit Brief node:
  1. Deal duration ≥ THREE YEARS
  2. Opening quote contains "25 minutes" and ends with "?"
  3. Opening intro is declarative (no question mark)
  4. footer_date matches today UTC
  5. industry_meta has no trailing date
  6. THE CASE p2 and deck do not contain `[Team]` near a vacancy clause within 100 chars (refined proximity-based Pattern B replaces the old window-based form that false-flagged the Datadog reference)
  7. Word count ceilings on all sections
  8. confidence_level not LOW
  9. Track label is exactly empty string or " · ALUMNI INTELLIGENCE"
  10. Risk count: 2 if value_section true, 3 if false
  11. Page-2 character budget: 2500 chars with value_section, 2300 without
  12. value_section must render when score ≥ 70
  13. **NEW** — 5+ word substantive phrase overlap between the_case_p2 and why_team_para flagged (medium severity). Catches Primer-style soft duplications the syntactic patterns miss.
- **Regression-tested** against four real briefs: Datadog reference (passes), Strava deck failure (correctly flagged), Nscale p2 contradiction (correctly flagged), Primer phrase overlap (correctly flagged).
- **Builder.py reads `value_section_label` from brief_data with backwards-compat fallback to `operational_fit_section`/`operational_fit_content`.**

### Architectural state — what runs in production today

```
6am Weekdays Trigger
   ↓
Anthropic — Run Signals (web_search; 10 candidates; FE quota ≥3; full-grid matching)
   ↓
Parse Signal Data (deterministic filter, FE rotation Tue/Fri, dedup, brief number, cooling list emit)
   ↓                                                                            ↘
Anthropic - Write Brief (v2.1.8 prompt; 3 modes; deck rule; retry-aware)         Format Cooling Snapshot → Google Sheets — Cooling List Mirror
   ↑                                                                            
   │                                                                            
Parse Claude Response
   ↓
Audit Brief (13 rules; emits _audit_route)
   ↓                                                                            ↘
Audit Route (Switch on _audit_route)                                            Format Audit Log Rows → Google Sheets — Audit Log
   ├── pass → 1440 Builder — Render PDF → Outlook — Send Brief → Google Sheets — Log Signal
   ├── retry → Retry Prep ──→ (loops back to Anthropic - Write Brief)
   └── manual_review → Outlook — Operator Manual Review Alert (to operator, NOT MD)
```

## Pending Decisions *(captured 22 May 2026)*

1. **Weekend behaviour (Sat/Sun execution now enabled).** Current code: rotation rule (`todayDow === 2 || todayDow === 5`) does not cover Sat/Sun, so weekends pick the highest-scoring eligible candidate regardless of series. Decision needed: should Sat/Sun also force FE, or pick by score, or run a different mode entirely?
2. **Score-70 threshold confirmation.** v2.1.8 enforces value_section render at score ≥ 70. If MD wants only HOT briefs (≥ 70) to circulate at all, threshold for entire brief production may move to 70.
3. **CRM choice for Phase 3b — Salesforce confirmed.** Phase 3c renamed accordingly.

## Phase 3 — Data Integrations (Planned, scope ~4-5 weeks)

**Goal:** Replace web-search-based ground truth with structured API data, and turn the blocklist into a live CRM read.

### 3a — Crunchbase Integration (priority — credentials confirmed)

- User has Crunchbase Pro; API key in n8n credential store.
- Full scope in `phase3a_crunchbase_scope.md`.
- Four new n8n nodes: Resolve Crunchbase UUIDs, Crunchbase — Fetch Company (HTTP), Crunchbase — Fetch Funding (HTTP), Merge CB Into Signals.
- Permalink cache sheet to avoid first-day search calls.
- Shadow week: emit BOTH web-derived and CB-derived capacity figures to a Sheets tab before cutting over to CB-first.
- Replace Gate 2 (Capacity) web-search heuristics with structured Crunchbase data: current valuation, funding round history, investors, board, employee growth, M&A events.

### 3b — Salesforce CRM Integration (confirmed; user has access, needs API scoping)

- Live read of pursuit pipeline: replaces manual `blocklist.md` with structured query.
- Closed-loop learning: track conversion rates by score band over 6 months.
- Score recalibration based on closed-deal evidence.
- API scoping required:
  - Which Salesforce objects to push to (Account, Contact, Opportunity, Activity)?
  - Auth flow — OAuth user-token vs Connected App vs JWT bearer?
  - Sandbox-first deployment before production.

### 3c — Passive Executive Tracking *(NEW — drafted 22 May 2026)*

**Goal:** Track senior executives at target companies and on the F1/FE alumni database passively across conferences, events, networking, panels, board appointments, podcast appearances. AI detects convergence patterns over time.

**Architectural considerations:**
- Data sources need legality/ethics review before any scraping. Acceptable: public LinkedIn job-change events, conference speaker lists (public), press releases, USPTO/EPO patent co-filings, trademark filings, GitHub organisational activity for tech sponsors, public podcast metadata, board appointment announcements.
- Excluded: corporate jet flight tracking, calendar/email metadata, anything requiring scraping behind authentication.
- Trigger logic: convergence of 2+ signals within 90 days fires an alert — single signals are noise.
- Output style: convergence narrative ("Sarah Franklin attended SaaStr May 14, scheduled to keynote Money 20/20 June 7, joined the Cerebras board April 12 — three intentional moves into enterprise-AI-finance positioning in 60 days") not a numeric score.
- New parallel track (V2.4) — does not bypass V2.1/V2.2 logic, layers convergence as a signal type.

### 3d — What Phase 3 enables

- Anti-hallucination strengthens — sponsor and capacity claims no longer rely on web-search recency.
- Closed-loop learning starts once Salesforce is live — engine learns which score bands actually convert.
- Phase 4 (NEWCO) becomes feasible (depends on Crunchbase M&A data).
- Phase 5 (Convergence) emerges from Phase 3c data accumulation.

## Phase 4 — NEWCO / Spinoff Track V2.3 (Planned, ~3-4 weeks)

**Goal:** Catch newly-formed billion-dollar entities at the brand-formation moment.

### Signal sources
- SEC Form 10 filings (US spinoffs)
- LSE main market announcements (UK separations / demergers)
- Crunchbase M&A feed (when Phase 3a wired)
- Press releases mentioning "demerger" / "spin-off" / "separation transaction"
- IPO Day Zero (S-1 filings as 6-month lead-time signal)

### Scoring logic
- Has the NEWCO published a brand strategy? Hired a CMO? Registered new trademarks since separation?
- If yes → 18-month action window is open.
- New archetype: BRAND FORMATION.

## Phase 5 — Convergence Intelligence Track V2.4 (now subsumed into 3c above)

The "God-level eyes" on executive movement the MD asked for. Originally a separate phase; now folded into Phase 3c since passive executive tracking IS the convergence engine. Phase 5 remains as the placeholder for the maturity build — where convergence detection becomes the primary track rather than a layer.

## Ongoing Workstreams (parallel to phases)

- **Renewal calendar maintenance** — surface targets 6-12 months before sponsor contract end dates (data in `active_sponsor_db.md` Section 7)
- **Geographic GP surge** — schedule region-specific target surfacing 8 weeks before that region's race
- **Holding-company graph** — track PE/family-office portfolios (RedBird, Eldridge, Liberty, MSP, CVC) as warm-intro paths
- **F2/F3/W Series/WEC crossover** — secondary market for mid-size companies that can't justify F1 ceiling
- **Database freshness** — quarterly full re-verification of `active_sponsor_db.md` (next: 20 August 2026)
- **Scoring calibration** — append-only log in `scoring_calibration.md`; quarterly review of score-band conversion rates once Salesforce is wired

## Tech Stack

| Component | Service | Monthly cost (est) |
|---|---|---|
| Workflow orchestration | n8n self-hosted on Hetzner VPS | £4 |
| LLM inference | Anthropic API (Claude Sonnet 4) | £20-30 |
| Web search | Anthropic web_search tool | included |
| Database | Google Sheets *(blocklist + alumni mirror + audit log + cooling list)* | free |
| Email | M365 SMTP | included |
| Notifications | Slack | included |
| PDF generation | Railway-hosted Flask + reportlab | ~£5 |
| Crunchbase API *(Phase 3a)* | Crunchbase Pro | TBC from credentials |
| Salesforce API *(Phase 3b)* | Salesforce (user has access) | TBC |
| **Total today** | | **~£30-50/month** |
| **Projected Phase 3** | | **~£100-150/month** |

## Risk Mitigations

- **API cost runaway:** Anthropic API budget alerts at £25, £50, £75 monthly.
- **Hallucinated sponsor claims:** Phase 1 pre-flight check + Confidence Card gate + Phase 2.1.7 audit + retry loop.
- **Stale `active_sponsor_db.md`:** Quarterly full re-verification (next: 20 August 2026).
- **Stale alumni database:** Monthly LinkedIn check; quarterly addition of new F1/FE deal signatories.
- **VPS failure:** Document recovery procedure; consider warm spare.
- **Brand drift:** Quarterly review of prompt outputs against `brand_voice.md`.
- **Audit false positives:** Regression-test every audit rule change against the Datadog reference brief before deployment.
- **Page-2 overflow:** Rule 11 character budget calibrated to 2500/2300; retune if false positives emerge.

## Success Metrics *(measure from Day 30 of Phase 2.1.8 deployment)*

- **Top 3 hit rate:** % of daily Top 3 signals that 1440 actually pursues *(target: >50%)*
- **False positive rate:** % of surfaced signals 1440 immediately discards *(target: <20%)*
- **Audit pass rate on first attempt:** *(target: >85%)*
- **Audit pass rate after retry:** *(target: >98%)*
- **Manual review trigger rate:** *(target: <2%)*
- **FE-track contribution:** % of weekly briefs that are FE-track *(target: ~40%; 2 of 5 by rotation rule)*
- **Conversion to meeting:** % of pursued signals that result in first meeting *(target: >15%)*
- **MD time saved:** Hours/week saved on lead research *(target: >5 hours)*

## Next Conversation Should Start With

"Pick up the 1440 production build. Read /mnt/skills/user/1440-sponsorship-intelligence/SKILL.md and references/production_roadmap.md to confirm state — we're at Phase 2.1.8 deployed (VALUE TO [TEAM] + 13-rule audit + retry loop). Next priorities: weekend rotation behaviour decision, Phase 3a Crunchbase integration, Phase 3b Salesforce integration, Phase 3c passive executive tracking architecture."

Or for ongoing maintenance:

"Quarterly refresh of active_sponsor_db.md — sweep team partner pages and update."

"Add new alumni entries from [Q1/Q2/Q3/Q4] deal announcements."
