# UiPath → TGR Haas F1 Team — verification log (N° 193, issued for 12 Jun 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox), with Claude acting as scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code from the case spec `uipath.case.json`.

**Sandbox limitation, stated plainly:** uipath.com, ir.uipath.com, sec.gov, businesswire.com, nasdaq.com and morningstar.com were blocked by the egress proxy. Every claim below was checked against the search summary of the primary page named as the evidence URL. Treat VERIFIED lines as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, re-dated

The thin row carried `new_leadership` (the CMO appointment of 25 Aug 2025, 291 days before the row and therefore stale on its own) and a diginomica article about the May 2025 quarter. The real in-window trigger is the **Q1 fiscal 2027 release of 28 May 2026** (15 days before the row): the first GAAP-profitable quarter in company history. The earlier check's correction stands: a first profitable *quarter*, not a first profitable year, and no agentic-ARR figure is used because none is stated in the release.

## The team, re-chosen

The thin row suggested McLaren. McLaren's roster already carries Workday, Alteryx, Smartsheet, Freshworks and Dropbox in the enterprise-workflow lane at a top-tier price. A first build of this case pointed at Visa Cash App Racing Bulls; the pipeline's GRID FIT check marked both Red Bull teams TAKEN because **Siemens is categorised as industrial software / automation at Red Bull Racing and Racing Bulls** (`seeds/sponsor_categories.json`). That adjacency is real enough that a team would have to clear it with Siemens, so the case was re-pointed to **TGR Haas F1 Team**: the American privateer, no enterprise-automation, AI-agent or workflow partner in the sponsor table, three US races, and the leanest back office on the grid. Two 2026 Haas additions sit outside the table and are therefore not written as "Brand at Team" in the copy: **Emburse** (Official Travel and Expense Solution Partner, Business Wire 3 Jun 2026) and **Exein** (physical AI security, from the Belgian GP). Emburse is why the UiPath workstream is scoped to freight and customs paperwork, procurement and cost-cap reporting, not expenses. Case N° 196 (TensorWave) in this batch also recommends Haas: our signals are not placements, and each is judged against the real roster only.

## Ledger (all claims verified against the release, the appointment notice and the tables)

| Claim | Status | Evidence |
|---|---|---|
| Michael Atalla, Chief Marketing Officer, appointed 25 Aug 2025; ex-F5 SVP Worldwide Marketing; ~15 years at Microsoft | VERIFIED | ir.uipath.com / Business Wire, 25 Aug 2025 |
| Revenue $418M (+17%), ARR $1.901B (+12%), GAAP operating income $28M, first GAAP-profitable quarter; cash etc. $1.42B; $500M buyback (Mar 2026); FY2027 guidance $1.776-1.781B revenue | VERIFIED | ir.uipath.com Q1 FY2027 release, 28 May 2026 (also SEC 8-K Ex. 99.1) |
| Daniel Dines, Founder and CEO since 1 Jun 2024 | VERIFIED | uipath.com founder's update; diginomica |
| Ashim Gupta, CFO and COO on the row date | VERIFIED | ir.uipath.com, Sep 2024 (COO expansion) |
| HQ New York, 1 Vanderbilt Ave; founded Bucharest 2005; ~3,900 employees | REPORTED | Wikipedia / CB Insights / Unify |
| Haas: Kannapolis HQ, Banbury and Maranello sites; Toyota Gazoo Racing title from 2026 | VERIFIED | Ruckus Networks release Jan 2026; formula1.com Dec 2025; Wikipedia |
| Haas roster (TGR, Mphasis, Haas Automation, Ruckus, CommScope, Infobip); rivals Siemens (both Red Bull teams), ServiceNow (Aston Martin), SAP and Meta AI (Mercedes), Salesforce (F1 series; departed McLaren), Workday/Alteryx/Smartsheet/Freshworks (McLaren), IFS/TWG AI (Cadillac), Airia (Williams), NinjaOne (Audi), IBM/Genesys/DXC (Ferrari), Microsoft (Mercedes, Alpine) | VERIFIED | sponsor table (`seeds/sponsors.json`, `seeds/sponsor_categories.json`) |
| United States GP (Austin, late Oct), Las Vegas GP (Nov), Miami GP (May) | VERIFIED | calendar table (`seeds/calendar_2026.json`); formula1.com |

## Decision path

Sponsorship owner: **Michael Atalla, CMO** (brand, performance, demand generation, communications). C-level sponsor: **Daniel Dines, Founder and CEO**. Finance/operations: **Ashim Gupta, CFO and COO** on the row date. **Update after the row date (3 Sep 2026, Q2 FY2027 release):** Hitesh Ramani promoted to CFO; Gupta now COO only; Brad Brubaker named Chief Legal and Administrative Officer. Q2 FY2027: revenue $410M (+13%), ARR $1.938B (+12%), net income $36M, the second consecutive GAAP-profitable quarter, which strengthens the case for a re-dated approach today.

## Leadership ties

`leadership_ties: []` — searched Atalla, Dines and Gupta against F1/FE/motorsport; none found. No UiPath partnership with any team, series or race was found on the F1 or Formula E partner pages or in sponsorship coverage.

## Screen-outs and things not claimed

- **No agentic-product ARR figure** is used (not in the release).
- **The F1 workstream is 1440's proposal**, not a UiPath case study: UiPath publishes finance, procurement and document-processing work for other industries; no sports customer was found.
- **Deal size ($3-5M a year) is an ESTIMATE**, labelled as such.
- **Score 73, not the row's 80:** the trigger is an earnings milestone rather than fresh capital (urgency 12) and the archetype is generic B2B software (brand fit 14).

## Ledger as built (N° 193, 19 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Michael Atalla, Chief Marketing Officer at UiPath |
| decision_maker | person_role | yes | verified | Michael Atalla, Chief Marketing Officer, UiPath at UiPath |
| key_facts | funding | yes | verified | Public company (NYSE: PATH); cash, cash equivalents and marketable securities of $1.42B at 30 Apr 2026; $500M buyback authorised in March 2026 |
| deck | revenue | yes | verified | UiPath, the New York-headquartered enterprise-automation company, reported on 28 May 2026 the first GAAP-profitable quarter in its history: revenue of $418M, up |
| key_facts | revenue | yes | verified | Q1 FY2027 revenue $418M (+17% YoY); ARR $1.901B at 30 Apr 2026 (+12%); FY2027 guidance revenue $1.776-1.781B |
| the_case_p1 | revenue | yes | verified | On 28 May UiPath reported first-quarter fiscal 2027 revenue of $418M, up 17% year on year, ARR of $1.901B and GAAP operating income of $28M, its first GAAP-prof |
| key_facts | date | yes | verified | Q1 FY2027 results, 28 May 2026: first GAAP-profitable quarter in company history (GAAP operating income $28M) |
| the_case_p1 | funding | yes | verified | Cash, equivalents and marketable securities stood at $1.42B and the board authorised a $500M buyback in March; |
| key_facts | sponsorship | yes | verified | ServiceNow sits with Aston Martin Aramco; SAP and Meta AI with Mercedes; Siemens (industrial software / automation) with both Red Bull teams; Salesforce is an F |
| the_case_p1 | revenue | yes | verified | full-year guidance is $1.776-1.781B of revenue. |
| key_facts | other | yes | verified | CMO Michael Atalla, appointed 25 Aug 2025 from F5 after about fifteen years at Microsoft, owns brand; founder Daniel Dines back as CEO since June 2024 |
| bottom_line | funding | yes | verified | A first GAAP-profitable quarter on 28 May, $1.42B of cash and a CMO rebuilding the brand around agentic AI give UiPath the budget and the motive; |
| key_facts | other | yes | verified | HQ New York (1 Vanderbilt Ave); founded in Bucharest in 2005; about 3,900 employees |
| the_case_p2 | sponsorship | yes | verified | SAP at Mercedes |
| trigger | date | yes | verified | earnings milestone |
| extended | revenue | no | verified | On 28 May 2026 UiPath reported first-quarter fiscal 2027 revenue of $418M, up 17% year on year, ARR of $1.901B and GAAP operating income of $28M: the first GAAP |
| extended | revenue | no | verified | Cash, cash equivalents and marketable securities were $1.42B at 30 April 2026, the board authorised a $500M buyback in March, and full-year guidance is $1.776-1 |
| extended | event | no | verified | The United States GP |
| extended | event | no | verified | Las Vegas GP |
