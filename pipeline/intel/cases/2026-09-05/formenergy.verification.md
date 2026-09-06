# Form Energy → Andretti Formula E — verification log (N° 129, 5 Sep 2026)

Built in-session at no API cost with Claude as scanner, verifier and writer through the
pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page
render ran as code. `formenergy.run.json` is the case record.

**Sandbox limitation, stated plainly:** direct fetches of formenergy.com, axios.com,
techcrunch.com, energy-storage.news, andrettiglobal.com and motorsport.com were blocked by the
egress proxy. Every claim below was checked against the search summary of the primary page named
as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link.
Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, corrected

The desk row carried '~$4.3B (PitchBook estimate)' and a trigger date of 11 Aug. Both are wrong:
the company release is dated **12 Aug 2026**, and Axios reports the Series G priced at **$1.75B
pre-money, down from about $3B in October 2024** — a down round. The brief says so in the deck,
the case, the first risk row and the app page. The '2027 listing' is reported by Axios and
TechCrunch, not company-confirmed, and is labelled reported wherever it appears.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Mateo Jaramillo, Co-Founder & CEO; ex-Tesla energy (Powerwall) | VERIFIED | formenergy.com/team (summary); Boston Globe |
| Ted Wiley, Co-Founder, President & COO; Navneet Govil CFO; Wes Sloan COO (new); no CMO listed | VERIFIED | formenergy.com/about (summary, 17 Aug 2026); company announcements; Crunchbase / The Org |
| $750M Series G, 12 Aug 2026, T. Rowe Price lead, investor list, >$2B total equity, backlog 20→80 GWh | VERIFIED | Form Energy release (summary); TechCrunch; Mercom; Boston Globe |
| $1.75B pre-money, down from ~$3B (Oct 2024) | REPORTED | Axios Pro, 12 Aug 2026 |
| 2027 listing being prepared | REPORTED | Axios 28 Jan 2026; TechCrunch 26 Feb 2026 |
| 300 MW / 30 GWh Google–Xcel system, Pine Island MN; 1.9 GW deal; phases 2028-31 | VERIFIED | TechCrunch 24 Feb 2026; Energy-Storage.News; Xcel newsroom (summaries) |
| Google paid ~$1B | REPORTED | TechCrunch 26 Feb 2026 |
| Crusoe 12 GWh agreement, CERAWeek Mar 2026, deliveries from 2027 | VERIFIED | Energy-Storage.News / Renewable Energy World (summaries) |
| Weirton: 550,000 sq ft, former steel site, ~400 staff, ≥500 MW/yr by 2028, shipments early 2027 | VERIFIED | formenergy.com/form-factory-1 (summary); WTOV9 |
| HQ Somerville; founded 2017; founders | VERIFIED | Wikipedia; Crunchbase; MIT News |
| Andretti: Indianapolis; TWG Motorsports also operates Cadillac F1; Nissan GEN4; Dennis + Drugovich | VERIFIED | andrettiglobal.com (summary); Wikipedia; The Race |
| DS Automobiles exit after Season 12; Penske entry unregistered at last report | REPORTED | Motorsport.com |
| Andretti roster; Google Cloud championship partner; Envision Group, TotalEnergies, Shell, Castrol lanes | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Jeddah 18-19 Dec 2026; Austin 6 Feb 2027; Miami 20 Feb 2027 | VERIFIED | calendar table (`seeds/calendar_fe.json`) |

## Screen-outs and things not claimed

- **No motorsport tie found** for Jaramillo, Wiley, Govil or Sloan after three searches (beware the
  'Phorm Energy' NASCAR and 'Monster Energy' name collisions); `leadership_ties` is empty.
- **No revenue figure** is used: none is public.
- **COO** is stated both ways because the sources conflict: the leadership page (17 Aug 2026) lists
  Wiley as President and COO; a company announcement names Wes Sloan as incoming COO.
- **Deal size ($1.5-2.5M a year) is an ESTIMATE**, labelled as such.
- **DS Penske** (the desk row's team) is ruled out transparently: DS leaves after Season 12 and
  Penske's Season 13 entry was unregistered at the last report.
- **Andretti is also the team recommended for N° 128 Antora Energy** the same day. That is not a
  placement; the desk judges whitespace against the sponsor table only. Both are honest MODE B
  halos with different audiences (Antora: industrial heat and hyperscalers; Form: utilities,
  regulators and a listing).
- **Crusoe** (N° 121) is named as a customer only; it holds no grid seat.
- **Score 70, not the desk row's 74**: down round, factory-earmarked capital, MODE B, listing only reported.

## Ledger as built (N° 129, 22 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Mateo Jaramillo, Co-Founder & CEO at Form Energy |
| decision_maker | person_role | yes | verified | Mateo Jaramillo, Co-Founder & CEO, Form Energy at Form Energy |
| key_facts | funding | yes | verified | $750M Series G announced 12 Aug 2026, led by T. Rowe Price; total equity raised over $2B; Axios reports a $1.75B pre-money valuation, down from about $3B in Oct |
| deck | funding | yes | verified | Form Energy, the Somerville iron-air battery maker building Google's 30 GWh, 100-hour system in Minnesota, closed a $750M Series G led by T. |
| key_facts | funding | yes | verified | T. Rowe Price (lead); new: Sequoia Capital, Janus Henderson, Franklin Templeton, PEAK6; existing: Breakthrough Energy Ventures, Coatue, TPG Rise Climate, GE Ver |
| deck | funding | yes | verified | Rowe Price on 12 August 2026, taking total equity past $2B as its announced backlog jumped from roughly 20 GWh to 80 GWh. |
| key_facts | date | yes | verified | $750M Series G announced 12 Aug 2026 to scale Form Factory 1 in Weirton, West Virginia and fund deployments; announced backlog up from roughly 20 GWh to 80 GWh |
| the_case_p1 | funding | yes | verified | Form announced the $750M Series G on 12 August, led by T. |
| key_facts | sponsorship | yes | verified | No energy-storage brand on any Formula E team roster in the sponsor table; Envision Group (owner of Envision Racing) owns the battery maker Envision AESC; Total |
| the_case_p1 | funding | yes | verified | Total equity passes $2B; |
| key_facts | other | yes | verified | 300 MW / 30 GWh, 100-hour iron-air system for Google and Xcel Energy at Pine Island, Minnesota (Feb 2026; TechCrunch reports Google paid about $1B), 12 GWh for  |
| the_case_p1 | funding | yes | verified | Axios reports the round priced at $1.75B pre-money, down from about $3B in October 2024. |
| key_facts | other | yes | verified | HQ Somerville, Massachusetts; Form Factory 1 in Weirton, West Virginia (550,000 sq ft on a former steel-mill site, about 400 employees, planned 500 MW a year by |
| bottom_line | funding | yes | verified | $750M closed on 12 August, an 80 GWh order book led by Google and Crusoe, a West Virginia factory and a reported 2027 listing: Form Energy needs a national bran |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | Form Energy announced a $750M Series G on 12 August 2026, led by T. |
| extended | funding | no | verified | Total equity raised now exceeds $2B. |
| extended | funding | no | verified | The anchor is the 300 MW / 30 GWh Google and Xcel Energy system at Pine Island, Minnesota, announced in February 2026 as the largest battery system by energy ca |
| why_now_callout | event | yes | verified | Austin E-Prix on 6 February 2027 |
| extended | event | no | verified | Austin E-Prix at Circuit of The Americas on 6 February 2027 |
| extended | event | no | verified | Miami E-Prix on 20 February 2027 |
| extended | event | no | verified | Austin E-Prix |
