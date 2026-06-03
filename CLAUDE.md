# CLAUDE.md — 1440 Sports Origination Engine

> **Read this first.** It orients a fresh session: what this project is, where
> everything lives, the current state of play, and the operating rules. The
> **repo is the source of truth** — chat history is not saved, so this file and
> the committed artifacts are the durable memory.

## What this is

An internal **origination engine** for 1440 Sports (a motorsport sponsorship
agency). It finds B2B / pre-IPO companies ripe for a **multi-year (min. 3-yr)
sponsorship** in **Formula 1 / Formula E**, scores each on a 5-pillar model,
matches it to the right team (catching category clashes), **fact-verifies every
load-bearing claim against a live source**, and renders a brand-locked **2-page
intelligence brief**. Audience: the MD (Ricky Paugh) and partners. Internal tool
for now — **not** a customer-facing SaaS app (decided deliberately; see below).

The scarce, defensible thing is the **judgment + verification layer**, not the
information. Lead with "who to call, why now, which team" — never a research dump.

## Repo map

| Path | What |
|---|---|
| `data/prospects.json` | The prospect database + scores + trust fields. The engine's memory. |
| `data/catalysts.json` | **Catalyst radar** — the born-big / overnight-$1B+-unicorn watchlist (spin-off/merger/acquisition). Detection inbox; promote events into `prospects.json`. |
| `engine/scoring.py` | 5-pillar /100 model, ranking, cooldown, catalyst-freshness boost. |
| `engine/catalysts.py` | Loads the catalyst radar + freshness; `python3 engine/catalysts.py [--open]`. |
| `engine/team_fit.py` | Matches prospect→team; flags category conflicts/crowding (fit_lane vs fit_domain). |
| `engine/verify_brief.py` | **The trust gate** — required fields, claim-level citations, fact-drift, staleness, team-fit overclaim. BLOCKER stops a send. |
| `engine/generate_brief.py` | Renders the 2-page brief (HTML+PDF+MD) via WeasyPrint + `templates/brief.html.j2`. |
| `engine/run_daily.py` | Picks today's hero on the weekly cadence, verifies, renders, logs to history. |
| `engine/cadence.py` | Weekly rota: Mon–Wed FE, Thu–Sat F1, Sun decision day. |
| `engine/methodology.md` | Full scoring methodology. |
| `briefs/<date>/<id>.{pdf,html,md}` | **Generated signals.** All rendered briefs live here. |
| `briefs/history.json` | **Signals log** — which hero was picked when; `last_hero` drives rotation cooldown. |
| `pitch/` | MD pitch deck + the Glean deep-dive dossier (showcase artifacts). |
| `brand/assets/` | Logos (navy/gold). Brand: navy `#191a48`, gold `#d1ae7a`, Georgia serif. |
| `README.md`, `STRATEGY_ASSESSMENT.md`, `PROMPT_DAILY.md` | Project overview, business case, the scheduled daily-run prompt. |

## Current state of play (as of 2026-05-30)

- **Branch:** `claude/confident-cray-Q9sAc` → **open as PR #1** (github.com/trushil27/1440sports/pull/1). Push to this branch to update the PR; do **not** open a new one.
- **Two worked proof heroes** (both verified, 0 blockers, 2 pages, logged in `history.json`):
  - **Cohesity → Cadillac F1 Team** (82/100, HOT) — F1 proof. `briefs/2026-05-29/cohesity.*`
  - **Glean → Mahindra Racing** (72/100, WARM) — FE proof. `briefs/2026-05-30/glean.*`
- **MD pitch deck:** `pitch/1440-origination-desk.pdf` (built by `pitch/build_deck.py`) — pitches the engine to Ricky as a funded "origination desk." Ask = role + budget + performance kicker.
- **Deep-dive dossier (gated Tier-2 showcase):** `pitch/glean-deepdive.pdf` (built by `pitch/glean_dossier.py`) — full company breakdown, leadership/decision path, financials, competitive-moat analysis, FE fit, with every claim confidence-tagged (VERIFIED/REPORTED/GAP/ESTIMATE) + source ledger.
- **11 scored prospects** live in `data/prospects.json` (Ramp 87, JFrog 86, Cohesity 82, Quantinuum 76, 1Password 72, Glean 72, Plaid 71, + more). Only Cohesity and Glean carry the **full** trust-field standard (key_facts, fit_lane/domain, thesis, last_verified); the others are lighter.

## The two-tier product

1. **The 2-page brief** (the daily signal): should we move, why now, which team, opening angle. The thing Ricky loves.
2. **The deep-dive dossier** (gated, on request only): everything to walk into the meeting — leadership, financials-where-they-exist, moat, deal architecture.

## Operating rules (non-negotiable)

- **Re-verify, don't recall.** Before shipping any fact, check it live against a primary source. Never trust memory or prose fluency for a number/name/date.
- **Tag confidence.** VERIFIED = primary source · REPORTED = credible secondary · GAP/ESTIMATE = explicitly not confirmed. If you can't source it, say so — never invent (e.g. the dossier flags that Glean has no public CFO rather than guessing one).
- **The verification gate must pass.** Run `python3 engine/verify_brief.py <id> --net` before shipping. 0 blockers on shippable briefs.
- **Briefs are strictly 2 pages.** The renderer errors on overflow. Trim copy in `prospects.json`, don't loosen the rule.
- **Brand is locked** to navy/gold/Georgia + 1440 masthead.

## Common commands

```bash
python3 engine/run_daily.py --date YYYY-MM-DD --no-email          # today's hero on cadence
python3 engine/run_daily.py --force <id> --no-email               # force a specific prospect
python3 engine/verify_brief.py <id> --net                         # trust gate (live citation check)
python3 pitch/build_deck.py                                       # rebuild MD deck
python3 pitch/glean_dossier.py                                    # rebuild Glean dossier
```

## Next steps / open TODOs

- **Outcomes loop (the moat, not yet built):** extend `history.json` to track brief → sent? → meeting? → deal. Cheap, in-repo, no UI. Start logging early so the proprietary "which signals convert" dataset compounds. **Highest-leverage next build.**
- **Catalyst radar (live):** the born-big/overnight-unicorn signal is now systematised — `data/catalysts.json` + `engine/catalysts.py`, with a freshness boost in scoring and a daily-scan step in `PROMPT_DAILY.md` (methodology §9). **Versigent** (Aptiv spin-off, ~$17B EV-electrical) sits on the radar awaiting triage — would it sponsor, and is it `already_present` via Aptiv? Run `python3 engine/catalysts.py --open`.
- **On request:** when the MD names a company, run it through the engine → verified 2-page brief, + deep-dive dossier only if asked.
- **Watching PR #1:** can subscribe to CI/review events if asked.
- Deep-dive infra is currently per-company scripts (`pitch/glean_dossier.py`); generalize into the engine only once demand justifies it (sequencing: prove value before building infra).

## Known quirks

- Brief numbering reset between earlier sessions; `history.json` was reconstructed 2026-05-30 to restore Cohesity (001) and Glean (002) in date order.
- This is Claude Code on the web: ephemeral container, fresh clone each session. **Commit + push anything worth keeping** — `git push -u origin claude/confident-cray-Q9sAc`.
