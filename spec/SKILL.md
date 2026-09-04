---
name: 1440-sponsorship-intelligence
description: Surface daily sponsorship leads for 1440Sports — a B2B motorsport sponsorship consultancy in London. Use whenever the user asks for sponsorship signal generation, daily Top 3 briefs, alumni intelligence, or PDF intelligence briefs in 1440Sports brand format. Triggers include "run today's signals", "find sponsorship targets", "build a brief on [company]", "score this company for F1/FE", "who has moved from [F1 sponsor] to [new company]", "build the alumni database", "generate the daily digest", or any mention of motorsport sponsorship intelligence, F1/Formula E target scoring, or executive alumni tracking. Always use this skill for any 1440Sports sponsorship intelligence work — never approximate from memory because the architecture has specific scoring gates and the brand format has specific typography requirements that must be applied exactly.
---

# 1440Sports Sponsorship Intelligence Engine

A two-track intelligence system that surfaces daily F1 / Formula E sponsorship leads for 1440Sports, with named decision-makers, opportunity scores, and brand-formatted PDF briefs ready to share with the MD.

**Current scoring: Phase 2.1 — /100 cap, 5 dimensions × /20 each, Operational Fit retained as first-class 5th dimension.** Historical /100 scores in `scoring_calibration.md` are directly comparable to new scores.

## When to Use This Skill

Trigger this skill for **any** 1440Sports sponsorship intelligence task:

- Generating daily Top 3 signal digests
- Scoring individual companies as sponsorship targets *(V2.1 prompt)*
- Tracking alumni moves from F1/FE-sponsoring companies *(V2.2 logic)*
- Building 2-page intelligence briefs in 1440Sports brand format
- Expanding the alumni database
- Drafting outreach emails to surfaced decision-makers
- Recommending which signal to escalate to the MD

Never approximate the scoring or the brand format from memory — the architecture has six commercial gates, specific score weights, and specific typography (Lora serif + Poppins sans, navy + signature gold) that must be applied exactly.

## Core Architecture

The engine has **two independent tracks** that feed a merged daily Top 3:

### Track 1 — Company Signal Engine *(V2.1, Phase 2.1)*
Scans companies for: funding rounds, IPO filings, leadership changes, strategic pivots, geographic expansions, competitive disruptions. Filters through six commercial gates. Scores 0-100 across five weighted dimensions (Timing, Capacity, Brand Fit, Urgency, Operational Fit — each /20).

### Track 2 — Executive Alumni Intelligence Engine *(V2.2)*
Maintains database of named executives (CEO, CMO, CRO) who shaped major F1/FE sponsorship deals over the past 7-15 years. When alumnus moves jobs → runs new company through Track 1's V2.1 logic → applies alumni boost (+9 to +12 strict, +5 to +8 medium) if it qualifies.

**Key principle:** Track 2 does not bypass Track 1. The alumnus tells us *whom* to look at; V2.1 tells us *whether they're worth pursuing*.

## Workflow

### Step 1 — Determine the request type

| User intent | Workflow path |
|---|---|
| "Run today's signals" / "Daily digest" | → Phase A: Search → Score → Format Top 3 |
| "Score [Company X]" / "Build a brief on X" | → Phase B: Run V2.1 on X, optionally with PDF |
| "Find alumni signals" / "Who's moved from [Sponsor]" | → Phase C: Track 2 alumni search |
| "Expand the alumni database" | → Phase D: Database build |
| "Draft outreach to [Person]" | → Phase E: Outreach draft |

### Step 2 — Always read the relevant reference file first

- For **scoring any company** → read `references/v21_prompt.md` AND `references/team_needs_taxonomy.md` AND `references/active_sponsor_db.md`
- For **alumni tracking** → read `references/v22_alumni.md` and `references/alumni_database.md`
- For **building a PDF brief** → read `references/pdf_brief_template.md`
- For **the active deal blocklist** → read `references/blocklist.md`

### Step 3 — Apply the scoring rigorously

Never invent scores. Always run the six gates, the five-dimension scoring (Timing /20, Capacity /20, Brand Fit /20, Urgency /20, Operational Fit /20), and the alumni boost calculation transparently. Show the breakdown.

### Step 4 — Default output formats

- **Daily Top 3 digest** → ASCII box format, one paragraph per signal, named person + score + timing
- **Single signal score** → Full V2.1 markdown report with all gates visible
- **Brief for MD** → Always offer the PDF in 1440Sports brand format. Never send a brief without offering this.

## Core Reference Files

The following files contain the full architecture. Read them when doing the relevant work — do not try to reconstruct from memory.

- **`references/v21_prompt.md`** — Full V2.1 Phase 2.1 prompt: six gates, five-dimension scoring /20 each, output template. Read whenever scoring a company.
- **`references/v22_alumni.md`** — Track 2 logic: alumnus tier definitions, boost calculation, qualification flow. Read whenever an alumnus is relevant.
- **`references/team_needs_taxonomy.md`** — 8-category map of F1/FE team operational needs. Required reading for any Operational Fit score.
- **`references/active_sponsor_db.md`** — Canonical F1/FE sponsor database. Required reading for any sponsor claim or Pre-Flight check.
- **`references/pdf_brief_template.md`** — Complete instructions for building brand-consistent 2-page PDFs. Includes typography spec, color palette, layout structure, copy style guide. Read whenever creating a brief PDF.
- **`references/alumni_database.md`** — Current state of the alumni database (5 strict-tier confirmed). Append-only; update when new alumni discovered.
- **`references/blocklist.md`** — 1440's active deal pipeline. Companies on this list are auto-suppressed at Gate 5. **User must populate and maintain.**
- **`references/scoring_calibration.md`** — Test results from 24 historical signals plus calibration anchors. Use to calibrate new scores against precedent — directly comparable since Phase 2.1 restores /100.
- **`references/brand_voice.md`** — How 1440Sports talks. Tone, vocabulary, what to avoid. Read when drafting any user-facing text (briefs, outreach, emails).
- **`references/production_roadmap.md`** — Build path: where the engine has been, where it is now, and where it's going.
- **`references/n8n_v21_prompts.md`** — Exact prompt replacements for the production n8n workflow under Phase 2.1.
- **`references/phase3a_crunchbase_scope.md`** — Scope for the next phase: Crunchbase Pro integration replacing Gate 2 web-search heuristics.

## Critical Rules

1. **Never name a person without a verifiable Tier-1 source.** "I think the CMO is X" is not acceptable. Always verify via company press release, SEC filing, or the executive's verified LinkedIn.

2. **Never bypass the saturation filter.** OpenAI, Anthropic, Stripe, PepsiCo (parent), Coca-Cola get pitched constantly. They get a -3 to -5 score penalty unless there's a specific recent unlock event.

3. **Never bypass the active deal check.** Before any signal is surfaced, cross-reference against `references/blocklist.md`. If the company is in 1440's pursuit pipeline, log it but do not surface — except as a "we already spotted this, here's validation" framing if user asks.

4. **Always show the score breakdown transparently.** "JFrog 87" is not acceptable. "JFrog 87 = V2.1 base 75 + Alumni boost 12 *(strict tier, Genefa Murphy ex-Udemy CMO)*" is.

5. **Default to paraphrasing in any web-sourced content.** Direct quotes only when material to the score (e.g., a CEO's own words about brand strategy). Keep quotes under 15 words and use only one per source.

6. **Never use bullet points in PDF briefs.** Briefs must be prose-formatted. Bullet points only allowed in: (a) Daily Top 3 digest ASCII box, (b) Score grid table on PDF page 2.

7. **Never write any sponsor claim without consulting `active_sponsor_db.md`.** Sponsor and category-lock claims invented from memory are the highest-severity hallucination class.

8. **Never score Operational Fit without `team_needs_taxonomy.md` open.** OF is the dimension most likely to be over-scored from "vibes" — taxonomy match has to be named explicitly.

9. **Never elevate a high-OF / low-BF signal to Top 3.** The OF Gate (Brand Fit ≥ 12/20 required for OF to count toward Top 3 ranking) exists for this exact reason.

10. **Never generate a brief from a LOW-confidence signal.** The Confidence Card (7 fields, HIGH = 6/7 ✅, MEDIUM = 4-5/7 with no ❌) gates brief generation.

11. **Never mix scoring scales.** All current scoring is /100 (Phase 2.1). If you see a /125 score anywhere, that's a Phase 2.0 artifact — recalibrate by reading the dimensions out of /20 and summing.

## Daily Digest Output Template

When generating the Daily Top 3:

```
╔══════════════════════════════════════════════════════════════════╗
║  1440 SPORTS — INTELLIGENCE BRIEF                                  ║
║  Daily Top 3 — [DATE]                                              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  🥇 #1 — [COMPANY]                                                ║
║         [📊 COMPANY SIGNAL (Track 1) | 🕵️ EXECUTIVE INTENT (Track 2)]║
║         Score: XX/100 | [HOT TOP TIER/HOT/WARM] | [Series/Team]   ║
║         Person: [NAME] ([ROLE])                                   ║
║         [One-sentence executive take]                              ║
║         → [Action recommendation + horizon]                        ║
║                                                                    ║
║  🥈 #2 — [COMPANY]                                                ║
║         [...]                                                      ║
║                                                                    ║
║  🥉 #3 — [COMPANY]                                                ║
║         [...]                                                      ║
║                                                                    ║
║  📋 Pursue with longer horizon:                                   ║
║     - [Companies scored 55-69]                                    ║
║                                                                    ║
║  ⚠️ Verify before action:                                          ║
║     - [VERIFY tier signals — 40-54]                               ║
║                                                                    ║
║  ⚪ Plant-and-hold:                                                ║
║     - [Sub-55 signals worth tracking]                             ║
║                                                                    ║
╚══════════════════════════════════════════════════════════════════╝
```

## Phase A: Daily Digest Workflow

1. **Search broadly** for fresh signals across both tracks (last 0-72 hours preferred):
   - Track 1 web searches: "enterprise software unicorn funding [current month]", "[major industry] new CMO appointment", "Series C announcement enterprise AI [current month]", IPO filings, leadership changes
   - Track 2 web searches: cross-reference recent executive moves against alumni database in `references/alumni_database.md`

2. **Apply six gates** to each candidate (read `references/v21_prompt.md` for gate definitions). Discard fails immediately.

3. **Score qualifying signals** on five dimensions (each /20). Apply alumni boost if Track 2.

4. **Cross-reference blocklist.** Suppress active deals.

5. **Rank, format, deliver.** Surface Top 3 in box format. Show secondary tier underneath.

6. **Offer PDF for the top signal** if user wants to escalate to MD.

## Phase B: Single Company Score Workflow

1. Read `references/v21_prompt.md`, `references/team_needs_taxonomy.md`, and `references/active_sponsor_db.md` to ensure full V2.1 logic plus operational fit and sponsor context is in context.
2. Search company name + relevant signal category (funding, leadership, strategic shift).
3. Apply six gates explicitly. Show the breakdown.
4. Score five dimensions /20 each. Show the math.
5. Check alumni database — does any alumnus work at this company?
6. Check blocklist.
7. Write the full V2.1 markdown report.
8. Offer PDF version.

## Phase C: Alumni Search Workflow

1. Read `references/v22_alumni.md` and `references/alumni_database.md`.
2. For "find alumni signals" → systematic search of database executives' current LinkedIn/press for job changes since last update.
3. For "who moved from [Sponsor]" → web search "[former-employer] CMO/CEO [current year - 1] [current year]" + "left" + "joined".
4. For each alumnus move detected:
   - Verify via Tier-1 source
   - Determine alumnus tier (strict / medium / loose — see v22_alumni.md)
   - Run new company through V2.1 (Phase B)
   - Apply alumni boost
   - Surface qualifying signals; log non-qualifying
5. Update `references/alumni_database.md` with any new findings.

## Phase D: Database Build Workflow

For systematic expansion of alumni database. See `references/v22_alumni.md` for full methodology. Key heuristic: focus on F1/FE sponsorship deals from 2018-2025 where named executives are verifiable from public press releases (CEO, CMO who signed announcements). Strict tier first; medium tier if time allows.

## Phase E: Outreach Drafting

Reference `references/brand_voice.md` for tone. Default structure:
- Opening line: shared history reference (alumni signals) OR specific recent trigger (Track 1 signals)
- One sentence: why now
- One sentence: what 1440 specifically offers (not generic agency language)
- Specific time ask: "25 minutes" not "a quick chat"

## Glossary

- **Track 1 / V2.1** — Company Signal Engine. Cold signals. Six gates, five dimensions /20 each, 0-100 score.
- **Track 2 / V2.2** — Executive Alumni Intelligence Engine. Layered on top of V2.1; boosts qualifying signals.
- **Strict tier alumnus** — CEO/CMO who personally signed an F1/FE deal, quoted in announcement press release. Boost: +9 to +12.
- **Medium tier alumnus** — VP+ in seat at sponsoring company during deal years. Boost: +5 to +8.
- **Loose tier** — Director-level or below. Excluded (too noisy).
- **Active deal blocklist** — Companies 1440 is currently pursuing. Auto-suppress.
- **Saturation filter** — Companies pitched constantly. Auto-penalty unless specific unlock.
- **Compound signal** — Multiple independent triggers within 90 days. +2 to +5 bonus.
- **Operational Fit Gate** — OF only counts to Top 3 ranking if Brand Fit ≥ 12/20.
- **HOT TOP TIER** — Score 85+, eyebrow flag, urgent action horizon.
- **HOT** — Score 70-84, action horizon 4-8 weeks.
- **WARM** — Score 55-69, action horizon 1-3 months.
- **VERIFY** — Score 40-54 with complications (ESG, division fit, fired exec). Human review before action.
- **PLANT** — Sub-55 (technically 25-39), log for re-evaluation in 6-12 months.
- **DISCARD** — Saturation, off-strategy, or already on blocklist (technically 0-24).

## Production Notes

- **Daily run target time:** 8am London. Weekdays only.
- **Signal volume target:** Top 3 daily, plus 5-7 secondary tier visible.
- **Track 2 contribution target:** At least 1 of Top 3 per week should be alumni-driven. *(Historical rate from testing: 2 of 3.)*
- **FE-track contribution target:** At least 1 of Top 3 per weekday is FE-track.
- **Quality gate:** A surfaced signal must pass the "would I actually email this person tomorrow?" test. If no, downgrade.
