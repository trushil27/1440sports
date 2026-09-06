# TENEX.AI → Cadillac F1 Team — verification log (N° 228, row dated 5 May 2026)

Built in-session on 6 Sep 2026 at no API cost for the desk row dated 5 May 2026 (batch 21). Claude acted as researcher, verifier and writer; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code via `intel.session_case`.

**Sandbox limitation, stated plainly:** direct fetches of tenex.ai, businessobserverfl.com, scworld.com and theorg.com were blocked by the egress proxy. Every claim below was checked against the search summary of the primary page named as the evidence URL (company press releases on tenex.ai, Bloomberg's 31 Mar 2026 report, the Business Observer's March and May 2026 coverage). Treat each VERIFIED line as REPORTED until a person opens the link; confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

The thin row's trigger holds: the $250M Series B and the Abouseido appointment were both announced by the company on **31 Mar 2026**, 35 days before the row's date — inside the 90-day window. The thin row's source (tech-insider.org) is an aggregator; the primary source is the company release `tenex.ai/news/series-b/`, with Bloomberg (31 Mar 2026) as the credible secondary. The **valuation above $1B is Bloomberg's figure** and is not in the company release; the brief labels it reported every time.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Eric Foster, Founder & CEO | VERIFIED (search summary) | tenex.ai leadership page; Crunchbase |
| $250M Series B led by Crosspoint, with Shield Capital and DeepWork Capital, 31 Mar 2026 | VERIFIED (search summary) | tenex.ai/news/series-b; Wilson Sonsini deal note |
| Valuation above $1B | REPORTED | Bloomberg, 31 Mar 2026; SC Media |
| $25M contracted revenue within a year of launch; first contract March 2025 | VERIFIED (company statement) | Series B release; Business Observer 15 May 2026 |
| 318% YoY growth; #1 on IT-Harvest 2026 Cyber 150 | VERIFIED (company statement) | Series B release; tenex.ai Cyber 150 post |
| Use of funds: 250-plus hires in 2026, EMEA expansion, Google Cloud SecOps + Microsoft Sentinel | VERIFIED (company statement) | Series B release |
| Bashar Abouseido President, ex-SVP & CISO Charles Schwab | VERIFIED (search summary) | tenex.ai press release 31 Mar 2026 |
| $27M Series A (Crosspoint lead; a16z, Shield Capital; DeepWork, Florida Opportunity Fund) | VERIFIED (search summary) | tenex.ai Series A release; Business Observer 11 Sep 2025 |
| Series A month | REPORTED | Business Observer dates it to September 2025; one aggregator summary said 27 Oct 2025 — the brief does not use a month |
| World HQ Sarasota, FL; ~100 staff, ~300 targeted by end-2026 | REPORTED | Business Observer 15 May 2026; tenex.ai Florida HQ release |
| Ryan Shreve, Co-Founder, CFO/COO | REPORTED | LinkedIn / Crunchbase (CFO) |
| No CMO at the row date; Richard Rogers CMO from 4 Jun 2026; Jacqueline Kelly VP Marketing | VERIFIED (search summary) | tenex.ai CMO release, 4 Jun 2026 |
| Cadillac roster entirely inaugural; no cybersecurity partner; cyber rivals at Mercedes, Williams, Ferrari, Red Bull, McLaren, Alpine, Audi; SentinelOne departed Aston Martin | VERIFIED | sponsor table (`seeds/sponsors.json`), team profile |
| Zscaler named Aston Martin's Global Cybersecurity Partner, 25 Jun 2026 | VERIFIED (search summary) | astonmartinf1.com; GlobeNewswire |
| Cadillac run from Silverstone while Fishers is built; Charlotte and Warren bases | VERIFIED (search summary) | GM News 19 Jan 2026; Motorsport.com |
| Miami GP 3 May 2026; Austin late Oct; Las Vegas Nov | VERIFIED | calendar table + formula1.com results page |

## Post-row-date facts (used only where labelled)

- Richard Rogers named CMO on 4 Jun 2026 — noted in the decision path so the MD calls the right person now.
- Aston Martin named Zscaler Global Cybersecurity Partner on 25 Jun 2026 — used only to rule Aston Martin out on the app page.
- 27 May 2026: TENEX.AI named a launch partner for Google AI Threat Defense; 17 Jun 2026: an NFL team as a client (Business Observer). Not used in the brief.
- Business Observer's 15 May 2026 profile is headlined on an IPO ambition; treated as reporting, not a company statement, and not used in the score.

## Screen-outs and things not claimed

- **Leadership ties: none found.** Foster (three-time CISO; RiskIQ; Stairwell), Abouseido (Schwab, Thomson Reuters, Rockwell), Shreve, Rogers (ExtraHop) — no F1/FE or sponsorship-deal history surfaced. One profile summary lists cars and motorsport among Foster's hobbies; unverified and not used.
- **Score is un-inflated.** The thin row's 89 is not supported: $25M contracted revenue is thin for a mid-tier F1 fee (capacity 13), the brand is B2B security with no consumer pull (brand fit 13), and there is no hard external deadline (urgency 14). 71 is a HOT signal on the strength of the open lane and the real workstream, not on capacity.
- **Deal size ($2-4M a year) is an ESTIMATE**, labelled as such.
- **A podcast claim of $43M ARR in year one** was found but contradicts the company's own $25M contracted-revenue statement; not used.

## Ledger as built (N° 228, 21 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Eric Foster, Founder & CEO at TENEX.AI |
| decision_maker | person_role | yes | verified | Eric Foster, Founder & CEO, TENEX.AI at TENEX.AI |
| key_facts | funding | yes | verified | $250M Series B led by Crosspoint Capital Partners with Shield Capital and DeepWork Capital, announced 31 Mar 2026; valuation above $1B (Bloomberg, reported) |
| deck | funding | yes | verified | TENEX.AI, the Sarasota-based AI-native security operations firm, closed a $250M Series B led by Crosspoint Capital Partners on 31 March 2026 at a valuation Bloo |
| key_facts | funding | yes | verified | Crosspoint Capital Partners (lead, Series A and B), Andreessen Horowitz, Shield Capital, DeepWork Capital, Florida Opportunity Fund |
| the_case_p1 | funding | yes | verified | On 31 March 2026 TENEX.AI announced a $250M Series B led by Crosspoint Capital Partners, with Shield Capital and DeepWork Capital, at a valuation Bloomberg repo |
| key_facts | revenue | yes | verified | $25M contracted revenue within a year of launch (company statement in the 31 Mar 2026 Series B release) |
| the_case_p1 | revenue | yes | verified | The company stated $25M of contracted revenue within a year of launch and 318% year-on-year growth, first on IT-Harvest's 2026 Cyber 150. |
| key_facts | date | yes | verified | $250M Series B at a reported valuation above $1B, and former Charles Schwab CISO Bashar Abouseido appointed President, both announced 31 Mar 2026 |
| bottom_line | funding | yes | verified | A $250M Series B at a reported $1B-plus valuation, a president hired from Charles Schwab and a 250-hire, EMEA-bound growth plan put TENEX.AI at the moment a bra |
| key_facts | sponsorship | yes | verified | CrowdStrike at Mercedes, Keeper at Williams, Bitdefender at Ferrari, Okta at McLaren, Cato Networks at Alpine, NinjaOne at Audi, and Red Bull's 1Password; Senti |
| extended | funding | no | verified | On 31 March 2026 TENEX.AI announced a $250M Series B led by Crosspoint Capital Partners, with Shield Capital and DeepWork Capital, and the same day appointed fo |
| key_facts | other | yes | verified | 318% year-on-year growth and first place on IT-Harvest's 2026 Cyber 150; the round funds 250-plus hires in 2026, expansion into EMEA and deeper Google Cloud Sec |
| extended | funding | no | verified | Bloomberg reported the valuation at more than $1B; |
| key_facts | other | yes | verified | World headquarters in Sarasota, Florida; around 100 staff, targeting about 300 by end-2026 (Business Observer, reported) |
| extended | revenue | no | verified | The company states $25M of contracted revenue within a year of launch, 318% year-on-year growth and first place on IT-Harvest's 2026 Cyber 150. |
| trigger | date | yes | verified | funding round and president appointment |
| extended | revenue | no | verified | The stated uses of the $250M are 250-plus hires in 2026 across engineering, sales and SOC analysts, expansion into Europe, the Middle East and Africa, and deepe |
| why_now_callout | event | yes | verified | United States GP |
| extended | event | no | verified | The Miami GP ran on 3 May 2026 |
| extended | event | no | verified | Las Vegas GP |
