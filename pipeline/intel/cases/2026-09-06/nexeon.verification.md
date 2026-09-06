# Nexeon → Jaguar TCS Racing — verification log (N° 241, 6 Sep 2026)

Built in-session at no model-API cost: Claude acted as scanner, verifier and writer through the
pipeline's injectable stages; freshness, dedup, scoring, the claims ledger with the calendar and
sponsor-table checks, the 13-rule audit and the strict 2-page render ran as code.

**Sandbox limitation, stated plainly:** direct fetches of nationalwealthfund.org.uk,
nexeonglobal.com, theorg.com, fiaformulae.com and the trade press were blocked by the egress
proxy. Every claim below was checked against the search summary of the primary page named as its
evidence URL. Treat each VERIFIED line as REPORTED until a person opens the link. Confidence is
MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, and a date worth checking

**31 August 2026** — the National Wealth Fund announced a £52.6 million ($70 million) investment
completing Nexeon's £100 million ($133 million) round. The NWF's own newsroom is the primary
source. Trade coverage clustered on 31 August and 1 September (EU-Startups carried it under an
August URL, Electronics Weekly and WOWTALE under 1 September), so the brief uses 31 August and
**the first thing to confirm on a call is the announcement date**. Either way the trigger sits
well inside the 90-day window.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| NWF £52.6M ($70M) completing a £100M ($133M / €116.7M) round, 31 Aug 2026 | VERIFIED | nationalwealthfund.org.uk newsroom |
| Korea Development Bank and Honda Xcelerator Ventures are the other new investors | VERIFIED | same release |
| Money is for UK expansion and commercialisation of next-generation battery technology | VERIFIED | same release |
| Silicon anode materials raise energy density, cut charging time, extend EV range | VERIFIED | same release; Nexeon product pages |
| Founded 2006; circa $400m raised before this round; Scott Brown CEO since June 2009, PhD Chemistry, MBA Oxford Brookes | VERIFIED | Nexeon leadership profile / Deep Tech Leaders |
| David Lamb CFO; Tony Cochrane Chief Commercial Officer; no CMO listed | VERIFIED | Nexeon leadership listing (The Org) |
| Binding long-term supply agreement with Panasonic; commercial material from early 2025 | VERIFIED | Nexeon media release |
| Gunsan plant beside OCI's monosilane supply, world's first commercial-scale silicon anode facility, online December 2025 | VERIFIED | Nexeon media release; electrive |
| HQ Oxfordshire; application engineering and customer support centre in Yokohama | VERIFIED | Nexeon site |
| Jaguar TCS Racing = TCS (title), Castrol, Jaguar powertrain; no battery/materials partner; other FE rosters as quoted | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| GEN4 season opens Jeddah 18-19 Dec 2026; London E-Prix at Brands Hatch 29-30 May 2027; new COTA and Zandvoort rounds; Jaguar among committed GEN4 manufacturers | VERIFIED | calendar table + fiaformulae.com |

## Screen-outs and things deliberately not claimed

- **Leadership ties: none found.** No Formula E or Formula 1 history was found for Scott Brown,
  Tony Cochrane or David Lamb after checking. `leadership_ties` is empty, not assumed.
- **No revenue figure** is used: Nexeon is private and none is public.
- **No claim of a supply relationship with Jaguar Land Rover.** None was found; the case does not
  need one and does not imply one.
- **MODE B is stated on the page, not hidden.** Formula E's battery is a spec component, so the
  brief says outright that Nexeon cannot supply the race car. Every mechanic offered — audience,
  hospitality, content, recruitment — is one that survives that fact.
- **Deal size (£0.8-1.5M a year) is an ESTIMATE**, labelled as such and set at Formula E team
  rates.

## Why not the other teams

Judged only against `seeds/sponsors.json`, never against other 1440 prospects. Envision Racing is
the hard conflict — its title partner runs a battery business and Teijin holds materials — and
every other conflicting team is named in `extended.ruled_out` with the partner that closes the
lane.

## Honest brake on the score

70/100, which is the threshold and not a point above it. Capacity is the brake: Nexeon is
pre-profit and this round is state money earmarked for plant and commercialisation, so a
sponsorship line has to be argued for. Ops fit is 13 because the race car's battery is a spec
part — this is a Mode B case with concrete mechanics, not an engineering partnership dressed up
as one. If the MD wants only Mode A signals, this one should be passed over, and the brief says
so rather than inflating the number to hide it.

## Ledger as built (N° 241, 19 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Scott Brown, Chief Executive Officer at Nexeon |
| decision_maker | person_role | yes | verified | Dr Scott Brown, Chief Executive Officer, Nexeon at Nexeon |
| key_facts | funding | yes | verified | £100 million ($133 million) round completed on 31 August 2026, including £52.6 million ($70 million) from the UK National Wealth Fund; roughly $400 million rais |
| deck | funding | yes | verified | Nexeon, the Oxfordshire silicon-anode company whose materials cut lithium-ion charging times, closed a £100 million round on 31 August with £52.6 million from t |
| key_facts | funding | yes | verified | National Wealth Fund (£52.6 million), with the Korea Development Bank and Honda Xcelerator Ventures as the other new investors |
| the_case_p1 | funding | yes | verified | The National Wealth Fund committed £52.6 million on 31 August 2026, completing a £100 million round that also brought in the Korea Development Bank and Honda Xc |
| key_facts | date | yes | verified | The National Wealth Fund committed £52.6 million on 31 August 2026, completing Nexeon's £100 million investment round |
| the_case_p1 | funding | yes | verified | Nexeon has raised roughly $400 million since 2006. |
| key_facts | sponsorship | yes | verified | Jaguar TCS Racing runs TCS as title partner with Castrol and a Jaguar powertrain; at Envision Racing the title partner Envision Group runs its own energy and ba |
| bottom_line | funding | yes | verified | A £100 million round with £52.6 million of UK state money behind it, a Korean plant already running and a Panasonic agreement signed, put Nexeon at the point wh |
| key_facts | other | yes | verified | A binding long-term supply agreement with Panasonic, a top-five global EV cell manufacturer, with commercial material from early 2025; the Gunsan plant in South |
| extended | funding | no | verified | The UK National Wealth Fund announced a £52.6 million ($70 million) investment in Nexeon on 31 August 2026, completing a £100 million ($133 million) round whose |
| key_facts | other | yes | verified | Headquartered in Oxfordshire, UK, with an application engineering and customer support centre in Yokohama, Japan and the commercial plant at Gunsan, South Korea |
| extended | funding | no | verified | Nexeon was founded in 2006 and had raised roughly $400 million before this one. |
| trigger | date | yes | verified | funding round |
| why_now_callout | event | yes | verified | Jeddah E-Prix |
| why_now_callout | event | yes | verified | London E-Prix |
| extended | event | no | verified | Jeddah E-Prix double-header on 18-19 December 2026 |
| extended | event | no | verified | London E-Prix to Brands Hatch on 29-30 May 2027 |
