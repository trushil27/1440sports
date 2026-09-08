# Screened-out company profiles

> Operator request, 7 Sep 2026: "update the signals we eliminated into the app — company
> name, their current status on funds and valuation, what business they are in, why
> eliminated, a link to their company page, which team or championship it was ideally fit for,
> and a small brief about their company & senior leadership."

The app's **Screened out** page (left panel, under Signals) lists every company the desk
researched in full and decided not to pitch. The desk already holds, for each: the trigger
and its figures, the series and team it was aimed at, the industry line, the verdict, the
full reasoning and the sources. What it did **not** hold — and what this file standard adds —
is a company profile: website, business one-liner, funding and valuation as of today, senior
leadership, and a short brief.

Profiles live in `data/screened_profiles/*.json`. Several files, one per research batch, so
parallel runs never conflict; `intel.profiles.load_profiles` reads them all and a later file's
record for the same company replaces an earlier one. The export attaches each profile to its
screened row; the page shows **"Not on file yet"** for any field a profile does not carry.

## The standard (the same as every other record in this desk)

- **Re-verify, don't recall.** Every field comes from a page you actually opened. The
  company's own site for website, business and leadership; a primary or Tier-1 source for
  funding and valuation. Never from memory.
- **Never invent.** No name, figure, date or URL that is not on a page you read. A field you
  could not verify is **omitted** — the app says "Not on file yet". A company that turned out
  not to exist as described (several screen-outs were exactly that) gets `confidence: "GAP"`
  and a `brief` saying so.
- **Tag confidence** for the record as a whole: `VERIFIED` (company's own pages + a primary
  source for the money), `REPORTED` (credible secondary for some of it), `GAP` (could not be
  established).
- **Leadership = the real senior team** from the company's leadership/about page: CEO, and
  where listed the CMO or commercial lead, CFO, CTO, President EMEA. Two to five people.
  Each with the page it came from. No titles inferred from LinkedIn snippets.
- **Funding status is as of the day you check**, with the date. "Series B, $26m, 1 Sep 2026
  (Insight Partners); total raised $40m" — and `valuation` only if a source states it,
  otherwise `null`.
- **Brief**: two or three plain sentences — what they make or do, for whom, where they are,
  and where they stand. Business language, no marketing copy.

## Record

```json
{
  "company": "Ore Energy",
  "website": "https://ore.energy",
  "business": "Iron-air long-duration batteries that store renewable power for up to 100 hours.",
  "funding": {
    "status": "€37.3m Series A, 4 Aug 2026, co-led by Plural and HV Capital; total raised $61m",
    "valuation": null,
    "as_of": "2026-09-08"
  },
  "leaders": [
    {"name": "Aytac Yilmaz", "role": "Co-founder & CEO", "source": "https://ore.energy/team"}
  ],
  "brief": "Amsterdam-based spin-out building iron-air batteries for multi-day grid storage. First factory under construction; commercial team being hired after the Series A.",
  "checked_at": "2026-09-08",
  "sources": ["https://ore.energy", "https://ore.energy/team", "https://mercomcapital.com/…"],
  "confidence": "VERIFIED"
}
```

Field notes: `company` must match the desk's spelling (given in the worklist). Every other
field is optional. `leaders[].source` and `sources` are the pages actually opened.

## Workflow

1. `python -m intel.profiles` prints the worklist: every full-check screen-out with no profile
   yet, with what the desk already knows (date, series, team, industry, trigger, source, why).
2. Research each company against the standard above. Start from the desk's own record — the
   trigger and the screen-out reasoning already name the round, the investors and often the
   people — and confirm it on the company's pages.
3. Write `data/screened_profiles/batch-NN.json` as a JSON list of records.
4. `python -m intel.site_export --out site` republishes; the page fills in.

Nothing in this workflow calls the model API. It is the same zero-cost pattern as
`data/contacts.json` (the decision paths) and `data/signal_checks.json` (the signal checks).
