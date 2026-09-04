# V2.1 — Track 1 Company Signal Engine *(Phase 2.1 recalibration — May 2026)*

The full Company Signal scoring prompt. Apply this rigorously to any company being evaluated as an F1/FE sponsorship target. Never approximate the scoring.

**Cumulative version history:**
- Phase 1 (May 2026): Step 0 Track Determination, FE archetypes, Pre-Flight Sponsor Check, Citation Enforcement Gate, Confidence Card *(7 fields)*. Scoring /100 across 4 dimensions of 25 each.
- Phase 2.0 (May 2026, superseded): Operational Fit added as 5th dimension /25; score cap moved to /125. Team-needs taxonomy required reading. "What Could Run On The Car" brief section unlocked when Operational Fit ≥ 18.
- **Phase 2.1 (May 2026, current): MD directed scoring revert to /100. Operational Fit retained as first-class 5th dimension but scaled to /20; all other dimensions also scaled to /20. Tier thresholds restored to original Phase 1 anchors (85/70/55/40/25). Confidence Card unchanged at 7 fields. Tighter brief spacing applied.** Historical /100 calibration figures in `scoring_calibration.md` are now valid by absolute number again.

## Step 0 — Track Determination

Every signal is committed to a track before scoring. This stops the engine from defaulting to F1-flavoured reasoning for companies whose natural sponsorship logic is FE.

Score the company on a track-fit comparison:

| Indicator | Pulls toward F1 | Pulls toward FE |
|---|---|---|
| Industry | Enterprise software, B2B SaaS, financial services, cloud/AI, consumer luxury, oil & gas, classic automotive | Cleantech, mobility, EV charging, battery, sustainability SaaS, ESG, smart cities, urban infra, electrification, public-sector tech |
| Audience | Global enterprise CIO/CMO, premium consumer, investor narrative for IPO/growth | Regulator, sovereign LP, urban policymaker, fleet buyer, board ESG committee |
| Geographic footprint | Global, with US/EU/Middle East/Singapore concentration | Urban-centric, EU heavy, Asian megacity, LatAm, MENA city-states |
| Pitch logic | "Investor narrative + enterprise buyer trust at scale" | "Sustainability credentials + electrification showroom + regulatory tailwind" |
| Operating model | Software margin, capital-light, IP-driven | Capex-heavy, hardware-adjacent, public-sector contract, regulatory mandate |

**Decision rule:**
- 4+ indicators pull one way → **commit to that track**.
- 2-3 each way → **dual-track**. Score against both archetype sets; surface to whichever yields higher Brand Fit + Urgency combined.
- Default for unclear → score as F1 *only* if F1 Brand Fit ≥ 14/20; otherwise default FE.

## The Six Internal Gates (silent, applied before scoring)

### Gate 0 — Source Quality
- **Tier 1 (pass)**: Company press release, SEC/Companies House filing, mainstream business press *(WSJ, Bloomberg, Reuters, FT, TechCrunch, The Verge)*, verified executive LinkedIn
- **Tier 2 (pass with caution)**: Industry publication, well-sourced news aggregator
- **Tier 3 (fail)**: Forum posts, rumour sites, unverified social media

### Gate 1 — Recency
- **Pass**: Trigger event within 0-12 months
- **Recency penalty**: Beyond 6 months, deduct 2-3 points from Timing dimension
- **Fail**: Beyond 12 months without fresh trigger

### Gate 2 — Capacity
- **Pass**: Public company >$1B mkt cap OR >$100M revenue; private $1B+ valuation OR $100M+ ARR
- **Pass with note**: $300M-$1B valuation = mid-tier deal capacity only ($1-3M/year)
- **Fail**: Pre-revenue, sub-$300M valuation, bootstrapped

*(Phase 3a will replace web-search heuristics here with structured Crunchbase data — see `phase3a_crunchbase_scope.md`.)*

### Gate 3 — Motorsport Relevance
- **Score 1-10** on combined audience/narrative/geographic fit against the chosen track
- **Pass**: 5+ on the 10 scale
- **Fail**: Sub-5

### Gate 4 — Saturation Filter
- **HIGH saturation (-5)**: OpenAI, Stripe, every major US bank, large CPG conglomerates
- **MEDIUM saturation (-3)**: Established Series C+ AI unicorns without new triggers, large tech vendors
- **LOW saturation (0)**: Niche category leaders, geographic challengers, mid-market companies
- **VERY LOW saturation (+0)**: Greenfield categories *(Physics AI, DevSecOps, agentic AI; FE side: carbon accounting, EV charging-software, battery analytics)*

**Override**: A specific recent unlock event can negate up to half the saturation penalty.

### Gate 5 — Active Deal Check
Cross-reference `blocklist.md`. If in pursuit pipeline → suppress (log only).

### Gate 6 — Alumni Intelligence (Track 2 Layer)
Cross-reference `alumni_database.md`:
- **Strict tier match**: +9 to +12 boost
- **Medium tier match**: +5 to +8 boost
- **Loose tier match**: Suppressed (too noisy)

## Pre-Flight Sponsor Check

Runs against `active_sponsor_db.md` per Section 6 of that file:
1. Identity check — is target already a sponsor or owned by one?
2. Category lock check — is target's industry locked at championship level?
3. Team slot check — for each candidate team, is the category already filled?
4. Conflict check — competitors on the recommended team?
5. Category density note — how crowded is the broader category?

**Outcome codes:** CLEAN / CONSTRAINED / CONFLICTED / BLOCKED.

## The Five Scoring Dimensions *(Phase 2.1 — each /20)*

Each scored 0-20. Total now 0-100.

### TIMING (0-20)
How fresh is the trigger? How well-timed is outreach?

- **18-20**: Trigger within 30 days; first-100-days window for new exec; pre-IPO 3-6 months out
- **14-17**: Trigger 1-3 months old; clear strategic window
- **11-13**: Trigger 3-6 months old; window past peak freshness but actionable
- **8-10**: Trigger 6-9 months old
- **4-7**: Trigger 9-12 months old; cold opening
- **0-3**: Beyond freshness; no specific trigger

### CAPACITY (0-20)
Can they afford a deal? At what tier?

- **18-20**: Title-deal capacity ($20M+/year). Public >$50B mkt cap or private $20B+
- **14-17**: Major partner capacity ($5-15M/year). $5-50B or $5-20B private
- **11-13**: Mid-tier team partner ($2-5M/year). $1-5B valuation
- **8-10**: Lower tier ($500k-2M/year). $300M-1B valuation
- **4-7**: Stretch deal possible
- **0-3**: No realistic capacity

### BRAND FIT (0-20) — track-aware

**F1-track archetypes:** BRAND RECKONING (17-20), CATEGORY INFLECTION (16-19), NARRATIVE-PERFECT (14-18), LUXURY/PREMIUM (13-17), GEOGRAPHIC PLAY (13-16).

**FE-track archetypes:** SUSTAINABILITY MANDATE (17-20), FLEET INFLECTION (17-20), REGULATORY URGENCY (16-19), SHOWROOM PLAY (16-19), CITY-STATE/SOVEREIGN (14-17), NARRATIVE-CLEAN (13-16).

Score against the matching archetype for the committed track.

### URGENCY (0-20)
Is there a competitive trigger or external deadline?

- **18-20**: Hard deadline (IPO <6 months; competitor signed; rebrand; activist pressure)
- **14-17**: Strong external trigger (post-Series C GTM; major customer; regulatory window)
- **11-13**: Internal trigger (new exec mandate; new strategy phase)
- **8-10**: General positioning pressure
- **4-7**: Opportunistic
- **0-3**: No identifiable trigger

### OPERATIONAL FIT (0-20) *(Phase 2.1 — rebalanced from /25)*

How well does the target's product map to a genuine F1/FE team operational need? *(Required reading: `team_needs_taxonomy.md`.)*

**Sum of four sub-scores:**

**Sub-score 1 — Product-to-Need Match (0-8):**
- 7-8: Flagship product directly answers a specific named need in the taxonomy
- 5-6: Strong adjacent fit
- 4: Workable fit with creative framing
- 2-3: Stretched
- 0-1: No real operational fit; pure brand-only

**Sub-score 2 — Slot Availability (0-4):**
- 4: Category empty across grid OR specific team's slot open
- 3: 1-3 teams filled; slot exists at 7+ teams
- 2: 4-7 teams filled; tight
- 0-1: Saturated

**Sub-score 3 — On-Camera Demonstrability (0-4):**
- 4: Visibly running during race (pit-wall screens, engineer headsets, livery integration, broadcast data feeds)
- 3: Visible at activations and facility tours
- 1-2: Behind-the-scenes only
- 0: No demonstrable activation

**Sub-score 4 — Strategic Lock-In Potential (0-4):**
- 4: Embedded operationally; high switching cost (cloud, PLM, security stacks)
- 3: Strong embed but switchable in off-season
- 1-2: Lightly integrated tool
- 0: Pure brand placement

**Sub-score total: 8 + 4 + 4 + 4 = 20.**

**OPERATIONAL FIT GATE:** Operational Fit only counts toward Top 3 ranking if **Brand Fit ≥ 12/20**. This prevents the engine from elevating signals where operational integration is strong but the company isn't a credible brand fit. Operational Fit always appears in the output, but its weight in the ranking is conditional.

## Compound Signal Bonus

If three or more independent triggers within 90 days → add +2 to +5 to total score.

## Score Tier Thresholds *(Phase 2.1 — restored to original /100 anchors)*

| Score | Tier | Action |
|---|---|---|
| 85-100 | HOT TOP TIER | Daily Top 3, urgent Slack alert if Timing 18+ |
| 70-84 | HOT | Daily Top 3 candidate |
| 55-69 | WARM | Top 3 if HOT tier underfills; otherwise pursue with horizon |
| 40-54 | VERIFY | Human review before action — complications flagged |
| 25-39 | PLANT | Log for re-evaluation in 6-12 months |
| 0-24 | DISCARD | Reason logged, removed from active scanning |

These are the same anchors used to calibrate the 24 historical signals in `scoring_calibration.md`. Phase 2.1 means a brief from May 2026 onward can be compared directly by absolute number against any Phase 1 signal: JFrog 87, Mistral 78, Luminary 80, etc. — all directly comparable to a new signal scored today.

## Citation Enforcement Gate

Every assertion in the output classified at output time:
1. **CITED** — backed by Tier-1 or corroborated Tier-2 source URL. Pass.
2. **INFERRED** — follows from cited facts but not directly sourced. Mark with *"This suggests…"* or *"Likely…"*. Pass with annotation.
3. **UNSUPPORTED** — no traceable source. **REJECT** — find source or remove claim.

**Specifically forbidden without explicit Tier-1 source:** named decision-maker (need press release / SEC / verified LinkedIn URL); funding round / valuation (need Crunchbase, Pitchbook, SEC, or company announcement); sponsorship status (cross-ref `active_sponsor_db.md`); contract end date or renewal year (public reporting); executive quote (original source, ≤15 words, one per source).

**The £100 test:** for every numeric and named-person claim — would I bet £100 this is right? If no, paraphrase into hedged language or drop.

## Required Output Structure

```
═══════════════════════════════════════════════════════════════════
TRACK DETERMINATION
═══════════════════════════════════════════════════════════════════
Committed Track: [F1 / FE / DUAL]
F1 indicators:   [N/5]    FE indicators:   [N/5]
Decision basis:  [1 sentence]

═══════════════════════════════════════════════════════════════════
INTERNAL GATES (silent)
═══════════════════════════════════════════════════════════════════
Gate 0 — Source: [Tier]                                          ✅/❌
Gate 1 — Recency: [Date/window]                                  ✅/❌
Gate 2 — Capacity: [Valuation/revenue]                           ✅/❌
Gate 3 — Motorsport relevance: [X/10]                            ✅/❌
Gate 4 — Saturation: [LEVEL]                                     [+/- N]
Gate 5 — Active deal: [Status]                                   ✅/❌
Gate 6 — Alumni intelligence: [tier or NONE]                     [+N or n/a]

PRE-FLIGHT SPONSOR CHECK
  1. Identity check:         [CLEAN/BLOCKED]
  2. Category lock:          [CLEAN/CONSTRAINED — lockholder named]
  3. Team slot check:        [per team — CLEAN/CONFLICTED]
  4. Conflict check:         [CLEAN/CONFLICTED — competitor named]
  5. Category density:       [N teams in this category]
  Outcome:                   [CLEAN / CONSTRAINED / CONFLICTED / BLOCKED]
═══════════════════════════════════════════════════════════════════

🎯 EXECUTIVE TAKE
[2-3 sentence summary]
[Recommendation line]

Score: XX/100 | Timing: [HOT/WARM/VERIFY/PLANT] | Fit: [Series/Team]
Confidence: [HIGH/MEDIUM/LOW]

WHY THIS LEADS TO A MEETING:
[Paragraph explaining conversion logic]

───────────────────────────────────────────────────────────────────
📊 SIGNAL ANALYSIS
───────────────────────────────────────────────────────────────────
Company:           [Legal name]
Industry:          [Specific category]
HQ:                [Location]
Source:            [Tier 1/2 sources — URLs]
Signal Date:       [Specific date]
Signal Type:       [Compound / Track 2 / Funding / Leadership]

What Happened:     [Bulleted facts]
Why It Matters:    [2-3 sentences synthesising]

───────────────────────────────────────────────────────────────────
🎯 STRATEGIC INTENT (Company)
───────────────────────────────────────────────────────────────────
[1-2 paragraphs on commercial strategy and how F1/FE fits]
Existing Sponsorships: [List or "None publicly identified"]

───────────────────────────────────────────────────────────────────
🏎️ MOTORSPORT FIT
───────────────────────────────────────────────────────────────────
WHY IT FITS:
[Three numbered reasons anchored to the chosen track's archetype]

WHERE IT FITS:
Series:     [F1/FE/Both]
Archetype:  [Specific archetype from Brand Fit section]
Geography:  [Specific races where audience concentrates]

Best Team Matches *(pre-flight checked)*:
  1. [Team] — [Reason] — Slot status: [CLEAN/CONFLICTED]
  2. [Team] — [Reason] — Slot status: [CLEAN/CONFLICTED]
  3. [Team] — [Reason] — Slot status: [CLEAN/CONFLICTED]

HOW IT FITS:
Sponsorship Type: [Deal type]
Deal Shape:        [Years, $/yr, signing window]
Activation Idea:  [Specific creative concept]

───────────────────────────────────────────────────────────────────
🔧 OPERATIONAL FIT
───────────────────────────────────────────────────────────────────
Primary Product: [What the target sells]
Taxonomy Match:  [Category from team_needs_taxonomy.md — e.g. C3 Observability]
Incumbent Map:   [Who currently fills this slot across F1/FE per active_sponsor_db.md]
Open Teams:      [List of teams where this slot is empty]

WHAT COULD RUN ON THE CAR / IN THE TEAM:
[1-2 paragraph specific description of how the target's product would 
actually plug into a team's operations. Name the specific team, the 
specific operational need, the specific activation. This is the 
content that maps to the brief's "WHAT COULD RUN ON THE CAR" section.]

Operational Fit Score: [X+Y+Z+W = N/20]
  Sub-1 Product-to-need:    [X/8] — [reasoning]
  Sub-2 Slot availability:  [Y/4] — [reasoning]
  Sub-3 Demonstrability:    [Z/4] — [reasoning]
  Sub-4 Lock-in potential:  [W/4] — [reasoning]

Operational Fit Gate: [APPLIED — Brand Fit ≥12, OF counts to ranking] 
                     OR [NOT APPLIED — Brand Fit <12, OF logged but 
                        doesn't influence Top 3 rank]

───────────────────────────────────────────────────────────────────
⏱️ TIMING & PSYCHOLOGY
───────────────────────────────────────────────────────────────────
Timing Class:     [HOT/WARM/VERIFY]
Window:           [Specific weeks/months]
Psychological Trigger: [Internal pressure driving yes]

Risks:
(1) [Specific risk + counter]
(2) [Specific risk + counter]
(3) [Specific risk + counter]

───────────────────────────────────────────────────────────────────
📈 OPPORTUNITY SCORE: XX/100
───────────────────────────────────────────────────────────────────
Track 1 Base: XX
  - Timing:          X/20 — [reasoning]
  - Capacity:        X/20 — [reasoning]
  - Brand Fit:       X/20 — [reasoning, naming archetype]
  - Urgency:         X/20 — [reasoning]
  - Operational Fit: X/20 — [reasoning] [GATE APPLIED/NOT APPLIED]

[Saturation: -N if applicable]
[Compound: +N if applicable]
Track 2 Alumni Boost: +N (if applicable)

FINAL SCORE: XX/100 — [HOT TOP TIER / HOT / WARM / VERIFY / PLANT]

───────────────────────────────────────────────────────────────────
👥 CONTACT INTELLIGENCE
───────────────────────────────────────────────────────────────────
Primary Target:
  Name:          [Full name] — Source: [URL]
  Role:          [Title, Company]
  Profile:       [Background, LinkedIn URL]
  Why Critical:  [Why this person specifically]

Secondary Target (if applicable):
  Name:          [Full name] — Source: [URL]
  Role:          [Title]
  Why Relevant:  [Fallback rationale]

───────────────────────────────────────────────────────────────────
💬 RECOMMENDED OUTREACH ANGLE (if HOT signal)
───────────────────────────────────────────────────────────────────
[Strategic framing — for OF ≥14 signals, lead with operational angle 
rather than brand-trust angle; the technical decision-maker is often 
the right entry point in this case]

Opening Hook (suggested):
"[Draft, 4-6 sentences, ending with specific time ask]"

───────────────────────────────────────────────────────────────────
🔒 CONFIDENCE CARD
───────────────────────────────────────────────────────────────────
Funding / valuation figure: [✅ Source: URL, date / ⚠ inferred / ❌ unconfirmed]
Decision-maker identity:    [✅ Source: URL / ⚠ inferred / ❌ unconfirmed]
Decision-maker role:        [✅ Source: URL / ⚠ inferred / ❌ unconfirmed]
Sponsor / partnership claims: [✅ active_sponsor_db.md last verified DD MMM YYYY / ⚠ / ❌]
Trigger event date:         [✅ Source: URL, date / ⚠ inferred / ❌ unconfirmed]
Contract / renewal claims:  [✅ Source: URL / ⚠ inferred / ❌ unconfirmed / N/A]
Operational fit claims:     [✅ team_needs_taxonomy.md + active_sponsor_db.md / ⚠ inferred / ❌ unconfirmed]

Overall Confidence:         [HIGH / MEDIUM / LOW]
  HIGH = ≥6 of 7 fields ✅
  MEDIUM = 4-5 fields ✅, no ❌
  LOW = 3 or fewer ✅, or any ❌

If confidence is LOW → engine must NOT generate a PDF brief from this signal.
```

## FE-Specific Search Query Templates

(unchanged from Phase 1) — rotate daily across SUSTAINABILITY MANDATE, FLEET INFLECTION, REGULATORY URGENCY, SHOWROOM PLAY, CITY-STATE/SOVEREIGN searches.

## Daily Top 3 — FE Quota

(unchanged from Phase 1) — at least one FE-track signal in Daily Top 3 each weekday; relax to ≥60/100 then to best-of-day if needed.

## When Operational Fit Triggers the Brief Section *(Phase 2.1 thresholds)*

If a signal's Operational Fit ≥ 14/20 AND Brand Fit ≥ 12/20, the brief generated from it MUST include the "What Could Run On The Car" section per `pdf_brief_template.md`. The PDF builder reads the `operational_fit_section` boolean and `operational_fit_content` string in the brief data to render it.

For Operational Fit 8-13/20, the section is optional and only included if user explicitly requests.

For Operational Fit <8/20, the section is omitted from the brief entirely — the signal is a brand-only play and the brief reflects that without padding.

## Common Mistakes to Avoid

1. **Don't conflate trigger date with deal date.**
2. **Don't confuse capacity with willingness.**
3. **Don't apply saturation as binary** — it's a gradient.
4. **Don't surface VERIFY signals in Top 3.**
5. **Don't invent named contacts.**
6. **Don't skip the gates if the signal feels obvious.**
7. **Don't default to F1 framing for FE-natural companies.**
8. **Don't generate a brief from a LOW-confidence signal.**
9. **Don't write any sponsor claim without consulting `active_sponsor_db.md`.**
10. **Don't score Operational Fit from memory.** Always cross-reference `team_needs_taxonomy.md` for the category match and `active_sponsor_db.md` for slot availability. Operational Fit invented without these references is a Phase 2.1 violation.
11. **Don't elevate a high-OF / low-BF signal in Top 3.** The Operational Fit Gate exists for this reason — a brilliant product fit at a team whose brand doesn't resonate gets surfaced in secondary tier, not Top 3.
12. **Don't pad the "What Could Run On The Car" section.** If OF <8, the section is omitted, not weakened. Better silence than vague language about how the product "could integrate."
13. **Don't mix /125 and /100 scoring.** *(NEW Phase 2.1)* All scores from May 2026 onward are /100 with 5 dimensions of /20 each. If you see a /125 score in older notes, it was a Phase 2.0 artifact — the canonical scale is /100. Historical /100 scores in `scoring_calibration.md` are directly comparable.

## Implementation Notes for Phase 2.1

- `team_needs_taxonomy.md` MUST be readable in context alongside `active_sponsor_db.md` and this V2.1 file when scoring.
- Output structure adds the OPERATIONAL FIT block; PDF builder reads `operational_fit_section` flag + `operational_fit_content` and renders the new section when OF ≥ 14/20.
- Historical signals scored under Phase 1 use the SAME /100 scale — direct comparison is valid again.
- The Confidence Card has 7 fields (Operational fit claims is the 7th) — HIGH requires 6 of 7, MEDIUM 4-5 of 7. *(Unchanged from Phase 2.0.)*
- Score cells in the PDF brief now show "/ 20" rather than "/ 25" — still 5 cells.
- Hero score on the brief reads "OPP / 100" — restored from "OPP / 125".
- Eyebrow tag "HOT TOP TIER" triggers at score ≥ 85 — restored from ≥ 106.
