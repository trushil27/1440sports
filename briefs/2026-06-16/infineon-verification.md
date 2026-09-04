# Verification — Infineon Technologies → Jaguar TCS Racing (FE)

**Date:** 2026-06-16 (Tue, Formula E day)  ·  **Hero:** Infineon  ·  **Score:** 79/100 (HOT)
**Gate:** `python3 engine/verify_brief.py infineon --net` → **0 blockers** (7 `cite_blocked` 403s). No fact-drift. 2 pages.
Today's FE hero at the signal quality bar, built on the recalibrated electrical/electronics profile.

## Claim ledger
| Claim | Source | Status |
|---|---|---|
| Revenue **~$17.2B** TTM; FY26 guidance raised | companiesmarketcap / Infineon IR | VERIFIED |
| Market cap **~$120B** (Jun 2026) | companiesmarketcap | VERIFIED |
| **Jochen Hanebeck** — CEO & Chairman (contract extended Feb 2026) | Infineon management board | VERIFIED |
| **Andreas Urschitz** — CMO & Management Board (since 2022) → decision-maker | Infineon management board | VERIFIED |
| **Peter Schiefer** — President, Automotive Division (since 2016) → technical counterpart | Infineon CV | VERIFIED |
| SiC EV-inverter module (1300V, to 205°C) — HybridPACK Drive | semiconductor-today | VERIFIED |
| Existing motorsport presence | checked | NONE (Infineon Raceway naming ended 2012; not a current F1/FE sponsor) → not `already_present` |
| Leadership ties to F1/FE/deal-structuring | board checked | NONE FOUND — `leadership_ties: []` |

## Why this clears the bar (matched, not forced)
- **Profile-matched:** electrical/electronics deep-tech, public co — the nVent/Versigent electrical thread.
- **Inflection:** FY26 guidance raised on the AI + automotive up-cycle; SiC benchmarks → capital + brand motive aligned.
- **REAL workstream (not a halo):** FE powertrains are *manufacturer-developed*, so SiC is a genuine in-car choice — Infineon's SiC in Jaguar's traction inverter (the biggest lever on efficiency/thermal/regen). MODE-A, `ops_fit` 16.
- **Open lane on a deliberately-chosen team:** Jaguar is a works manufacturer; `team_fit` = OPEN (TCS = IT, Schaeffler = mechanical, Chase = finance — no power-semi).
- **Verified named decision PATH:** CMO Urschitz → CEO Hanebeck → Automotive President Schiefer (+ CFO Schneider).

## Disciplined screen-outs done first (the judgment IS the product)
- **Eaton:** its only FE-relevant segment (eMobility) is being *spun off* and is small/declining ($125M Q4, -15%); Eaton-core is an F1/data-electrical fit. Not a clean FE signal.
- **Porsche (team):** TDK (technology partner) + Synopsys (EDA) already occupy electronics/semiconductor.
- **Mahindra (team):** Renesas is its semiconductor partner.
- **onsemi:** held the FE SiC heritage (Mercedes-EQ) — team departed; lane reopened, but onsemi noted as the prior-incumbent context.

## Honesty guardrails
- 79 carried by capacity (18) + real workstream (16) + timing (16); `urgency` 13 (no dated trigger), `brand_fit` 16 (SiC has prior onsemi/FE association, so not pristine). Not inflated.
- Inverter-supply framed as the ownable *forward* co-engineering partnership, not a claim Infineon is already in the car.

All 7 WARN lines are `cite_blocked` HTTP 403s, not missing/contradicted facts.
