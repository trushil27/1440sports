# Scoring Calibration — Test Results From Sessions

The 24 historical signals scored across build sessions, plus calibration anchors. Use this to calibrate new scores against precedent — if you're tempted to score something at 75, find the closest analogue here and check the math.

> **Phase 2.1 note (May 2026):** Scoring has reverted to /100 (5 dimensions × /20 each, Operational Fit retained as 5th first-class dimension). The Phase 2.0 dual-scale note that briefly applied is removed. The historical /100 scores below are the canonical reference scale again — directly comparable to scores generated today. New entries since May 2026 record the Operational Fit dimension explicitly in the breakdown.

## Tested Signals — Full Set *(scores out of 100)*

| # | Company | Person | Track | Score | Tier | Verdict |
|---|---|---|---|---|---|---|
| 1 | JFrog *(NASDAQ: FROG)* | Genefa Murphy *(CMO)* | Track 2 | 87 | HOT TOP TIER | Pursue |
| 2 | Crypto F1 disruption play | — | Track 1 | 84 | HOT | Multi-target |
| 3 | Databricks | Rick Schultz *(CMO)* | Track 1 | 81 | HOT | Outreach 4-6wks |
| 4 | Luminary Cloud | Pete Schlampp *(CEO)* | Track 2 | 80 | HOT | Outreach this week |
| 5 | Mistral AI | Arthur Mensch *(CEO)* | Track 1 | 78 | HOT | Pursue (sent to MD) |
| 6 | Factory AI | Matan Grinberg *(CEO)* | Track 1 | 78 | HOT | MD already in contact |
| 7 | Vontier | — | Track 1 | 74 | HOT | FE focus |
| 8 | DeepL | Detlef Krause *(CRO)* | Hybrid | 73 | HOT | Outreach 2-3wks |
| 9 | Kraken Technologies *(Octopus spinoff)* | — | Track 1 | 73 | HOT | Pursue |
| 10 | Aikido Security | — | Track 1 | 71 | HOT | Pursue |
| 11 | Lattice | Sarah Franklin *(CEO)* | Track 2 | 71 | HOT | Pursue with horizon |
| 12 | Stripe | — | Track 1 | 71 | DISCARD | Saturation |
| 13 | Legora | — | Track 1 | 70 | HOT | Pursue |
| 14 | Lovable | — | Track 1 | 68 | WARM | Plant |
| 15 | WorkOS | Michael Grinich *(CEO)* | Track 1 | 67 | WARM | 6-8wks |
| 16 | PepsiCo Int'l Foods | Jonnie Cahill *(CMO)* | Track 2 | 66 | VERIFY | Division-fit check |
| 17 | Shield AI | Gary Steele *(CEO)* | Track 2 | 64 | VERIFY | ESG check |
| 18 | Nscale | — | Track 1 | 64 | WARM | Plant |
| 19 | Cast AI | Yuri Frayman *(CEO)* | Track 1 | 62 | PLANT | Re-evaluate post-D round |
| 20 | Sumo Logic | — | Track 1 | 62 | WARM | Plant |
| 21 | Version 1 / CD&R | Brian Humphries *(CEO)* | Track 2 | 62 | VERIFY | Psychological complexity |
| 22 | Apollo.io | Marcio Arnecke *(CMO)* | Track 1 | 61 | PLANT | Re-evaluate Q4 |
| 23 | AMI Labs | — | Track 1 | 61 | PLANT | Pre-revenue |
| 24 | Coursera | — | Track 1 | 58 | PLANT | Stage drift |
| 25 | n8n | — | Track 1 | 52 | PLANT | Early-stage |
| 26 | Concentrix | — | Track 1 | 32 | DISCARD | Verify *(note: had real warm pipeline)* |
| 27 | Encord | — | Track 1 | DISCARD | DISCARD | Stage + relevance |

*Tier labels above use the Phase 2.1 anchors (85+ HOT TOP TIER, 70-84 HOT, 55-69 WARM, 40-54 VERIFY, 25-39 PLANT, 0-24 DISCARD). JFrog at 87 is reclassified as HOT TOP TIER under Phase 2.1; substantively unchanged.*

## Phase 2.1 Tested Signals *(signals re-scored with Operational Fit explicit — append as scored)*

| # | Date | Company | Track | T/20 | C/20 | BF/20 | U/20 | OF/20 | Boost | Final | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| *(empty — first Phase 2.1 production signals to be logged here)* | | | | | | | | | | | |

## Track 1 vs Track 2 Performance *(historical data, /100)*

| Track | Avg Score | Hot/Warm Hit Rate |
|---|---|---|
| **Track 2 (Alumni)** | **74** | **5 of 5 (100%)** |
| **Track 1 (Cold signals)** | **65** | **13 of 19 (68%)** |

**Pattern observation:** Track 2 alumni signals consistently outperformed cold signals by ~9 points on average. The alumni boost did real work — pre-qualified buyers convert at materially higher rates than cold pitches. This is the core commercial argument for V2.2. **Phase 2.1 watch item:** does adding Operational Fit as a 5th dimension expand or compress Top 3 ranking vs the original 4-dim /100? Track in the Phase 2.1 row of this file once enough signals are scored.

## Calibration Anchors *(/100, directly applicable to current scoring)*

Use these as reference points when scoring something new.

### "What does an 87/100 look like?"
JFrog/Murphy. Pre-qualified buyer at NASDAQ-listed company in correct stage, first-100-days window, no saturation, narrative-perfect category. The ceiling for a *single-person-driven* signal. **HOT TOP TIER.**

### "What does an 80/100 look like?"
Luminary/Schlampp. Strict-tier alumnus as CEO at mid-stage company with near-perfect narrative match. Capacity ceiling reduces base score; alumni override pushes it back up. Under Phase 2.1 the Operational Fit dimension (Physics AI → A2/A3 in the taxonomy) likely raises this materially — Luminary is the canonical OF-elevation case.

### "What does a 78/100 look like?"
Mistral or Factory. Cold Track 1 signal with compound triggers (3+ within 90 days), correct stage, very low saturation, near-perfect brand fit. The ceiling for a *Track 1 only* signal.

### "What does a 71/100 look like?"
Lattice/Franklin or Aikido. Either a Track 2 with reduced freshness boost (Franklin moved 2+ years ago), or a Track 1 with clean fundamentals but no compound trigger. **HOT under Phase 2.1.**

### "What does a 64/100 look like?"
VERIFY tier. Real signal but with complications — Shield AI (defense ESG), Version 1 (fired CEO), Nscale (recency drift). Worth flagging, not worth surfacing as Top 3.

### "What's the floor for surfacing?"
55/100 — below WARM, plant-and-hold or discard. The floor exists because below that, you're losing more attention by surfacing weak signals than you'd gain from occasional hits.

## Phase 2.1 Tier Anchors

| Tier | Score band | Notes |
|---|---|---|
| HOT TOP TIER | 85-100 | Reserved for compound signal + alumni + strong OF. JFrog at 87 is the historical exemplar. |
| HOT | 70-84 | Bulk of Top 3. Mistral, Factory, Databricks, Luminary, DeepL, Aikido, Vontier, Kraken, Lattice. |
| WARM | 55-69 | Secondary tier. Lovable, WorkOS, Sumo Logic, Cast AI. |
| VERIFY | 40-54 | Complications flagged, human review. Some historical "VERIFY" signals scored in 60s due to complications inflating below the line — re-tag by complication, not by raw score. |
| PLANT | 25-39 | Re-evaluate 6-12 months. Concentrix at 32 is the archetype. |
| DISCARD | 0-24 | Saturation, off-strategy, or already on blocklist. Encord. |

## Common Scoring Errors to Watch For

### Error 1: Inflating capacity for stage signals
Just because a company raised a big round doesn't mean it's title-deal capacity. $1B valuation = mid-tier capacity. $5B+ = major partner. $20B+ = title.

### Error 2: Inflating brand fit for "AI" companies
Not every AI company has F1-level brand-fit. AI infrastructure (developer tools) has weaker consumer reach than enterprise AI applications. Score on actual audience overlap, not category vibes.

### Error 3: Forgetting saturation
OpenAI, Anthropic, Stripe, Ramp — these get pitched constantly. Saturation penalty is mandatory unless there's a specific recent unlock event.

### Error 4: Confusing "interesting" with "scoreable"
A fascinating company story is not the same as a scoreable signal. The signal needs a trigger, a timing window, and a path to a meeting. "Interesting" without that is content, not intelligence.

### Error 5: Over-applying alumni boost for medium tier
Medium-tier alumni get +5 to +8, not +9 to +12. Save the high boost for strict tier (CEO/CMO who personally signed deals).

### Error 6: Inflating Operational Fit from product-deck reasoning
The taxonomy in `team_needs_taxonomy.md` defines named team needs. Score Operational Fit against those named needs, not against general "could be useful to motorsport" intuition. A general-purpose enterprise SaaS company without a specific category match should score Sub-1 (product-to-need) at 3-4/8, not 6-7/8. Default to lower bound when uncertain.

### Error 7: Bypassing the Operational Fit Gate
A high OF with weak Brand Fit (BF < 12/20) is the OF Gate trigger — that signal goes to secondary tier, NOT Top 3. Resist the urge to elevate it just because the operational fit is interesting.

### Error 8: Translating /125 scores from the brief Phase 2.0 window
Any /125 score from Phase 2.0 should be re-derived from its dimension breakdown out of /20 each and re-summed to /100. Do not divide /125 by 1.25; the linear rescale loses the Operational Fit weighting nuance. Recompute from primary dimensions.

## Score Distribution Sanity Check

Of 24 historical signals tested:
- 85+ HOT TOP TIER: 1 *(JFrog)*
- 70-84 HOT: 8
- 55-69 WARM: 11
- 40-54 VERIFY: 0 *(though several were VERIFY tier with scores 60+ due to complications)*
- 25-39 PLANT: 1 *(Concentrix)*
- DISCARD: 2 *(Stripe, Encord)*

This is roughly the expected distribution. If a session produces 5+ HOT signals, recheck the calibration — likely scoring inflation.

## Phase 2.1 Sanity Targets *(to track)*

- HOT TOP TIER (85+): ~1 per month, rare exemplars
- HOT (70-84): ~3-5 per week — Top 3 candidates
- WARM (55-69): bulk of weekly volume
- VERIFY: 1-2 per week with explicit complications
- PLANT: longer-tail logging
- DISCARD: blocked at gates, not surfaced

If any week produces >5 HOT TOP TIER, suspect scoring inflation (likely OF being over-scored or Brand Fit slipping past archetype anchors).
