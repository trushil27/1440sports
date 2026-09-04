# V2.2 — Track 2 Executive Alumni Intelligence *(Phase 2.1 recalibration — May 2026)*

The Track 2 layer that compounds with Track 1's V2.1. Alumni signals consistently outperform cold signals (historical: 74 average vs 65 average across 24 tested signals, all on /100). This is the engine's commercial differentiator.

**Phase 2.1 scoring scale:** V2.1 base scores are on /100 across 5 dimensions × /20 each (Timing, Capacity, Brand Fit, Urgency, Operational Fit). Alumni boost magnitudes are unchanged (+9 to +12 strict, +5 to +8 medium) and remain additive on top of the V2.1 base. Final scores are /100 and directly comparable to historical Phase 1 scores in `scoring_calibration.md`.

## Core Logic

```
1. Maintain database of executives who shaped F1/FE deals over past 7-15 years
2. Track each executive's current company through public sources
3. When alumnus moves to a new company:
   3a. Run new company through V2.1 (full Phase 2.1 logic, all 5 dimensions /20)
   3b. If V2.1 qualifies (Base score 55+/100) → apply alumni boost → surface signal
   3c. If V2.1 disqualifies → log alumni move, do not surface
4. Alumni boost is transparent and additive: "Final = V2.1 base /100 + Alumni boost"
```

**Critical: Alumni presence does NOT override commercial reality.** A strict-tier alumnus moving to a 50-person bootstrapped startup is logged for monitoring, not surfaced. Track 2 USES Track 1's gates, not bypasses them.

## Alumni Tier Definitions

### Strict Tier — Boost +9 to +12

The alumnus was directly responsible for an F1/FE deal at their previous employer. Specific qualifying evidence:

- **Quoted in announcement press release** as CEO, CMO, or other named decision-maker
- **CEO of company at time deal was signed** (regardless of whether quoted)
- **CMO who is documented in trade press as having led the activation**

Examples from our database:
- Genefa Murphy *(Udemy CMO during McLaren deal launch Nov 2023)* → JFrog *(Jan 2026)* — strict
- Pete Schlampp *(Workday CMO who signed McLaren deal March 2023)* → Luminary Cloud *(Aug 2024)* — strict
- Sarah Franklin *(Salesforce President & CMO during F1 deal + McLaren)* → Lattice *(Jan 2024)* — strict
- Brian Humphries *(Cognizant CEO who signed Aston Martin title deal 2021)* → Version 1 / CD&R — strict but complicated *(fired)*
- Gary Steele *(Splunk CEO during 4-year McLaren deal)* → Shield AI *(May 2025)* — strict but complicated *(defense ESG)*

### Medium Tier — Boost +5 to +8

VP-level or senior leadership in seat at the sponsoring company during the deal years, but not the named decision-maker. Evidence required:

- LinkedIn shows tenure overlapping deal years
- Public role suggests material involvement in marketing/commercial strategy
- Not named in press release, but role implies awareness

Example: Detlef Krause *(senior at Salesforce during F1 deal years, but not the named decision-maker — that was Sarah Franklin)* → DeepL CRO. Medium tier.

### Loose Tier — Excluded

Director-level or below who happened to work at the sponsoring company. Excluded entirely — generates too much noise.

## Alumni Boost Calculation

Three modifiers determine the actual boost size:

### Modifier 1 — Seniority at New Company

| Current Role | Multiplier |
|---|---|
| CEO / Founder | 1.0x (full boost) |
| CMO / President | 0.9x |
| CRO / VP-level | 0.7x |
| Other senior | 0.5x |

### Modifier 2 — Recency of Move

| Time in role | Multiplier |
|---|---|
| 0-3 months *(first-100-days window)* | 1.0x |
| 3-6 months | 0.95x |
| 6-12 months | 0.85x |
| 12-24 months | 0.7x |
| Beyond 24 months | 0.5x |

### Modifier 3 — Capacity of New Company

| New company stage | Effect |
|---|---|
| Public company / late-stage private with $5B+ valuation | Full boost |
| Mid-stage ($300M-$5B) | -2 boost adjustment |
| Early stage / pre-revenue | Suppress signal regardless of alumnus |

### Worked Examples *(Phase 2.1 — /100 scale)*

**JFrog / Genefa Murphy:**
- Strict tier base: +12
- New role: CMO (0.9x) → +10.8
- Time in role: 4 months (0.95x) → +10.3
- New company stage: Public ($5.4B mkt cap) → no adjustment
- **Final boost: +10 to +12** (rounded)
- *V2.1 base under Phase 2.1: 75/100 (4-dim Phase 1) + Operational Fit dimension. DevSecOps maps to taxonomy C2/C3; estimated OF 14-16/20. New V2.1 base estimate: 75 + OF contribution at margin ≈ 75-78/100 (the 4 original dims rescale 1:1 from /25 to /20 in tier band, so the historic 75 remains a fair anchor; OF adds where applicable). Final with alumni: 85-90/100 — HOT TOP TIER.*

**Luminary Cloud / Pete Schlampp:**
- Strict tier base: +12
- New role: CEO (1.0x) → +12
- Time in role: 18 months (0.7x) → +8.4
- New company stage: $380M valuation → -2 adjustment
- **Final boost: +6 to +8** (formula); +11 used historically with narrative override
- *V2.1 base under Phase 2.1: Physics AI maps directly to taxonomy A2/A3 (Vehicle Dynamics / CFD) — likely OF 17-19/20, the canonical OF-Gate-elevation case. Phase 1 base was 69/100; with OF added, estimate 80-83/100. Final with alumni override: ~91/100 — HOT TOP TIER.*

**Shield AI / Gary Steele:**
- Strict tier base: +12
- New role: CEO (1.0x) → +12
- Time in role: 12 months (0.85x) → +10.2
- New company stage: Defense unicorn (Series F+) → no capacity adjustment
- ESG/political complications → -3 special adjustment for defense in F1 context
- **Final boost: +7 to +8**

## Database Maintenance Workflow

### Monthly: Update Existing Entries

For each executive in `alumni_database.md`:
1. Verify still in stated current role via LinkedIn / company press
2. If moved → update entry, run new company through V2.1 (this triggers a fresh signal)
3. If still in seat → no action

### Quarterly: Add New F1/FE Sponsorship Deals

Search for major F1/FE sponsorship announcements from the past quarter:
- Identify named decision-makers from press releases
- Add as "in seat" entries — they only become signals when they move
- Note announcement date, deal type, deal duration

### Annually: Backfill Historical Deals

Once per year, dedicate session(s) to expanding historical coverage. Target year-by-year backfill of major deals.

## Track 2 Search Patterns

When actively searching for new alumni signals:

### Pattern 1: Forward search (executive name)
```
"[Executive Name]" [former employer] new role [year]
"[Executive Name]" left [former employer]
"[Executive Name]" CEO OR CMO joined [year]
```

### Pattern 2: Reverse search (former employer alumni)
```
former [Sponsor Company] CMO new appointment
former [Sponsor Company] CEO joined [year]
"ex-[Sponsor]" [executive role]
```

### Pattern 3: Industry-specific
```
"new CMO" appointed [year] enterprise software unicorn
"new CEO" announcement [year] [target industry]
```

## Required Output Format *(Phase 2.1 — /100 scale)*

When surfacing a Track 2 signal:

```
🕵️ EXECUTIVE INTENT (Track 2)
[Executive Take incorporating alumnus context]

Score: XX/100 | Timing: [HOT/WARM] | Fit: [...]
Confidence: [HIGH/MEDIUM/LOW]

WHY THIS LEADS TO A MEETING:
[Paragraph emphasising why the alumnus dimension makes this a 
warm relationship, not a cold pitch. Include shared work history 
with 1440Sports if applicable.]

[Standard V2.1 Phase 2.1 sections — including OPERATIONAL FIT block...]

📈 OPPORTUNITY SCORE: XX/100
Track 1 (V2.1) Base Score: XX
  - Timing:          X/20
  - Capacity:        X/20
  - Brand Fit:       X/20
  - Urgency:         X/20
  - Operational Fit: X/20 [GATE APPLIED/NOT APPLIED]

Track 2 Alumni Boost: +N
  - [Tier]: [Alumnus name] was [previous role] at [previous 
    employer] during [deal years]
  - [Modifier reasoning]

FINAL SCORE: XX/100 — [TIER]

[Standard contact intelligence with primary target = the alumnus]

[Recommended outreach angle should ALWAYS reference shared history 
or known commercial relationship. The opening hook leverages the 
warm connection.]
```

## Critical Rules

1. **Never claim a person is an alumnus without verification.** Both the previous employment AND the deal involvement must be confirmed via Tier 1 sources.

2. **Always verify the current role.** Before surfacing, check that the alumnus is in fact at the company you're scoring. Job changes happen fast.

3. **Show the alumni boost transparently in the score breakdown.** "Score 87/100 = V2.1 base 75 + Alumni boost 12 (Murphy strict tier)" — never hide the math.

4. **Don't double-count.** If someone is medium-tier alumnus AND the company already scores high on Track 1 fit, don't add additional unrelated bonuses. The +5 to +8 medium tier boost already factors in the indirect alumnus benefit.

5. **Override the formula only with explicit reasoning.** If a narrative match is so strong it justifies more than the formula provides, write the reasoning. Default to the formula otherwise.

6. **Alumni signals still apply Operational Fit Gate.** A strict-tier alumnus at a company where OF ≥ 14/20 but Brand Fit < 12/20 is still subject to the OF Gate — OF doesn't count toward Top 3 ranking, the signal goes to secondary tier. Alumni boost itself doesn't override the gate.
