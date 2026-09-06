# Fireworks AI → Visa Cash App Racing Bulls — verification log (N° 162, brief dated 14 Jul 2026)

Built in-session on 6 Sep 2026 at no API cost from a case spec: Claude did the research and writing; the pipeline's calendar and sponsor-table checks, 13-rule audit and 2-page render ran as code.

**Date note, stated plainly:** the desk row sits on 14 Jul 2026 and cites a Sacra profile, but the Series D was announced by the company on 16 Jul 2026, two days after the row's date. The brief keeps the row's issue date (14 Jul) and takes the trigger date from the announcement (16 Jul); the pipeline's freshness rule keeps a trigger dated after the run date. Everything in the brief rests on the 16 Jul release and the 27 May Bloomberg report, not on the Sacra estimate.

**Sandbox limitation, stated plainly:** direct fetches of fireworks.ai, businesswire.com, cnbc.com, bloomberg.com and confluent.io were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## The trigger

Company-announced: Fireworks' release of 16 Jul 2026 (BusinessWire, fireworks.ai blog, mirrored by OTPP and Fortune; CNBC and Quartz coverage) states the $1.505B Series D at $17.5B, the leads and participants, the $1B annualised run-rate and the token volumes.

## Corrections to the thin row

- The row said "ARR estimated ~$800M May 2026, up from $305M end-2025" from Sacra. Those are third-party estimates and are not used; the brief uses the company's own statement (run-rate above $1B, fivefold year on year) and labels it a company figure, unaudited.
- "4.4× Series C valuation in 9 months": $4B (Oct 2025) to $17.5B (Jul 2026) is about 4.4×; the brief says "roughly fourfold".
- "Pre-IPO brand-awareness phase initiated": no IPO statement by the company or its CEO was found. URGENCY is scored 12 and the brief does not claim a listing.
- The row scored 88; re-scored 77. Capacity 19 is earned by the round; brand fit 14 and urgency 12 hold it back, and the decision path is thin (no CMO, COO or CRO named), which the bio says.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $1.505B Series D at $17.5B; Atreides, Index, TCV leads; Nvidia, Lightspeed, Evantic, Bessemer, Menlo, Insight, OTPP, Lone Pine, 20VC; 16 Jul 2026 | VERIFIED (company release via search summary) | BusinessWire; fireworks.ai blog |
| Run-rate above $1B, fivefold; 40T tokens/day from 15T | COMPANY FIGURE (unaudited) | same release; CNBC |
| Bloomberg 27 May: talks at $15B, Index co-lead | REPORTED | Bloomberg via Investing.com / TradingView |
| Series C $250M at $4B (28 Oct 2025); total then $327M; 2024 $52M at $552M led by Sequoia; total now ~$1.8B | VERIFIED / REPORTED | BusinessWire 28 Oct 2025; Bloomberg 11 Jul 2024; Seedtable (total, reported) |
| Customers Uber, DoorDash, Notion, Samsung, Verizon, Cursor, Upwork; Cursor once >50% of revenue; ~200 staff to 600 by end-2026 | REPORTED (CEO to CNBC) | CNBC 16 Jul 2026 |
| HQ Redwood City; founded 2022 by seven ex-Meta PyTorch engineers | VERIFIED / conflicting dateline | Crunchbase address (Redwood City); CNBC interview dateline says San Mateo; Contrary Research |
| Lin Qiao CEO (led PyTorch at Meta); Dmytro Dzhulgakov CTO; no CMO/COO/CRO named; CFO unnamed | VERIFIED / GAP | fireworks.ai team page; Contrary; Index Ventures |
| Confluent multi-year partnership, >1M data points/s, halo and upper sidepods from Singapore GP (1 Oct 2025) | VERIFIED | confluent.io release; BusinessWire |
| Dynatrace Official Observability and Performance Analytics partner; RebelDot; Neural Concept engineering AI (3 Jun 2025) | VERIFIED | Dynatrace IR release; rebeldot.com; BusinessWire |
| Faenza base; Milton Keynes aero/design at the Red Bull Technology Campus from Jan 2025 | VERIFIED | Motorsport Week; PlanetF1 |
| Groq at McLaren (26 Sep 2025); CoreWeave at Aston Martin (22 May 2025) | VERIFIED | groq.com; astonmartinf1.com |
| Racing Bulls roster and rival lanes across the grid | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| United States GP (Oct), Las Vegas GP (Nov) 2026 | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Screen-outs and things not claimed

- **Leadership ties:** no Fireworks leader found with prior F1/FE employment or sponsorship history; `leadership_ties` empty after checking.
- **Neural Concept** is an official supplier to Racing Bulls (Jun 2025) but is not in the sponsor table; it is named descriptively on the app page, not as a roster row, and it works in aerodynamic design, not inference.
- **The Racing Bulls deployment** in VALUE is a proposal, written as one; Fireworks has no motorsport customer.
- **Deal size $3-5M a year** is a 1440 ESTIMATE, labelled as such.

## Ledger as built (N° 162, 30 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Lin Qiao, CEO & Co-Founder at Fireworks AI |
| decision_maker | person_role | yes | verified | Lin Qiao, CEO & Co-Founder, Fireworks AI at Fireworks AI |
| key_facts | funding | yes | verified | $1.505B Series D at a $17.5B post-money valuation, led by Atreides Management, Index Ventures and TCV (company release, 16 Jul 2026); $250M Series C at $4B in O |
| deck | revenue | yes | verified | Fireworks AI, the Redwood City inference cloud founded by the Meta engineers behind PyTorch, announced a $1.505B Series D at a $17.5B valuation on 16 July 2026, |
| key_facts | funding | yes | verified | Atreides Management, Index Ventures, TCV (leads); Nvidia, Lightspeed Venture Partners, Evantic Capital, Bessemer Venture Partners, Menlo Ventures, Insight Partn |
| the_case_p1 | funding | yes | verified | Bloomberg reported on 27 May that Fireworks was in talks at $15B with Index co-leading; |
| key_facts | revenue | yes | verified | Annualised revenue run-rate above $1B, up fivefold year on year (company statement, Jul 2026; not audited) |
| the_case_p1 | funding | yes | verified | the round priced above that on 16 July at $17.5B, led by Atreides Management, Index Ventures and TCV, with Nvidia, Lightspeed, Evantic, Bessemer, Menlo, Insight |
| key_facts | date | yes | verified | $1.505B Series D at $17.5B announced 16 Jul 2026, above the $15B Bloomberg reported it was seeking in May |
| the_case_p1 | funding | yes | verified | It follows a $250M Series C at $4B in October 2025, a fourfold step in nine months; |
| key_facts | sponsorship | yes | verified | Groq at McLaren (inference chip, Official Partner since Sep 2025); CoreWeave at Aston Martin (Official AI Cloud Computing Partner, May 2025); Oracle at Red Bull |
| the_case_p1 | funding | yes | verified | total funding is about $1.8B (reported). |
| key_facts | other | yes | verified | The inference layer on Racing Bulls' Confluent real-time data stream: open-weight models fine-tuned on the team's own telemetry, hosted by Fireworks; customers  |
| the_case_p1 | revenue | yes | verified | The company says annualised revenue passed $1B, up fivefold, and tokens served rose from 15 to over 40 trillion a day. |
| key_facts | other | yes | verified | HQ Redwood City, California; founded 2022 by seven former Meta PyTorch engineers; about 200 staff, headcount planned to reach 600 by end-2026 (CEO to CNBC) |
| the_case_p2 | revenue | yes | verified | A $17.5B private company with $1B of revenue has the public market as its next audience. |
| trigger | date | yes | verified | funding round |
| bottom_line | revenue | yes | verified | A $1.505B Series D at $17.5B, revenue past $1B on the company's figures and headcount tripling put Fireworks at peak brand-investment authority. |
| the_case_p2 | sponsorship | yes | verified | Groq at McLaren |
| the_case_p2 | sponsorship | yes | verified | CoreWeave at Aston Martin |
| extended | funding | no | verified | On 16 July 2026 Fireworks announced a $1.505B Series D at a $17.5B post-money valuation, led by Atreides Management, Index Ventures and TCV, with Nvidia, Lights |
| extended | funding | no | verified | Bloomberg had reported on 27 May that the company was in talks at $15B; |
| extended | funding | no | verified | The Series C of October 2025 was $250M at $4B, led by Lightspeed, Index Ventures and Evantic with Sequoia participating, and brought total funding to $327M; |
| extended | funding | no | verified | two years earlier Sequoia led a $52M round at $552M with Nvidia, AMD and MongoDB. |
| extended | funding | no | verified | Total funding after the Series D is about $1.8B (reported). |
| extended | revenue | no | verified | Fireworks says annualised revenue run-rate has passed $1B, fivefold year on year, and that tokens served rose from 15 trillion to more than 40 trillion a day. |
| extended | revenue | no | verified | A 25-minute call with Lin Qiao before the United States GP to confirm the customer mix behind the $1B run-rate, walk through an inference deployment on Racing B |
| why_now_callout | event | yes | verified | The United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | United States GP |
