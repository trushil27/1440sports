# Verification — Kraken (Octopus Energy spin-out) → Jaguar TCS Racing (FE) — on-request

**Date:** 2026-06-15 (additional FE prospect, on request)  ·  **Score:** 79/100 (HOT)
**Gate:** `python3 engine/verify_brief.py kraken --net` → **0 blockers** (6 WARN — 5 are
`cite_blocked` 403s, 1 is the intended "2030" GEN4-cycle reference). No fact-drift. 2 pages.
*Not logged as a daily hero — today's signal was Mistral AI; this is an additional run.*

## Claim ledger
| Claim | Source | Status |
|---|---|---|
| Spun out of Octopus Energy as independent co at **$8.65B** ($1B raise; D1 Capital, Fidelity, Durable, Ontario Teachers') | CNBC · ESG News · Sifted | VERIFIED |
| **70M+** utility accounts (EDF, E.ON, Tokyo Gas, Origin, Severn Trent) | ESG News / Kraken | VERIFIED |
| **$500M+** contracted annual revenue | ESG News | VERIFIED |
| Kraken Flex manages **2GW+** distributed assets (smart EV charging, VPP) | EV Infrastructure News | VERIFIED |
| IPO-track by mid-2026 | CNBC / TFN | REPORTED (intent, not filed — framed as "IPO-track") |
| CEO **Amir Orad** (appointed Aug 2024; ex-Sisense, NICE Actimize) | Octopus/Kraken press | VERIFIED — current |
| CFO **Tim Wan** (ex-Asana) | press | VERIFIED |
| Leadership ties to F1/FE/deal-structuring | CEO + CFO checked | NONE FOUND — `leadership_ties: []` |

## Grid-fit / whitespace
- **Recommended: Jaguar TCS Racing** — `team_fit` returns **OPEN**. Jaguar's locks are
  IT/data + title (TCS) and financial services (Chase); **no energy/grid-software /
  EV-charging partner**, so Kraken's lane is open. British team ↔ London-based Kraken.
  GEN4 commitment runs 2026-2030, supporting a full multi-year deal.
- Positioned precisely in the **energy/grid-software vertical** (distinct from TCS's
  broad IT role) to avoid a perception overlap — logged as a risk with its counter.

## Why it's a strong fresh signal
A genuine **spin-out catalyst** (independent $8.65B entity, $1B fresh raise) + **IPO
timing** (mid-2026 = brand-building motive now) + a **near-perfect FE category fit**
(clean-energy / smart-EV-charging / grid-flexibility tech for an all-electric series)
+ an **open lane** + a verified enterprise-software CEO. Scored 79 HOT.

## Honesty guardrails
- **IPO is "track/intent," not filed** — brief says "IPO-track," never states a filing.
- `ops_fit` held at **15/20**: Kraken Flex's EV-charging/VPP tech is a *credible*
  energy-data/sustainability workstream (team operations/facilities), explicitly **not**
  an in-car race-system — value_to_team names concrete mechanics, not a green logo.
- Kraken's parent context noted (Octopus founder Greg Jackson remains a stakeholder);
  Kraken is now independent, so not `already_present`.

The five `cite_blocked` WARNs are HTTP 403s; the "2030" WARN is the intended GEN4 cycle.
