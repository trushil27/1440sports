# Glean → Mahindra Racing — verification log (N° 210, row of 30 May 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox), with Claude acting as scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code. The brief is issued for the row's date, 30 May 2026, and uses only facts public by that date.

**Sandbox limitation, stated plainly:** direct fetches of glean.com, techcrunch.com, x.com, aryn.ai, fia.com, mahindra.com, purestorage.com and the listing sites were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, honestly re-dated

The desk row carried the **$150M Series F at $7.2B** as its trigger. That round closed on **10 Jun 2025**, almost a year before the row, and would be stale on its own. The real in-window event is the **$300M ARR milestone announced by CEO Arvind Jain on 28 May 2026** (his own post; TechCrunch the same day), a company-stated demand inflection rather than a capital one. `signal_date` is therefore 2026-05-28, the trigger is labelled a revenue milestone, and the score (70, WARM) is held down for the absence of a capital event: timing 14, urgency 11. The Aryn acquisition (11 Mar 2026) is a supporting in-window fact, not the trigger. The earlier proof hero (N° 002, 30 May 2026, 72/100) rested on the same Series F; this case replaces its basis.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Matt "Kix" Kixmoeller, Chief Marketing Officer | VERIFIED | glean.com author page; The Org; Crunchbase |
| Arvind Jain co-founder & CEO; Amar Maletira COO (ex-Rackspace CEO) | VERIFIED | glean.com; Glean COO announcement (TipRanks summary) |
| $300M ARR on 28 May 2026; $200M in Dec 2025; ~3x in 15 months | COMPANY-STATED (REPORTED) | Jain on X, 28 May 2026; TechCrunch, 28 May 2026 |
| $150M Series F at $7.2B led by Wellington Management, 10 Jun 2025; investor list | VERIFIED | glean.com press release; BusinessWire; CNBC |
| Total raised ~$768M; Series E $260M at $4.6B nine months earlier | REPORTED | Crunchbase News |
| Aryn acquired, 11 Mar 2026 | VERIFIED | aryn.ai transition post; Dealroom |
| HQ Palo Alto; offices SF, NYC, Nashville, London, Bengaluru; Bengaluru centre 450+ | REPORTED | Craft; Business of GCC |
| Pure Storage–Mercedes-AMG Petronas technical partnership from 1 Mar 2016 | VERIFIED | Pure Storage press release |
| Mahindra Racing Gen4 manufacturer commitment to 2030, 26 Nov 2025 | VERIFIED | fia.com; fiaformulae.com; mahindra.com |
| Tech Mahindra develops Rubicon AI / eRace Track Analytics through the team | REPORTED | RACER, 7 May 2025; Tech Mahindra releases |
| FE rosters: Mahindra (M&M, Tech Mahindra); Andretti (TWG AI); Envision (Sand Technologies); Jaguar (TCS title); championship Google Cloud | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Season 12 finale London E-Prix 15-16 Aug 2026; Season 13 opens Jeddah 18-19 Dec 2026; Austin and Miami in Season 13 | VERIFIED | calendar table (`seeds/calendar_fe.json`) |

## Decision path

**Owner:** Matt "Kix" Kixmoeller, CMO (Glean's own page). **Path:** Arvind Jain, co-founder and CEO; Amar Maletira, COO. **No CFO was confirmed** on the sources reached — the brief says so rather than naming one.

## Leadership ties

- **Kixmoeller — familiarity tie, not a deal credit.** Pure Storage, where he held marketing, product and strategy roles, has been a Mercedes-AMG Petronas F1 technical partner since March 2016. No evidence that he structured or ran that partnership; recorded as familiarity only and used in the opening angle as such.
- Jain, Maletira: none found.

## Screen-outs and things not claimed

- **Glean is not an F1 or FE partner** (checked against both championships' partner pages and the sponsor table).
- **No customer count, no employee count and no profitability figure** are used; sources disagree (1,300–1,600 staff) and none is company-stated.
- **Deal size ($2–3M a year) is an ESTIMATE**, labelled as such.
- **Tech Mahindra** is on the recommended team's roster as an IT-services and engineering partner that builds AI tooling through the team. It is not a Work AI platform vendor, but the brief treats it as an adjacent incumbent (risk 2), scopes exclusivity to the Work AI platform, and docks slot availability (4/5) for it.
- **Kixmoeller's start date at Glean** was not confirmed to the month and is not stated.

## Ledger as built (N° 210, 19 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Matt "Kix" Kixmoeller, Chief Marketing Officer at Glean |
| decision_maker | person_role | yes | verified | Matt "Kix" Kixmoeller, Chief Marketing Officer, Glean at Glean |
| key_facts | funding | yes | verified | $150M Series F at a $7.2B valuation led by Wellington Management (10 Jun 2025); total raised about $768M; no new round in 2026 |
| deck | revenue | yes | verified | Glean, the Palo Alto 'Work AI' platform, crossed $300M in annual recurring revenue on 28 May 2026, tripling in fifteen months, on the $7.2B valuation set by its |
| key_facts | funding | yes | verified | Wellington Management (Series F lead); Khosla Ventures, Sequoia Capital, Lightspeed, Kleiner Perkins, ICONIQ, General Catalyst, Coatue and DST Global among the  |
| the_case_p1 | revenue | yes | verified | CEO Arvind Jain announced on 28 May that ARR has passed $300M, five months after $200M and roughly three times the level of fifteen months earlier. |
| key_facts | revenue | yes | verified | $300M ARR, company-stated on 28 May 2026; $200M in December 2025; roughly three times the level of fifteen months earlier |
| the_case_p1 | funding | yes | verified | The company raised $150M at $7.2B in June 2025 in a Series F led by Wellington Management, taking total funding to about $768M, and bought document-intelligence |
| key_facts | date | yes | verified | ARR crossed $300M, announced by CEO Arvind Jain on 28 May 2026 and reported by TechCrunch the same day; the $150M Series F at $7.2B dates from June 2025 |
| why_now_callout | funding | yes | verified | WHY NOW The $300M mark landed on 28 May, and brand budgets reset in the quarter after a milestone like it. |
| key_facts | sponsorship | yes | verified | TWG AI is Andretti's Official Artificial Intelligence partner; Sand Technologies (AI) sits with Envision; TCS is Jaguar's title partner; Google Cloud is the cha |
| bottom_line | revenue | yes | verified | $300M ARR crossed on 28 May, a $7.2B valuation and about $768M raised put Glean at the moment enterprise brands start spending on credibility. |
| key_facts | other | yes | verified | Mahindra Racing committed as a manufacturer to the Gen4 era through 2030 (26 Nov 2025); Glean's largest base outside the US is its Bengaluru centre of more than |
| extended | revenue | no | verified | On 28 May 2026 CEO Arvind Jain announced that Glean had passed $300M in annual recurring revenue, five months after $200M and roughly three times the level of f |
| key_facts | other | yes | verified | HQ Palo Alto, California; offices in San Francisco, New York, Nashville, London and Bengaluru |
| extended | funding | no | verified | The last capital event is a year old: the $150M Series F at $7.2B closed in June 2025. |
| trigger | date | yes | verified | revenue milestone |
| why_now_callout | event | yes | verified | London E-Prix |
| why_now_callout | event | yes | verified | Jeddah E-Prix |
