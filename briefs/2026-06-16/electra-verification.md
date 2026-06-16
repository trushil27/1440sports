# Verification — Electra → Nissan Formula E (FE)

**Date:** 2026-06-16 (Tue, Formula E day)  ·  **Hero:** Electra  ·  **Score:** 68/100 (WARM)
**Gate:** `python3 engine/verify_brief.py electra --net` → **0 blockers** (6 WARN: 5
`cite_blocked` 403s + 1 intended "2030" expansion-target reference). No fact-drift. 2 pages.

## Why this hero
The board's top FE picks (Kraken 79, Redwood 74, Mistral 74) are now in the pipeline,
and the other strong WARMs (Wayve/Celonis/Helion/Cohere) were all featured within the
last week. So I sourced a genuinely fresh name in the one on-message FE lane not yet
covered — **EV charging**.

## Claim ledger
| Claim | Source | Status |
|---|---|---|
| **>€1B** total secured capital | Sifted / Mobility Plaza | VERIFIED |
| **€304M** Series B (led by PGGM; EDF, Eurazeo, SNCF/574 Invest) | Sifted | VERIFIED |
| **€433M** debt syndicate (ING, MUFG, ABN AMRO, SocGen, Rabobank, Bpifrance) | Mobility Plaza | VERIFIED |
| "Approaching unicorn" (valuation not disclosed) | Sifted (CEO quote) | VERIFIED (sub-unicorn — reflected in capacity score) |
| Co-Founder & CEO **Aurélien de Meaux** | Sifted / Crunchbase | VERIFIED — current |
| Target **2,200** stations / 15,000 points, 9 countries by 2030 | FoundersToday | VERIFIED (plan) |
| HQ **Paris, France** | Crunchbase | VERIFIED |
| Leadership ties to F1/FE/deal-structuring | founder-CEO checked | NONE FOUND — `leadership_ties: []` |

## Grid-fit / whitespace
- **Recommended: Nissan Formula E** — `team_fit` **OPEN**. France-based team (French
  resonance for French Electra), EV-pioneer identity, explicitly open "EV tech" category.
  Per signals-not-placements, Mistral being aimed at Nissan in a *different* category (AI)
  does not occupy it.
- **ABB nuance (honest):** ABB is FE's *series-level* charging partner (it charges the
  race cars). Electra operates a *public/urban* charging network — a distinct category and
  a team-level brand play, not a race-car-charging claim. Stated plainly in the brief +
  logged as a risk with its counter.

## Honesty guardrails (this is a modest WARM, scored as such)
- `capacity` held at **14/20**: much of the >€1B is debt for capex (building stations) and
  the valuation is sub-unicorn → realistically a **value-tier** deal (~$1.5–2.5M/yr), not a
  marquee spend. `ops_fit` at **13** (brand/audience, not a technical workstream),
  `urgency` at **11** (no hard clock). Total **68** — a genuine but modest signal, not
  inflated.
- The single real edge is the **rare audience match** (FE fans = EV drivers = Electra's
  customers) — value_to_team names concrete activation mechanics (QR-to-charge fan offers,
  host-city hub activations, loyalty tie-ins as an acquisition channel), not a green logo.

The five `cite_blocked` WARNs are HTTP 403s; the "2030" WARN is the intended expansion target.
