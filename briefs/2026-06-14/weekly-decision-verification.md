# Verification — Weekly DECISION (week of 08 Jun 2026)

**Date:** 2026-06-14 (Sunday DECISION day)  ·  **GO: Ramp → Visa Cash App Racing Bulls** · 84/100 · HOT
**Gate:** `python3 engine/verify_brief.py ramp --net` → **0 blockers** (5 WARN, all `cite_blocked` 403s — re-verified live below). GO brief: **2 pages**.

## Hold applied (systemic fix)
JFrog (86) is the engine's raw #1 but has been on the **MD's standing hold since
2026-06-06**. Until now the engine re-surfaced it as the pick every single day. Fixed
properly: added a `hold` gate to `engine/scoring.py::is_eligible_for_hero` (held
prospects stay in the DB and are still scored, but are excluded from hero selection
**and** the weekly decision), tagged JFrog's record with `hold`, and made `--list`
print the reason. JFrog now shows under "Gated / parked → HOLD". Lift by removing the
field. With JFrog held, the true GO is **Ramp (84)**.

## GO live re-verification (≈10 days since last check)
| Claim | Source | Status |
|---|---|---|
| Valuation **$44B** (Series F, Jun 4 2026; $750M, led by ICONIQ/GIC/Ontario Teachers') | GIC newsroom · Bloomberg · TechCrunch · CNBC | VERIFIED live today |
| **$1B+ annualized revenue**, 70,000+ customers, FCF-positive | CNBC / company | VERIFIED live today |
| Up ~38% from **$32B** six months earlier | TechCrunch (Jul 2025 history) | VERIFIED |
| Acquired **Billhop** (UK/EU payments), Mar 2026; UK/EU launch this summer | PR Newswire / Ramp blog | VERIFIED |
| CEO & co-founder **Eric Glyman** | TechCrunch / company | VERIFIED — current |
| Leadership ties to F1/FE/deal-structuring | checked | NONE FOUND — `leadership_ties: []` |

## Ranked contenders (across both series)
1. **Ramp 84** F1 (Visa Cash App Racing Bulls) ← GO
2. Cohesity 82 F1 (Cadillac)
3. UiPath 80 F1 (McLaren)
4. Applied Intuition 77 F1 (Haas)
5. Quantinuum 76 F1 (Aston Martin)
6. AlphaSense 75 F1 (McLaren)

(FE bench this week — Wayve 74, Helion 73, Celonis 73, Cohere 73 — all sit just below
the F1 leaders; the GO is F1.)

## Why Ramp is the proceed call
Highest eligible score (84, HOT), inbound in the 50-100 sweet spot (~60), and a sharp
dual "why now": the just-closed **$44B** round (institutional brand-reckoning moment)
plus a **UK/EU launch this summer** that lines up with a home-market British GP
activation on Racing Bulls. Fully verified, no blockers, 2 pages.

All five WARN lines are `cite_blocked` (HTTP 403), not missing/contradicted facts.
