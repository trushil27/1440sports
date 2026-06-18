# Verification — batch: Cyera + 19–22 Jun 2026 signals

All records built on the recalibrated profile, verified live, gated (0 blockers), 2 pages each.
WARNs across these are `cite_blocked` 403s / intended future-year refs unless noted.

## Cyera → Cadillac F1 Team — 77/100 (HOT) · on-request (2026-06-16), NOT logged
- **APPROACHED** (in `data/approached.json`): this brief *supports the existing human-layer outreach*, not a cold pitch. Cyera's prospect record is now flagged `approached: true` → excluded from auto hero/decision selection (renderable on request only).
- $12B (Series G, Jun 2026, $600M); >$1.7B raised; "trust layer for enterprise AI" (DSPM/DLP/identity/behavioural). CEO Yotam Segev (ex-Unit 8200); **CMO Naveen Palavalli = decision-maker**; CTO/co-founder Tamar Bar-Ilan.
- Team: re-pointed off Williams (Keeper triggered an exclusivity blocker) to **Cadillac** — teams.json lists cybersecurity as explicitly open (greenfield); `team_fit` PRIME LANE. DSPM lane framed as distinct from endpoint/identity/network security already on the grid.

## Fri 19 Jun (F1): Cadence Design Systems → Cadillac — 79/100 (HOT)
- Just completed the **Hexagon Design & Engineering acquisition** (Feb 2026; MSC Nastran, Adams) → full multiphysics/CFD/structural stack — the literal toolchain F1 cars are designed with (REAL MODE-A, ops_fit 17). FY26 growth guidance raised ~17%; NVIDIA "Physical AI" partner; CEO Anirudh Devgan.
- Decision path: **SVP Marketing & BD Nimish Modi** → CEO Anirudh Devgan → System Design & Analysis (multiphysics) org.
- Cadillac greenfield = building CAE from zero (`team_fit` clean/PRIME). Not already_present.

## Sat 20 Jun (F1): Eaton → Aston Martin — 76/100 (HOT)
- Intelligent-power-management leader; **record FY25 revenue $27.4B (+10%)** on electrification + AI-data-centre power; focusing on core Electrical + Aerospace (spinning off eMobility). nVent electrical thread at scale, public.
- Real workstream: electrical backbone of Aston's new campus (factory, wind tunnel, simulator) + works power-unit programme + trackside; **electrical lane OPEN** at Aston (roster is compute/AI/data).
- Decision path: **CEO Paulo Ruiz** + Global Marketing & Comms Director Camie Hanily (brand owner). Not an F1 sponsor → not already_present.

## Sun 21 Jun: WEEKLY DECISION → PROCEED: Cohesity (82) · F1 · Cadillac
- Engine's raw pick was **Ramp again**, but Ramp is now flagged `approached` (in pipeline) and excluded from auto-selection (new gate, same logic as the JFrog hold). Next-best non-approached GO = **Cohesity (82)** — fully trust-complete record. Digest + GO brief in `briefs/2026-06-21/`.

## Mon 22 Jun (FE): GE Vernova → Porsche — 77/100 (HOT)
- ~**$303B** electrification/power pure-play GE **spun out in 2024** (~$38B rev; Q1'26 backlog +$13B QoQ; guidance raised) — the Versigent born-big-spinoff archetype at marquee scale, on-theme for electric racing.
- **Honestly MODE-B (ops_fit 13):** GE Vernova doesn't make race-car tech, so the team workstream is clean event/paddock power + microgrid + a verified sustainability story — real but off-car, scored accordingly (not inflated). Porsche (reigning FE champion) electrification lane OPEN.
- Decision path: **CCO Pablo Koziner** (partnership owner) → CEO Scott Strazik. Not in motorsport → not already_present.

## Engine change
Added an `approached` eligibility gate to `scoring.is_eligible_for_hero` (mirrors `hold`):
approached companies stay in the DB and are scored, but are excluded from auto hero/decision
selection and shown as "approached (human-layer pipeline)" in `--list`; still renderable via
`--force`. Flagged Ramp + Cyera.

## Scores cluster 76–79 (Cohesity GO 82) — matching the bar consistently, not escalating.
