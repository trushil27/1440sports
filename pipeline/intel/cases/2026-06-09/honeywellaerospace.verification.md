# Honeywell Aerospace → Aston Martin Aramco F1 Team — verification log (N° 199, 9 Jun 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) with Claude acting as
scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor
table, 13-rule audit and the 2-page render ran as code. The case sits on the row's date, 9 Jun 2026,
in rebuild mode; `honeywellaerospace.run.json` is the case record `python -m intel.backfill --cases`
imports.

**Sandbox limitation, stated plainly:** direct fetches of honeywell.com, investor.honeywell.com,
sec.gov and prnewswire.com were blocked by the egress proxy. Each claim below was checked against the
search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED
until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, re-dated

The thin row cited a valuesense.io aggregator and "Form 10-12B". The Form 10 was filed on 3 Mar 2026,
98 days before the row date and therefore outside the 90-day window, and the separation itself
(29 Jun) and the board approval (15 Jun) fall after the row date. The trigger inside the window is
Honeywell's release of **5 Jun 2026** setting the 15 Jun record date, the 29 Jun distribution, the
one-for-two ratio and the HONAV/HONA trading dates (Investing.com confirms, 5 Jun). Nothing dated
after 9 Jun is used in the brief.

## Score: 71, value section on, two risks

The thin row said 69, and a first pass anchored on it. Re-scored against the spec's own rubric:
a dated listing (29 Jun, 20 days from the row) is a hard external date, so timing 17 and urgency 13
rather than 16 and 12; capacity is obvious ($17.4B 2025 sales). What holds it back is unchanged:
brand fit is a B2B/B2G halo (12), no marketing owner is named, and the power unit is Honda's and
homologated, so the workstream is an engineering exchange around the regulated unit rather than
product on the car (ops fit 11). The value section is therefore MODE B (brand launch) with a bounded
engineering exchange, not an operational claim. The pipeline's production gate (`MD_THRESHOLD`, 70)
is unchanged; a 69 would not have produced a record.

## Ledger (claims verified against search summaries of the primary pages)

| Claim | Status | Evidence |
|---|---|---|
| James (Jim) Currier, 60, President & CEO; ran Aerospace Technologies since Aug 2023 | VERIFIED | Honeywell release Nov 2025; Form 10 officer list |
| 5 Jun 2026 release: record date 15 Jun; distribution 29 Jun, 12:01 a.m.; 1-for-2; HONAV/HONA | VERIFIED | honeywell.com release; Investing.com |
| 2025 net sales $17.4B (+12% organic), led by aftermarket and defence | VERIFIED | Honeywell Q4 2025 release, 29 Jan 2026 |
| Josh Jepsen CFO (from 23 Feb 2026, ex-Deere); BU leaders Buddecke, Marinick, DeGraff | VERIFIED | Honeywell release Jan 2026 |
| Craig Arnold non-executive chair (ex-Eaton) | VERIFIED | Honeywell release Nov 2025 |
| HQ Phoenix; Form 10 filed 3 Mar 2026 | VERIFIED | Honeywell release Mar 2026; Flight Global |
| 1 MW generator: 1.02 MVA, 900 kW continuous, ~97% efficiency, ~8 kW/kg, doubles as motor | VERIFIED | Aerospace Testing International; Honeywell Aerospace pages |
| Grid occupancy: Boeing (Alpine), Atlas Air (Aston Martin), Bombardier departed, Aramco, Honda PU, Arm, CoreWeave | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Austrian GP 28 Jun; British GP 5 Jul 2026; Austin, Las Vegas in the autumn | VERIFIED | calendar table + silverstone.co.uk / RacingNews365 |

## Screen-outs and things not claimed

- **No chief marketing officer is named** anywhere reached; the brief says so rather than inventing a marketing counterpart.
- **No motorsport tie found** for Currier, Jepsen or Arnold; `leadership_ties` is empty after checking. (Garrett Motion, a former Honeywell turbocharger business now on Ferrari's roster, is independent since 2018 and not claimed as a tie.)
- **No Honeywell F1 sponsorship found** (checked); stated as a risk, not a fact about appetite.
- **Deal size ($5-8M a year) is an ESTIMATE**, labelled as such.
- **Parent rename** ("Honeywell Technologies") is not used; not needed and not confirmed from a primary page.

## Decision path

CEO Jim Currier (owner) → CFO Josh Jepsen → chair Craig Arnold. Business-unit presidents Buddecke, Marinick and DeGraff are the technical counterparts. Ask on the first call who owns brand.

## Ledger as built (N° 199, 20 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | James Currier, President & Chief Executive Officer at Honeywell Aerospace |
| decision_maker | person_role | yes | verified | James Currier, President & CEO, Honeywell Aerospace at Honeywell Aerospace |
| key_facts | funding | yes | verified | Spin-off from Honeywell: record date 15 Jun 2026, distribution 29 Jun 2026, one Honeywell Aerospace share for every two Honeywell shares; Nasdaq HONA regular-wa |
| deck | revenue | yes | verified | Honeywell Aerospace, the $17.4B-revenue avionics, engines and electrification supplier, becomes a standalone Nasdaq company on 29 June 2026: Honeywell's board s |
| key_facts | funding | yes | verified | Distributed pro rata to Honeywell shareholders; no external capital raise |
| the_case_p1 | revenue | yes | verified | The business reported 2025 net sales of $17.4B, up 12% organically, led by commercial aftermarket and defence. |
| key_facts | revenue | yes | verified | 2025 net sales $17.4B, up 12% organically (Honeywell fourth-quarter release, 29 Jan 2026) |
| bottom_line | funding | yes | verified | A $17.4B business listing on its own on 29 June, an open aerospace-engineering lane at Aston Martin and a British GP a week later give Honeywell Aerospace a cle |
| key_facts | date | yes | verified | Honeywell board sets the record date and the 29 Jun 2026 distribution for the Honeywell Aerospace spin-off, announced 5 Jun 2026 |
| why_team_para | funding | no | verified | Honeywell's 1-megawatt generator, about 97% efficient and usable as a motor, speaks to the hybrid era better than any consumer brand could. |
| key_facts | sponsorship | yes | verified | Boeing sits on the Alpine roster and Atlas Air on Aston Martin's; Bombardier has departed Aston Martin; no aerospace engines-or-avionics supplier is on any F1 c |
| extended | revenue | no | verified | The business reported 2025 net sales of $17.4B, up 12% organically, led by commercial aftermarket and defence and space. |
| key_facts | other | yes | verified | Honeywell's 1-megawatt aerospace generator ran at 1.02 MVA and 900 kW continuously at about 97% efficiency and 8 kW/kg and doubles as a motor: an electrificatio |
| extended | funding | no | verified | Honeywell's 1-megawatt aerospace generator ran at 1.02 MVA and 900 kW continuously at about 97% efficiency and roughly 8 kW/kg, and doubles as a motor. |
| key_facts | other | yes | verified | Headquarters Phoenix, Arizona; Nasdaq listing |
| why_now_callout | event | yes | verified | Austrian GP |
| trigger | date | yes | verified | spin-off listing |
| why_now_callout | event | yes | verified | British GP |
| extended | event | no | verified | The United States GP |
| extended | event | no | verified | Las Vegas GP |
