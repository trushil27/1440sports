# Hydrostor → Andretti Formula E — verification log (N° 141, row of 5 Sep 2026)

Built in-session at no API cost on 6 Sep 2026 (batch 3) with Claude as scanner, verifier and writer through `intel.session_case`; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code.

**Sandbox limitation, stated plainly:** hydrostor.ca, businesswire.com, mondaq.com, mercomcapital.com, dwpv.com and theorg.com are egress-blocked. Every claim was checked against the search summary of the primary page named as the evidence URL. Treat each VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## The trigger, honestly labelled

Hydrostor's release of 12 Aug 2026 states a US$230 million equity investment that *includes previously announced funding from a convertible note* committed by Canada Growth Fund, Goldman Sachs Alternatives and CPP Investments (the US$150M note of Feb 2025), plus a strategic equity round with Baker Hughes (returning), Realize Capital Partners and Hatch (new). The release does not break out the new money. The brief says so in the deck, the case, the capacity cell and the first risk. The thin row's wording ("secured $230M of equity from CGF, Goldman Sachs and CPP plus Baker Hughes and Hatch") was correct in names but silent on the conversion; corrected here. Valuation is not stated anywhere and is not claimed.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Curtis VanWalleghem, Co-Founder & CEO; launched 2010 | VERIFIED | 12 Aug 2026 release quote (summary); Bloomberg / Crunchbase profiles |
| Jon Norman President; Jordan Cole CCO; Beth Summers CFO; no CMO listed | REPORTED | hydrostor.ca/our-company (summary), LinkedIn, Equilar, 360 Energy podcast. The Org's listing names a different CEO and is disregarded as a data error |
| $230M equity, 12 Aug 2026; note conversion; Baker Hughes / Realize / Hatch; 7 GW pipeline; Willow Rock financial close later 2026 | VERIFIED | hydrostor.ca release via Mercom / Mondaq / DWPV summaries |
| $200M Feb 2025 ($150M note + $50M CGF loan) | VERIFIED | Globe and Mail; hydrostor.ca release |
| US$55M Export Development Canada, Sep 2025 | VERIFIED | Business Wire, 16 Sep 2025 |
| Baker Hughes: equity + up to 1.4 GW orders, investor since 2019, 28 Jan 2026 | VERIFIED | Baker Hughes investor release |
| Willow Rock 500 MW, Kern County; CEC licence 19 Dec 2025; 3CE 25-year ~$1B for 200 MW; CC Power 50 MW, 12 Feb 2026; ~$1.5B cost | VERIFIED / REPORTED | hydrostor.ca project page; 3cenergy.org; Utility Dive; Business Wire; CalCCA (cost, reported) |
| Silver City 200 MW / 1,600 MWh; grid-connection approval 2 Sep 2026; construction due Sep 2026 | VERIFIED | pv magazine, 2 Sep 2026; pv magazine Australia |
| Goderich commercial since Aug 2020, world's first commercial A-CAES | VERIFIED | hydrostor.ca project page; Nov 2019 release |
| Denver US HQ (May 2024); Toronto HQ; Sydney, Melbourne | VERIFIED | hydrostor.ca release; BizWest |
| Envision AESC grid-storage cells; 60 GWh expansion | VERIFIED | EnergyTrend, 27 Apr 2026; Energy-Storage.News |
| Andretti roster; Envision Group title; Shell, TotalEnergies, Castrol positions | VERIFIED | sponsor table `seeds/sponsors.json` |
| Jeddah 18-19 Dec 2026; Austin 6 Feb; Miami 20 Feb 2027 | VERIFIED | calendar table `seeds/calendar_fe.json` |

## Decision path

Curtis VanWalleghem (Co-Founder & CEO) fronts every raise and every release; a first brand partnership is his call. Path: Jon Norman (President), Jordan Cole (Chief Commercial Officer), Beth Summers (CFO). No chief marketing officer exists on any listing found; the brief says so rather than inventing one.

## Leadership ties

Searched Hydrostor and its leaders against Formula E / motorsport / racing sponsorship: none found. `leadership_ties` = none found.

## Screen-outs and things not claimed

- **Score is 70, not higher, on purpose.** Capacity 13: the round includes converted notes, capital is earmarked for projects, no valuation or marketing budget exists. Ops fit 13: MODE B with no car workstream. Brand fit 14: on-message for Formula E but a B2B audience.
- **Envision Racing ruled out** on a real conflict: Envision Group owns Envision AESC, a grid-storage battery maker.
- **The US DOE loan guarantee** reported for Willow Rock (Utility Dive) is not used: its current status could not be confirmed.
- **Deal size ($1–2M a season) is an ESTIMATE**, labelled as such.
- Project cost (~$1.5B) is REPORTED (CalCCA), used once in the note only.

## Ledger as built (N° 141, 19 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Curtis VanWalleghem, Co-Founder & CEO at Hydrostor |
| decision_maker | person_role | yes | verified | Curtis VanWalleghem, Co-Founder & CEO, Hydrostor at Hydrostor |
| key_facts | funding | yes | verified | $230M equity investment closed 12 Aug 2026, which includes the conversion of the previously announced note from Canada Growth Fund, Goldman Sachs Alternatives a |
| deck | funding | yes | verified | Hydrostor, the Toronto developer of cavern-scale compressed-air storage backed by Goldman Sachs, CPP Investments and Canada Growth Fund, closed a $230M equity i |
| key_facts | funding | yes | verified | Canada Growth Fund, Goldman Sachs Alternatives, CPP Investments; strategic investors Baker Hughes (investor since 2019, equity plus up to 1.4 GW of equipment or |
| the_case_p1 | funding | yes | verified | On 12 August Hydrostor closed a $230M equity investment: the conversion of the note committed by Canada Growth Fund, Goldman Sachs Alternatives and CPP Investme |
| key_facts | date | yes | verified | $230M equity investment announced 12 Aug 2026 to progress a 7 GW pipeline and take the 500 MW Willow Rock project to financial close later in 2026 |
| the_case_p1 | funding | yes | verified | It follows US$55M from Export Development Canada in September 2025 and Baker Hughes' January agreement pairing equity with up to 1.4 GW of equipment orders. |
| key_facts | sponsorship | yes | verified | No energy-storage, utility or grid brand on the Andretti Formula E roster (TWG AI, Quest Global, Crowe UK, Reflo, Nissan powertrain from Season 13); Envision Gr |
| the_case_p2 | funding | yes | verified | Willow Rock holds a California licence granted on 19 December 2025 and a 25-year offtake with Central Coast Community Energy worth about $1B; |
| key_facts | other | yes | verified | Two flagship projects turn from paper to construction in the same half-year: Willow Rock in Kern County, California (500 MW, 25-year offtake of about $1B with C |
| extended | funding | no | verified | Hydrostor closed a $230M equity investment on 12 August 2026. |
| key_facts | other | yes | verified | US headquarters in Denver, Colorado since May 2024; flagship US project Willow Rock in Kern County, California; offices in Sydney and Melbourne |
| extended | funding | no | verified | February 2025 brought $200M from the same three institutions ($150M convertible note plus a $50M development loan). |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | Export Development Canada added US$55M in September 2025 for Silver City. |
| extended | funding | no | verified | Willow Rock in Kern County, California (500 MW) holds a state licence granted on 19 December 2025, a 25-year offtake with Central Coast Community Energy worth a |
| extended | event | no | verified | Austin E-Prix |
| extended | event | no | verified | Miami E-Prix on 20 February 2027 |
