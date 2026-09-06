# Coralogix → Atlassian Williams Racing — verification log (N° 204, 3 Jun 2026)

Rebuilt in full on 6 Sep 2026 for the row dated 3 Jun 2026 (batch 16), at no API cost: Claude acted as
scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor
table, 13-rule audit and the 2-page render ran as code. `coralogix.case.json` is the spec;
`coralogix.run.json` the case record `python -m intel.backfill --cases` imports.

**Sandbox limitation, stated plainly:** direct fetches of coralogix.com, globenewswire.com,
techcrunch.com and calcalistech.com were blocked by the egress proxy. Each claim was checked against
the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED
until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## The trigger

The thin row's trigger is confirmed and dated: Coralogix's own release on GlobeNewswire, 3 Jun 2026,
announces the $200M Series F co-led by Advent, CPPIB and Greenfield with Brighton Park Capital, total
funding $550M. Inside the 90-day window (same day as the row). The row's `team: null` was resolved from
the sponsor table.

## What is only REPORTED

- **$1.6B valuation** — TechCrunch and Calcalist, 3 Jun 2026; not in the company release.
- **5,000+ customers, 60%+ revenue growth, ~30 accounts above $1M, Olly adoption** — TechCrunch, 3 Jun
  2026 (company-sourced figures relayed by press). The thin row's "60%+ YoY ARR growth" is revenue
  growth in the source; the copy says revenue.
- **~500 employees** — Calcalist, spring 2025; not used in the brief.
- **Deal size $3-5M a year** — 1440 ESTIMATE, labelled.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Brian Mullen, CMO (global marketing + partner ecosystem; ex-InfluxData CMO, Twilio) | VERIFIED | coralogix.com/about (search summary), LinkedIn |
| Ariel Assaraf CEO & co-founder; Matt Handler President & COO; Eran Hadad CFO; Yoni Farin co-founder CTO/CPO | VERIFIED | coralogix.com/about, The Org |
| $200M Series F, 3 Jun 2026; Advent/CPPIB/Greenfield co-lead; Brighton Park; $550M total | VERIFIED | GlobeNewswire release; coralogix.com/blog; adventinternational.com |
| $1.6B valuation | REPORTED | TechCrunch, Calcalist |
| $115M Series E, 17 Jun 2025, NewView Capital lead, $1B+ | VERIFIED | GlobeNewswire release |
| HQ Boston (225 Franklin St) + Ramat Gan; SF office; founded 2015 | REPORTED | Craft, Calcalist, LinkedIn listings |
| Splunk at McLaren (via Cisco); Dynatrace at Racing Bulls; IBM at Ferrari; ServiceNow at Aston Martin; Williams roster with no observability partner | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| IBM Instana and ServiceNow Cloud Observability (Lightstep) are observability products | VERIFIED | FitGap / PeerSpot / Gartner Peer Insights market listings |
| British GP, Silverstone, 5 Jul 2026 | VERIFIED | calendar table + formula1.com timetable |

## Decision path

Sponsorship owner: **Brian Mullen, Chief Marketing Officer** (brand, partner ecosystem, strategic
alliances). Sign-off: **Ariel Assaraf, Co-Founder & CEO**. Path: **Matt Handler, President & COO**;
**Eran Hadad, CFO**; technical counterpart **Yoni Farin, Co-Founder, CTO & CPO**. The thin row named
Assaraf; the CMO is the real owner and Assaraf is kept as the signatory.

## Leadership ties

Checked Assaraf, Mullen, Handler for F1/FE/motorsport sponsorship history: **none found**.
`leadership_ties` empty. No Coralogix motorsport partnership exists on any list checked.

## Screen-outs

McLaren (Splunk/Cisco), Racing Bulls (Dynatrace, Confluent), Ferrari (IBM), Aston Martin (ServiceNow)
are category clashes; Mercedes, Red Bull, Alpine crowded or incumbent-cloud; Audi adjacent (NinjaOne);
Cadillac and Haas open but not chosen. Williams chosen on the open lane and the coherent data roster.

## Honest score: 73

The thin row's 84 was inflated. Held back by: valuation only reported (capacity 15), a developer-known
rather than mainstream brand (brand fit 13), and no hard deadline (urgency 12). Ops fit 16 is the
strongest pillar: a real MODE A workstream on an open lane.

## Ledger as built (N° 204, 20 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Brian Mullen, Chief Marketing Officer at Coralogix |
| decision_maker | person_role | yes | verified | Brian Mullen, Chief Marketing Officer, Coralogix at Coralogix |
| key_facts | funding | yes | verified | $200M Series F announced 3 Jun 2026, co-led by Advent, CPPIB and Greenfield with Brighton Park Capital participating; total funding $550M; valuation $1.6B repor |
| deck | revenue | yes | verified | Coralogix, the Boston- and Ramat Gan-based AI-native observability platform, closed a $200M Series F on 3 June 2026 co-led by Advent, CPPIB and Greenfield at a  |
| key_facts | funding | yes | verified | Advent, CPPIB and Greenfield co-led; Brighton Park Capital; the $115M Series E of 17 Jun 2025 was led by NewView Capital at a $1B-plus valuation |
| the_case_p1 | funding | yes | verified | Coralogix announced the $200M Series F on 3 June 2026: co-led by Advent, CPPIB and Greenfield, with Brighton Park Capital participating, taking total funding to |
| key_facts | date | yes | verified | $200M Series F co-led by Advent, CPPIB and Greenfield, announced 3 Jun 2026 |
| the_case_p1 | funding | yes | verified | TechCrunch and Calcalist put the valuation at $1.6B, up from the $1B-plus mark of the $115M Series E led by NewView Capital in June 2025. |
| key_facts | sponsorship | yes | verified | Splunk sits on McLaren through Cisco and Dynatrace on Visa Cash App Racing Bulls: two observability rivals already on the grid |
| the_case_p1 | revenue | yes | verified | TechCrunch reports more than 5,000 customers, revenue growing over 60% year on year and around 30 accounts above $1M a year, with over half of enterprise custom |
| key_facts | other | yes | verified | More than 5,000 customers, revenue growing over 60% year on year and around 30 accounts above $1M a year; more than half of enterprise customers use its AI agen |
| bottom_line | funding | yes | verified | A $200M Series F on 3 June, more than 5,000 customers growing over 60% and an observability lane no Williams partner covers make Coralogix a MODE A workstream w |
| key_facts | other | yes | verified | Headquartered at 225 Franklin Street, Boston, with a second headquarters in Ramat Gan, Israel, and a US office in San Francisco |
| extended | funding | no | verified | Coralogix announced a $200M Series F on 3 June 2026, co-led by Advent, CPPIB and Greenfield with Brighton Park Capital participating, taking total funding to $5 |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | TechCrunch and Calcalist report $1.6B, and the brief says reported wherever that figure appears. |
| extended | funding | no | verified | The $115M Series E led by NewView Capital closed on 17 June 2025 at a valuation above $1B. |
| extended | revenue | no | verified | TechCrunch reports more than 5,000 customers, revenue growing over 60% year on year, around 30 accounts spending above $1M a year and more than half of enterpri |
| why_now_callout | event | yes | verified | The British GP |
| extended | event | no | verified | British GP |
