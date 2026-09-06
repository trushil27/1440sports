# Helion Energy → Andretti Formula E — verification log (N° 195, issued for 11 Jun 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox), with Claude acting as scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code from the case spec `helionenergy.case.json`.

**Sandbox limitation, stated plainly:** helionenergy.com, businesswire.com, geekwire.com and techcrunch.com were blocked by the egress proxy. Every claim below was checked against the search summary of the primary page named as the evidence URL. Treat VERIFIED lines as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

The row's trigger holds: **$465M Series G led by Thrive Capital at $15.5B post-money, announced 4 Jun 2026** (7 days before the row), in Helion's own release. Total raised $1.5B. The prior mark was $5.425B (Series F, 28 Jan 2025), so "nearly triple" is arithmetic, not spin.

## The team, re-checked

The thin row suggested Envision Racing. Envision Racing is owned by **Envision Group**, which designs and sells wind turbines, storage, green-hydrogen systems and Envision AESC batteries; the team exists to carry the owner's energy story, so a fusion brand on that car competes with the title. The case is pointed at **Andretti Formula E**: no energy, power or fuel partner in the sponsor table, the American team for a US-facing company, and the two US rounds (Austin, new for Season 13, and Miami). Post-row update: on 24 Jul 2026 Nissan announced it will supply Andretti's GEN4 powertrain from Season 13 (Porsche's supply ends with Season 12); the sponsor table already carries both rows, but the brief, issued for 11 June, does not mention the switch because it was not public on that date.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| David Kirtley, Founder & CEO; founded 2013; HQ Everett, WA | VERIFIED | Crunchbase, LinkedIn, GeekWire 2026 profile |
| $465M Series G, Thrive lead, $15.5B post-money, 4 Jun 2026; total $1.5B; investor list | VERIFIED | helionenergy.com newsroom / Business Wire (20260604) |
| $425M Series F at $5.425B, 28 Jan 2025 | VERIFIED | helionenergy.com newsroom / Business Wire |
| Orion in Malaga, Chelan County, WA; construction from July 2025; Microsoft PPA, 2028, 50 MW or more after a one-year ramp; state licences | VERIFIED | helionenergy.com newsroom (30 Jul 2025; May 2023); CNBC; 425business.com |
| Polaris D-T fusion at 150 million °C, Feb 2026; tritium licence | VERIFIED | helionenergy.com newsroom; TechCrunch 13 Feb 2026; GeekWire |
| Nucor 500 MW plant agreement (2023, target 2030) | VERIFIED | helionenergy.com newsroom; Nucor |
| Sam Altman left the board, Mar 2026, as OpenAI explores buying Helion power | REPORTED | TechCrunch 23 Mar 2026 |
| Pragav Jain, CFO since Jul 2024 (ex-Waymo, Goldman Sachs); Savanna Thompson, Chief Business Operations Officer; no CMO listed | VERIFIED | The Org / Crunchbase / LinkedIn; NYSE Live (Jun 2026) |
| Andretti roster (TWG AI, Quest Global, Crowe UK, Reflo, TWG Motorsports); energy lane: Shell (Lola Yamaha ABT), TotalEnergies (DS Penske), Castrol (Jaguar); Envision Group owns Envision Racing; TWG Motorsports also parent of Cadillac F1 | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Season 13 opener Jeddah 18-19 Dec 2026; Austin E-Prix 6 Feb 2027; Miami E-Prix 20 Feb 2027 | VERIFIED | calendar table (`seeds/calendar_fe.json`, fiaformulae.com 23 Jun 2026) |

## Decision path

Sponsorship owner: **David Kirtley, Founder & CEO** (no CMO exists; brand decisions sit with the founder). Path: **Pragav Jain, CFO** and **Savanna Thompson, Chief Business Operations Officer**. Co-founder and CTO Chris Pihl appears on third-party listings only and is not named in the brief.

## Leadership ties

`leadership_ties: []` — Kirtley, Jain and Thompson searched against F1/FE/motorsport; none found. No Helion partnership with any team, series or race on the Formula E or F1 partner pages.

## Screen-outs and things not claimed

- **No revenue figure**: Helion is pre-revenue; none is claimed.
- **Nvidia is not listed as an investor** in the Series F or Series G releases found; the earlier repo record's Nvidia mention is not repeated.
- **Sam Altman** is not used as a hook: he left the board in March 2026, so the case rests on Microsoft, Nucor, Orion and Polaris.
- **Deal size ($1.5-3M a year) is an ESTIMATE**, sized to a pre-revenue company and labelled as such.
- **MODE B is stated as MODE B**: fusion does not power a Formula E car; ops fit is scored 12/20 accordingly and the total is 70, not the row's 73.

## Ledger as built (N° 195, 21 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | David Kirtley, Founder & CEO at Helion Energy |
| decision_maker | person_role | yes | verified | David Kirtley, Founder & CEO, Helion Energy at Helion Energy |
| key_facts | funding | yes | verified | $465M Series G led by Thrive Capital at a $15.5B post-money valuation, announced 4 Jun 2026; total raised $1.5B; prior round $425M Series F at $5.425B (28 Jan 2 |
| deck | funding | yes | verified | Helion, the fusion company building the world's first fusion power plant for Microsoft, announced on 4 June 2026 a $465M Series G led by Thrive Capital at a $15 |
| key_facts | funding | yes | verified | Thrive Capital (lead); new: Lux Capital, Peak XV Partners, BoxGroup, Anti Fund, Alta Park Capital, Bill Ford; returning: Lightspeed, SoftBank Vision Fund 2, Mit |
| the_case_p1 | funding | yes | verified | On 4 June Helion announced a $465M Series G led by Thrive Capital at a $15.5B post-money valuation, with Lux Capital, Peak XV, BoxGroup and Bill Ford joining Li |
| key_facts | date | yes | verified | $465M Series G at a $15.5B valuation, announced 4 Jun 2026 |
| the_case_p1 | funding | yes | verified | total raised is $1.5B, nearly triple the $5.425B set by the $425M Series F in January 2025. |
| key_facts | sponsorship | yes | verified | Shell sits with Lola Yamaha ABT and TotalEnergies with DS Penske; Castrol with Jaguar TCS Racing; Envision Racing is owned by Envision Group, a wind, storage an |
| bottom_line | funding | yes | verified | A $465M round at $15.5B on 4 June, a licensed fusion plant under construction for Microsoft and a first-of-its-kind Polaris result put Helion at peak brand-inve |
| key_facts | other | yes | verified | Orion, the first fusion power plant, under construction in Malaga, Washington since July 2025 to supply Microsoft by 2028; Polaris demonstrated deuterium-tritiu |
| extended | funding | no | verified | On 4 June 2026 Helion announced a $465M Series G led by Thrive Capital at a $15.5B post-money valuation, with Lux Capital, Peak XV Partners, BoxGroup, Anti Fund |
| key_facts | other | yes | verified | HQ Everett, Washington; founded 2013; Orion plant in Chelan County, Washington; Nucor 500 MW plant agreement |
| extended | funding | no | verified | Total raised is $1.5B. |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | The $425M Series F of 28 January 2025 valued Helion at $5.425B; |
| why_now_callout | event | yes | verified | Austin E-Prix in February 2027 |
| bottom_line | event | yes | verified | Austin E-Prix |
| extended | event | no | verified | Jeddah E-Prix double-header on 18-19 December 2026 |
| extended | event | no | verified | Austin E-Prix on 6 February 2027 |
| extended | event | no | verified | Miami E-Prix |
