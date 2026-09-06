# Fluidstack → Atlassian Williams Racing — verification log (N° 127, 6 Sep 2026)

Today's signal, built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) with
Claude acting as scanner, verifier and writer through the pipeline's injectable stages; the
calendar table, sponsor table, 13-rule audit and the 2-page render ran as code. Reproduce with
`fluidstack.session_run.py` against a migrated + seeded database; `fluidstack.run.json` is the
case record `python -m intel.backfill --cases` imports (also under `pipeline/intel/cases/`).

**Sandbox limitation, stated plainly:** direct fetches of forbes.com, fluidstack.io, anthropic.com,
williamsf1.com, astonmartinf1.com, techcrunch.com and news.crunchbase.com were blocked by the
egress proxy. Each claim below was checked against the search summary of the primary page named as
the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. The brief's
confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, honestly labelled

Forbes (3 Sep 2026) and Crunchbase News (5 Sep 2026) report a **$1.5B round led by Jane Street at
an $18B valuation**. No Fluidstack press release was found. The brief says "reported" every time
the figure appears, the first risk row is REPORTED, NOT CONFIRMED, and the ask is to confirm the
round on the first call. The confirmed, company-announced fact the case rests on is Anthropic's
$50B US data-centre programme starting on Fluidstack sites (Anthropic, 12 Nov 2025).

## Ledger (16 of 16 claims verified: 15 load-bearing, 1 supporting on the app page)

| Claim | Status | Evidence |
|---|---|---|
| Gary Wu, Co-Founder & CEO | VERIFIED | The Org / Fluidstack leadership listing |
| César Maklary, Co-Founder & President; Rob Perdue COO (Feb 2025); Katherine Ollerhead GC; no CMO or CFO listed | VERIFIED | Fluidstack leadership announcement, Feb 2025; The Org |
| $1.5B round led by Jane Street at $18B | REPORTED | Forbes, 3 Sep 2026 (no company release) |
| Total funding just over $2.6B | REPORTED | Crunchbase News, 5 Sep 2026 |
| ~$750M round at ~$7–7.5B closed July 2026; Jane Street talks reported April | REPORTED | TechCrunch (Bloomberg-sourced), 14 Apr 2026; Dealroom, Jul 2026 (figures vary $750M–$830M) |
| Anthropic $50B US programme; Fluidstack sites in Texas and New York; announced 12 Nov 2025; sites online through 2026 | VERIFIED | anthropic.com newsroom |
| Founded Oxford 2017; HQ now New York | REPORTED | Forbes profile |
| Claude is Atlassian Williams Racing's Official Thinking Partner (multi-year, 2026 livery) | VERIFIED | williamsf1.com announcement |
| CoreWeave Official AI Cloud Computing Partner, Aston Martin Aramco, May 2025 | VERIFIED | astonmartinf1.com announcement |
| Williams roster (Atlassian, VAST, Keeper, Airia, Brillio); no cloud/GPU partner; Cadillac (Core Scientific, TWG AI), Red Bull (Oracle), Mercedes/Alpine (Microsoft), McLaren (Google Cloud, Dell), Ferrari (HP, IBM), Audi (HPE) | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| United States GP (Austin, late Oct) and Las Vegas GP (Nov) in 2026 | VERIFIED | calendar table (`seeds/calendar_f1_2026.json`) |

## Screen-outs and things not claimed

- **No motorsport tie found** for any Fluidstack leader; `leadership_ties` is empty after checking.
- **No revenue figure** is used: none is public.
- **Deal size ($4–7M a year) is an ESTIMATE**, labelled as such in the brief.
- **Jane Street's CoreWeave/Crusoe compute commitments** are stated as "billions" without a figure
  because the reported numbers vary by outlet.

## Pipeline defect found and fixed by this build

The first attempt was blocked: "WHY NOW  The round was reported on 3 September" was read by the
event extractor as a race called "WHY NOW The" and contradicted by the calendar table. A funding
round followed by "was / led / at / closed / …" is no longer treated as a race round
(`verify._FUNDING_ROUND_TAIL`, regression test in `tests/test_m3_verify.py`). The same file
carried a stray backspace byte inside `_RACE_NOUN_TAIL` that silently disabled the "win" tail;
removed.
