# Verification log — Cerebras Systems (2026-07-03 F1 hero)

**Re-verified live via WebSearch on 2026-07-03.** Claim-by-claim VERIFIED / CORRECTED /
UNVERIFIED. (`verify_brief.py --net` is non-functional in-container — no shell network;
live verification via WebSearch/WebFetch.)

## Already-sent check (log + disk)
- **VERIFIED net-new.** No `cerebras` in the history log; no `cerebras.pdf` on disk before
  `briefs/2026-07-03/`. (Only truly-fresh eligible F1 name in the DB was Snowflake, which
  the MD rejected — hence net-new sourcing.)

## Already-present / lane check
- **VERIFIED no F1/motorsport presence** for Cerebras (searched; absent). F1 CFD is served
  by CAE *software* (Ansys/Siemens/Cadence) — Cerebras is the compute *hardware* underneath,
  a distinct sub-lane; recommended team Cadillac has no AI-compute partner (gridfit: PRIME).

## Load-bearing claims
1. **Blockbuster Nasdaq IPO May 2026 (CBRS); priced $185, opened +108%, ~$67B market cap;
   raised ~$5.55B.** → **VERIFIED.** Yahoo Finance, The Register, TradingKey. (Note: pre-IPO
   guidance was ~$23-27B; the pop took it to ~$67B — used the traded figure.)
2. **$510M 2025 revenue at a 47% net margin (profitable); OpenAI + AWS multi-billion
   deals.** → **VERIFIED.** Tech-insider S-1 teardown, Futurum, TradingKey.
3. **WSE-3 = largest AI chip ever (~4 trillion transistors, wafer-scale).** → **VERIFIED.**
   Cerebras press release, IEEE Spectrum.
4. **Co-Founder & CEO Andrew Feldman (since 2015; prior co-founded SeaMicro, sold to AMD).**
   → **VERIFIED** (well-established; Wikipedia/company). Decision-maker is a factual, named
   individual, not invented.
5. **Customer concentration: MBZUAI ~62% of 2025 revenue; G42 largest backer.**
   → **VERIFIED.** AGBI, Futurum S-1 teardown. Kept as an explicit RISK, not scored away.

## Honest limitations (in the brief, reflected in the score)
- **F1 ATR cap:** F1 regulates CFD/wind-tunnel volume per team, so compute can't be scaled
  without limit — framed as maximising fidelity/iteration PER allocated unit + uncapped
  PU/strategy/ML sim, not evading the cap. urgency/brand_fit tempered.
- **CAE software incumbents** (Ansys/Cadence/Siemens) occupy the toolchain — Cerebras is the
  compute layer beneath (distinct hardware sub-lane), not a replacement.
- **Customer concentration / G42 geopolitics** — noted as a risk; deal-capability itself is
  not in question (~$67B, profitable, diversifying via OpenAI/AWS).

## Team & conflict check
- **Cadillac** (greenfield PRIME LANE): building its simulation/compute stack from zero →
  a foundational AI-compute partner is the strongest fit; American compute champion ↔
  American works team; GM = deep-pocketed counterpart. No AI-compute incumbent (IFS=ERP,
  TWG AI=data/analytics services, not wafer-scale HPC). Transparent: this is a 4th 1440
  signal aimed at Cadillac — signals are not placements, and greenfield genuinely fits a
  compute partner; distinct lane from the prior three (backup / CAE / power).
- **No backer conflict:** G42/OpenAI/AWS ties are not Cadillac/GM rivals.

## Two-way exchange (per MD framework — 3 mutual swaps)
1. **Compute ↔ elite CFD benchmark** (wafer-scale compute maximises CFD within ATR + PU/
   strategy sim ↔ F1 aero = Cerebras's hardest real-world HPC benchmark & showcase).
2. **Co-engineered workloads ↔ product validation** (joint HPC optimisation advances
   Cerebras's reference architecture ↔ faster, higher-fidelity aero = lap time).
3. **Talent + brand ↔ enterprise reach** (American-champion halo for HPC/ML talent ↔ the
   paddock's OEM/industrial ecosystem opens Cerebras's enterprise buyers).

## Result
5 load-bearing claims VERIFIED, 0 corrections; net-new; no motorsport presence; conflict-free
on Cadillac (PRIME). Real MODE-A compute workstream, honestly bounded by the ATR cap +
concentration risk. Score 79 HOT (capacity/timing-led). 0 blockers, 2 pages.
