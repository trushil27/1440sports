# Celonis → Porsche Formula E Team — verification log (N° 200, 8 Jun 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) with Claude acting as
scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor
table, 13-rule audit and the 2-page render ran as code. The case sits on the row's date, 8 Jun 2026,
in rebuild mode; `celonis.run.json` is the case record `python -m intel.backfill --cases` imports.

**Sandbox limitation, stated plainly:** direct fetches of celonis.com, businesswire.com, prnewswire.com
and porsche.com were blocked by the egress proxy. Each claim below was checked against the search
summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a
person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

Celonis' own release of 12 May 2026 (Business Wire): launch of the Celonis Context Model and a
definitive agreement to acquire Ikigai Labs; MIT becomes a shareholder; Devavrat Shah becomes Chief
Scientist, Enterprise AI. Confirmed by Forrester, Constellation Research, diginomica and ERP Today. The
row date is 8 Jun; the trigger is 27 days earlier, inside the 90-day window. It is a product-launch
and M&A trigger, not a capital event: the timing label is WARM, not HOT.

## Team choice

The thin row suggested Jaguar TCS Racing. Ruled out: TCS is title partner and an IT-services
integrator that owns Jaguar's technology narrative (a channel conflict for Celonis). Porsche Formula E
Team chosen because Porsche AG already runs Celonis in production (MHP success story; Porsche AG's own
post), the lane is open on the sponsor table, and Porsche doubles to two works entries in Season 13
(fiaformulae.com). The team's Season 12 partners (TDK, NetApp, Synopsys, Cato Networks, Mobil 1,
Loctite, Puma) come from the team's own page and are NOT in the sponsor table, which carries only
Porsche, TAG Heuer and Hugo Boss for this team; the brief says "reported to include" and never writes
them as a Brand-at-Team sponsorship sentence. Operator: consider adding those rows to the seed.

## Ledger (claims verified against search summaries of the primary pages)

| Claim | Status | Evidence |
|---|---|---|
| Carsten Thoma, President (since Aug 2023; marketing in remit) | VERIFIED | Business Wire release, Aug 2023 |
| Context Model launch + Ikigai Labs agreement, 12 May 2026; MIT shareholder; Shah Chief Scientist | VERIFIED (company) | celonis.com release; Forrester; Constellation |
| $1B Series D at $11B, Jun 2021 | VERIFIED | PR Newswire / Bloomberg |
| $400M extension led by QIA at ~$13B, Aug 2022; ~$2.4B raised | REPORTED | The SaaS News / PR Newswire; Tracxn |
| Co-CEOs Rinke and Nominacher; CFO Fouilland (Dec 2024); CCO Khandelwal; no current CMO listed | VERIFIED / GAP on CMO | company releases; Craft, Comparably |
| HQ Munich and New York; founded 2011 | VERIFIED | Celonis About (via Tracxn/PitchBook) |
| Porsche AG runs Celonis; MHP 25+ projects; centre of excellence | VERIFIED | mhp.com success story; Porsche AG on Medium |
| Porsche two works teams from Season 13 (GEN4); Cupra Kiro customer team | VERIFIED | fiaformulae.com |
| Porsche FE Season 12 partners (TDK etc.) | REPORTED (team page; not in sponsor table) | racing.porsche.com |
| Grid occupancy (TCS, Tech Mahindra, Sand Technologies, TWG AI, Genpact) | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| London E-Prix 15-16 Aug 2026; Berlin; Season 13 opens Jeddah, Dec 2026 | VERIFIED | calendar table (fiaformulae.com) |

## Screen-outs and things not claimed

- **No revenue or ARR figure** is used: Celonis does not disclose it (third-party estimates ignored).
- **No customer count** is used: figures in coverage vary and none is from a company page reached.
- **No motorsport tie found** for Thoma, Rinke, Nominacher or Fouilland; `leadership_ties` is empty after checking.
- **Deal size ($2-3M a year) is an ESTIMATE**, labelled as such.
- **Score 73 (thin row 73):** capacity 17 despite the $13B mark because there has been no priced round since 2022 and no public revenue; urgency 12 because a product launch has no deadline; timing 14 because the trigger is four weeks old on the row date.

## Decision path

President Carsten Thoma (marketing owner) → co-CEOs Alexander Rinke and Bastian Nominacher → CFO Benoit Fouilland. No CMO exists on the listings reached; say so on the first call.

## Ledger as built (N° 200, 15 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Carsten Thoma, President at Celonis |
| decision_maker | person_role | yes | verified | Carsten Thoma, President, Celonis at Celonis |
| key_facts | funding | yes | verified | $1B Series D at an $11B valuation (Jun 2021); $400M Series D extension led by Qatar Investment Authority at about $13B (Aug 2022); roughly $2.4B raised in total |
| deck | funding | yes | verified | Celonis, the Munich- and New York-based process-intelligence company last valued at about $13B, launched the Celonis Context Model on 12 May 2026 and agreed to  |
| key_facts | funding | yes | verified | Qatar Investment Authority led the 2022 extension; MIT becomes a shareholder through the Ikigai Labs acquisition |
| the_case_p1 | funding | yes | verified | Celonis last priced at about $13B in an August 2022 extension led by Qatar Investment Authority, after a $1B Series D at $11B in June 2021; |
| key_facts | date | yes | verified | Celonis Context Model launch and definitive agreement to acquire Ikigai Labs, announced 12 May 2026 (company release; Business Wire) |
| the_case_p1 | funding | yes | verified | it has raised roughly $2.4B in total. |
| key_facts | sponsorship | yes | verified | TCS (Jaguar title), Tech Mahindra (Mahindra), Sand Technologies (Envision) and TWG AI (Andretti) hold Formula E's technology lanes; no process-intelligence or o |
| bottom_line | funding | yes | verified | A product launch and an MIT-linked acquisition at a company last valued at $13B, a customer in Porsche that already runs the software, and a Formula E grid with |
| key_facts | other | yes | verified | Porsche AG runs Celonis process mining with its consultancy MHP across more than 25 projects from supply chain to production and finance; Porsche fields two wor |
| extended | revenue | no | verified | it has raised roughly $2.4B in total and does not disclose revenue. |
| key_facts | other | yes | verified | Dual headquarters Munich and New York; founded 2011 in Munich |
| extended | event | no | verified | London E-Prix |
| trigger | date | yes | verified | product launch and acquisition |
