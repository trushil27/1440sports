# Base Power → Andretti Formula E — verification log (N° 136, issued for 5 Sep 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec
(`basepower.case.json`) with Claude acting as scanner, verifier and writer through
`intel.session_case`; the calendar table, sponsor table, 13-rule audit and the 2-page render ran
as code. The row sat on the desk as a thin FE signal (78, Andretti) from the 5 Sep run; this is the
full case on that date. The signal date is the trigger's real date, 3 Aug 2026 (33 days before the
row, inside the 90-day window).

**Sandbox limitation, stated plainly:** direct fetches of businesswire.com, basepowercompany.com,
techcrunch.com, andrettiglobal.com, coserv.com, envision-group.com, fiaformulae.com and dell.com
were blocked by the egress proxy. Each claim below was checked against the search summary of the
primary page named as the evidence URL (several from more than one summary). Treat every VERIFIED
line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY
BEFORE CIRCULATION.

## The trigger

Company-announced: Business Wire, 3 Aug 2026, "Base Power Announces $1B Series D and Launches
Base Core". $1B at a $13B post-money valuation, led by Ribbit, Addition, Valor Equity Partners and
JPMorganChase's Strategic Investment Group, with Altimeter, D1 Capital Partners, Sands Capital,
Coatue, Layer Global and Energy Impact Partners. Secondary: TechCrunch, 3 Aug 2026. The thin row's
facts held on re-verification; the row's "~40 kWh" is the release's 39.2 kWh.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Zach Dell, Co-Founder & CEO | VERIFIED | Business Wire release quote; company About page / Wikipedia |
| Justin Lopas, Co-Founder & COO (ex-SpaceX, Anduril); Zina Bash CLO and Travis Kavulla Head of Policy (14 Jan 2026); no CMO, CCO or CFO listed | VERIFIED (Bash/Kavulla) · REPORTED (Lopas career) | Business Wire 14 Jan 2026; Wikipedia / Texas Monthly |
| $1B Series D at $13B post-money, 3 Aug 2026; >$2.5B raised to date; Base Core 39.2 / 78.4 kWh built at Base Factory 1, Austin | VERIFIED | Business Wire 3 Aug 2026 |
| Series C $1B led by Addition, Oct 2025, $4B post-money; Series B $200M, Apr 2025 | VERIFIED (C) · REPORTED (B, valuation) | Business Wire 8 Oct 2025; TechCrunch |
| Illinois (ComEd territory) launch 24 Jun 2026 | VERIFIED | basepowercompany.com/illinois-press |
| CoServ 100 MW residential storage programme, North Texas, 6 Mar 2026, largest to date | VERIFIED | CoServ / Business Wire release |
| Model: home battery + electricity subscription, dispatched in ERCOT as a virtual power plant; founded Austin 2023 | REPORTED | TechCrunch 8 Oct 2025; Canary Media |
| Andretti Formula E owned by TWG Motorsports; TWG Global also fields the Cadillac F1 Team with GM | VERIFIED | Andretti Global Feb 2025; sponsor table |
| Nissan GEN4 powertrain to Andretti from Season 13 (24 Jul 2026); Porsche ends with Season 12 | VERIFIED | Andretti Global / Nissan newsroom; sponsor table |
| Andretti roster (TWG AI, Quest Global, Crowe UK, Reflo); no energy/battery/utility partner at any FE team | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Envision Group owns Envision Racing and controls AESC | VERIFIED | envision-group.com |
| DS exits at end of Season 12; Penske alignment unannounced | VERIFIED | fiaformulae.com 20 Mar 2026 |
| Jeddah 18 Dec 2026; Austin E-Prix 6 Feb 2027; Miami E-Prix 20 Feb 2027 | VERIFIED | calendar table (`seeds/calendar_fe.json`) |
| Dell Technologies at McLaren F1 Team (since 2018); Zach Dell is Michael Dell's son | VERIFIED (table) · REPORTED (family) | dell.com; sponsor table; Fortune |

## Screen-outs and things not claimed

- **Leadership ties: none found.** Neither founder has held a motorsport role or structured a
  sponsorship. Dell Technologies' McLaren partnership is family-company adjacency and is recorded as
  context only; `leadership_ties` is empty after checking.
- **No revenue figure** is used: none is public (Sacra estimates exist and are not relied on).
- **No deployment totals** ("100+ MWh", "180 MW across five utilities") are used: the figures vary
  by outlet and none was traced to a company page.
- **Deal size ($2-3M a year) is an ESTIMATE**, labelled as such in the brief.
- **TWG ownership watch item:** August 2026 reports of a federal investigation into TWG Global's
  Mark Walter and a TWG statement that the Cadillac F1 Team is not for sale (motorsport.com, ESPN)
  are noted for the human layer; nothing in the case rests on them.
- **Team choice:** Envision Racing (owner's AESC battery business), Lola Yamaha ABT (Shell), Nissan
  (AESC co-founder, no US story), Penske (unresolved entry), Porsche and Jaguar (works teams, no US
  story), Mahindra / Cupra Kiro / Citroën (no US presence) ruled out by name; Cadillac F1 held as
  the second step under the same owner. Base Power is aimed at Andretti on the sponsor table alone,
  not against any other 1440 prospect.

## Batch context

The same batch screened Stegra (rescue round, pre-revenue, below threshold), Lyten (MOU only inside
the window, last raise Jul 2025, below threshold), Slate Auto (Series C 13 Apr 2026, stale; CEO is
Peter Faricy since Mar 2026, not Chris Barman) and VoltaGrid (investment 11 May 2026, stale, no
closing announced). Base Power is the one signal of the five that clears the bar on its own facts.

## Ledger as built (N° 136, 24 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Zach Dell, Co-Founder & CEO at Base Power |
| decision_maker | person_role | yes | verified | Zach Dell, Co-Founder & CEO, Base Power at Base Power |
| key_facts | funding | yes | verified | $1B Series D at a $13B post-money valuation, announced 3 Aug 2026 (Business Wire); the company says it has raised more than $2.5B to date |
| deck | funding | yes | verified | Base Power, the Austin company that installs grid-connected home batteries and sells the electricity behind them, closed a $1B Series D at a $13B post-money val |
| key_facts | funding | yes | verified | Led by Ribbit, Addition, Valor Equity Partners and JPMorganChase's Strategic Investment Group; Altimeter, D1 Capital Partners, Sands Capital, Coatue, Layer Glob |
| the_case_p1 | funding | yes | verified | Base Power announced on 3 August that it had raised a $1B Series D at a $13B post-money valuation, led by Ribbit, Addition, Valor Equity Partners and JPMorganCh |
| key_facts | date | yes | verified | $1B Series D at $13B and the launch of the Base Core home battery, 3 Aug 2026 |
| the_case_p1 | funding | yes | verified | It follows a $1B Series C led by Addition in October 2025 at $4B and a $200M Series B in April 2025; |
| key_facts | sponsorship | yes | verified | No battery, energy-storage or utility partner on any Formula E team roster; Envision Group, owner of Envision Racing, also controls battery maker AESC; Shell si |
| the_case_p1 | funding | yes | verified | the company says it has raised more than $2.5B. |
| key_facts | other | yes | verified | The Austin E-Prix on 6 Feb 2027 is a home race in Base's HQ city; Andretti Formula E is owned by TWG Motorsports, whose parent TWG Global also fields the Cadill |
| bottom_line | funding | yes | verified | A $1B round at $13B, more than $2.5B raised, a factory-built product to launch nationally and a home race in Austin on 6 February 2027 put Base Power at peak br |
| key_facts | other | yes | verified | HQ Austin, Texas; Base Factory 1 in Austin; sells in Texas (ERCOT) and, since 24 Jun 2026, Illinois (ComEd territory) |
| extended | funding | no | verified | Base Power announced on 3 August 2026 a $1B Series D at a $13B post-money valuation, led by Ribbit, Addition, Valor Equity Partners and JPMorganChase's Strategi |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | The company says it has raised more than $2.5B in total. |
| key_facts | event | yes | verified | The Austin E-Prix on 6 Feb 2027 |
| extended | funding | no | verified | The Series C of October 2025, $1B led by Addition, valued the company at $4B; |
| extended | funding | no | verified | the Series D puts it at $13B. |
| why_now_callout | event | yes | verified | Austin E-Prix on 6 February 2027 |
| opening_angle_quote | event | yes | verified | Austin E-Prix |
| extended | event | no | verified | Jeddah E-Prix on 18 December 2026 |
| extended | event | no | verified | The Austin E-Prix on 6 February 2027 |
| extended | event | no | verified | Miami E-Prix |
