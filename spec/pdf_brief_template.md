# PDF Intelligence Brief Template *(Phase 2.1 recalibration — May 2026)*

The 1440Sports brand-format 2-page strategic memo. Phase 2.1 restores the /100 score scale (5 dimensions × /20 each, hero label "OPP / 100") and tightens vertical spacing between the score panel and THE CASE. The 5-cell Score Composition grid and "WHAT COULD RUN ON THE CAR" section introduced in Phase 2.0 are retained.

**Cumulative version history:**
- Phase 1 (May 2026): Navy + gold rebrand, real logo embedded, Lora + Poppins typography, /100 hero.
- Phase 2.0 (May 2026, superseded): "WHAT COULD RUN ON THE CAR" section added, Score Composition expanded 4 → 5 cells, hero label /125, OF threshold ≥18.
- **Phase 2.1 (May 2026, current): Hero label restored to "OPP / 100". Score cells display "/ 20" per dimension. HOT TOP TIER eyebrow trigger restored to score ≥ 85. "WHAT COULD RUN ON THE CAR" trigger restored to OF ≥ 14/20. Score-panel-to-CASE vertical gap tightened from ~34pt to ~16pt. Transparent RGBA logo replaces the prior PNG that had black background baked in.**

## When to Build a Brief

- User requests a PDF brief on a specific signal
- A signal scores 70+ on /100 scale and user wants to escalate to MD
- User wants to test the engine with a specific company
- Daily Top 3 surfaces a signal worth full-document treatment
- The production n8n workflow auto-builds one each weekday at 06:00

## Working Build Script Location

- **`assets/build_brief_template.py`** — Parameterised local builder. Phase 2.1 reflects /100 hero, /20 cells, tighter pre-CASE spacing.
- **`assets/1440_logo.png`** — Phase 2.1 *transparent RGBA* PNG, 4000×700, navy #191A48 + gold #D1AE7A strokes on transparent. Replaces prior version that shipped with a black background baked in.

## Brand Specification

(unchanged from Phase 1 — navy `#191A48`, gold `#D1AE7A`, ink `#0E0E10`, paper `#FBFAF7`, muted `#65656B`, soft `#C9B89A`, panel `#F4EFE5`. Lora + Poppins typography.)

## Page Setup

- A4, margins 22mm L/R, 30mm top, 22mm bottom
- Page chrome unchanged: logo masthead, single hairline 9mm below logo top, footer with company + date + page

## Layout Structure

### Page 1 — The Hook

```
[MASTHEAD — logo + confidentiality marker + black hairline]
INTELLIGENCE BRIEF / N° XXX [· ALUMNI INTELLIGENCE if Track 2] [· HOT TOP TIER if score ≥ 85]
Company Name (Lora 46pt navy)
Industry · Location · Date (Lora-Italic 12pt muted)
[1.5pt gold horizontal rule]
[DECK — 4-5 line italic Lora 15pt]
[SCORE ROW — three-column asymmetric: hero score left "OPP / 100", mini-stats right]
[8pt vertical breathing room — TIGHTENED from 22pt]
[hairline rule]
[6pt section header lead-in — TIGHTENED from 10pt]
THE CASE (gold caps section header)
[2 paragraphs Lora justified body]
[WHY NOW timing callout — beige panel + gold left bar]
[PAGE BREAK]
```

**Phase 2.1 hero score:** the big hero number reads `XX` with label "OPPORTUNITY / 100" beneath. The HOT TOP TIER eyebrow tag fires at score ≥ 85.

**Phase 2.1 spacing change:** the gap between the score panel and THE CASE section header is now ~16pt total (Spacer 8 + hairline + section_h spaceBefore 6), down from ~34pt. The intent is the score panel pulls into THE CASE more tightly — closes a layout dead zone that read as accidental whitespace under Phase 2.0.

### Page 2 — The Argument

```
[MASTHEAD]

WHY [TEAM/SERIES] (gold caps section header)
[1 paragraph, 5-6 lines]

WHAT COULD RUN ON THE CAR  ←─── conditional on OF ≥ 14/20
(gold caps section header)
[1-2 paragraphs, 4-6 lines total. Names specific team need from 
team_needs_taxonomy.md, names specific activation. Inline bold 
emphasis on the team's operational need and the specific 
deployment surface.]

DEAL ARCHITECTURE
[1 paragraph, 4-5 lines, includes inline bold deal-term labels]

[TWO COLUMN LAYOUT — vertical hairline divider]
PRIMARY DECISION-MAKER     |  OPENING ANGLE
[Person Name Lora 22pt navy]|  [Strategic framing 9.5pt]
[Role Poppins 9pt muted]   |
[Bio paragraph 9.5pt — 3-4 lines]
                          |  [Hook quote — Lora-Italic 10.5pt
                          |   ~4 lines]

SCORE COMPOSITION
[Five-column beige panel grid]
[TIMING / CAPACITY / BRAND / URGENCY / OPS-FIT]
[Each column: label small caps muted, big serif number 20pt navy,
"/ 20" in soft gold tint, explanation 8.5pt]

RISKS
[2 paragraphs, each starts with INLINE BOLD CAPS LABEL]

[FOOTER]
```

## Section Content Boundaries *(Phase 2.1 — added 21 May 2026)*

Every brief has exactly **one team-specific narrative claim** — the single sentence explaining why this team and only this team is the answer (e.g. "Aston Martin is the only team on the grid where the data-infrastructure narrative is being publicly built", "Alpine is the only French-headquartered F1 team and only team whose commercial narrative is aligned with European industrial sovereignty"). This claim lives in **WHY [TEAM] and only WHY [TEAM]**.

The most common writer failure mode is to leak that claim into the deck because it sounds like the punchline. The deck is not the punchline — it sets up the *company-side* opportunity. The team-fit punchline belongs on page 2.

| Section | What it covers | What it does NOT cover |
| --- | --- | --- |
| **deck** (italic, ≤50 words) | Company-side opportunity thesis: what just changed for the company, why this is the brand-reckoning moment. The team is named only as a destination, never argued for. | Team-specific narrative claims. Why-this-team logic. |
| **the_case_p1** (≤95 words) | Trigger event + financial context + one BRAND RECKONING bold-uppercase phrase. | Team-fit logic. |
| **the_case_p2** (≤75 words) | Competitive landscape — who's already in F1/FE, what's open, what conflict logic excludes which teams. | The recommended team's specific narrative fit. |
| **why_now_callout** (≤55 words) | Calendar/event anchor for WHY NOW. | The trigger from p1; the team-fit from why_team_para. |
| **why_team_para** (≤85 words) | THE ONLY place the team-specific narrative claim appears. State it sharply, once, here. | Trigger; landscape; deadline; deal commercials. |
| **operational_fit_content** (≤70 words) | What the product physically does on the car / in the factory / on the broadcast feed. | Narrative team-fit; deal commercials. |
| **deal_arch_para** (≤70 words) | Years, $/yr, tier, race-by-race or city anchors. | Narrative; operational claims. |

**Anti-duplication self-check (mandatory before submission):** Identify the single team-specific narrative claim. Then read deck → the_case_p1 → the_case_p2 → why_now_callout in order. If any of them contains that claim — verbatim, paraphrased, or merely the same idea reworded — rewrite to remove it. The deck failing this check is the most frequent error; if your deck reads like a WHY [TEAM] sentence, rewrite it to be 100% company-side.

**Worked example — Datadog N°011 (May 2026) duplication and fix:**

*Before (duplicated):* Deck contained "...the slot that matches Datadog architecturally is open at Aston Martin, where the data-infrastructure narrative is already being built." WHY ASTON MARTIN then opened with "Aston Martin Aramco is the only team on the grid where the data-infrastructure narrative is being publicly built rather than already owned." — same claim, twice.

*After (clean):* Deck reads "An observability category-leader has just crossed its first $1B revenue quarter. The brand-reckoning moment has arrived, two direct competitors are already on the F1 grid, and the architecturally correct slot is open." The team name moves down to the score row (which already carries it as the RECOMMENDED TEAM mini-cell); the narrative claim is held back to WHY ASTON MARTIN where it has space to land properly.

## What Could Run On The Car — Section Specification

Positioned on Page 2, between WHY [TEAM/SERIES] and DEAL ARCHITECTURE.

**Header:** "WHAT COULD RUN ON THE CAR" — gold caps Poppins-Bold 8.5pt, exactly like other section headers. The deliberately operational verb "RUN" — this section is about embedded deployment, not brand activation.

**Body:** 1-2 paragraphs Lora 10pt justified, same body style as THE CASE and DEAL ARCHITECTURE. Maximum 6 lines combined.

**Required content elements:**
1. **Named operational need** — pulls from `team_needs_taxonomy.md`. Examples: "race-strategy decision support" / "telemetry observability" / "battery cell-health analytics" / "carbon accounting".
2. **Named team and named surface** — exactly where in the team's operations the product would deploy. Examples: "Alpine's pit-wall strategy stack" / "Mahindra Racing's battery-monitoring loop" / "McLaren's engineering data lake".
3. **Inline bold emphasis** on the specific operational benefit, format: `<font name='Poppins-Bold' size='9.5'>UPPERCASE PHRASE</font>`. Examples: PIT-WALL DECISION TIME / TELEMETRY LATENCY / CELL-LEVEL VISIBILITY / RACE-WEEKEND UPTIME / FACTORY-TO-TRACK SYNC.
4. **Specific activation** — what becomes visible during race weekends: "data feed visible on broadcast strategy graphics" / "logo placement on engineer headsets" / "co-branded factory telemetry wall".

**What this section is NOT:**
- It is not a feature list — reads like a sales deck and breaks the strategic-memo tone.
- It is not vague ("our partner brings cutting-edge AI") — must be specific to a named operational need.
- It is not generic ("perfect fit for motorsport") — must be specific to a named team's specific stack.

**When this section appears *(Phase 2.1 thresholds)*:**
- If Operational Fit ≥ 14/20 → section is **mandatory**.
- If Operational Fit 8-13/20 → section is **optional**, included only on user request.
- If Operational Fit < 8/20 → section is **omitted entirely**, no placeholder.

This conditional inclusion is implemented in the builder via the `operational_fit_section` boolean field in `BRIEF_DATA`.

## Score Composition Grid

Five cells, each ~33.2mm wide on the 166mm usable width.

**Layout:**

```
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│ TIMING  │CAPACITY │ BRAND   │URGENCY  │OPS FIT  │ (Poppins-Med 7.5pt muted)
│         │         │ FIT     │         │         │
│  18     │  16     │  15     │  17     │  17     │ (Lora 20pt navy + /20 soft gold)
│  / 20   │  / 20   │  / 20   │  / 20   │  / 20   │
│         │         │         │         │         │
│ [note]  │ [note]  │ [note]  │ [note]  │ [note]  │ (Lora 8.5pt ink, ~3 lines)
└─────────┴─────────┴─────────┴─────────┴─────────┘
```

Phase 2.1 callers populate the `score_cells` field in `BRIEF_DATA` with 5 tuples, each `(label, num, "/ 20", note)`. Notes are 8 words maximum.

## Score Tier Implications for Brief Generation *(Phase 2.1)*

| Score | Tier | Brief generation |
|---|---|---|
| 85+ | HOT TOP TIER | Auto-generated; eyebrow gains "· HOT TOP TIER"; daily auto-brief candidate |
| 70-84 | HOT | Generated on user request; standard HOT signal |
| 55-69 | WARM | Generated on user request; WARM signal |
| 40-54 | VERIFY | Brief held until VERIFY tier complications resolved |
| <40 | PLANT/DISCARD | No brief — digest entry only |

## Confidence-Card-Gated Generation

Brief generation is gated by the V2.1 Confidence Card (still 7 fields under Phase 2.1):
- **HIGH** confidence (6+/7 fields ✅) → brief generates normally
- **MEDIUM** confidence (4-5/7 fields ✅, no ❌) → brief generates with a discreet "VERIFY BEFORE CIRCULATION" stamp in the footer left, replacing "1440 SPORTS · LONDON" with "1440 SPORTS · LONDON · VERIFY BEFORE CIRCULATION"
- **LOW** confidence → brief does not generate; engine returns to user with the unverified field list

## Copy Style Guide

### What Could Run On The Car — copy guidance

The voice for this section is **technical-strategic, not technical-sales**. The reader is an MD looking at a sponsorship deal; they need to see that the operational integration is real enough to justify the deal premium without being so technical that it reads as a product brochure.

**Good examples:**
- *"Datadog's observability stack maps directly to Aston Martin's data-engineering buildout under CoreWeave. The team has just moved its race-weekend data lake to a CoreWeave/AWS hybrid; a single observability layer across both clouds would give CoreWeave's compute the **PIT-WALL VISIBILITY** the team currently lacks. Deployment surface: engineer headsets, broadcast strategy graphics, the team's factory telemetry wall."*
- *"Watershed's emissions accounting fits Mahindra Racing's structural problem: a Stellantis-adjacent OEM brand needs CSRD-grade reporting before the 2027 deadline, and Formula E is the most credible **PUBLIC LEDGER** for an EV-maker's lifecycle emissions story. Activation: lifecycle accounting visible in fan-facing dashboards on race weekends; live carbon receipt for every kWh used at the trackside."*

**Bad examples (do not write like this):**
- *"Our AI is best-in-class and would be a perfect fit for any F1 team."* — vague, no named need, no named team.
- *"We provide enterprise-grade observability with industry-leading SLAs."* — product-deck voice, no strategic frame.
- *"The opportunity is significant and the synergies are compelling."* — empty consultancy-speak.

### Inline Bold Emphasis

- Tech-into-operations: PIT-WALL DECISION TIME / TELEMETRY LATENCY / DATA-LAKE LATENCY / RACE-WEEKEND UPTIME / FACTORY-TO-TRACK SYNC / CELL-LEVEL VISIBILITY / PUBLIC LEDGER
- Demonstrability: BROADCAST DATA FEED / ENGINEER HEADSETS / LIVERY INTEGRATION / FAN-FACING DASHBOARD
- Lock-in: TWO-SEASON EMBED / SWITCHING COST / RENEWAL TRIGGER

Maximum 4 inline bolds across the document (counts across THE CASE, WHAT COULD RUN ON THE CAR, DEAL ARCHITECTURE, OPENING ANGLE, RISKS combined).

## Production Checklist *(Phase 2.1)*

Before delivering any brief:

- [ ] Page count is exactly 2
- [ ] Logo PNG is the transparent RGBA version (corners alpha=0); renders correctly in masthead on both pages
- [ ] Hero score reads **"OPPORTUNITY / 100"** (not "/ 125")
- [ ] Gap between score panel and THE CASE is ~16pt (not the prior 34pt)
- [ ] Score panel: hero number left in navy, two mini-stat columns right
- [ ] Score Composition grid is **5 cells, each "/ 20"** (not "/ 25")
- [ ] If Operational Fit ≥ 14/20: "WHAT COULD RUN ON THE CAR" section present
- [ ] If Operational Fit < 8/20: "WHAT COULD RUN ON THE CAR" section NOT present
- [ ] Decision-maker named, role correct, profile factually accurate, source confirmed
- [ ] Hook quote includes specific time ask
- [ ] Inline bold emphasis used (one phrase per major section, max 4 across the doc)
- [ ] Eyebrow tag includes "ALUMNI INTELLIGENCE" suffix if Track 2
- [ ] Eyebrow tag includes "HOT TOP TIER" if score ≥ 85
- [ ] Risks section: 2 paragraphs each starting with inline bold label
- [ ] If Confidence is MEDIUM: footer reads "1440 SPORTS · LONDON · VERIFY BEFORE CIRCULATION"
- [ ] Save to `/mnt/user-data/outputs/1440_Intelligence_Brief_[CompanyName].pdf`
- [ ] Use `present_files` tool to deliver

## Integration with the n8n Production Workflow

The Railway-deployed builder service (`builder.py`) and the local `build_brief_template.py` are kept in lockstep. Phase 2.1 changes to BOTH:

1. Hero label: `"OPPORTUNITY  /  125"` → `"OPPORTUNITY  /  100"`
2. Score cells iterate `(label, num, denom, note)` where `denom` is now `"/ 20"`
3. `Spacer(1, 22)` between score row and the post-score hairline becomes `Spacer(1, 8)`
4. `section_h` style: `spaceBefore=10` → `spaceBefore=6` *(applies to all gold caps section headers)*
5. `hot_top_tier` boolean triggers at score ≥ 85 (caller responsibility)
6. `operational_fit_section` boolean triggers at OF ≥ 14/20 (caller responsibility)
7. Logo file replaced with transparent RGBA PNG (drop-in; same `LOGO_PATH`)

n8n prompt nodes also need updating — exact replacements per node are in `n8n_v21_prompts.md`.
