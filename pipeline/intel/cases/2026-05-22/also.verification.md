# Also → Visa Cash App Racing Bulls — verification log (N° 214, issued for 22 May 2026)

Built in-session on 6 Sep 2026 at no API cost (batch 18): Claude did the research, verification and writing; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code. The brief is issued for the desk row's date, 22 May 2026.

**Sandbox limitation, stated plainly:** direct fetches of ridealso.com, prnewswire.com, techcrunch.com, bloomberg.com, rivian.com and bikeradar.com were blocked by the egress proxy. Each claim was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## What the thin row got wrong

- **Trigger date.** The row dated the $200M Series C to 22 May 2026. The round was announced closed on **31 March 2026** (company release 'ALSO Announces Strategic Partnership with DoorDash'; TechCrunch the same day), 52 days before the row: inside the 90-day window, so the case is built with `signal_date` 2026-03-31. Greenoaks' $200M at $1B was first *reported* by Bloomberg on 8 Jul 2025; the brief says so.
- **Person.** The row carried 'Undisclosed CEO'. No CEO title is listed anywhere; the company is run by **Chris Yu, Co-Founder & President** (ex-Specialized chief product and technology officer, ex-Rivian VP future programs), with **RJ Scaringe** (Rivian founder/CEO) as chairman and **Ben Steele** as Chief Commercial Officer. The brief is addressed to Yu.
- **Series.** The row said F1 with no team. F1 is kept because the category precedent (Specialized at Audi, 21 May 2026) is an F1 fact and Also is a US company; Formula E was considered (city-centre racing, electrification) and would be the fallback if Racing Bulls declines.
- **Score.** The row carried 72; re-scored at 70. Capacity is the drag: $305M raised, first product still shipping, and an e-bike partnership is a small-fee, product-heavy deal.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $200M Series C led by Greenoaks; DoorDash strategic; Prysm Capital; announced 31 Mar 2026 | VERIFIED (company release via PR Newswire / ridealso.com) + REPORTED (TechCrunch) | TechCrunch 31 Mar 2026 |
| Multi-year DoorDash autonomous-delivery agreement; Stanley Tang board observer | VERIFIED | company release; TechCrunch |
| Total funding $305M; $1B valuation | REPORTED | TechCrunch (Dealroom says $505M; discrepancy noted, lower figure used) |
| Greenoaks $200M at $1B first reported Jul 2025 | REPORTED | Bloomberg 8 Jul 2025 |
| Spin-out March 2025 with $105M from Rivian and Eclipse; Rivian minority stake; Scaringe chairman; Project Inder 2022 | VERIFIED | Rivian newsroom; TechCrunch |
| TM-B $4,500 Launch Edition revealed 22 Oct 2025; pedal-by-wire; 240W power-bank battery; US deliveries spring 2026 | VERIFIED | TechCrunch 22 Oct 2025; InsideEVs |
| Chris Yu Co-Founder & President; 10+ years at Specialized as CPTO | VERIFIED | micromobility.io; Yahoo Finance / Business Insider |
| Ben Steele CCO (ex-REI); Seattle office Apr 2026; ~350 staff Palo Alto / Seattle / Ghent | VERIFIED | GeekWire 2026 |
| Specialized official bicycle and e-bike partner of Audi Revolut F1 Team, 2026-27, announced 21 May 2026 | VERIFIED | BikeRadar; Pinkbike; audif1.com partners |
| Grid occupancy (Racing Bulls roster; Specialized/Audi; Zoox/Williams; Mobilize/Alpine; GM/Cadillac; Toyota/Haas) | VERIFIED | sponsor table `seeds/sponsors.json` |
| Canadian GP 22-24 May; Monaco 5-7 Jun; British 3-5 Jul; US GP Oct; Las Vegas Nov | VERIFIED | calendar table + formula1.com dates via ESPN / F1 Experiences |

## Screen-outs and things not claimed

- **No revenue figure**: none is public; the company is pre-delivery at the brief date.
- **No motorsport tie found** for Yu, Steele or Scaringe after checking; `leadership_ties` is empty. Yu's Specialized tenure is a category tie, not a motorsport one.
- **Also is not a partner of any F1 or FE team** (sponsor table; live search).
- **Deal size ($1-2M a year plus product) is an ESTIMATE**, labelled as such.
- **The Ford / Rivian OEM sensitivity is stated as a risk**, not resolved: Ford's exclusivity terms at Racing Bulls are not public.
- **Post-brief events, for the operator (after 22 May 2026):** Electrek (13 Aug 2026) reported TM-B deliveries delayed again; Also announced a **$150M Series D led by Prysm Capital on 19 Aug 2026** (Eclipse, Greenoaks, MVP Ventures participating) to take its small EVs autonomous. Neither is in the brief, which is issued for 22 May; both strengthen capacity and weaken the 'deliveries this spring' line if the case is re-run today.

## Decision path

Chris Yu (Co-Founder & President) is the sponsorship owner. Path: Ben Steele (Chief Commercial Officer) and RJ Scaringe (Chairman). No CEO, CMO or CFO title is listed on any source found.

## Ledger as built (N° 214, 26 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Chris Yu, Co-Founder & President at Also |
| decision_maker | person_role | yes | verified | Chris Yu, Co-Founder & President, Also at Also |
| key_facts | funding | yes | verified | $200M Series C led by Greenoaks with DoorDash (strategic) and Prysm Capital, announced 31 March 2026; total funding $305M at a $1B valuation (TechCrunch) |
| deck | funding | yes | verified | Also, the small-EV company spun out of Rivian, closed a $200M Series C led by Greenoaks on 31 March 2026 with DoorDash as strategic investor, taking funding to  |
| key_facts | funding | yes | verified | Greenoaks (lead); DoorDash; Prysm Capital; Rivian and Eclipse ($105M at the March 2025 spin-out) |
| the_case_p1 | funding | yes | verified | Also spun out of Rivian in March 2025 with $105M from Rivian and Eclipse after three years inside the carmaker as Project Inder. |
| key_facts | date | yes | verified | $200M Series C closed with DoorDash as strategic investor and a multi-year autonomous-delivery agreement, announced 31 March 2026 |
| the_case_p1 | funding | yes | verified | Bloomberg reported Greenoaks' $200M at a $1B valuation in July 2025; |
| key_facts | sponsorship | yes | verified | Specialized became Audi Revolut F1 Team's official bicycle and e-bike partner for 2026-27, announced 21 May 2026; no other bicycle, e-bike or micromobility part |
| the_case_p1 | funding | yes | verified | Total funding is $305M. |
| key_facts | other | yes | verified | Chris Yu, Co-Founder & President, spent more than ten years at Specialized as chief product and technology officer; Also is a Rivian spin-out with RJ Scaringe a |
| the_case_p1 | funding | yes | verified | The first product, the $4,500 TM-B e-bike revealed in October 2025, starts US deliveries this spring; |
| key_facts | other | yes | verified | HQ Palo Alto; Seattle office opened April 2026; about 350 staff across Palo Alto, Seattle and Ghent, Belgium |
| the_case_p2 | funding | yes | verified | The template exists, the man who built the incumbent's product now runs the challenger, and the challenger has a fresh $200M to spend. |
| trigger | date | yes | verified | funding round |
| why_now_callout | funding | yes | verified | Also's US deliveries begin this spring on a fresh $200M. |
| bottom_line | funding | yes | verified | A $200M Series C with DoorDash aboard, a first product shipping this spring, and a president who built the product line of the brand that just took the e-bike l |
| why_team_para | funding | no | verified | Racing Bulls carries Visa and Cash App at the front, with Yugo, Student.com, Airtasker and Hugo behind them: a roster built for a younger consumer audience, the |
| extended | funding | no | verified | On 31 March 2026 Also announced its $200M Series C closed, led by Greenoaks with DoorDash joining as strategic investor alongside Prysm Capital, together with a |
| extended | funding | no | verified | TechCrunch puts total funding at $305M and the valuation at $1B. |
| extended | funding | no | verified | The $4,500 TM-B Launch Edition, revealed in October 2025, begins US deliveries this spring, with Europe to follow; |
| extended | funding | no | verified | a $4,500 design-led e-bike from a Rivian spin-out sells to the same people. |
| why_now_callout | event | yes | verified | M. Monaco GP |
| why_now_callout | event | yes | verified | British GP |
| extended | event | no | verified | Monaco GP |
| extended | event | no | verified | Las Vegas GP |
