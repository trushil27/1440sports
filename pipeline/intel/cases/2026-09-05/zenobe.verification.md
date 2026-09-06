# Zenobē → Jaguar TCS Racing — verification log (N° 130, 5 Sep 2026)

Built in-session at no API cost with Claude as scanner, verifier and writer through the
pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page
render ran as code. `zenobe.run.json` is the case record.

**Sandbox limitation, stated plainly:** direct fetches of zenobe.com, media.jaguar.com,
fiaformulae.com, prnewswire.com, energy-storage.news and the trade press were blocked by the
egress proxy. Every claim below was checked against the search summary of the primary page named
as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link.
Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, corrected

The desk row dated the financing 17 Jun (electrive's publication date). Zenobē's own release and
route-one.net date it **15 Jun 2026**, which is the `signal_date` (82 days before the row's date,
inside the 90-day window). The row's '$400M platform for Australia/NZ' was announced on 24 Jun,
after the trigger, and is presented as a follow-on, not part of the trigger. The £980M is **debt**
(bank facilities), not equity: the brief and the first risk row say so.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Donald Weir, CEO (joined 2025) | VERIFIED | zenobe.com news ('Zenobē welcomes Dr Donald Weir as CEO'; summary); Craft |
| Meersman (Co-Founder, EV Fleet), Boothman (CCO Electric Fleet), Wetherall (CFO, ex-Wizz Air); no CMO listed | VERIFIED | zenobe.com/our-story (summary); Equilar; LinkedIn / Bloomberg profiles |
| c.£980M financing, 15 Jun 2026, structure, 22 banks, 1,200 buses, >£3.2B raised | VERIFIED | zenobe.com release (summary); route-one; Sustainable Bus; electrive |
| KKR c.£600M + Infracapital c.£270M, Sep 2023, joint majority | VERIFIED | zenobe.com release (summary); PR Newswire; Energy-Storage.News |
| $400M ANZ platform, 24 Jun 2026 | VERIFIED | zenobe.com release (summary); The Driven; HVIA |
| sdp energie acquisition, 27 Jul 2026, 1.75 GW pipeline | VERIFIED | zenobe.com release (summary); Energy-Storage.News; Enerdata |
| Chicago NA HQ; Revolv acquisition Mar 2026; US school buses | VERIFIED | PR Newswire release (summary); zenobe.com/north-america |
| Extreme E Official Energy Storage Supplier, powerskids, 2021 to the Oct 2025 finale | VERIFIED | zenobe.com/extreme-e; Extreme E newsroom; Electrek (summaries); Wikipedia for the series' end |
| Jaguar: 2025/26 Teams' champions; Evans + da Costa; Kidlington; GEN4 to 2030; Ian James | VERIFIED | fiaformulae.com news (summary); Jaguar Racing media |
| Jaguar roster (TCS, Castrol, Jaguar); no fleet/charging/storage brand; Shell, TotalEnergies, Envision Group, TDK lanes | VERIFIED | sponsor table (`seeds/sponsors.json`) + team profile |
| Jeddah 18-19 Dec 2026; Berlin 8-9 May 2027; London at Brands Hatch 29-30 May 2027 | VERIFIED | calendar table (`seeds/calendar_fe.json`) |

## Screen-outs and things not claimed

- **Leadership ties:** none found for Weir, Meersman, Basden, Beatty, Boothman or Wetherall after two
  searches; `leadership_ties` is empty. The **company-level** tie (Extreme E supplier, five seasons)
  is real and is the warmest fact in the case.
- **No revenue figure** is used: Zenobē's accounts are filed at Companies House but no figure
  surfaced in search; third-party estimates are ignored.
- **Wolfspeed, Reflo, OpenText, Dow and Chase** appear on Jaguar's partner page but are not in the
  sponsor table; they are named only on the app page and never as 'Brand at Team' sentences.
- **Jaguar's team profile lists no open categories.** The recommendation stands on the sponsor table
  itself: no fleet, charging or storage brand is on the roster, and the only recorded lock is
  financial services (Chase), which Zenobē does not touch.
- **Powerskids trackside** is stated as subject to Formula E's event-power rules; the deployable
  MODE A floor is garage/hospitality load and depot electrification.
- **Deal size (£1-2M a year) is an ESTIMATE**, labelled as such.
- **Score 71, not the desk row's 72**: trigger twelve weeks old, debt not equity, no hard deadline;
  held up by a real workstream and the Extreme E precedent.

## Ledger as built (N° 130, 22 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Donald Weir, Chief Executive Officer at Zenobē |
| decision_maker | person_role | yes | verified | Donald Weir, Chief Executive Officer, Zenobē at Zenobē |
| key_facts | funding | yes | verified | c.£980M financing announced 15 Jun 2026 for the UK and Ireland electric-fleet facility (£480M long-dated term commitments, £400M capex facility, £100M ancillari |
| deck | funding | yes | verified | Zenobē, the London fleet-electrification and grid-battery operator owned by KKR and Infracapital, secured c.£980M of new financing on 15 June 2026 to put 1,200  |
| key_facts | funding | yes | verified | KKR and Infracapital (joint majority shareholders since Sep 2023); Jera and TEPCO Power Grid (minority); lenders include NatWest, Lloyds, Santander and Aviva |
| the_case_p1 | funding | yes | verified | Zenobē announced on 15 June that 22 banks, NatWest, Lloyds, Santander and Aviva among them, had committed c.£980M to its UK and Ireland electric-fleet facility: |
| key_facts | date | yes | verified | c.£980M financing announced 15 Jun 2026 to fund more than 1,200 new electric buses and charging in the UK and Ireland over three years; followed by a $400M Aust |
| the_case_p1 | funding | yes | verified | Capital raised since 2017 now exceeds £3.2B. |
| key_facts | sponsorship | yes | verified | No fleet-electrification, charging or storage brand on any Formula E team roster in the sponsor table; Shell at Lola Yamaha ABT and TotalEnergies at DS Penske h |
| the_case_p1 | funding | yes | verified | Nine days later it closed a $400M platform for zero-emission fleets in Australia and New Zealand, and on 27 July it bought Bavaria's sdp energie with a 1.75 GW  |
| key_facts | other | yes | verified | Official energy-storage supplier to Extreme E from its first season to its final event in October 2025, using second-life bus-battery powerskids; Jaguar TCS Rac |
| the_case_p1 | funding | yes | verified | KKR and Infracapital have been joint majority owners since a c.£870M equity round in September 2023. |
| key_facts | other | yes | verified | North American headquarters in Chicago with a New York office; acquired California electric-truck operator Revolv in March 2026; electric school-bus deployments |
| bottom_line | funding | yes | verified | £980M closed in June, a $400M Australasian platform and a German acquisition inside six weeks, five seasons of paying for motorsport at Extreme E, and a home ra |
| trigger | date | yes | verified | financing round |
| extended | funding | no | verified | On 15 June 2026 Zenobē announced c.£980M of new financing for its UK and Ireland electric-fleet facility, the facility's third round: £480M of new long-dated te |
| key_facts | event | yes | verified | London E-Prix moves to Brands Hatch on 29-30 May 2027 |
| extended | funding | no | verified | It funds more than 1,200 new electric buses and their charging over three years and takes capital raised since 2017 past £3.2B. |
| extended | funding | no | verified | Nine days after the UK round, Zenobē closed a $400M platform for zero-emission heavy-vehicle fleets across Australia and New Zealand, seeded with four operating |
| extended | funding | no | verified | Combined with the €325M European facility, the company expects to support up to 5,000 electric buses by 2028. |
| why_now_callout | event | yes | verified | London E-Prix moves to Brands Hatch on 29-30 May 2027 |
| extended | event | no | verified | The London E-Prix |
