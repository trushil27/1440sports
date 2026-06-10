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
These fields make the brief trustworthy **and** fill page 1 — the template
auto-renders three page-1 panels when (and only when) the data is present, so
every hero should get the full set. The `cohesity` record is the worked example
to copy the shape from.

- `last_verified`: today's date, once facts are re-checked.
- `key_facts`: each load-bearing figure/person/date as `{fact, value, source}`,
  with `source` also present in `sources`. **The first 6 render as the page-1
  "Proof Points" grid** — so lead with the punchiest verified items (ARR, margin,
  valuation, key hire, HQ, a dated event). Each `value` must also appear in the
  prose or `verify_brief` flags `fact_drift`.
- `fit_lane` / `fit_domain`: narrow lane + broad space. These feed
  `engine/team_fit.py`, which checks the recommended team for conflicts **and
  powers the page-1 "Grid Fit" panel** (recommended → PRIME/OPEN, rivals →
  CROWDED/TAKEN with named incumbents). Keep `fit_domain` tight — drop over-broad
  tokens (e.g. a bare `data`) that match unrelated partners. Cohesity uses lane
  `[backup, recovery, ransomware, resilience]`, domain `[security, protection,
  storage, cyber]`. Sanity-check the panel before shipping:
  ```bash
  python3 -c "import sys;sys.path.insert(0,'engine');import json,generate_brief,scoring;p=[x for x in json.load(open('data/prospects.json'))['prospects'] if x['id']=='<hero-id>'][0];[print(r['label'],r['team'],'-',r['detail']) for r in generate_brief.build_gridfit(scoring.enrich(p))]"
  ```
  The recommended team should read PRIME or OPEN, not CROWDED. If it reads
  CROWDED, either the domain tokens are too broad (fix them) or the pick is
  genuinely contested (re-point the team).
- `thesis`: one or two crisp sentences (~30–40 words) — renders as the page-1
  "Bottom Line" bar. Pack in the money fact + why-now + why-this-team.

Re-run `verify_brief.py <hero-id>` until clean (only INFO left). All four panels
hide automatically if their data is missing, so a half-empty page 1 means a field
wasn't stamped — go back and add it.

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
- **`value_to_team` must be rich and specific — never vague or guessed.** Think
  hard about how the prospect is *actually* valuable to *that racing team*, and
  spell it out concretely: a real technical/operational workstream where one
  exists (race strategy, energy/simulation modelling, data, supply chain), the
  commercial/brand lift the team specifically gains, ecosystem access, content
  and talent. If the honest answer is "mostly a brand halo," still name the
  concrete halo mechanics — don't fall back on "brand association + hospitality."
  A thin `value_to_team` is a defect to fix, not an acceptable MODE-B default.
- **Never treat 1440's own prospect signals as occupying a team.** These briefs
  are signals; the human layer has not placed/closed them. Team fit and
  whitespace are judged ONLY against *real, verified* grid occupancy (actual
  sponsors in `data/teams.json`). Multiple prospects may recommend the same team
  — that is fine. Do not down-rank or re-point a team because another 1440
  prospect is aimed there.
- **Leadership-tie gate — check every prospect.** Research whether any senior
  leader was previously part of the F1/FE ecosystem or structured a sponsorship
  deal (CMO/CEO/President/CRO who built a prior team partnership, etc.). Record in
  `leadership_ties` (`[{name, role, tie, relevance, source}]`; set `[]` once
  checked and none found — never leave it unassessed). A confirmed tie is the
  warmest signal (a proven motorsport buyer pre-answers the B2B doubt), boosts
  ranking, and `verify_brief.py` surfaces it. JFrog (Genefa Murphy → Udemy–McLaren)
  is the worked example.
