# Eaton → Cadillac F1 Team — verification log (N° 188, issued for 20 Jun 2026)

Built in-session on 6 Sep 2026 at no API cost (batch 13). Claude acted as scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code.

**Sandbox limitation, stated plainly:** eaton.com, sec.gov, businesswire.com, dana.com and news.gm.com are egress-blocked from the build sandbox. Every claim below was checked against the search summary of the primary page named as the evidence URL. Treat each VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM.

## The trigger, re-verified

The thin desk row called this `never_entered, category_whitespace, funding_event` on 20 June with an SEC exhibit from the 2025 annual results as its source. The real trigger is the **Dana Reverse Morris Trust**: definitive agreements signed **10 June 2026**, announced 11 June (Eaton release, Dana release, Eaton 8-K exhibit 99.1). Transaction value ~$5.1B; Eaton shareholders ≥ 50.1% of the combination; ~$1.1B cash to Eaton; closing expected Q1 2027. It replaces the standalone Mobility spin-off Eaton had planned. Signal date set to 10 June (10 days before the row; inside the 90-day rule).

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Paulo Ruiz, CEO since 1 Jun 2025; ex-Siemens (18 yrs), Fiat | VERIFIED | eaton.com leadership page / 2024 succession release (search summary) |
| David Foster EVP & CFO from 2 Mar 2026; Heath Monesmith President & COO Electrical Sector; no CMO listed | VERIFIED | eaton.com release 2 Mar 2026; corporate-officers listing (search summary) |
| Dana RMT: 10 Jun 2026, ~$5.1B, ≥50.1%, ~$1.1B cash, close Q1 2027 | VERIFIED | eaton.com / dana.com releases 11 Jun 2026; SEC exhibit 99.1 |
| Q1 2026: sales $7.5B +17%, Electrical Americas $3.6B +20%, data-centre orders ~+240%, backlog +48%, guidance 10% | VERIFIED | eaton.com / Business Wire 4 May 2026 |
| 2025 sales $27.4B, +10%; Dublin HQ; NYSE: ETN | VERIFIED | Q4 2025 release, Feb 2026 |
| Eaton–NVIDIA Beam Rubin DSX, 800 V DC, 16 Mar 2026 | VERIFIED | eaton.com / Business Wire 16 Mar 2026 |
| Cadillac: GM + TWG Motorsports; $200M, 400,000 sq ft Fishers HQ under construction, ~300 staff; Concord NC power-unit site; Silverstone | REPORTED | GM News 19 Jan 2026; Inside INdiana Business; IBJ |
| Cadillac roster (TWG AI, Claro, Core Scientific, IFS, Jim Beam, Tenneco); Siemens at both Red Bull teams; Schneider Electric joined McLaren 2026; ABB FE title | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| 2026 power units ~50% electrical (MGU-K 350 kW) | VERIFIED | formula1.com regulations explainer |
| United States GP (Austin), Las Vegas GP, Miami GP in 2026 | VERIFIED | calendar table |

## Judgement calls

- **Team.** The thin row pointed at Aston Martin. Chosen instead: **Cadillac F1 Team** — the only US-manufacturer works entry, three sites in fit-out (a greenfield power specification is the MODE A workstream), and a roster with no electrical, power or energy brand. Aston Martin is ruled out transparently (campus already built and powered; technology-heavy roster under an energy title). Siemens (both Red Bull teams), Schneider Electric (McLaren, joined 2026) and ABB (FE title) rule out the rest.
- **Ruiz's 18 years at Siemens** is context, not a motorsport tie. `leadership_ties` = none found after checking Ruiz, Foster and Monesmith.
- **Score 76, not higher.** Industrial B2B brand with no consumer pull (BRAND FIT 13); no raise or listing catalyst, the closing is the only hard date (URGENCY 13). The thin row's 76 happens to hold.
- **Deal size $5–8M a year is an ESTIMATE**, labelled as such.
- **Not used:** Eaton's Q2 2026 results (30 Jul 2026) post-date the brief; the $30M US switchgear investment (single secondary source); Eaton's motorsport supply heritage (superchargers, differentials) sits in the Mobility business that is leaving, so it is not claimed as a tie.
- **Cadillac's launch-material partners** Tommy Hilfiger, Pirelli and Alpinestars are named from the team's announcement (search summary), not the sponsor table; no 'Brand at Team' sentence depends on them.

## Ledger as built (N° 188, 28 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Paulo Ruiz, Chief Executive Officer at Eaton |
| decision_maker | person_role | yes | verified | Paulo Ruiz, Chief Executive Officer, Eaton at Eaton |
| key_facts | funding | yes | verified | Public company (NYSE: ETN); 2025 sales a record $27.4B, up 10%; Q1 2026 sales $7.5B, up 17% |
| deck | funding | yes | verified | Eaton, the $27.4B intelligent-power group, agreed on 10 June 2026 to separate its Mobility business and combine it with Dana in a ~$5.1B Reverse Morris Trust, t |
| key_facts | funding | yes | verified | Public shareholders; Eaton shareholders will hold at least 50.1% of the Dana-Mobility combination |
| deck | funding | yes | verified | What remains is a pure electrical and aerospace company riding a 240% surge in US data-centre orders. |
| key_facts | revenue | yes | verified | $27.4B in 2025; Q1 2026 $7.5B with Electrical Americas at $3.6B |
| the_case_p1 | funding | yes | verified | On 10 June 2026 Eaton signed definitive agreements to separate its Mobility business and combine it with Dana in a Reverse Morris Trust valued at about $5.1B. |
| key_facts | date | yes | verified | Definitive agreements signed 10 June 2026 to separate the Mobility business and combine it with Dana in a ~$5.1B Reverse Morris Trust; ~$1.1B cash to Eaton; clo |
| the_case_p1 | funding | yes | verified | Eaton shareholders keep at least 50.1% of the combined company, Eaton receives roughly $1.1B in cash, and closing is expected in the first quarter of 2027. |
| key_facts | sponsorship | yes | verified | Siemens sits on the rosters of Oracle Red Bull Racing and Visa Cash App Racing Bulls; Schneider Electric joined McLaren F1 Team for 2026; ABB is the Formula E c |
| the_case_p1 | revenue | yes | verified | First-quarter sales were a record $7.5B, up 17%, Electrical Americas reached $3.6B, up 20%, data-centre orders rose about 240% and organic growth guidance went  |
| key_facts | other | yes | verified | Eaton-NVIDIA Beam Rubin DSX platform for 800 V DC AI factories (16 Mar 2026); Electrical Americas data-centre orders up about 240% in Q1 2026 |
| the_case_p2 | revenue | yes | verified | The identity reset arrives with money and a story: 2025 sales were a record $27.4B, and in March Eaton and NVIDIA unveiled the Beam Rubin DSX platform for 800-v |
| key_facts | other | yes | verified | Electrical Americas is the largest segment ($3.6B Q1 2026 sales); Dublin-domiciled, NYSE-listed, run from the United States |
| bottom_line | funding | yes | verified | A $27.4B company becomes pure-play intelligent power in Q1 2027, with about $1.1B of cash and data-centre orders up 240%. |
| trigger | date | yes | verified | spin-off / Reverse Morris Trust |
| why_team_para | funding | no | verified | Cadillac is the first American works entry in a generation: General Motors and TWG Motorsports, a $200M, 400,000 sq ft headquarters under construction in Fisher |
| extended | funding | no | verified | The transaction is valued at about $5.1B; |
| extended | funding | no | verified | Eaton shareholders will own at least 50.1% of the combined company and Eaton receives a cash distribution of about $1.1B. |
| extended | revenue | no | verified | First-quarter 2026 sales were a record $7.5B, up 17%; |
| extended | funding | no | verified | Electrical Americas reached $3.6B, up 20%, with data-centre orders up about 240% and sector backlog up 48%. |
| extended | funding | no | verified | Eaton is selling into the largest capital build-out in the US economy and has raised 2026 organic growth guidance to 10%. |
| extended | funding | no | verified | A $200M, 400,000 sq ft headquarters is under construction in Fishers, Indiana; |
| why_now_callout | event | yes | verified | United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | The United States GP |
| extended | event | no | verified | Miami GP |
