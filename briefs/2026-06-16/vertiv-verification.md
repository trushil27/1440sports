# Verification — Vertiv → Cadillac F1 Team (F1) — recalibrated-profile signal

**Date:** 2026-06-16  ·  **Score:** 82/100 (HOT)  ·  *First signal under the recalibrated profile (electrification/power-backbone, public co's in scope). On-request F1 brief — not the logged FE daily hero.*
**Gate:** `python3 engine/verify_brief.py vertiv --net` → **0 blockers** (5 `cite_blocked` 403s). No fact-drift. 2 pages.

## Why Vertiv (mapping to the MD's approached-list pattern)
- **Electrification / power backbone** (the Versigent + nVent thread) — Vertiv IS power + thermal/cooling + critical infrastructure.
- **Public company, in scope** (the Five9/SLB/nVent lesson) — NYSE: VRT.
- **Capital + identity inflection** — peak of the AI-power supercycle (the budget + brand motive crest together).
- **Real motorsport workstream, not a halo** — powers/cools a team's compute (factory + trackside + edge).
- **Why now** — F1's 2026 ~50%-electric era + the sport's compute arms race.

## Claim ledger
| Claim | Source | Status |
|---|---|---|
| Q1'26 net sales **$2.65B** (+30%, 23% organic) | BigGo/earnings | VERIFIED |
| Backlog **$15.0B** (+109% YoY) | BigGo/earnings | VERIFIED |
| Stock **+102% YTD 2026** (AI-power demand) | BigGo | VERIFIED |
| CEO **Giordano Albertazzi** | SEC 8-K | VERIFIED — current |
| **ThermoKey** thermal-management acquisition completed 12 Jun 2026 | BigGo/company | VERIFIED |
| HQ **Westerville, OH** (NYSE: VRT) | vertiv.com | VERIFIED |
| Existing motorsport presence | checked | NONE FOUND — not `already_present` |
| Leadership ties to F1/FE/deal-structuring | CEO checked | NONE FOUND — `leadership_ties: []` |

## Grid-fit / whitespace
- **Recommended: Cadillac F1 Team** — `team_fit` returns **PRIME LANE** (greenfield 2026
  entrant, roster built from zero). Critical-power/cooling/infrastructure lane open: IFS = ERP,
  TWG = AI, Tenneco = powertrain — none is power/cooling. American champion ↔ American team.
- Panel also shows Williams TAKEN (data/storage + security) — correctly distinct from Vertiv's
  physical power/cooling layer; McLaren/Red Bull OPEN. Cadillac is the deliberate pick for the
  greenfield "build the backbone from day one" workstream.

## Honesty guardrails
- **Decision-maker = verified CEO Giordano Albertazzi**, with an explicit note to confirm the
  current CMO/brand lead before outreach — did NOT invent a marketing title.
- Score 82 is carried by **capacity (19)** and a **real workstream (ops_fit 16)** + peak
  **timing (17)** — `brand_fit` held at 16 (B2B-infra logic leans on the workstream), `urgency`
  14 (no single dated trigger). Not inflated.
- value_to_team names concrete mechanics (UPS/switchgear, precision cooling, trackside edge,
  factory data centre) — not a logo.

The five WARN lines are `cite_blocked` HTTP 403s, not missing/contradicted facts.
