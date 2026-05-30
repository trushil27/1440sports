---
name: daily-sponsorship-signal
description: >
  Run the 1440 Sports daily sponsorship-signal workflow end to end: pick the
  single hero prospect for today per the series cadence, verify its claims live,
  stamp the trust fields, render the brand-locked 2-page brief, and send or
  preview it. Use when the user says "run today's signal/brief", "pick today's
  hero", "do the daily 1440 run", "who's today's prospect", or wants to
  generate/verify/ship a sponsorship brief from this repo.
---

# Daily Sponsorship Signal (1440 Sports)

The engine emits **exactly one signal per day**. This skill drives that run with
the verification discipline that makes the output trustworthy enough to ship
unattended. Never skip the verification step — a wrong fact in a brief is the
one failure mode that loses the customer.

## 0. Orient
- Working dir: repo root (contains `engine/`, `data/`, `briefs/`).
- Cadence (`engine/cadence.py`): Mon–Wed → Formula E, Thu–Sat → Formula 1,
  Sun → weekly DECISION (single GO pick across both series).
- One hero per day, 5-day cooldown so picks rotate. Scoring is deterministic
  (5 pillars × /20 → /100); see `engine/methodology.md`.

## 1. See today's leaderboard (no side effects)
```bash
python3 engine/run_daily.py --list                 # today
python3 engine/run_daily.py --date YYYY-MM-DD --list
```
The top eligible prospect for today's series is the presumptive hero. Gated out:
wrong series, sub-3-year fit, already on a grid (incl. via parent), or
oversaturated (`est_inbound_pitches > 100`).

## 2. Verify the hero BEFORE rendering (the trust gate)
```bash
python3 engine/verify_brief.py <hero-id>           # add --net to check URLs resolve
```
Resolve findings by severity:
- **BLOCKER** → must fix in `data/prospects.json` before shipping. Includes:
  missing fields, generic decision-maker, no sources, an uncited `key_fact`,
  stale data on a shippable hero, or `exclusivity_overclaim` (the recommended
  team already has a product rival in the prospect's lane AND the copy claims
  category whitespace — narrow the claim or re-point the team).
- **WARN** → `never_verified` / `no_key_facts` / aging data / figure-not-restated.
  Clear them by doing step 3.

Then **live-verify every high-risk claim** (figures, named people, dates, the
team's current partner roster) against a primary source. Log it to
`briefs/<date>/<hero>-verification.md`, one line per claim →
`VERIFIED / CORRECTED / UNVERIFIED`. When a claim can't be confirmed, write the
weaker true sentence — do not ship the strong unverified one.

## 3. Stamp the trust fields on the hero (in `data/prospects.json`)
- `last_verified`: today's date, once facts are re-checked.
- `key_facts`: each load-bearing figure/person/date as `{fact, value, source}`,
  with `source` also present in `sources`.
- `fit_lane` / `fit_domain`: narrow lane + broad space so `engine/team_fit.py`
  can check the recommended team for conflicts. If it suggests a better team,
  confirm the pick is intentional.
Re-run `verify_brief.py <hero-id>` until clean (only INFO left).

## 4. Render + ship
```bash
python3 engine/run_daily.py --date YYYY-MM-DD            # render + send (if SMTP/Graph configured)
python3 engine/run_daily.py --date YYYY-MM-DD --no-email # render only (preview)
python3 engine/run_daily.py --date YYYY-MM-DD --batch    # render ALL eligible (reviewer pack, not a send)
```
Output lands in `briefs/<date>/` as PDF + HTML + MD. The PDF is brand-locked
(navy/gold, 1440 masthead) and **must be exactly 2 pages** — the generator errors
if it overflows. Email transport: SMTP (`engine/send_email.py`) or Microsoft
Graph (`engine/send_graph.py`); `--no-email` if neither is configured.

## 5. Commit
Commit the data edits + the day's `briefs/<date>/` folder with a message naming
the hero and score. Push to the working branch. Do **not** open a PR unless asked.

## Guardrails
- One signal/day — don't batch-send multiple briefs to the recipient.
- Truth over punch: a narrowed true claim beats a bold unverified one.
- Don't invent a decision-maker — a verified named individual, or the verified
  CEO with the vacancy noted. Never a generic title.
- The batch pack is for internal review only, never a customer send.
