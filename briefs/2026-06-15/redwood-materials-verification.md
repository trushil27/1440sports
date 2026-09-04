# Verification — Redwood Materials → Andretti (FE) — on-request

**Date:** 2026-06-15 (additional FE prospect, on request)  ·  **Score:** 74/100 (WARM)
**Gate:** `python3 engine/verify_brief.py redwood-materials --net` → **0 blockers**
(6 WARN: 5 `cite_blocked` 403s + 1 intended "2030" Gen4-cycle reference). No fact-drift.
2 pages. *Not logged as a daily hero — today's signal was Mistral AI.*

## Claim ledger
| Claim | Source | Status |
|---|---|---|
| **$6B+** valuation; **$425M Series E** (Jan 2026, led by Eclipse, with Alphabet/Google) | Bloomberg · Sacra · Tracxn | VERIFIED |
| **~$2B equity raised + $2B DOE loan** commitment | Sacra / Utility Dive | VERIFIED |
| Founder & CEO **JB Straubel** (Tesla co-founder & ex-CTO) | redwoodmaterials.com | VERIFIED — current |
| **Redwood Energy** second-life grid storage (profitable; Crusoe deployment) | Sacra | VERIFIED |
| HQ **Carson City, NV** | company | VERIFIED |
| Leadership ties to F1/FE/deal-structuring | founder-CEO checked | NONE FOUND — `leadership_ties: []` (Straubel's Tesla EV pedigree noted as color, not a motorsport tie) |

## Grid-fit / whitespace (the disciplined part)
- **Battery-materials is crowded grid-wide** — verified: **Umicore** partners Mahindra
  (battery materials + recycling, direct clash → Mahindra OUT); **Envision Racing's**
  parent (Envision AESC) makes EV cells (→ Envision OUT).
- **Recommended: Andretti** — `team_fit` returns **OPEN**. Its materials/recycling
  partner **NAGASE works in carbon-fibre/CFRP recycling — a distinct material stream**,
  not batteries; TWG AI holds AI, Porsche the powertrain. So the battery-circularity
  lane is open and complementary. American team ↔ American company; charter,
  sustainability-leading FE team; Gen4 commitment 2026-2030 supports a full deal.
- Claim is **team-level**, not grid-wide exclusivity (honest, given Umicore/Envision) —
  logged as a risk with its counter.
- `verify_brief` INFO suggested McLaren ranks higher on raw token-fit; Andretti is the
  **deliberate** pick (American/charter/sustainability identity + verified open battery
  lane) — noted, not a blocker.

## Honesty guardrails
- `ops_fit` held at **14/20**, `urgency` at **11/20**: Redwood is well-funded/private with
  no imminent IPO or competitor clock, and the fit is a circularity/sustainability +
  content workstream, **not** an in-car race system — value_to_team names concrete
  closed-loop mechanics, not a green logo. Score 74 (WARM) reflects this honestly.

The five `cite_blocked` WARNs are HTTP 403s; the "2030" WARN is the intended Gen4 cycle.
