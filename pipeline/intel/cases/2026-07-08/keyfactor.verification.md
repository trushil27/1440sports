# Keyfactor → Cadillac F1 Team — verification log (N° 165, issued for 8 Jul 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec: Claude did the research and writing; the pipeline's code stages ran the freshness window, the claims ledger with the calendar and sponsor-table checks, the 13-rule audit and the 2-page render. The row came from a thin scan whose source was a Crunchbase News round-up; the primary source is Keyfactor's own press release (PR Newswire, 6 Jul 2026).

**Sandbox limitation, stated plainly:** direct fetches of keyfactor.com, prnewswire.com, insightpartners.com, summitpartners.com, alpinef1.com and thequantuminsider.com were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

Keyfactor announced a **$1B+ strategic growth investment led by Summit Partners** on 6 July 2026; Insight Partners and Sixth Street Growth keep significant ownership. **No valuation was disclosed** and none is used. The row's claim that it was "the largest cybersecurity deal of the week per Crunchbase" was not confirmed and is not used.

## Decision path (from the company's own leadership pages and releases)

- **Jordan Rackie, Chief Executive Officer** (CEO since May 2019).
- Path: **Mike Volanoski, President & Chief Revenue Officer** (appointed Jan 2026; owns sales, marketing and channel), **Jamie Walker, Chief Marketing Officer**, **Scott Meyerhoff, Chief Financial Officer**. Ted Shorter, CTO and co-founder, is the technical counterpart.

## Leadership ties

No motorsport or sponsorship-deal history was found for Rackie, Volanoski, Walker or Meyerhoff after searching; `leadership_ties` is empty.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $1B+ round led by Summit Partners, 6 Jul 2026; Insight and Sixth Street remain | VERIFIED (search summary of the release) | keyfactor.com press release / PR Newswire |
| $77M Insight (Jan 2019); $125M + PrimeKey merger (Apr 2021); Sixth Street at ~$1.3B (Oct 2023) | VERIFIED | keyfactor.com and Insight Partners releases |
| 2,500+ customers in 150 countries; >40% of Fortune 100; FedRAMP in 2026 | VERIFIED (release boilerplate) | keyfactor.com; Summit Partners note |
| HQ Independence, Ohio | VERIFIED | keyfactor.com; Clay / Glassdoor listings |
| ~550 employees (Apr 2026) | REPORTED (third-party count) | Clay |
| Automotive PKI / ECU identity / firmware signing | VERIFIED | keyfactor.com automotive solution page |
| SEALSQ at Alpine since Nov 2025 | VERIFIED | alpinef1.com; sealsq.com |
| Grid security brands and Cadillac roster | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| US GP (Austin) Oct, Las Vegas GP Nov | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Screen-outs and things not claimed

- **No revenue or ARR figure** is used: none is public.
- **Deal size ($3-5M a year) is an ESTIMATE**, labelled as such.
- **General Motors is not claimed as a Keyfactor customer**; the brief says only that vehicle identity is Keyfactor's automotive practice and that GM is Cadillac's parent.
- **"Six teams carry a security brand"** counts CrowdStrike, Keeper, 1Password, Bitdefender, Okta and SEALSQ from the sponsor table; Cisco, Rubrik, Cato Networks, NinjaOne and Mphasis are listed as adjacent, not counted.
- Post-quantum migration deadlines are described without dates because the specific regulatory timelines were not verified in-session.

## Ledger as built (N° 165, 16 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Jordan Rackie, Chief Executive Officer at Keyfactor |
| decision_maker | person_role | yes | verified | Jordan Rackie, Chief Executive Officer, Keyfactor at Keyfactor |
| key_facts | funding | yes | verified | $1B+ strategic growth investment led by Summit Partners, announced 6 Jul 2026; Insight Partners and Sixth Street Growth retain significant ownership; valuation  |
| deck | funding | yes | verified | Keyfactor, the Ohio machine-identity and PKI company, announced a $1B+ strategic growth investment led by Summit Partners on 6 July 2026, with Insight Partners  |
| key_facts | funding | yes | verified | Summit Partners (lead, 2026); Insight Partners ($77M in Jan 2019 and $125M with the PrimeKey merger in Apr 2021); Sixth Street Growth (minority investment at ab |
| the_case_p1 | funding | yes | verified | On 6 July Keyfactor announced a $1B+ strategic growth investment led by Summit Partners; |
| key_facts | date | yes | verified | $1B+ strategic growth investment led by Summit Partners, announced 6 Jul 2026 |
| the_case_p1 | funding | yes | verified | It follows $77M from Insight in 2019, $125M with the PrimeKey merger in 2021 and a Sixth Street minority round at about $1.3B in October 2023. |
| key_facts | sponsorship | yes | verified | Cybersecurity brands on the 2026 grid: CrowdStrike (Mercedes), Keeper (Williams), 1Password (Red Bull), Bitdefender (Ferrari), Okta (McLaren), SEALSQ post-quant |
| the_case_p1 | funding | yes | verified | The company manages billions of machine identities a year for more than 2,500 customers in 150 countries, over 40% of the Fortune 100 among them, and reached Fe |
| key_facts | other | yes | verified | Keyfactor's automotive practice issues certificate identities to vehicles and ECUs and signs their firmware; Cadillac F1 Team is General Motors' works entry, de |
| bottom_line | funding | yes | verified | A $1B+ round led by Summit Partners, a category the grid has validated six times over, and a debut American team that lists cybersecurity as an open lane put Ke |
| key_facts | other | yes | verified | HQ 6150 Oak Tree Boulevard, Independence, Ohio; about 550 employees across six continents (reported, Apr 2026); FedRAMP status achieved in 2026 |
| extended | funding | no | verified | On 6 July 2026 Keyfactor announced a $1B+ strategic growth investment led by Summit Partners. |
| trigger | date | yes | verified | funding round |
| extended | event | no | verified | Las Vegas GP |
