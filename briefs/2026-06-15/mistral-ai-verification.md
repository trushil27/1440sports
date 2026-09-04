# Verification — Mistral AI → Nissan Formula E (FE)

**Date:** 2026-06-15 (Mon, Formula E day)  ·  **Hero:** Mistral AI  ·  **Score:** 74/100 (WARM)
**Gate:** `python3 engine/verify_brief.py mistral-ai --net` → **0 blockers** (6 WARN, all
`cite_blocked` 403s — verified manually). No fact-drift. 2 pages.

## Why this hero
Engine's presumptive FE pick was **Wayve (74)** — but Wayve was the hero just 5 days
ago (6/10) and only cleared its 5-day cooldown today. Per the user's clear preference
for fresh signals, picked the strongest **never-featured** FE name: Mistral AI (74).
Its record was a "lighter" one (no `last_verified`, no trust fields, `leadership_ties`
unassessed, decision-maker title wrong) — so it got a full re-verification + rebuild.

## Corrections made (lighter-record cleanup)
- **Decision-maker title:** record said "Jon Bock, Head of Marketing." Verified Jon Bock
  is real and **SVP of Marketing** at Mistral (joined 2024; ex-Snowflake/NetApp/VMware) →
  title corrected; CEO **Arthur Mensch** named as co-decision-maker/escalation.
- **Valuation:** "multi-billion EUR" → **€11.7B confirmed (Series C, Sep 2025)**, plus
  **reportedly raising ~€3B at ~€20B** (Bloomberg, Jun 12 2026) and **$830M debt** (Mar 2026).
- Stamped `last_verified`, `fit_lane`/`fit_domain`, `key_facts` (6), `thesis`,
  `leadership_ties: []`; re-scored 72 → **74** to reflect the live raise.

## Claim ledger
| Claim | Source | Status |
|---|---|---|
| **€11.7B** valuation (Series C, Sep 2025) | TechCrunch (Jun 2026) | VERIFIED |
| Reportedly raising **~€3B at ~€20B** (Bloomberg) | TechCrunch / IndexBox | REPORTED — framed as "in talks / reportedly", not closed |
| **$830M** debt round (Mar 2026, data centres) | Tracxn | VERIFIED |
| CEO & co-founder **Arthur Mensch** (ex-DeepMind) | TechCrunch / multiple | VERIFIED — current |
| **Jon Bock**, SVP Marketing (decision-maker) | TheOrg / LinkedIn | VERIFIED — current |
| HQ **Paris, France** | multiple | VERIFIED |
| Leadership ties to F1/FE/deal-structuring | CEO + SVP Marketing + founders checked | NONE FOUND — `leadership_ties: []` |

## Grid-fit / whitespace
- **Recommended: Nissan Formula E** — `team_fit` returns **OPEN**. Nissan's FE partners
  are powertrain (Alpine Tech), hardware (Marelli) and ESG/carbon-AI (Coral) — **no
  foundation-model / LLM partner**, so the team-level AI lane is open. Formula E's
  series-level AI deal (Infosys, Race Centre) is distinct from a team partnership —
  noted in the brief to avoid overclaiming "no AI anywhere."
- Team is **France-based** (Renault e.dams heritage) → genuine "French AI champion,
  European innovation" resonance.

## Honesty guardrails
- The **~€20B raise is REPORTED/in-talks**, not closed — the brief says "reportedly /
  in talks," never states it as done. The load-bearing valuation fact is the confirmed
  **€11.7B**.
- `ops_fit` held at **13/20**: AI for strategy/energy/fan content is a *credible*
  workstream, not a locked deployment — scored as MODE-A-leaning-B, value_to_team names
  concrete mechanics (energy/regen modelling, multilingual fan content, engineering copilot).

All six WARN lines are `cite_blocked` (HTTP 403), not missing/contradicted facts.
