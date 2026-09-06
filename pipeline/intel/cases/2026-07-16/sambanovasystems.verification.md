# SambaNova Systems → TGR Haas F1 Team — verification log (N° 161, brief dated 16 Jul 2026)

Built in-session on 6 Sep 2026 at no API cost from a case spec: Claude did the research and writing; the pipeline's calendar and sponsor-table checks, 13-rule audit and 2-page render ran as code. The brief is issued for the date the signal sits on in the desk (16 Jul 2026); the trigger is the 8 Jul 2026 first close, inside the 90-day window.

**Sandbox limitation, stated plainly:** direct fetches of generalatlantic.com, sambanova.ai, businesswire.com, techcrunch.com, cnbc.com, bloomberg.com and theorg.com were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## The trigger

Company-announced: the SambaNova release of 8 Jul 2026 (carried by General Atlantic, BusinessWire, TechCrunch, Bloomberg, Quartz) states the $1B first close at $11B post-money, the lead and named investors, the expected second close and the use of proceeds. The JPMorganChase inference-infrastructure selection was reported the same day (TechCrunch, The AI Insider). The thin row's source (TechCrunch) is a credible secondary; the primary release is now the evidence URL.

## Corrections to the thin row

- The thin row (8 Jul) said "CEO publicly on record strongly considering IPO". The sourced wording is that Liang said an IPO in 2027, most likely in the US, is under consideration; the brief says "under consideration (reported)" and scores URGENCY 13, not higher.
- The row's series/team hint (Haas) was checked against the sponsor table and kept on merit: no compute, AI, cloud or chip partner on the Haas roster.
- Scored 77, matching the row's 77 but with a different composition: capacity 18 on the $1B close, ops fit 15 (MODE A on-premises inference, product-to-need 6 because the team use is a proposal, not a deployment).

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $1B Series F first close at $11B post-money; General Atlantic lead; Seligman, T. Rowe Price, Capital Group; BlackRock, Intel Capital, QIA, Battery, Vista, Volantis; second close expected | VERIFIED (company release via search summary) | generalatlantic.com; BusinessWire |
| JPMorganChase inference-infrastructure partner, SN40L/SN50 on-premises | REPORTED | TechCrunch; The AI Insider, 8 Jul 2026 |
| $350M Series E, Feb 2026, Intel strategic investment and multi-year partnership; implied ~$2.2B | REPORTED | CNBC 24 Feb 2026; DCD |
| Intel takeover talks near $1.6B incl. debt stalled | REPORTED | Bloomberg (Dec 2025 / 21 Jan 2026) via DCD, EE Times |
| SN40L (Sep 2023), SN50 shipping H2 2026, SoftBank first deployment; customers Saudi Aramco, OVHcloud | REPORTED | DCD (Mar 2026); TechCrunch |
| IPO in 2027, most likely US, under consideration | REPORTED | TechCrunch / IndexBox interview summary |
| Founded 2017 Palo Alto by Liang, Olukotun, Ré; Liang ex-Oracle SVP (SPARC) and Sun | VERIFIED | sambanova.ai about page; Clay / MWC bios |
| Total funding ~$2.48B | REPORTED (Tracxn) | brief says "reported" |
| Annie Shea Weckesser CMO; Harry Ault CRO; Matt Padfield CFO (12 Jun 2026) | VERIFIED / REPORTED | BusinessWire 12 Jun 2026; LinkedIn; The Org; Crunchbase |
| Clyde Hosein President & COO | CONFLICTING — not used | The Org lists him; Equilar records tenure Apr 2025–Mar 2026 |
| Groq Official Partner of McLaren, logo from 2025 Singapore GP | VERIFIED | groq.com newsroom; PR Newswire 26 Sep 2025 |
| Haas: Kannapolis HQ, Banbury race ops, Maranello design office; TGR title 2026; Mphasis, CommScope/Ruckus, Orion180 | VERIFIED | haasf1team.com; formula1.com |
| Haas roster and rival lanes across the grid | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| United States GP (Oct), Las Vegas GP (Nov), Miami GP 2026 | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Screen-outs and things not claimed

- **Leadership ties:** no SambaNova leader found with prior F1/FE employment or sponsorship history; `leadership_ties` empty after checking.
- **Revenue:** not public; none used.
- **Mohsen Moazami** (Vice Chair, Global Strategy and Partnerships) joined in August 2026, after the brief date; not used.
- **The Haas deployment** described in VALUE is a proposal, written as one; no SambaNova system is deployed at any F1 team.
- **Deal size $4-7M a year** is a 1440 ESTIMATE, labelled as such.

## Ledger as built (N° 161, 22 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Rodrigo Liang, Co-Founder & CEO at SambaNova Systems |
| decision_maker | person_role | yes | verified | Rodrigo Liang, Co-Founder & CEO, SambaNova Systems at SambaNova Systems |
| key_facts | funding | yes | verified | $1B first close of a Series F at an $11B post-money valuation, led by General Atlantic with Seligman Ventures, T. Rowe Price Associates and Capital Group (compa |
| deck | funding | yes | verified | SambaNova, the Palo Alto AI-chip maker, completed the first close of a $1B Series F at an $11B post-money valuation on 8 July 2026, led by General Atlantic, fiv |
| key_facts | funding | yes | verified | General Atlantic (lead), Seligman Ventures, T. Rowe Price Associates, Capital Group, BlackRock, Intel Capital, Qatar Investment Authority, Battery Ventures, Vis |
| the_case_p1 | funding | yes | verified | General Atlantic led the $1B first close, with Seligman Ventures, T. |
| key_facts | date | yes | verified | $1B Series F first close at $11B post-money announced 8 Jul 2026; JPMorganChase named as an on-premises inference-infrastructure customer the same day |
| the_case_p1 | funding | yes | verified | Five months earlier SambaNova raised a $350M Series E with Intel after Bloomberg-reported takeover talks near $1.6B stalled, so the price has risen roughly five |
| key_facts | sponsorship | yes | verified | Groq at McLaren (Official Partner, inference chip on the car since the 2025 Singapore GP); AMD at Mercedes; ARM (Aston Martin); CoreWeave at Aston Martin; Core  |
| bottom_line | funding | yes | verified | A $1B first close at $11B, a fivefold re-rating in five months, JPMorganChase on-premises and an IPO under consideration put SambaNova at peak brand-investment  |
| key_facts | other | yes | verified | On-premises inference for a cost-capped team: SN40L systems running open-weight models on the team's own data, the JPMorganChase private-inference story at a ra |
| extended | funding | no | verified | On 8 July 2026 SambaNova announced the first close of $1B in strategic financing as part of a Series F at an $11B post-money valuation, led by General Atlantic  |
| key_facts | other | yes | verified | HQ Palo Alto, California; founded 2017 out of Stanford by Rodrigo Liang, Kunle Olukotun and Christopher Ré |
| extended | funding | no | verified | In December 2025 Bloomberg reported Intel in advanced talks to buy SambaNova for about $1.6B including debt. |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | in February 2026 Intel instead took a stake in a $350M Series E at a reported ~$2.2B valuation and signed a multi-year partnership. |
| key_facts | event | yes | verified | Singapore GP |
| extended | funding | no | verified | Five months later the company priced at $11B. |
| the_case_p2 | event | yes | verified | Singapore GP |
| why_now_callout | event | yes | verified | The United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | United States GP |
