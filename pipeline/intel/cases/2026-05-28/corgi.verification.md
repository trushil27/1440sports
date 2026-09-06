# Corgi → Cadillac F1 Team — verification log (N° 212, row of 28 May 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox), with Claude acting as scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code. The brief is issued for the row's date, 28 May 2026, and uses only facts public by that date.

**Sandbox limitation, stated plainly:** direct fetches of corgi.insure, prnewswire.com, techcrunch.com, forbes.com, axios.com, haasf1team.com, cadillacf1team.com and motorsport.com were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

The desk row carried the **$160M Series B at $1.3B (6 May 2026)**. Both that round and the **$106M Series B1 at $2.6B announced on 28 May 2026**, the row's own date, are company-announced (corgi.insure press releases, PR Newswire) and inside the window. The brief uses the B1 as the trigger and the B as context; `signal_date` is 2026-05-28.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Nico Laqua, Co-Founder & CEO (also CTO); Emily Yuan, Co-Founder & COO; founded 2024, YC S24 | VERIFIED | Y Combinator page; Corgi releases |
| $106M Series B1 led by TCV at $2.6B, 28 May 2026; total raised $378M; investor list | VERIFIED | corgi.insure press release; PR Newswire; Morningstar |
| $160M Series B led by TCV at $1.3B, 6 May 2026; total over $268M; lines written; regulatory approval July 2025 | VERIFIED | PR Newswire release; TechCrunch; The Insurer |
| $108M seed + Series A, January 2026, at $630M | REPORTED (valuation) | Axios, 8 Jan 2026; Insurance Innovation Reporter |
| Profitable in April 2026 | REPORTED (founder statement) | TechCrunch, 28 May 2026 |
| $450M annualised revenue projected by end 2026, from $40M seven months earlier; ~250 staff | REPORTED (projection) — used on the app page only, labelled | Forbes, 28 May 2026 |
| HQ San Francisco | VERIFIED | Axios; YC; Forbes |
| Dan Towriss CEO of TWG Motorsports and of Group 1001 Insurance ($66B AUM) | VERIFIED | AP, 25 Feb 2025; Andretti Global release |
| Cadillac debut Australian GP Mar 2026; Fishers 450,000 sq ft base under construction; racing from Silverstone; Charlotte hub | VERIFIED | Motorsport.com; Sky Sports |
| Orion180 multi-year partnership with Haas from Oct 2024 | VERIFIED | haasf1team.com announcement |
| Cadillac roster (no insurer / financial-services brand); Haas (Orion180); Ferrari (AON); fintech lanes at Racing Bulls, Audi, Alpine, Williams, Mercedes, Aston Martin, McLaren, Red Bull | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| British GP 3-5 Jul; United States GP 23-25 Oct; Las Vegas GP 19-21 Nov 2026 | VERIFIED | calendar table (`seeds/calendar_2026.json`); dates via ESPN / formula1.com |

## Decision path

**Owner:** Nico Laqua, Co-Founder & CEO (Corgi's own releases and the YC page). **Path:** Emily Yuan, Co-Founder & COO. **No CMO and no CFO** are listed on any source checked — the brief says so rather than inventing one.

## Leadership ties

- Laqua, Yuan: **none found** after checking (search on motorsport / Formula 1 ties returned nothing).

## Screen-outs and things not claimed

- **Revenue is left blank** in the key facts: the only figures are a founder's profitability statement and a Forbes-reported projection; both are labelled reported and neither is treated as a company financial.
- **Deal size ($3–5M a year) is an ESTIMATE**, labelled as such.
- **Corgi's licensing footprint** (which states, which lines) was not confirmed; the value section says 'within its licensed footprint' and the ask is to confirm it on the first call.
- **Post-row context for the operator (not used in the brief):** on 14 Jul 2026 Corgi launched 'Golden by Corgi', a dedicated sports and entertainment insurance vertical serving US national governing bodies (PR Newswire; USA Luge renewal, Sep 2026). That confirms the sports intent named on 28 May and makes the MODE A workstream more concrete for any follow-up conversation.
- **The 2026 calendar table carries no dates**; the British, United States and Las Vegas GP dates in the copy come from formula1.com via ESPN and are recorded in the calendar evidence entry.
- **Taxonomy:** insurance has no slot in `team_needs_taxonomy.md`; C2 (cybersecurity, the closest operational need, cyber liability cover) is used and the ops-fit sub-scores are set conservatively.

## Ledger as built (N° 212, 20 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Nico Laqua, Co-Founder & CEO at Corgi |
| decision_maker | person_role | yes | verified | Nico Laqua, Co-Founder & CEO, Corgi at Corgi |
| key_facts | funding | yes | verified | $106M Series B1 led by TCV at a $2.6B valuation (28 May 2026), three weeks after a $160M Series B led by TCV at $1.3B (6 May 2026); total raised $378M |
| deck | funding | yes | verified | Corgi, the San Francisco AI-native insurance carrier for start-ups, closed a $106M Series B1 at a $2.6B valuation on 28 May 2026, three weeks after a $160M Seri |
| key_facts | funding | yes | verified | TCV (lead, both rounds); Prime Capital, Zone 2 Ventures, Oliver Jung, Leblon Capital, Kindred Ventures, Quadri Ventures, First Order Fund, Y Combinator (S24) |
| the_case_p1 | funding | yes | verified | Corgi announced on 28 May a $106M Series B1 led by TCV at a $2.6B valuation, three weeks after the same investor led its $160M Series B at $1.3B on 6 May. |
| key_facts | date | yes | verified | $106M Series B1 at a $2.6B valuation announced 28 May 2026, doubling the $1.3B set by the $160M Series B on 6 May; new verticals named: trucking, small business |
| the_case_p1 | funding | yes | verified | Total funding stands at $378M for a company founded in 2024 that came out of stealth in January with $108M at a reported $630M. |
| key_facts | sponsorship | yes | verified | Orion180 (homeowners insurer) has a multi-year partnership with Haas since October 2024; Aon is a Ferrari partner; fintech lanes crowded at Racing Bulls (Visa,  |
| bottom_line | funding | yes | verified | Two rounds in three weeks, a $2.6B valuation and a named push into sports put Corgi at the moment a brand gets built in public. |
| key_facts | other | yes | verified | Cadillac's inaugural roster has no insurer or financial-services brand; TWG Motorsports CEO Dan Towriss also runs Group 1001, a US insurance and financial-servi |
| extended | funding | no | verified | On 28 May 2026 Corgi announced a $106M Series B1 led by TCV at a $2.6B valuation, three weeks after the same investor led a $160M Series B at $1.3B on 6 May. |
| key_facts | other | yes | verified | HQ San Francisco; full-stack carrier with US regulatory approval since July 2025; customers are US start-ups |
| extended | funding | no | verified | Total funding is $378M. |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | Corgi came out of stealth in January 2026 with $108M and has since doubled its valuation twice. |
| why_now_callout | event | yes | verified | The British GP |
| why_now_callout | event | yes | verified | United States GP |
| bottom_line | event | yes | verified | British GP |
| extended | event | no | verified | Las Vegas GP |
