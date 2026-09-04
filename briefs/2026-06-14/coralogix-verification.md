# Verification — Coralogix → Williams (F1) — on-request brief

**Date:** 2026-06-14 (on request — "check Coralogix")  ·  **Score:** 76/100 (HOT)
**Gate:** `python3 engine/verify_brief.py coralogix --net` → **0 blockers** (6 WARN, all
`cite_blocked` 403s — verified manually). No fact-drift. 2 pages. *Not logged as a
daily hero — today's signal was the weekly DECISION (Ramp); this is an ad-hoc run.*

## Claim ledger

| Claim | Source | Status |
|---|---|---|
| Valuation **$1.6B** (Series F, 3 Jun 2026; $200M, led by Advent + CPPIB; Greenfield, Brighton Park) | Calcalist/Ctech · SiliconANGLE · Globes | VERIFIED live (403 to bot; confirmed via search) |
| ARR run-rate **$150–200M** (~60% growth, CEO-stated) | SiliconANGLE / Ctech | VERIFIED (company-stated) |
| **$550M** total raised | coralogix.com | VERIFIED |
| **5,000+** customers (incl. IBM, Tradeweb, JFrog) | coralogix.com | VERIFIED |
| CEO & co-founder **Ariel Assaraf** | Crunchbase / company | VERIFIED — current |
| CMO **Brian Mullen** (brand, partner ecosystem, alliances) | Craft.co / company | VERIFIED — current; named as decision-maker |
| Leadership ties to F1/FE/deal-structuring | CEO + CMO checked | NONE FOUND — `leadership_ties: []` |

## Grid-fit / whitespace (the disciplined part)
- **McLaren → TAKEN:** Cisco is McLaren's security partner and **now owns Splunk's
  observability platform** — a direct rival locked there. Updated `data/teams.json`
  (added Cisco/Splunk, moved observability out of `open_categories`, added
  `competitor_locks`) so the engine's grid-fit panel now reads **McLaren TAKEN**.
- **Recommended: Williams** — `team_fit` returns **OPEN**. Williams' enterprise roster
  is storage (VAST Data), collaboration (Atlassian), AI (Anthropic) and security
  (Keeper) — verified via `teams.json` `competitor_locks` + web — but **no
  observability/APM brand**. Distinct, ownable lane; fits Williams' data-led
  "preferred testing ground for enterprise software" identity.

## Why this is a strong fresh signal
Fresh **funding catalyst** (Series F closed 11 days ago → live capital + brand
mandate), a real **MODE-A** deployment story (monitoring the team's telemetry/factory
software estate), a **sitting CMO** who owns alliances (fast path to yes), and a
**competitor counter-clock** (Splunk-via-Cisco already on the grid at McLaren →
urgency to claim the open observability position now). Capacity scored honestly at
15/20 — a $1.6B mid-cap funds a value-to-mid Official Observability Partner tier, not
title-level spend.

All six WARN lines are `cite_blocked` (HTTP 403), not missing/contradicted facts.
