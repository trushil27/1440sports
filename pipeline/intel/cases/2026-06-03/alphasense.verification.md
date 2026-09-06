# AlphaSense → McLaren Mastercard F1 Team — verification log (N° 205, 3 Jun 2026)

Rebuilt in full on 6 Sep 2026 for the row dated 3 Jun 2026 (batch 16), at no API cost: Claude acted as
scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor
table, 13-rule audit and the 2-page render ran as code. `alphasense.case.json` is the spec;
`alphasense.run.json` the case record `python -m intel.backfill --cases` imports.

**Sandbox limitation, stated plainly:** direct fetches of alpha-sense.com, globenewswire.com,
nasdaq.com, prnewswire.com and mclaren.com were blocked by the egress proxy. Each claim was checked
against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as
REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## The trigger

The thin row said "reported $350M funding" via Verdict. The primary source is AlphaSense's own release
(alpha-sense.com/press, GlobeNewswire, Nasdaq) dated New York, 3 Jun 2026: $350M at $7.5B, led by
Vitruvian Partners, Accenture Ventures and J.P. Morgan Asset Management; ARR above $600M in Q1 2026.
Same day as the row: inside the window. Team hint (McLaren) confirmed against the sponsor table.

## What is only REPORTED

- **IPO "a possibility"** — Kokko quoted in press coverage (Yahoo Finance / Verdict); no filing.
- **$650M at $4B in 2024** — FinTech Global summary of the prior round.
- **Deal size $4-6M a year** — 1440 ESTIMATE, labelled.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Heather Zynczak, CMO since Apr 2024; ex-CMO Domo ($0-100M) and Pluralsight (IPO team); Oracle, SAP | VERIFIED | PR Newswire release, 9 Apr 2024; The Org 2026 |
| Jack Kokko Founder & CEO; Kiva Kolstein President & CRO; Samantha Greenberg CFO (14 Apr 2026); Raj Neervannan co-founder CTO | VERIFIED | GlobeNewswire release 14 Apr 2026; alpha-sense.com leadership (search summary) |
| $350M at $7.5B, 3 Jun 2026; leads Vitruvian, Accenture Ventures, JPMAM; new D. E. Shaw Ventures, Pinegrove; existing Goldman Sachs Alternatives, CapitalG, Viking; total > $1B; Bower-Straziota to board | VERIFIED | alpha-sense.com press release / GlobeNewswire / Nasdaq |
| ARR > $600M Q1 2026, from $500M Oct 2025; 7,000+ enterprises; 90% of S&P 100; all top global investment banks; 92% of top-50 pharma | VERIFIED | same release |
| Accenture strategic investment + partnership (agentic market-intelligence workflows) | VERIFIED | newsroom.accenture.com, 2026 |
| HQ New York | VERIFIED | release dateline |
| Gemini is McLaren's Primary Partner for AI | VERIFIED | mclaren.com partner page; Nov 2025 extension coverage |
| McLaren roster (Mastercard, Goldman Sachs, CNBC, Deloitte, Workday, Alteryx, Dell, Cisco/Splunk, Google Cloud, Gemini); no research platform on any team; Aston Martin FT/Public/Coinbase/Pepperstone; Mercedes Nasdaq/UBS; Williams BNY/Barclays/Nuveen/Stephens | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| British GP, Silverstone, 5 Jul 2026 | VERIFIED | calendar table + formula1.com |

## Decision path

Sponsorship owner: **Heather Zynczak, Chief Marketing Officer** (brand, global marketing). Sign-off:
**Jack Kokko, Founder & CEO**. Path: **Kiva Kolstein, President & Chief Revenue Officer**; **Samantha
Greenberg, CFO** (appointed 14 Apr 2026). Technical counterpart, if a platform-seat workstream is
scoped: Raj Neervannan, Co-Founder & CTO.

## Leadership ties

Checked Kokko, Zynczak, Kolstein for F1/FE/motorsport sponsorship history: **none found**.
`leadership_ties` empty. No AlphaSense motorsport partnership exists on any list checked. A legacy
record in `data/prospects.json` (AlphaSense, 75) predates this case and is superseded by it.

## Screen-outs

Aston Martin (Financial Times, Public, Coinbase, Pepperstone, Circle) and Mercedes (Nasdaq, UBS)
crowded; Williams finance-heavy; Racing Bulls, Alpine, Audi retail-finance tone; Red Bull, Ferrari,
Cadillac, Haas open but not chosen. McLaren chosen on the open lane, the Goldman Sachs path and the
B2B partner programme. The Gemini AI adjacency is named as the first risk.

## Honest score: 73

The thin row's 75 was close. Held back by: a MODE B, off-car workstream (ops fit 12), a purely B2B
brand (brand fit 14) and an IPO that is a possibility, not a date (urgency 13). Capacity 17 and timing
17 are the strong pillars.

## Ledger as built (N° 205, 24 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Heather Zynczak, Chief Marketing Officer at AlphaSense |
| decision_maker | person_role | yes | verified | Heather Zynczak, Chief Marketing Officer, AlphaSense at AlphaSense |
| key_facts | funding | yes | verified | $350M round announced 3 Jun 2026 at a $7.5B valuation, led by Vitruvian Partners, Accenture Ventures and J.P. Morgan Asset Management; total funding over $1B; p |
| deck | funding | yes | verified | AlphaSense, the New York AI market-intelligence platform used by 90% of the S&P 100, closed a $350M round on 3 June 2026 at a $7.5B valuation, led by Vitruvian, |
| key_facts | funding | yes | verified | Vitruvian Partners, Accenture Ventures, J.P. Morgan Asset Management (leads); D. E. Shaw Ventures and Pinegrove Opportunity Partners new; Goldman Sachs Alternat |
| deck | revenue | yes | verified | Morgan Asset Management, on annual recurring revenue above $600M and reported IPO intent. |
| key_facts | revenue | yes | verified | Annual recurring revenue above $600M in Q1 2026, up from $500M in October 2025 (company release, 3 Jun 2026) |
| the_case_p1 | funding | yes | verified | AlphaSense announced the $350M round on 3 June 2026: led by Vitruvian Partners, Accenture Ventures and J.P. |
| key_facts | date | yes | verified | $350M round at a $7.5B valuation announced 3 Jun 2026 |
| the_case_p1 | funding | yes | verified | Morgan Asset Management, with Goldman Sachs Alternatives, CapitalG and Viking returning, taking total funding past $1B. |
| key_facts | sponsorship | yes | verified | No market-intelligence or research platform sits on the F1 grid; Financial Times at Aston Martin and CNBC at McLaren are the nearest financial-information adjac |
| the_case_p1 | funding | yes | verified | The $7.5B valuation nearly doubles the $4B set by the $650M round of 2024. |
| key_facts | other | yes | verified | More than 7,000 enterprise customers including 90% of the S&P 100 and all of the top global investment banks; Goldman Sachs Alternatives is an existing investor |
| the_case_p1 | revenue | yes | verified | Annual recurring revenue passed $600M in the first quarter, up from $500M in October 2025. |
| key_facts | other | yes | verified | Headquartered in New York; the 3 Jun 2026 release is datelined New York |
| the_case_p1 | funding | yes | verified | More than 7,000 enterprises use the platform, including 90% of the S&P 100 and every top global investment bank. |
| trigger | date | yes | verified | funding round |
| bottom_line | revenue | yes | verified | A $350M round at $7.5B on 3 June, ARR above $600M, a customer list that already fills McLaren's suites and an open market-intelligence lane put AlphaSense at pe |
| extended | funding | no | verified | AlphaSense announced on 3 June 2026 that it had closed a $350M round at a $7.5B valuation, led by Vitruvian Partners, Accenture Ventures and J.P. |
| extended | funding | no | verified | Total funding now exceeds $1B. |
| extended | revenue | no | verified | Annual recurring revenue passed $600M in the first quarter of 2026, up from $500M in October 2025, and the valuation nearly doubled from the $4B set by the $650 |
| extended | funding | no | verified | AlphaSense's buyers are analysts, bankers and corporate strategists at more than 7,000 enterprises, including 90% of the S&P 100. |
| why_now_callout | event | yes | verified | The British GP |
| extended | event | no | verified | British GP |
