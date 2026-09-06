# Infineon Technologies → Jaguar TCS Racing — verification log (N° 190, issued for 16 Jun 2026)

Built in-session on 6 Sep 2026 at no API cost (batch 13). Claude acted as scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code.

**Sandbox limitation, stated plainly:** infineon.com, jaguar.com, media.jaguarracing.com and wolfspeed.com are egress-blocked from the build sandbox. Every claim below was checked against the search summary of the primary page named as the evidence URL. Treat each VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM.

## The trigger, re-verified

The thin desk row called this `never_entered, category_whitespace, funding_event` with a companiesmarketcap.com page as its source. There is no funding event: Infineon is a EUR 14.7B public company. The real signal is a **peak-demand moment**: full-year guidance raised on **6 May 2026** (AI data-centre power demand, automotive orders improving, new segment structure from Q4) and, on **8 June 2026**, the Siemens circuit-breaker collaboration that takes its silicon carbide beyond the drivetrain. Signal date set to 8 June (the later of the two, 8 days before the row); both are inside the 90-day rule. Scored WARM (75), not the thin row's 79.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Andreas Urschitz, CMO and Management Board member since 2022, mandate to 31 May 2030 | VERIFIED | infineon.com leadership page (search summary) |
| Jochen Hanebeck CEO since 2022; Sven Schneider CFO since 2019 | VERIFIED | infineon.com leadership pages (search summary) |
| 6 May 2026 guidance raise: Q2 revenue EUR 3.81B +6%; margin ~20%; FCF ~EUR 1.65B (from 1.4B); AI data-centre revenue ~EUR 1.5B FY26, ~2.5B FY27 | VERIFIED | infineon.com press release infxx202605-082; evertiq |
| 8 Jun 2026 Siemens SENTRON 3QD2 SiC modules; PCIM 9-11 Jun | VERIFIED | infineon.com infgip202606-107; press.siemens.com |
| FY2025 revenue ~EUR 14.7B; ~57,000 employees; Neubiberg; #1 power semiconductors (Omdia) | VERIFIED | Infineon at-a-glance flyer; press release Mar 2026 |
| HybridPACK Drive CoolSiC: 1,200 V, 100-300 kW, >20 EV platforms, ~3M units | VERIFIED | infineon.com product page; Power Electronics News |
| Americas HQ Milpitas; Austin site | REPORTED | Zippia / Manta listings (no company page opened) |
| GEN4: 600 kW, permanent AWD, 55 kWh, 700 kW regen, Season 13 debut | VERIFIED | fiaformulae.com GEN4 reveal |
| Jaguar signed for GEN4, Seasons 13-16 | VERIFIED | media.jaguarracing.com, Apr 2024 |
| Wolfspeed Official Power Semiconductor Partner from 2023, SiC with Jaguar since 2017; JLR road-car SiC supply Oct 2022; Chapter 11 30 Jun–29 Sep 2025 | VERIFIED | wolfspeed.com; Manufacturing Dive; Financier Worldwide |
| Wolfspeed absent from the 2025/26 roster | REPORTED | Jaguar livery release Oct 2025 names TCS, Dow, Castrol, Reflo, Alpinestars, Chase only; not in the sponsor table |
| Infineon Raceway naming rights 2002-2012 | REPORTED | Wikipedia, Sonoma Raceway |
| Jaguar roster (TCS, Castrol, Jaguar); DS Penske components cluster; Andretti (TWG AI, Nissan); F1 semis lanes | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Jeddah E-Prix 18-19 Dec 2026; Austin 6 Feb 2027; Miami 20 Feb 2027; London Aug 2026 | VERIFIED | calendar table (`seeds/calendar_fe.json`) |

## Judgement calls

- **The open lane rests on an absence.** Wolfspeed is not on Jaguar's 2025/26 partner list and not in the sponsor table, but no announcement of the partnership ending was found. The brief says 'absent from the roster', never 'ended'. The ask includes settling the supplier question up front. If the human layer finds Wolfspeed still contracted, this case is an `existing_partner` screen-out.
- **The brief does not name Wolfspeed** in the 2-page copy ('its US supplier'); the name is in the ledger, evidence and app page so the MD has it. This keeps the sponsor-table check from reading a 'Brand at Team' pair for a brand the table does not carry.
- **Team.** The thin row's hint (Jaguar) held after checking the alternatives: DS Penske's components cluster, works teams with parent-only rosters, Andretti's TWG AI / Nissan story. F1 is ruled out as a series (EV-native story; semis lanes taken).
- **Leadership ties:** none found for Hanebeck, Schneider or Urschitz after checking. The corporate tie is the Infineon Raceway naming (2002-2012), REPORTED from Wikipedia.
- **Score 75.** No capital event (URGENCY 12); a component brand (BRAND FIT 14, lifted by a board-level CMO and the naming-rights precedent). The thin row's 79 was inflated.
- **Deal size EUR 3-5M a year is an ESTIMATE**, labelled as such.
- **Not used:** Q3 fiscal 2026 results (August 2026) post-date the brief; any claim that Jaguar's current inverter uses Infineon parts (not sourced).

## Ledger as built (N° 190, 15 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Andreas Urschitz, Chief Marketing Officer, Member of the Management Board at Infineon Technologies |
| decision_maker | person_role | yes | verified | Andreas Urschitz, Chief Marketing Officer, Member of the Management Board, Infineon at Infineon Technologies |
| key_facts | funding | yes | verified | Public company (FSE: IFX); fiscal 2025 revenue about EUR 14.7B; around 57,000 employees |
| the_case_p1 | revenue | yes | verified | On 6 May 2026 Infineon reported second-quarter revenue of EUR 3.81B, up 6%, and raised fiscal 2026 guidance: revenue growing significantly, a segment result mar |
| key_facts | funding | yes | verified | Public shareholders; adjusted free cash flow guidance for fiscal 2026 raised to about EUR 1.65B from EUR 1.4B |
| extended | revenue | no | verified | On 6 May 2026 Infineon raised its fiscal 2026 guidance: revenue now expected to grow significantly, a segment result margin of about 20%, adjusted free cash flo |
| key_facts | revenue | yes | verified | EUR 14.7B in fiscal 2025; Q2 fiscal 2026 revenue EUR 3.81B, up 6% |
| why_now_callout | event | yes | verified | Jeddah E-Prix on 18-19 December 2026 |
| key_facts | date | yes | verified | Full-year guidance raised on 6 May 2026 (revenue now to grow significantly; segment result margin about 20%) as AI data-centre power demand surged and automotiv |
| why_now_callout | event | yes | verified | London E-Prix |
| key_facts | sponsorship | yes | verified | Mouser Electronics, TTI, Molex and KYOCERA AVX hold the electronic-components lane at DS Penske; Wolfspeed, the power-semiconductor partner Jaguar ran from 2017 |
| extended | event | no | verified | Berlin E-Prix |
| key_facts | other | yes | verified | AI data-centre revenue expected at about EUR 1.5B in fiscal 2026 rising to about EUR 2.5B in fiscal 2027; number one in power semiconductors (Omdia); HybridPACK |
| key_facts | other | yes | verified | Americas headquarters in Milpitas, California; sites including Austin, Texas |
| trigger | date | yes | verified | guidance raise + peak demand |
