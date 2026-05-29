# 1440 Sports — Sponsorship Signals Engine: Methodology (v2, Ramp-standard)

This is the human-readable spec behind `scoring.py`, `data/prospects.json`, and
`run_daily.py`. The output format matches the **Ramp Intelligence Brief (N° 025,
28 May 2026)** — the client's most recent branded standard.

---

## 1. Mandate (Ideal Customer Profile)

B2B companies that can be sold a **multi-year (minimum 3-year)** sponsorship /
activation / title-rights deal where activation involves at least one of:

- **Formula 1** (team or championship)
- **Formula E** (team or championship)
- **A Formula E paddock team**

A qualified prospect must have **at least one** of:

1. **B2B tech genuinely useful in the car or to the championship** (MODE A).
2. **A narrative fit** between the brand story and motorsport.
3. **Financial capacity but never entered F1/FE.**
4. **A sponsorship deal reaching its end** (re-evaluating spend).
5. **A "born-big" spin-off / overnight $1B+ unicorn** (highest priority).
6. **An executive-migration signal** — a dealmaker who secured an F1/FE deal
   moves to a new company; that company inherits the thesis.

---

## 2. MODE A vs MODE B (shown on every brief)

- **MODE A** — the tech belongs in the car or is used by the championship/team
  technically (e.g. AVEVA digital twin at Porsche; JFrog software supply chain;
  Oracle race compute). Earns "official technology partner" credibility.
- **MODE B** — the tech serves the team's **back-office / commercial operation**
  (e.g. Ramp corporate spend management — treasury, supplier settlement,
  partner onboarding). Still a real value exchange, just off-car.

MODE is not a score by itself, but a low Ops-Fit prospect should usually be
MODE B, and a strong Ops-Fit prospect MODE A.

---

## 3. Scoring model — Opportunity /100 (v2)

**FIVE pillars, each /20** (this replaces the older 4×/25 model, to match the
Ramp scorecard):

- **TIMING /20** — Is the window open right now? Leadership honeymoon, budget
  cycle, deal expiry, IPO/spin-off brand mandate, a hard calendar anchor.
- **CAPACITY /20** — Can they fund ≥ $3M/yr for ≥ 3 years comfortably?
- **BRAND FIT /20** — Does the brand belong on the grid (category whitespace to
  own, narrative bridge, competitor counter-narrative)?
- **URGENCY /20** — Is there a forcing function (competitor on a livery, an
  exclusivity clock, a closing leadership window, an IPO roadshow, a race date)?
- **OPS FIT /20** — How real is the value exchange to the team? MODE A in-car/
  championship use scores high; MODE B back-office use scores moderate; pure
  logo placement scores low.

`Opportunity = Timing + Capacity + Brand Fit + Urgency + Ops Fit` → 0–100.

Header tiers (`scoring.tier`): **≥85 HOT · TOP TIER**, **≥75 HOT**, **≥65 WARM**,
**≥50 DEVELOPING**, **<50 PARK**.

---

## 4. Gates (hard filters before a prospect can be hero)

A prospect is eligible only if ALL hold:

1. `status == "active"`.
2. **Not already present** — `already_present == false`. A company already on an
   F1/FE grid **directly or via a parent/subsidiary** is excluded. *(This is why
   Schneider Electric is excluded: it owns AVEVA, which is Porsche FE's Technology
   Partner since Nov 2025.)*
3. `series` ∈ {F1, FE, FE paddock}.
4. `min_deal_years >= 3`.
5. **Crowding gate** — `est_inbound_pitches <= 100`. The client does not want to
   be the 100th+ agency in an inbox. `>100` is auto-excluded (kept as a tracker
   record). The **50–100** band is the target sweet spot; `<50` is "early."

---

## 5. Hero selection (`run_daily.py`)

1. Load `data/prospects.json` + `data/teams.json`.
2. Recompute each Opportunity Score.
3. Apply the gates (section 4).
4. Rank by score; tie-break by (a) lower crowding, (b) HOT timing, (c) presence
   of `exec_migration`/`spinoff_unicorn`.
5. **Cooldown**: a prospect that was hero within the last `cooldown_days`
   (default 5) is pushed down so the daily brief stays fresh.
6. Render the **strictly 2-page** branded brief (HTML + PDF + Markdown) and email
   it. The PDF renderer **raises if the brief exceeds 2 pages** — overflow is a
   hard error, never shipped.

---

## 6. Provenance: seeded vs self-discovered

Every prospect carries `discovery: "seeded" | "self"`:

- **seeded** — given by the client (JFrog via the Genefa Murphy thread; SnapLogic;
  Ramp).
- **self** — surfaced by the engine's own research sweep (Cohesity, Snyk,
  Abnormal Security, 1Password, Quantinuum, Mistral, Isomorphic Labs, Sonatype,
  plus team-side signals like the Alpine/BWT title expiry and DS Penske's FE exit).

This makes it explicit which leads the engine found independently.

---

## 7. Team / category matching

`data/teams.json` holds the live F1 + FE sponsor inventory: title slots, taken
categories, open categories, and `competitor_locks`. The engine recommends a team
by avoiding categories a direct rival owns, preferring identity fit, surfacing
open title slots, and weaponising competitor-on-grid as a counter-narrative.

---

## 8. Daily refresh

`PROMPT_DAILY.md` is the research brief a scheduled Claude session runs each day:
refresh leadership moves, funding/IPO/spin-off events, sponsorship
announcements/expiries, and executive migrations; update the JSON; re-score;
ship the hero. Always cite sources and re-check `already_present` before scoring.
