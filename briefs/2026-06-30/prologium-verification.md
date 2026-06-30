# Verification log — ProLogium Technology (2026-06-30 FE hero)

**Re-verified live via WebSearch/WebFetch on 2026-06-30.** One line per load-bearing
claim → VERIFIED / CORRECTED / UNVERIFIED, with the source actually checked.

> Tooling note: `engine/verify_brief.py --net` is **non-functional in this
> container** — the shell/subprocess has no outbound network (curl returns 000 even
> for wikipedia.org; the proxy at 127.0.0.1 is only reachable from the
> WebSearch/WebFetch harness tools). Proof: running `--net` on the canonical
> known-good `cohesity` brief marks **all 9** of its citations `cite_dead` too,
> and so does adding `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt`. So `cite_dead`
> under `--net` here means "shell can't reach it," NOT "fabricated." Live
> verification therefore has to be done with WebSearch/WebFetch — logged below.

## Already-sent check (log + disk)
- **VERIFIED net-new.** `prologium` appears in the history log only on 2026-06-30,
  and the only `prologium.pdf` on disk is `briefs/2026-06-30/`. Never previously
  featured or bench-rendered.

## Load-bearing claims
1. **Going public on Nasdaq as PRLG via a ~$3.8B SPAC merger with Translational
   Development Acquisition Corp (TDAC); announced May 27 2026; closing H2 2026.**
   → **VERIFIED.** Multiple independent sources: ProLogium/GlobeNewswire release
   (27 May 2026), Battery-Tech Network ("$3.8B"), StockTitan (TDAC 8-K), Electrek
   (27 May 2026), ElectricCarsReport ("$3.8 billion Nasdaq SPAC merger").
2. **Dunkirk, France gigafactory — €5.2B investment, 48 GWh planned; broke ground
   Feb 2026; EU state-aid grant approved; Macron attended.**
   → **VERIFIED.** ProLogium press, GlobeNewswire (10 Feb 2026), ElectricCarsReport,
   evspecifications.
3. **Mercedes-Benz is a technology partner, investor, and holds a board seat
   (since Jan 2022).**
   → **VERIFIED.** ProLogium/PRNewswire (Jan 2022), Green Car Congress, Autovista24.
   (This is the basis for the team-conflict screen — see #6.)
4. **CES 2026 (ProLogium's 20th anniversary): unveiled an all-inorganic
   solid-state lithium-ceramic battery with an all-silicon anode.**
   → **VERIFIED.** ProLogium/PRNewswire CES 2026 release; FEV Group joint release;
   BatteryTechOnline.
5. **Founder & CEO: Vincent Yang.**
   → **VERIFIED.** ProLogium CES 2026 release (direct quote, "Vincent Yang, Founder
   and CEO"); BatteryTechOnline.
6. **Team-conflict basis — Mercedes-Benz exited Formula E (end of 2022) and is a
   ProLogium board member, so a premium Mercedes rival (Jaguar/Porsche) is the
   wrong team.** → **VERIFIED.** Mercedes FE withdrawal (end-2022) confirmed via
   Electrek/Autosport/ESPN. Re-pointed to Mahindra (non-premium-rival).
7. **MODE-B honesty pivot — Formula E uses a single SPEC battery; teams/
   manufacturers cannot develop or choose their own cells, so a cell-maker
   cannot deploy on-car.** → **VERIFIED.** Williams Advanced Engineering is the
   exclusive Gen3 (2022+) battery supplier for the entire grid (Motorsport.com,
   Autosport, Race Tech, Motorsport Technology). This is why the brief is scored
   MODE-B (off-car brand/future-battery halo), not MODE-A.

## Items explicitly NOT claimed (kept honest)
- The ~$3.8B is a **pre-money / going-public valuation via SPAC** and the listing is
  **not yet closed** — flagged in the brief as in-process, not a closed round.
- **No motorsport presence** for ProLogium (already_present = false) — searched, none found.
- No revenue/profit figures asserted (capex-stage; capacity scored value-tier honestly).

## Result
All 7 load-bearing claims VERIFIED via reachable sources; 0 corrections needed on the
facts. The record's `sources` URLs are valid primary/credible pages that bot-block the
in-container checker — verify manually (as above), not via `--net` in this environment.
