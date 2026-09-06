# TwelveLabs → Visa Cash App Racing Bulls — verification log (N° 172, issued for 1 Jul 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY`), with Claude acting as scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code from `twelvelabs.case.json`. The desk row sat on 1 Jul 2026 with no team; this case names one.

**Sandbox limitation, stated plainly:** direct fetches of globenewswire.com, twelvelabs.io, sportsvideo.org and the team sites were blocked by the egress proxy. Each claim was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, and the correction to the thin row

The round is company-announced (GlobeNewswire, 1 Jul 2026) and covered by Sports Video Group, The Elec and PYMNTS. **$100M Series B co-led by NEA and NAVER Ventures; Red Bull Ventures a new, minority investor.** The thin row's phrase "structural warm-intro to Oracle Red Bull Racing commercial team" was the desk's inference: Red Bull Ventures is a group-level investor, which is a path, not a warm introduction to any team's commercial staff, and the brief says so. The team recommended is Racing Bulls, not Red Bull Racing, because Oracle's title deal makes cloud and AI that team's story while TwelveLabs has just named AWS its preferred cloud.

Total funding: the release summary says roughly $150M; one secondary (The Elec) says $200M. The brief uses the company's figure.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Jae Lee, Co-Founder & CEO; founded 2021; UC Berkeley; Korea Ministry of National Defense | VERIFIED | The Org; World Economic Forum profile |
| Yoon Kim, President & Chief Strategy Officer (Dec 2024; ex-SK Telecom CTO, Apple Siri); Soyoung Lee co-founder, Head of BD; Aiden Lee CTO; no CMO listed | VERIFIED | twelvelabs.io blog, Dec 2024; The Org |
| $100M Series B; co-leads and participants; ~$150M total | VERIFIED | GlobeNewswire company release, 1 Jul 2026 |
| AWS preferred cloud; Trainium; new offices New York, London; LA expansion | VERIFIED | company release, 1 Jul 2026 |
| $30M strategic round (Databricks, SK Telecom, Snowflake Ventures, HubSpot Ventures, In-Q-Tel), Dec 2024 | VERIFIED | twelvelabs.io blog |
| NFL Media and MLSE use Marengo / Pegasus on game footage | VERIFIED | twelvelabs.io sports page; AWS case study |
| Red Bull Ventures: launched 2025, €200M fund, Fuschl am See, led by Nai-Tseng Chen and Sabrina Jones; TwelveLabs its most prominent investment | REPORTED | Trending Topics (Austria); Global Venturing; deutsche-startups.de |
| Racing Bulls content rated excellent by 60 per cent of fans (Bayer); Creator Platform | REPORTED | Sector, Jul 2026 (Bayer interview) |
| Lawson / Lindblad pairing; 4M Instagram, 2.3M TikTok; Lindblad P8 on debut | REPORTED | Motorsport.com, Aug 2026; formula1.com |
| Salesforce Agentforce deployment (Jun 2026) and Neural Concept (Jun 2025) at Racing Bulls (app page only; not in the sponsor-table snapshot) | VERIFIED | salesforce.com press release |
| Rosters: Racing Bulls (Dynatrace, Confluent, Siemens, Randstad, Visa, Cash App, Hugo, Tudor); Red Bull (Oracle title); Mercedes/Alpine (Microsoft; Meta AI); McLaren (Google Cloud); Williams (Claude); Cadillac (TWG AI); Aston Martin (CoreWeave) | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Belgian, Hungarian, Dutch, Italian, US (Austin), Las Vegas GPs on the 2026 calendar | VERIFIED | calendar table; dates from formula1.com |

## Screen-outs and things not claimed

- **No motorsport tie found** for Jae Lee, Aiden Lee, Yoon Kim, Soyoung Lee or Dave Chung after searching; the only link to motorsport is the Red Bull Ventures shareholding. `leadership_ties` is empty.
- **No revenue figure** is used: none is public.
- **Deal size ($1.5-2.5M a year) is an ESTIMATE**, labelled as such.
- **Capacity is what holds the score back** (13/20): a company with ~$150M raised in total is an entry-tier sponsor, which is why the recommendation is Racing Bulls and a paid pilot first.
- The Salesforce and Neural Concept relationships at Racing Bulls are named on the app page only, because the desk's sponsor-table snapshot (20 May 2026) predates the June 2026 Salesforce announcement.

## Decision path

Jae Lee (Co-Founder & CEO) fronts every raise and would own a first sports partnership. Path: Yoon Kim (President & Chief Strategy Officer) for strategy and partnerships; Soyoung Lee (Co-Founder, Head of Business Development) for the commercial conversation. No chief marketing officer is listed on any leadership listing found.

## Ledger as built (N° 172, 22 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Jae Lee, Co-Founder & CEO at TwelveLabs |
| decision_maker | person_role | yes | verified | Jae Lee, Co-Founder & CEO, TwelveLabs at TwelveLabs |
| key_facts | funding | yes | verified | $100M Series B co-led by NEA and NAVER Ventures, announced 1 Jul 2026 (company release, GlobeNewswire); total funding roughly $150M |
| deck | funding | yes | verified | TwelveLabs, the San Francisco and Seoul video-understanding company whose models let broadcasters search footage by what happens in it, closed a $100M Series B  |
| key_facts | funding | yes | verified | NEA and NAVER Ventures (co-leads); Amazon (strategic); Radical Ventures, Korea Investment Partners, Index Ventures; new investors Quadrille Capital and Red Bull |
| the_case_p1 | funding | yes | verified | TwelveLabs announced on 1 July 2026 a $100M Series B co-led by NEA and NAVER Ventures, with Amazon, Radical Ventures, Korea Investment Partners, Index Ventures, |
| key_facts | date | yes | verified | $100M Series B, announced 1 Jul 2026 |
| the_case_p2 | funding | yes | verified | Red Bull Ventures, the group's corporate venture arm launched in 2025 with a €200M fund and led by Nai-Tseng Chen, Red Bull's Global Head of Corporate Finance,  |
| key_facts | sponsorship | yes | verified | No F1 team carries a video-intelligence partner in the sponsor table; nearest incumbents are cloud and data platforms (Oracle at Red Bull, Dynatrace and Conflue |
| bottom_line | funding | yes | verified | A $100M Series B, Amazon as preferred cloud and Red Bull Ventures on the cap table give TwelveLabs a fresh budget and a structural path into the Red Bull teams. |
| key_facts | other | yes | verified | Red Bull Ventures, the group's corporate venture arm, joined the round and calls TwelveLabs its most prominent investment; Amazon made AWS the preferred cloud i |
| why_team_para | funding | no | verified | Red Bull Ventures already holds TwelveLabs equity, so the introduction exists, and the entry price fits a company that has raised $150M. |
| key_facts | other | yes | verified | HQ San Francisco with Seoul; new offices planned in New York and London |
| extended | funding | no | verified | On 1 July 2026 TwelveLabs announced a $100M Series B co-led by NEA and NAVER Ventures, with Amazon as strategic investor, existing investors Radical Ventures, K |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | Total funding is roughly $150M. |
| extended | funding | no | verified | Red Bull Ventures, Red Bull GmbH's corporate venture arm launched in 2025 with a €200M fund and led by Nai-Tseng Chen, the group's Global Head of Corporate Fina |
| extended | funding | no | verified | At Racing Bulls there is no cloud incumbent to argue with, and the entry price matches a company that has raised $150M. |
| extended | funding | no | verified | Open lanes but no investor path and, at Ferrari and Audi, a partner price beyond a company with $150M raised. |
| why_now_callout | event | yes | verified | United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | The United States GP |
