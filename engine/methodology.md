# 1440 Sports — Sponsorship Signals Engine: Methodology

This document defines how the engine finds, scores, and ranks B2B prospects for
motorsport sponsorship deals, and how the daily "hero brief" is selected. It is
the human-readable spec behind `scoring.py`, `data/prospects.json`, and
`run_daily.py`.

---

## 1. Mandate (Ideal Customer Profile)

We hunt for B2B companies that can be sold a **multi-year (minimum 3-year)**
sponsorship / activation / title-rights deal where the activation involves at
least one of:

- **Formula 1** (team or championship)
- **Formula E** (team or championship)
- **A Formula E paddock team** (manufacturer or customer team)

A qualified prospect must have **at least one** of these characteristics:

1. **B2B tech that is genuinely useful in the car or to the championship** —
   the brand earns the right to be there (data, cloud, integration, security,
   simulation, connectivity, energy, materials, payments). e.g. *SnapLogic →
   agentic integration; JFrog → software supply chain security; Oracle → race
   strategy compute.*
2. **A narrative fit** between the B2B brand story and motorsport (precision,
   speed, trust, sustainability, engineering).
3. **Financial capacity but never entered F1/FE** — money is not the blocker,
   they simply have not been asked the right way yet.
4. **A sponsorship deal reaching its end** — they will be re-evaluating spend.
5. **A "born-big" spin-off / overnight unicorn** — a company that reaches a
   $1B+ valuation effectively overnight via spin-off, IPO, or mega-round, and
   suddenly has both budget and a brand-building mandate. *(Highest-priority
   class. e.g. DXC Technology, Quantinuum, Vertesia-class spin-outs.)*
6. **An executive-migration signal** — a senior leader who previously secured
   an F1/FE deal moves to a new company; that new company inherits the thesis.
   *(e.g. Genefa Murphy drove Udemy↔McLaren, then became CMO of JFrog → JFrog
   becomes a target.)*

---

## 2. Signal Taxonomy (the "flags")

Each prospect is tagged with one or more signal flags. Flags do not score
directly; they explain *why the prospect surfaced* and feed the sub-scores.

| Flag | Meaning | Primary scoring impact |
|---|---|---|
| `exec_migration` | A dealmaker exec moved to this company | Timing, Brand Fit |
| `spinoff_unicorn` | $1B+ overnight via spin-off / IPO / mega-round | Capacity, Timing |
| `never_entered` | Has capacity, no F1/FE history | Capacity, Brand Fit |
| `deal_expiring` | A current sponsorship is ending | Timing, Urgency |
| `new_leadership` | New CEO/CMO/President honeymoon window | Timing |
| `category_whitespace` | Their category is uncontested on the grid | Brand Fit |
| `competitor_on_grid` | A direct rival already sponsors a team | Urgency |
| `funding_event` | Recent raise / strong balance sheet | Capacity |

---

## 3. Scoring model — Opportunity Score /100

Mirrors the 1440 Intelligence Brief scorecard. Four pillars, each **/25**:

- **TIMING /25** — Is the window open *right now*? Leadership honeymoon, budget
  cycle, deal expiry, post-IPO/spin-off brand mandate. A stale prospect (no
  active window) is capped low here.
- **CAPACITY /25** — Can they fund ≥ $3M/yr for ≥ 3 years without strain?
  Driven by revenue/ARR, cash on balance sheet, funding, valuation.
- **BRAND FIT /25** — Does the tech belong in the car/championship, or is there
  a clean narrative bridge? Bonus for `category_whitespace` (they can *own* a
  category) and for `exec_migration` (a believer is already inside).
- **URGENCY /25** — Is there a forcing function? A competitor on a livery, an
  exclusivity clock, a closing leadership window, an IPO roadshow moment.

`Opportunity = Timing + Capacity + Brand Fit + Urgency`  → 0–100.

Bands: **80–100 HOT**, **65–79 WARM**, **50–64 DEVELOPING**, **<50 PARK**.

---

## 4. The "noise / crowding" filter (the 50–100 rule)

We do not want to be the 200th agency in an inbox. Each prospect carries an
estimated **inbound pitch crowding** (`est_inbound_pitches`):

- **`<50`** — *Early.* Best position. Small Timing bonus.
- **`50–100`** — *Sweet spot.* The deal is live enough to be real but not
  saturated. This is the target band the client asked for.
- **`>100`** — *Saturated.* Auto-deprioritised: the prospect is **excluded from
  hero selection** (kept in the tracker as `status: park` so we don't waste
  outreach effort competing with the noise).

This filter runs *after* scoring, as a gate on which prospect can become the
day's hero.

---

## 5. Hero selection (what `run_daily.py` does each day)

1. Load `data/prospects.json` and `data/teams.json`.
2. Recompute each prospect's Opportunity Score from its sub-scores.
3. **Gate**: keep only prospects where
   - `status == "active"`, and
   - `series` ∈ {F1, FE, FE paddock}, and
   - `min_deal_years >= 3` is feasible, and
   - `est_inbound_pitches <= 100`.
4. Rank by Opportunity Score; tie-break by (a) lower crowding, then (b) HOT
   timing window, then (c) presence of `exec_migration`/`spinoff_unicorn`.
5. The top prospect becomes **today's hero brief**. To avoid repeating the same
   company every day, a prospect that was hero within the last `N` days
   (`cooldown_days`, default 5) is skipped in favour of the next-ranked.
6. Render the 2-page brief (HTML + PDF + Markdown) and the email, then deliver.

---

## 6. Team / category matching

`data/teams.json` holds the live F1 + FE sponsor inventory: who has the title
slot, which categories are taken, and which are open. The engine recommends a
team by:

- avoiding categories already locked by a direct competitor on that team,
- preferring teams whose identity matches the prospect's narrative,
- surfacing **open title slots** (e.g. Porsche Formula E after TAG Heuer's exit)
  for title-rights-class prospects, and
- using *competitor-on-grid* as a counter-narrative weapon (pitch the rival
  team, as in the SnapLogic→McLaren/Aston-Martin case vs Confluent on Williams).

---

## 7. Daily refresh (keeping signals live)

The data files are the engine's memory. They should be refreshed by re-running
the research sweep (see `README.md` → "Refreshing the signal data"):

- leadership changes (new CMO/CEO/President),
- funding / IPO / spin-off events ($1B+ overnight),
- sponsorship announcements and expiries on the F1/FE grids,
- executive migrations from F1/FE-active companies.

New prospects are appended to `prospects.json`; changed signals update existing
records. The engine then re-scores and re-selects automatically.
