# Dana Incorporated → Mahindra Racing — verification log (N° 240, 11 Jun 2026)

Built in-session at no model-API cost: Claude acted as scanner, verifier and writer through the
pipeline's injectable stages; freshness, dedup, scoring, the claims ledger with the calendar and
sponsor-table checks, the 13-rule audit and the strict 2-page render ran as code.

**Sandbox limitation, stated plainly:** direct fetches of dana.com, eaton.com, prnewswire.com,
sec.gov, danatm4.com and fiaformulae.com were blocked by the egress proxy. Every claim below was
checked against the search summary of the primary page named as its evidence URL. Treat each
VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads
VERIFY BEFORE CIRCULATION.

## The trigger

**11 June 2026** — Eaton and Dana signed a definitive agreement to separate Eaton's Mobility Group
(the Vehicle and eMobility segments) and combine it with Dana in a Reverse Morris Trust. Company
announcements on both sides, plus PRNewswire 302797498 and Dana's Form 8-K / Form 425. Inside the
90-day window for a 6 September sweep; the row sits on the trigger's own date.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| RMT announced 11 Jun 2026; combined company valued at more than $10B | VERIFIED | Dana + Eaton newsroom, 11 Jun 2026 |
| Mobility Group valued at ~$5.1B; ~$1.1B cash distribution to Eaton; Eaton holders ≥50.1% | VERIFIED | same release |
| ~$11B pro forma sales, ~$1.7B adjusted EBITDA, $250M run-rate synergies in 24 months | VERIFIED | same release (fully synergised pro forma 2026 estimate — a projection, labelled as such) |
| Closing expected Q1 2027, subject to Dana shareholder approval and regulatory clearances | VERIFIED | same release |
| 2025 sales $7.5B, adjusted EBITDA $610M (8.1%), net income $85M; Off-Highway divested | VERIFIED | Dana FY2025 results release |
| Byron Foster CEO effective 1 Jul 2026; joined 2021 to lead global commercial, marketing and communications; SVP & President, Light Vehicle Systems | VERIFIED | Dana CEO appointment release; Dana leadership page; PRNewswire 301233165 (2021) |
| R. Bruce McDonald Chairman; Timothy Kraus CFO since December 2021; no CMO listed | VERIFIED | Dana CFO appointment release + leadership listing |
| Dana TM4 = Dana / Hydro-Québec JV for electric motors, power inverters and control systems | VERIFIED | danatm4.com |
| Pune plant building Dana TM4 motors, inverters and vehicle control units; eighteenth facility in India; Pune home to Mahindra & Mahindra | VERIFIED | Dana e-drive Pune release |
| Headquartered in Maumee, Ohio | VERIFIED | Dana newsroom |
| Mahindra Racing partner table = Mahindra & Mahindra + Tech Mahindra; other FE rosters as quoted | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| London E-Prix closes the season at ExCeL, 15-16 Aug 2026; GEN4 era begins next season; Mahindra among the committed GEN4 manufacturers | VERIFIED | calendar table + fiaformulae.com |

## Screen-outs and things deliberately not claimed

- **Leadership ties: none found.** No Formula E or Formula 1 history was found for Byron Foster,
  R. Bruce McDonald or Timothy Kraus after checking. `leadership_ties` is empty, not assumed.
- **No claim that Dana supplies Mahindra.** The verified adjacency is geographic and industrial:
  Dana's Pune e-drive plant sits in the city Mahindra & Mahindra is headquartered in. A supply
  relationship was not found and is not asserted.
- **No Dana motorsport heritage claim.** The Spicer driveline brand has a racing history in
  general circulation, but no primary source was opened for it in this session, so the brief does
  not use it.
- **Deal size ($1.5-3M a year) is an ESTIMATE**, labelled as such, and set at Formula E team
  rates rather than Formula 1 ones.
- **The pro forma $11B / $1.7B figures are the parties' own projection**, not reported results;
  the brief says "pro forma" every time they appear.

## Why not the other teams

Judged only against `seeds/sponsors.json`, never against other 1440 prospects. Every conflicting
team is named in `extended.ruled_out` with the partner that closes the lane.

## Honest brake on the score

74/100. Timing is the weak dimension: the agreement is signed but the company itself does not
exist until Q1 2027, so this is a relationship to open now and sign at close, not a deal to
announce in the next month. Brand fit is 13 because Dana sells to vehicle makers and a livery
has no retail work to do — the case for it is customer marketing, and the brief says so.

## Ledger as built (N° 240, 17 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Byron Foster, Chief Executive Officer at Dana Incorporated |
| decision_maker | person_role | yes | verified | Byron Foster, Chief Executive Officer, Dana Incorporated at Dana Incorporated |
| key_facts | funding | yes | verified | Reverse Morris Trust combining Eaton's Mobility Group with Dana, announced 11 June 2026; combined company valued at more than $10 billion, Mobility at about $5. |
| deck | revenue | yes | verified | Dana Incorporated, the $7.5 billion driveline and e-propulsion supplier, agreed on 11 June to combine with Eaton's Mobility Group in a Reverse Morris Trust - an |
| key_facts | funding | yes | verified | Eaton shareholders will own at least 50.1 per cent of the combined company; the deal is expected to close in the first quarter of 2027, subject to Dana sharehol |
| the_case_p1 | funding | yes | verified | Eaton and Dana signed a definitive agreement on 11 June 2026 to separate Eaton's Mobility Group and combine it with Dana in a Reverse Morris Trust, creating a c |
| key_facts | revenue | yes | verified | 2025 sales of $7.5 billion with adjusted EBITDA of $610 million and net income of $85 million; about $11 billion of sales and $1.7 billion of adjusted EBITDA pr |
| the_case_p1 | revenue | yes | verified | The transaction values Mobility at about $5.1 billion and the combined business at roughly $11 billion of sales and $1.7 billion of adjusted EBITDA on a fully s |
| key_facts | date | yes | verified | Eaton and Dana signed a definitive agreement on 11 June 2026 to separate Eaton's Mobility Group and combine it with Dana in a Reverse Morris Trust |
| the_case_p2 | revenue | yes | verified | Dana closed 2025 with $7.5 billion of sales, $610 million of adjusted EBITDA and $85 million of net income after divesting Off-Highway, a supplier that has alre |
| key_facts | sponsorship | yes | verified | DS Penske carries the components and electronics cluster on the Formula E grid - Mouser Electronics, TTI Inc., Molex and KYOCERA AVX - while Castrol holds fluid |
| bottom_line | revenue | yes | verified | A vehicle-systems company with about $11 billion of sales is being assembled in public, and the executive who ran Dana's commercial and marketing function now r |
| key_facts | other | yes | verified | Byron Foster, who joined Dana in 2021 to lead global commercial, marketing and communications, became chief executive on 1 July 2026; Dana TM4 builds electric m |
| extended | funding | no | verified | The combined company is valued at more than $10 billion, with Eaton's Mobility Group valued at approximately $5.1 billion and Eaton taking a cash distribution o |
| key_facts | other | yes | verified | Headquartered in Maumee, Ohio; eighteen facilities in India including a Pune plant producing Dana TM4 electric motors, inverters and vehicle control units |
| extended | revenue | no | verified | On a fully synergised pro forma 2026 basis the combination is expected to carry approximately $11 billion in sales and approximately $1.7 billion of adjusted EB |
| trigger | date | yes | verified | merger / spin-off |
