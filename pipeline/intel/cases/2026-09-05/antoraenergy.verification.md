# Antora Energy → Andretti Formula E — verification log (N° 128, 5 Sep 2026)

Built in-session at no API cost with Claude as scanner, verifier and writer through the
pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page
render ran as code. `antoraenergy.run.json` is the case record.

**Sandbox limitation, stated plainly:** direct fetches of antora.com, businesswire.com,
bloomberg.com, news.crunchbase.com, theorg.com, andrettiglobal.com, twgmotorsports.com and the
trade press (pv magazine, Energy-Storage.News, ESG Today, Canary Media) were blocked by the
egress proxy. Every claim below was checked against the search summary of the primary page
named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link.
Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, honestly labelled

The $550M Series C (30 Jul 2026, co-led by G2 Venture Partners and Eclipse) is company-announced
(Business Wire and antora.com/insights/series-c) and carried by Bloomberg, Crunchbase News,
Energy-Storage.News, ESG Today and pv magazine. **The $2.47B valuation is NOT in the company
release**; it appears in Crunchbase News and secondary aggregators. The brief says 'reported' every
time it appears and the second risk row is VALUATION IS REPORTED. The desk row's investor list was
corrected: Breakthrough Energy Ventures and Lowercarbon are EXISTING backers, not new participants.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Andrew Ponec, Co-Founder & CEO | VERIFIED | antora.com/company (summary); Crunchbase; Bloomberg |
| Justin Briggs, Co-Founder & COO (policy, communications); David Bierman, Co-Founder & CCO; Rene Griemens, CFO; no CMO listed | VERIFIED | antora.com/company (summary); Crunchbase / The Org person profiles |
| $550M Series C, 30 Jul 2026, G2 + Eclipse co-leads, investor list, second US manufacturing hub | VERIFIED | Business Wire release (summary) |
| $770M total funding; 2017 inception; San Jose base | REPORTED | Crunchbase News, 30 Jul 2026 |
| $2.47B valuation | REPORTED | Crunchbase News (not in the release) |
| Data-centre framing; signed but unnamed hyperscaler agreements | REPORTED | Bloomberg 30 Jul 2026; Energy-Storage.News / Latitude Media |
| 50 MW / 5 GWh POET Big Stone City system, 19 May 2026, >200 batteries, <12 months | VERIFIED | antora.com/insights/big-stone-release (summary); pv magazine, Power Technology |
| $150M Series B, Feb 2024, Decarbonization Partners lead | VERIFIED | antora.com/insights/series-b (summary); ARPA-E |
| HQ Sunnyvale; San Jose factory; two new facilities spring 2026 | REPORTED | antora.com manufacturing posts (summaries); directory listings |
| Andretti: Indianapolis base; TWG Motorsports also operates Cadillac F1; Nissan GEN4 powertrain; Dennis + Drugovich | VERIFIED | andrettiglobal.com (summary); Wikipedia; The Race |
| Andretti roster (TWG AI, Quest Global, Crowe UK, Reflo); no energy partner; Envision Group, TotalEnergies, Shell, Castrol lanes | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Jeddah 18-19 Dec 2026; Austin 6 Feb 2027; Miami 20 Feb 2027 | VERIFIED | calendar table (`seeds/calendar_fe.json`) |

## Screen-outs and things not claimed

- **No motorsport tie found** for Ponec, Briggs, Bierman or Griemens after two searches; `leadership_ties` is empty.
- **No revenue figure** is used: none is public.
- **Founding year** is left out of the brief: Crunchbase News says 2017, Bierman's bio says 2018.
- **Hyperscaler customers** are not named because Antora has not named them.
- **Deal size ($1.5-2.5M a year) is an ESTIMATE**, labelled as such.
- **Envision Racing** is ruled out on the owner's own battery business (Envision AESC) and the new
  Paysafe title partnership (14 Aug 2026, not yet in the sponsor table, so it is named only on the
  app page, never as a 'Brand at Team' sentence in the brief).
- **Score 71, not the desk row's 76**: MODE B halo, capital earmarked for factories, no external deadline.

## Ledger as built (N° 128, 21 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Andrew Ponec, Co-Founder & CEO at Antora Energy |
| decision_maker | person_role | yes | verified | Andrew Ponec, Co-Founder & CEO, Antora Energy at Antora Energy |
| key_facts | funding | yes | verified | $550M Series C closed 30 Jul 2026, co-led by G2 Venture Partners and Eclipse; total funding $770M; valuation of $2.47B reported by Crunchbase News, not stated b |
| deck | funding | yes | verified | Antora, the Californian thermal-battery maker whose 5 GWh South Dakota system is one of the largest storage projects in the world, closed an oversubscribed $550 |
| key_facts | funding | yes | verified | G2 Venture Partners and Eclipse (co-leads); new: Ribbit Capital, Salesforce Ventures, Activate Capital, John Doerr, Westly Group, StepStone Group, Liberty Mutua |
| the_case_p1 | revenue | yes | verified | Antora announced on 30 July that it had closed $550M of Series C funding, co-led by G2 Venture Partners and Eclipse, with Ribbit Capital, Salesforce Ventures, S |
| key_facts | date | yes | verified | $550M Series C closed 30 Jul 2026 to build a second US thermal-battery factory and deploy large-scale projects |
| the_case_p1 | funding | yes | verified | Total funding stands at $770M; |
| key_facts | sponsorship | yes | verified | No energy-storage brand on any Formula E team roster in the sponsor table; the closest lanes are Envision Group (owner of Envision Racing, which also owns the b |
| the_case_p1 | funding | yes | verified | Crunchbase News reports a $2.47B valuation, which the company has not stated. |
| key_facts | other | yes | verified | 50 MW / 5 GWh thermal battery commissioned at POET's Big Stone City plant in South Dakota on 19 May 2026, built in under 12 months; Bloomberg framed the raise a |
| bottom_line | funding | yes | verified | A $550M round closed on 30 July, one of the largest cleantech raises of the year, a 5 GWh proof plant running in South Dakota, and two US E-Prix in February: An |
| key_facts | other | yes | verified | HQ Sunnyvale, California; thermal-battery factory in San Jose expanded with two new facilities in spring 2026; second US manufacturing hub funded by the Series  |
| extended | revenue | no | verified | Antora closed an oversubscribed $550M Series C on 30 July 2026, co-led by G2 Venture Partners and Eclipse, with Ribbit Capital, Salesforce Ventures, Activate Ca |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | Total funding is $770M. |
| extended | funding | no | verified | Crunchbase News reports a $2.47B valuation; |
| why_now_callout | event | yes | verified | Austin E-Prix on 6 February 2027 |
| extended | event | no | verified | Austin E-Prix at Circuit of The Americas on 6 February 2027 |
| extended | event | no | verified | Miami E-Prix on 20 February 2027 |
| extended | event | no | verified | Austin E-Prix |
