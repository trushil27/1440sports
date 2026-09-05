# Fervo Energy → Andretti Formula E — verification log (N° 122, 5 Sep 2026)

The first **Formula E** case built to the Crusoe standard, and the first run of the pipeline's
**rebuild mode** (`Stages.rebuild=True`): the day already carried a live brief (N° 121 Crusoe), so
this case is stored with `historical=True` and its own number, the dedup rule was not applied to the
one company being rebuilt, and the app shows it as an engine row merged with the 13 May sweep entry.
Produced in-session (no `ANTHROPIC_API_KEY` in the sandbox) with Claude acting as scanner, verifier
and writer through the injectable stages; the calendar table, sponsor table, 13-rule audit and the
2-page render ran as code. Reproduce with `fervoenergy.session_run.py` against a migrated + seeded
database; `fervoenergy.run.json` is the case record `python -m intel.backfill --cases` imports.

**Sandbox limitation, stated plainly:** direct fetches of fervoenergy.com, ir.fervoenergy.com,
sec.gov, globenewswire.com, fortune.com, andrettiglobal.com, fiaformulae.com and racer.com were
blocked by the egress proxy. Each claim below was checked against the search summary of the primary
page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link.
The brief's confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## Why this signal, and what the sweep row got wrong

The 13 May sweep row said "$1.89B IPO … ~$7.65B fully diluted; shares opened ~30% up; 3.5× the
$2.86B Series E valuation". Re-verification: $1.89B is the 70M-share base deal; the 10-Q puts the
full raise at 80.5M shares and ~$2.2B gross; Fortune reported the open about 35% up and a market
value above $10B; the Series E valuation figure is a third-party estimate and is **not used**. The
fresh trigger is the 396 MW Google PPA of 1 Sep 2026, inside the 14-day Track-1 window.

## Ledger (17 of 17 claims verified: 15 load-bearing, 2 supporting figures on the app page)

| Claim | Status | Evidence |
|---|---|---|
| Tim Latimer, CEO & Co-Founder | VERIFIED | ir.fervoenergy.com management page (founded 2017 with CTO Jack Norbeck) |
| IPO 70,000,000 shares at $27; Nasdaq FRVO from 13 May 2026; $1.89B base | VERIFIED | Fervo pricing release (May 2026): upsized from 55,555,555; 10.5M greenshoe |
| 80,500,000 shares incl. greenshoe; ~$2.2B gross; closed 14 May | VERIFIED | Form 10-Q, quarter ended 30 Jun 2026 (sec.gov) |
| Opened ~35% up, market value above $10B; biggest clean-energy IPO | VERIFIED (reported) | Fortune, 14 May 2026 |
| Q2 2026 revenue $113,000; operating loss $28.7M; net loss $55.9M | VERIFIED | Q2 results release, 12 Aug 2026 (GlobeNewswire) |
| Cape Station GeoBlock 1 first power Q4 2026; GeoBlocks 2–3 early 2027; 1.1 GW by 2030 target | VERIFIED | Q2 results release |
| 396 MW, 15-year PPA with Google Energy; signed 26 Aug, announced 1 Sep; option to ~1 GW by Jun 2030; online 2028 | VERIFIED | Fervo release, 1 Sep 2026 (GlobeNewswire) |
| Market value ~$4.4–5.1B early Sep; +24.9% on 1 Sep | REPORTED | Stockopedia / Robinhood / TradingView quotes (market data, not company) |
| Series E $462M led by B Capital, Dec 2025; Google among investors | VERIFIED | Fervo Series E release |
| Cape Station Phase I 100 MW (2026), Phase II 400 MW (2028); Beaver County, Utah; permitted to 2 GW | VERIFIED (reported) | Canary Media; Fervo project-financing releases |
| HQ Houston, Texas | VERIFIED | Company boilerplate; Houston press |
| Sarah Jewett COO (10 Jun 2026) with communications, policy, strategy in remit | VERIFIED | Fervo release, 10 Jun 2026 (GlobeNewswire) |
| David Ulrey CFO (since 2021); no CMO exists | VERIFIED | ir.fervoenergy.com management page — **no marketing executive is listed; do not invent one** |
| Andretti: TWG AI primary partner / Official AI Partner; Quest Global, Crowe UK, Reflo | VERIFIED | andrettiglobal.com (Oct 2025 S12 launch; Jan 2026 Miami showrun) |
| Porsche powertrain ends after Season 12; Nissan from Season 13 (GEN4) | VERIFIED | fiaformulae.com news 1066678; RACER 24 Jul 2026 |
| Austin E-Prix at COTA 6 Feb 2027; Jeddah 18–19 Dec 2026; 21 races; Miami a fortnight after Austin | VERIFIED | Season 13 calendar (fiaformulae.com news 1074658) + seed calendar table |
| Envision Group owns Envision Racing; TotalEnergies (DS Penske); Shell (Lola Yamaha ABT); Castrol (Jaguar, Nissan); ABB title; Google Cloud championship partner | VERIFIED | sponsor table (spec/active_sponsor_db.md) |

Leadership ties: none found for Latimer, Norbeck, Ulrey, Jewett (`leadership_ties: []`). Existing
motorsport presence: none found for Fervo (Gate 5 saturation passes). Approached list: not on it.

## Score (honest, not inflated) — 72/100

Timing 16 · Capacity 16 · Brand fit 17 · Urgency 13 · **Ops fit 10 (MODE B)**. What holds it back:
no team workstream (Fervo sells power to grids and hyperscalers, not to race teams); a pre-revenue
public company whose shares sit well below the debut; no marketing executive. The sweep row's 78
was inflated on all three counts.

## Team choice, transparently

Andretti (chosen: the only American team; no energy, power or sustainability partner; Nissan
powertrain and new livery for GEN4 mean the roster is being redrawn now; COTA is a Texas home race).
Ruled out: Envision Racing (owner is a renewables group), DS Penske (TotalEnergies), Lola Yamaha ABT
(Shell), Jaguar TCS and Nissan (Castrol; Nissan is Andretti's incoming supplier), Porsche, Mahindra,
Cupra Kiro, Citroën (works or conglomerate rosters, no US stage).

## Pipeline defects found and fixed by this case

- Calendar check matched "Austin" to another United States round through the `austin → us` alias:
  name/city matches now rank before country matches.
- "Andretti's race engineers" was extracted as a race and contradicted: possessive or noun-phrase
  "race"/"round" mentions are no longer event claims.
- `run_day` treated a historical import on the same date as "already ran": historical rows and
  rebuild runs no longer count, and a rebuild on a day with a live brief stores the case as
  historical with its label instead of silently doing nothing.
