# Mercury → Cadillac F1 Team — verification log (N° 216, issued for 20 May 2026)

Built in-session on 6 Sep 2026 at no API cost (batch 18): Claude did the research, verification and writing; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code. The brief is issued for the desk row's date, 20 May 2026; the trigger is dated the same day.

**Sandbox limitation, stated plainly:** direct fetches of mercury.com, businesswire.com, cnbc.com and the calendar sites were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## What the thin row got right and wrong

- **Person, trigger and source are correct**: Immad Akhund, Co-Founder & CEO; $200M Series D at $5.2B; Business Wire release of 20 May 2026. The row's 'Mercury Command AI launch pending' was true on the day (Command launched 16 Jun 2026, after the brief date, and is not claimed as launched).
- **Score.** The row carried 82. Re-scored at 74: capacity and timing are strong, but there is no engineering workstream (MODE B, ops fit 11/20) and consumer reach is limited.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $200M Series D at $5.2B led by TCV; a16z, Coatue, CRV, Sapphire, Sequoia, Spark; 20 May 2026 | VERIFIED (company release) | Business Wire 20 May 2026; mercury.com blog |
| Valuation up 49% in 14 months | REPORTED | CNBC 20 May 2026 |
| $300M Series C at $3.5B led by Sequoia, Mar 2025; $500M revenue 2024; ten profitable quarters; $156B volume | VERIFIED (company release) | Business Wire 26 Mar 2025 |
| $650M annualised revenue (Q3 2025); 300,000+ customers; one in three US startups; applications 2.5x Q1 2026 | VERIFIED (company release) | Business Wire 20 May 2026; Fortune 7 Nov 2025 |
| OCC conditional approval, 27 Apr 2026; Mercury Bank, N.A.; Utah; Jon Auxier (ex-SoFi Bank CFO); application Dec 2025 | VERIFIED (company release) | Business Wire 27 Apr 2026; OCC Corporate Decision #1372 |
| Akhund CEO, Tagher CTO, Zhang COO (founders, 2017); Dan Kang CFO (May 2025); Rachel Moncton Oatway VP Marketing (reports to Akhund); no CMO | VERIFIED / REPORTED (The Org, LinkedIn) | mercury.com blog; The Org |
| HQ San Francisco | VERIFIED | Business Wire |
| Grid occupancy (Cadillac roster; Airwallex + Mastercard + Goldman / McLaren; Revolut / Audi; Cash App + Visa / Racing Bulls; Nu + UBS / Mercedes; Barclays + BNY / Williams; UniCredit / Ferrari; Coinbase + Circle + Public / Aston Martin; Visa + Carlyle / Red Bull; MoneyGram / Haas; Mobilize + eToro / Alpine) | VERIFIED | sponsor table `seeds/sponsors.json` |
| Cadillac is F1's first new American team since Haas (2016) | VERIFIED | formula1.com / ESPN |
| Canadian GP 22-24 May; Monaco 5-7 Jun; British 3-5 Jul; US GP Oct; Las Vegas Nov | VERIFIED | calendar table + formula1.com dates via ESPN / F1 Experiences |

## Screen-outs and things not claimed

- **Employee count** (Tracxn: 1,729 at Jul 2026) is not used.
- **No motorsport tie found** for Akhund, Tagher, Zhang, Kang or Oatway after checking; `leadership_ties` is empty.
- **Mercury is not a partner of any F1 or FE team** (sponsor table; live search).
- **MODE B is stated plainly**: there is no engineering workstream; the value is audience, hospitality and supplier banking, and ops fit is scored 11/20.
- **The TWG Global owner overlap** (Cadillac's co-owner is a financial-services group) is listed as a risk to test, not resolved.
- **Deal size ($4-6M a year) is an ESTIMATE**, labelled as such.
- **Ramp**, a Mercury competitor, is on 1440's approached list (`data/approached.json`); this brief does not re-pitch Ramp and treats Mercury on its own merits.

## Decision path

Immad Akhund (Co-Founder & CEO) is the sponsorship owner. Path: Rachel Moncton Oatway (VP, Marketing, reporting to Akhund) and Dan Kang (CFO). Jason Zhang (Co-Founder & COO) and Jon Auxier (President & CEO, Mercury Bank) are the operating counterparts. No CMO is listed.

## Ledger as built (N° 216, 27 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Immad Akhund, Co-Founder & CEO at Mercury |
| decision_maker | person_role | yes | verified | Immad Akhund, Co-Founder & CEO, Mercury at Mercury |
| key_facts | funding | yes | verified | $200M Series D at a $5.2B valuation led by TCV, with Andreessen Horowitz, Coatue, CRV, Sapphire Ventures, Sequoia Capital and Spark Capital returning, announced |
| deck | funding | yes | verified | Mercury, the business-banking platform used by one in three US startups, announced a $200M Series D at a $5.2B valuation led by TCV on 20 May 2026, three weeks  |
| key_facts | funding | yes | verified | TCV (lead, Series D); Sequoia Capital led the $300M Series C at $3.5B in March 2025; Andreessen Horowitz, Coatue, CRV, Spark Capital, Sapphire Ventures |
| deck | revenue | yes | verified | Revenue passed $650M annualised in 2025 after ten straight profitable quarters. |
| key_facts | revenue | yes | verified | $650M annualised revenue reached in Q3 2025 (company-stated); $500M revenue in 2024 with ten straight profitable quarters (Series C release, March 2025) |
| the_case_p1 | funding | yes | verified | On 20 May Mercury announced a $200M Series D at a $5.2B valuation led by TCV, with Andreessen Horowitz, Coatue, CRV, Sapphire, Sequoia and Spark returning; |
| key_facts | date | yes | verified | $200M Series D at a $5.2B valuation led by TCV, announced 20 May 2026 |
| the_case_p1 | funding | yes | verified | CNBC puts the valuation up 49% in 14 months. |
| key_facts | sponsorship | yes | verified | Airwallex at McLaren, Revolut as Audi's title partner, Cash App at Racing Bulls, Nu at Mercedes, Barclays and BNY at Williams; Cadillac's inaugural roster carri |
| the_case_p1 | revenue | yes | verified | Sequoia led the $300M Series C at $3.5B in March 2025, when Mercury reported $500M revenue for 2024 and ten straight profitable quarters. |
| key_facts | other | yes | verified | OCC conditional approval for Mercury Bank, N.A. on 27 April 2026; more than 300,000 customers including one in three US startups; Cadillac is the first new Amer |
| the_case_p1 | revenue | yes | verified | It reached $650M annualised revenue in Q3 2025 and serves more than 300,000 customers, one in three US startups. |
| key_facts | other | yes | verified | HQ San Francisco; founded 2017; Mercury Bank, N.A. to be headquartered in Utah |
| bottom_line | revenue | yes | verified | A $200M round at $5.2B, $650M-plus of profitable revenue, and a bank charter that turns Mercury into a bank in its own name give it the budget, the motive and a |
| trigger | date | yes | verified | funding round |
| the_case_p2 | sponsorship | yes | verified | Airwallex at McLaren |
| the_case_p2 | sponsorship | yes | verified | Cash App at Racing Bulls |
| the_case_p2 | sponsorship | yes | verified | Nu at Mercedes. |
| extended | funding | no | verified | On 20 May 2026 Mercury announced a $200M Series D at a $5.2B valuation led by TCV, with Andreessen Horowitz, Coatue, CRV, Sapphire Ventures, Sequoia Capital and |
| extended | funding | no | verified | CNBC puts the valuation up 49% in 14 months from the $3.5B Sequoia set in March 2025. |
| extended | revenue | no | verified | Mercury reported $500M revenue for 2024 with ten straight profitable quarters at the Series C, reached $650M annualised revenue in Q3 2025, and saw applications |
| why_now_callout | event | yes | verified | Canadian GP |
| why_now_callout | event | yes | verified | British GP |
| extended | event | no | verified | Monaco GP |
| extended | event | no | verified | Las Vegas GP |
