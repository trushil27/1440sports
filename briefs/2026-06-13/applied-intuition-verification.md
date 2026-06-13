# Verification — Applied Intuition → Haas (F1)

**Date:** 2026-06-13  ·  **Hero:** Applied Intuition  ·  **Score:** 77/100 (HOT)
**Gate:** `python3 engine/verify_brief.py applied-intuition --net` → **0 blockers**
(5 WARN, all `cite_blocked` 403 bot-blocks — verified manually below). No fact-drift.

## Why this hero (the swap)
- **Abnormal Security** (today's first pick, 72) — MD feedback: "not a good one." Pulled.
- **Bridgestone** (MD suggestion) — **SCREEN-OUT, verified.** From the 2026-27 season
  Bridgestone is the **sole tire supplier for the entire Formula E grid** (4-season
  deal, replacing Hankook) — the deepest possible form of `already_present`; it also
  **lost the F1 tire tender to Pirelli**; and it's a ¥4.5T-revenue public incumbent,
  not the pre-IPO/born-big origination target the engine hunts. Not a sponsor we'd
  originate — it *is* the series' technical partner.
- Read "something else" as *real motorsport/engineering DNA, not more generic
  security SaaS* → sourced Applied Intuition.

## Claim ledger

| Claim | Source | Status |
|---|---|---|
| Valuation **$15B** (Series F, Jun 2025; $600M, BlackRock + Kleiner Perkins) | appliedintuition.com/press-releases/series-f | VERIFIED (403 to bot; confirmed via live search) |
| ARR **~$830M** (2025, ~2x YoY from ~$415M) | Sacra | REPORTED (analyst estimate — flagged as ~) |
| **$1.2B** raised to date | appliedintuition.com / Tracxn | VERIFIED |
| CEO & co-founder **Qasar Younis** (ex-Y Combinator COO) | Wikipedia / Crunchbase / Kettering Univ. | VERIFIED — current |
| Customers = **18 of the top 20 automakers** (Toyota, VW, GM, Porsche, Stellantis) | appliedintuition.com/blog/2025-year-in-review | VERIFIED (company-stated) |
| No public CMO → decision-maker routed to founder-CEO | exec listings | VERIFIED — gap noted in record |
| Leadership ties to F1/FE/deal-structuring | checked | NONE FOUND — `leadership_ties: []` (Younis ex-GM is early-career engineer, not a motorsport/deal tie) |

## Grid-fit / whitespace (the disciplined part)
- **Cadillac → ruled out:** signed **TWG AI as *exclusive* AI partner** (Feb 2026) + IFS
  official technology partner → AI/engineering-software lanes locked.
- **Williams → ruled out:** Atlassian (title + collaboration software), **Anthropic**
  (AI "thinking partner"), VAST Data, Keeper — *and* a brand-new in-house Driver-in-Loop
  simulator signed off end-2025 ($20M capex). No whitespace.
- **Recommended: Haas** — lean American team, roster is largely consumer/commercial
  brands → genuine open enterprise-technology whitespace; `team_fit.py` returns clean
  (no conflict / no exclusivity overclaim). The "physical AI / autonomy" lane is
  **distinct** from the generic-AI deals on the grid and currently unclaimed.

## Honesty guardrail
Scored **MODE B** deliberately: Applied Intuition is **not** an F1 race-simulation
vendor, so `ops_fit` is held at 13/20 and the brief positions value as
**brand + B2B audience + engineering/talent adjacency**, explicitly NOT a claim that
Haas runs Applied Intuition's simulator. Overclaiming a technical deployment is logged
as a risk with its counter.

## Render
- `briefs/2026-06-13/applied-intuition.{html,md,pdf}` — **2 pages** (within rule).

All five WARN lines are `cite_blocked` (HTTP 403 bot-protection), not missing or
contradicted facts. No high-risk claim is UNVERIFIED or CONTRADICTED.
