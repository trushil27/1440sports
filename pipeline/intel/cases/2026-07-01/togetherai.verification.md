# Together AI → TGR Haas F1 Team — verification log (N° 170, issued for 1 Jul 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY`), with Claude acting as scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code from `togetherai.case.json`. The row sat on 1 Jul 2026 in the desk as an FE signal with no team; this case moves it to F1 and names the team.

**Sandbox limitation, stated plainly:** direct fetches of together.ai, businesswire.com, prnewswire.com, techcrunch.com and haasf1team.com were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, and the correction to the thin row

The round is company-announced (Business Wire, 1 Jul 2026) and Tier-1 covered (TechCrunch, Yahoo Finance, DCD the same day): **$800M Series C at $8.3B post-money, led by Aramco Ventures**. The thin row's framing, "Aramco Ventures lead investor creates direct FE / Jeddah E-Prix Gen4 ecosystem alignment", was the earlier writer's inference and does not survive the sponsor table: Aramco's motorsport money is in Formula 1 (championship Global Partner; Aston Martin title through 2028). The series is therefore F1, and the Aramco tie is treated as an ecosystem introduction, not a team path, because CoreWeave holds the AI-cloud lane at Aston Martin.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Vipul Ved Prakash, Co-Founder & CEO | VERIFIED | together.ai/about-us (search summary); The Org; Milken Institute |
| Kai Mak CRO; Charles Zedlewski CPO; Meicheng Shi SVP Finance; Ce Zhang CTO; no CMO or CFO listed | VERIFIED | together.ai/about-us (search summary) |
| $800M Series C at $8.3B post-money, led by Aramco Ventures; investors as listed | VERIFIED | Business Wire company release, 1 Jul 2026 |
| Annual bookings above $1.15B in the last quarter; thousands of paying customers incl. Cursor, Cognition, Decagon | VERIFIED (company statement) | Business Wire, 1 Jul 2026; TechCrunch |
| Footprint to grow ~50x over five years | VERIFIED (company statement) | Business Wire, 1 Jul 2026 |
| $305M Series B at $3.3B led by General Catalyst, Feb 2025 | VERIFIED | PR Newswire company release, 20 Feb 2025; SiliconANGLE |
| HQ San Francisco; founded 2022; Prakash ex-Topsy / Apple (Siri) | VERIFIED | SiliconANGLE; Milken / Wikipedia profile |
| Instant GPU Clusters (self-service, minutes); Frontier AI Factory (Blackwell, 1K-100K+ GPUs); fine-tuning and private inference | VERIFIED | together.ai product pages; HPCwire, Mar 2025 |
| IBM $240M multi-year inference cluster on IBM Cloud, 11 Aug 2026, online Q1 2027 (app page only) | VERIFIED | IBM newsroom, 11 Aug 2026; BNN Bloomberg |
| CoreWeave Official AI Cloud Computing Partner, Aston Martin Aramco, May 2025 | VERIFIED | astonmartinf1.com |
| Haas: American team, Kannapolis NC; TGR Haas F1 Team from 2026 with Toyota Gazoo Racing title | VERIFIED | haasf1team.com, Dec 2025 |
| Exein Official Physical AI Security Partner, Jul 2026 (app page only; not in the sponsor table snapshot) | VERIFIED | haasf1team.com, Jul 2026 |
| Eight AI partnerships in F1 in six months (Ampere Analysis) | REPORTED | Reuters via TechHQ, May 2026 |
| Rosters: Aramco (F1 Global + Aston Martin title to 2028), Cadillac (Core Scientific, TWG AI), McLaren (Google Cloud, Dell, Groq), Red Bull (Oracle), Mercedes/Alpine (Microsoft), Ferrari (HP, IBM), Audi (HPE, departed), Williams (Claude, VAST), Racing Bulls (Dynatrace, Confluent), Haas (Toyota Gazoo Racing, Mphasis, CommScope, Ruckus, Infobip) | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Miami, Belgian, Hungarian, Dutch, Italian, US (Austin), Las Vegas GPs on the 2026 calendar | VERIFIED | calendar table; dates from formula1.com |

## Screen-outs and things not claimed

- **No motorsport tie found** for Prakash, Zhang, Zedlewski, Mak or Shi after searching; `leadership_ties` is empty.
- **No revenue figure** is used: the company discloses bookings, not revenue, and the copy says bookings.
- **Deal size ($3-5M a year) is an ESTIMATE**, labelled as such; Haas partnerships are assumed to price below the front of the grid, which is a judgment, not a sourced figure.
- **"Only US-owned team until Cadillac"** (app page) is a description of the 2026 grid, not a sourced quote; Cadillac's parent is General Motors per the sponsor table.
- The Salesforce name appears as a Together AI customer (company customer page) and is not used in any team sentence.

## Decision path

Vipul Ved Prakash (Co-Founder & CEO) fronts every raise and would own a first sports partnership. Commercial path: Kai Mak (Chief Revenue Officer). Product and finance: Charles Zedlewski (Chief Product Officer), Meicheng Shi (SVP Finance). No chief marketing officer is listed on the leadership page, which the brief says.

## Ledger as built (N° 170, 22 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Vipul Ved Prakash, Co-Founder & CEO at Together AI |
| decision_maker | person_role | yes | verified | Vipul Ved Prakash, Co-Founder & CEO, Together AI at Together AI |
| key_facts | funding | yes | verified | $800M Series C at an $8.3B post-money valuation led by Aramco Ventures, announced 1 Jul 2026 (company release, Business Wire) |
| deck | funding | yes | verified | Together AI, the San Francisco cloud built for open-source AI, closed an $800M Series C at an $8.3B valuation on 1 July 2026, led by Aramco Ventures with Nvidia |
| key_facts | funding | yes | verified | Aramco Ventures (lead); Vista Equity Partners, General Catalyst, Emergence Capital, Nvidia, March Capital, Pegatron, S Ventures and others |
| the_case_p1 | funding | yes | verified | Together AI announced on 1 July 2026 an $800M Series C at an $8.3B post-money valuation, led by Aramco Ventures with Vista Equity Partners, General Catalyst, Em |
| key_facts | revenue | yes | verified | Annual bookings above $1.15B in the last quarter (company statement, 1 Jul 2026); no revenue figure disclosed |
| the_case_p1 | funding | yes | verified | Annual bookings topped $1.15B in the last quarter, with thousands of paying customers including Cursor, Cognition and Decagon. |
| key_facts | date | yes | verified | $800M Series C at $8.3B, announced 1 Jul 2026 |
| the_case_p1 | funding | yes | verified | The $305M Series B at $3.3B, led by General Catalyst, closed only in February 2025. |
| key_facts | sponsorship | yes | verified | CoreWeave is Aston Martin Aramco's Official AI Cloud Computing Partner (May 2025); Core Scientific and TWG AI sit on Cadillac's 2026 roster; Groq is on McLaren' |
| bottom_line | funding | yes | verified | An $800M round at $8.3B, bookings above $1.15B and a 50-fold build-out put Together AI at peak brand-investment authority with an F1-literate lead investor. |
| key_facts | other | yes | verified | Lead investor Aramco is F1's Global Partner and the Aston Martin title partner through 2028; Nvidia is an investor; Together's self-service GPU clusters and pri |
| extended | funding | no | verified | On 1 July 2026 Together AI announced an $800M Series C at an $8.3B post-money valuation, led by Aramco Ventures with Vista Equity Partners, General Catalyst, Em |
| key_facts | other | yes | verified | HQ San Francisco; founded 2022 |
| extended | funding | no | verified | The $305M Series B at $3.3B, led by General Catalyst, closed in February 2025. |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | Annual bookings passed $1.15B in the quarter before the Series C, with thousands of paying customers including Cursor, Cognition and Decagon. |
| extended | funding | no | verified | Since this brief's date, IBM signed a $240M multi-year agreement (11 August 2026) to host a Together AI inference cluster on IBM Cloud from the first quarter of |
| why_now_callout | event | yes | verified | United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | The United States GP |
