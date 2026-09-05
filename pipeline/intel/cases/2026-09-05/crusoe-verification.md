# Crusoe → TGR Haas F1 Team — verification log (N° 121, 5 Sep 2026)

Produced by the `pipeline/intel` engine run in-session (no `ANTHROPIC_API_KEY` in the sandbox), with
Claude acting as scanner, verifier and writer through the pipeline's injectable stages. Every gate,
the dedup check against the 128 backfilled historical signals, the 13-rule audit and the 2-page
render ran as code. Reproduce with `crusoe.session_run.py` against a migrated + seeded database.

**Sandbox limitation, stated plainly:** direct fetches of bloomberg.com, techcrunch.com, forbes.com,
crusoe.ai, globenewswire.com and the team sites were blocked by the egress proxy. Each claim below
was checked against the Tier-1 report that web search surfaced and quoted; the evidence URL is the
primary article. Treat every "VERIFIED (reported)" line as REPORTED, not company-confirmed, until a
person opens the link. The brief's own text says "reported" wherever that applies, its confidence is
MEDIUM, and the footer reads VERIFY BEFORE CIRCULATION.

## Screen-outs (the judgment is the product)

| Candidate | Trigger | Decision | Why |
|---|---|---|---|
| Fluidstack | $1.5B led by Jane Street at $18B (Forbes, 3 Sep) | eligible, outranked (74) | Same archetype, smaller; HQ just moved London→New York; keep as next-day candidate (Williams lane open) |
| Base Power | $1B Series D at $13B (TechCrunch, 3 Aug) | **stale** | 33 days old; Track-1 window is 14 days |
| Emerald AI | $150M Series A at $1.05B (25 Aug) | **below threshold** (66) | Capacity 11/20: Series A, unicorn only just; FE-native grid-flex story, no on-car workstream |
| Gimlet Labs | $300M at $3B (4 Sep) | **below threshold** (63) | Inference software, thin team workstream, early brand |

Blocklist: none of the five. Approached list (`data/approached.json`): none. Dedup: Crusoe was
surfaced once before (20 Jun 2026, Series E / IPO-candidate signal, score 76); 77 days ago and a
new capital event, so it passes the 30-day company+trigger rule and is not flagged resurfaced.

## The app page

`crusoe.web.html` is the long-form version the MD asked for (why now as a dated clock, why this
team as four business arguments plus the ruled-out table, value to the team as four workstreams,
the ask). Its figures and race mentions went through the same ledger as non-load-bearing claims;
the one left unverified is 1440's own $5-8M/yr price estimate, which has no external source by
design.

## Ledger (17 of 17 load-bearing claims verified)

| Claim | Status | Evidence |
|---|---|---|
| Chase Lochmiller, CEO & Co-Founder | VERIFIED | Crusoe Series E release (GlobeNewswire, 24 Oct 2025) |
| $3B+ Series F at ~$30B post-money, 3 Sep 2026 | VERIFIED (reported) | Bloomberg 3 Sep 2026; TechCrunch "reportedly"; no Crusoe release found |
| Co-leads Atreides Management + Valor Equity Partners; Mubadala Capital | VERIFIED (reported) | Bloomberg 3 Sep 2026 |
| ~$13B five-year Jane Street AI-cloud contract | VERIFIED (reported) | Bloomberg 3 Sep 2026 |
| $1.375B Series E at >$10B, Oct 2025; bookings ~5x; >45 GW pipeline | VERIFIED | Crusoe newsroom / GlobeNewswire 24 Oct 2025 |
| 1.2 GW Stargate campus, Abilene TX, first phase live for Oracle/OpenAI | VERIFIED | Crusoe newsroom; DCD |
| Customers OpenAI, Microsoft, Meta | VERIFIED (reported) | Bloomberg |
| HQ Denver; Bellevue office | VERIFIED | Series E release (Denver-based); GeekWire (Bellevue) |
| CoreWeave = Official AI Cloud Computing Partner, Aston Martin Aramco, May 2025 | VERIFIED | astonmartinf1.com announcement; sponsor table |
| Core Scientific joined Cadillac 2026 | VERIFIED | sponsor table (spec/active_sponsor_db.md) |
| Las Vegas GP; Austin race | VERIFIED | 2026 calendar table (rounds 22, 19) |
| Michael Gordon COO/CFO; Cully Cavness President & CSO (Dec 2025) | VERIFIED | Crusoe newsroom 11 Dec 2025 |
| Sharieff Mansour, VP Marketing | REPORTED | ZoomInfo / LinkedIn / Comparably; company leadership page not reachable — **confirm before outreach** |
| Nitin Perumbeti, CTO | REPORTED | Comparably / The Org — confirm |

Leadership ties: none found for Lochmiller, Cavness, Gordon, Mansour, Perumbeti (`leadership_ties: []`).
Existing motorsport presence: none found (Gate 5 saturation passes).

## Score (honest, not inflated) — 80/100 HOT

Timing 17 · Capacity 20 · Brand fit 15 · Urgency 13 · Ops fit 15 (MODE A). What holds it back:
the round is reported not confirmed; a B2B infrastructure brand with VP-level marketing and no
CMO; no hard deadline beyond the Austin/Las Vegas window and a probable listing.

## Team choice, transparently

Open cloud/compute lane: **Haas** (chosen: American privateer, most open tech roster, two US home
races), Audi, Racing Bulls, Williams. Ruled out: Aston Martin (CoreWeave, direct rival), Cadillac
(Core Scientific, TWG AI), Red Bull (Oracle), Mercedes (Microsoft), McLaren (Google Cloud, Dell,
Schneider Electric), Alpine (Microsoft), Ferrari (HP, IBM).

Naming note: the sponsor seed still keys the team as "MoneyGram Haas F1 Team" (mirrored from the
spec); the 2026 name is "TGR Haas F1 Team" and the brief uses that.
