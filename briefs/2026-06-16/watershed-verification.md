# Verification — Watershed → Mahindra Racing (FE) — additional option

**Date:** 2026-06-16  ·  **Score:** 70/100 (WARM)  ·  *Additional FE option (Electra remains the logged daily hero for 2026-06-16).*
**Gate:** `python3 engine/verify_brief.py watershed --net` → **0 blockers** (5 `cite_blocked` 403s). No fact-drift. 2 pages.

## Claim ledger
| Claim | Source | Status |
|---|---|---|
| **$1.8B** valuation (Series C 2024; $100M led by Greenoaks, w/ Sequoia, Kleiner) | ESG Dive · Trellis | VERIFIED |
| **$185M** raised | Tracxn | VERIFIED |
| Customers **Airbnb, FedEx, Walmart** (~1 gigaton tracked) | Trellis | VERIFIED |
| Verdantix-named category leader (2026) | watershed.com | VERIFIED |
| Co-founder & external-facing leader **Taylor Francis** (ex-Stripe) | LinkedIn / Trellis | VERIFIED — current (titled "Co-Founder," not asserting an unverified "CEO") |
| HQ **San Francisco, CA** | Tracxn | VERIFIED |
| Leadership ties to F1/FE/deal-structuring | founders checked | NONE FOUND — `leadership_ties: []` |

## Grid-fit / whitespace (the disciplined part)
- **Carbon is FE's most CONTESTED lane** — verified: **Envision** runs its net-zero
  claims on its own technology + **Earthly** (carbon removal); **Nissan** has **Coral**
  (ESG-AI). So the obvious "sustainability-flagship" homes are taken.
- **Recommended: Mahindra Racing** — `team_fit` returns **PRIME LANE**. EV-and-renewables
  conglomerate with net-zero commitments; carbon-software lane open (Umicore = battery
  materials, Renesas = chips, Tech Mahindra = broad IT). Distinct, ownable position.
- Claim is **team-level**, not grid-wide exclusivity (logged as a risk + counter).
- Panel shows Nissan OPEN only because `teams.json` doesn't encode Coral; I've stated the
  Nissan/Coral and Envision/Earthly occupancy honestly in the brief and recommend Mahindra.

## Why it's a substantive WARM (better fit than yesterday's Electra on workstream)
The product-to-need fit is unusually literal: FE is the first net-zero-certified motorsport,
teams face FIA + EU CSRD reporting, and Watershed measures/reports/cuts Scope 1/2/3 — so
`ops_fit` is a strong **15/20** (a real, deployable workstream). Held down by capacity
(mid-cap, value-tier: 14) and the contested category (brand_fit 15) → **70**.

## Honesty guardrails
- Decision-maker titled **"Co-Founder"** (verified), not an unverified CEO title.
- Value_to_team names concrete mechanics (Scope 1/2/3 measurement of freight/travel/energy/
  production, reduction levers, verified disclosures) — not a green logo.

The five WARN lines are `cite_blocked` HTTP 403s, not missing/contradicted facts.
