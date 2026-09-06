# Armada → TGR Haas F1 Team — verification log (N° 218, issued for 19 May 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec
(`armada.case.json`) with Claude doing the research, verification and writing; the calendar table,
sponsor table, 13-rule audit and the 2-page render ran as code via `python -m intel.session_case`.
The row came from a thin scan dated 19 May 2026 (score 87, no team); every fact was re-verified live
and the score re-set honestly.

**Sandbox limitation, stated plainly:** direct fetches of armada.ai, prnewswire.com, cnbc.com,
theorg.com, geekwire.com, pulse2.com, research.contrary.com and finance.yahoo.com were blocked by the
egress proxy. Each claim below was checked against the search summary of the primary page named as
the evidence URL (the company release text is quoted in several mirrors, which agree). Treat every
VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads
VERIFY BEFORE CIRCULATION.

## The trigger

The company release of 19 May 2026 (PR Newswire 302775720, mirrored on armada.ai, Yahoo Finance and
Pulse 2.0) and CNBC's same-day report agree: **$230M oversubscribed Series B at a $2B pre-money
valuation**, co-led by Overmatch, BlackRock and 8090 Industries; total funding nearly $500M; a
Johnson Controls investment alongside the **Galleon Forge One** agreement (up to 400,000 sq ft,
Arizona, 500+ jobs, continuous production from summer 2026, Leviathan first). The trigger date is
the row date, inside the 90-day window. The thin row's trigger text was accurate.

## Ledger (all load-bearing claims covered; see the table appended by the build)

| Claim | Status | Evidence |
|---|---|---|
| Dan Wright, Co-Founder & CEO | VERIFIED | The Org / LinkedIn |
| $230M Series B, $2B pre-money, co-leads, ~$500M total, 19 May 2026 | VERIFIED | company release (PR Newswire) + CNBC |
| Galleon Forge One: Johnson Controls, up to 400,000 sq ft, 500+ jobs, production from summer 2026 | VERIFIED | company release + CNBC |
| 540% bookings growth FY25–26; 2,000% Q1 FY27 | COMPANY-STATED, unaudited | company release (labelled as company figures in the copy) |
| $131M strategic round, 24 Jul 2025; Leviathan launch; investor list | VERIFIED | company release (PR Newswire 302513137) |
| M12-led $40M round, Jul 2024; Galleon form factors; Edarat Gulf deal | REPORTED | Data Center Dynamics / SDxCentral |
| Jon Runyan Co-Founder & COO; Pradeep Nair CTO; Prag Mishra Chief AI Officer; no CMO or CFO listed; Zissimos = advisor only | REPORTED | The Org leadership page; Contrary Research |
| HQ San Francisco; Seattle-area hub ~120 people; named US customers | REPORTED | GeekWire 2026; Armada first-year release |
| Core Scientific at Cadillac (Mar 2026); CoreWeave at Aston Martin (May 2025); HPE at Mercedes | VERIFIED | cadillacf1team.com partners; astonmartinf1.com; sponsor table |
| Haas roster: CommScope (Feb 2025), Ruckus (Jan 2026), Mphasis (Nov 2024); no compute/cloud/data-centre partner | VERIFIED | CommScope / RUCKUS releases; sponsor table (`seeds/sponsors.json`) |
| United States GP (Austin) and Las Vegas GP in 2026 | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Decision path

Dan Wright (Co-Founder & CEO) fronts every raise and the Johnson Controls deal and is the sponsorship
owner by default. Path: Jon Runyan (Co-Founder & COO). **No chief marketing officer is listed** on any
leadership listing found; John Zissimos appears on The Org only as "Advisor, Launch CMO and Brand
Architect", so the brief does not name a CMO. No CFO is listed either.

## Screen-outs and things not claimed

- **No motorsport tie found** for Wright, Runyan, Nair or Mishra after searching; `leadership_ties`
  is empty. Armada itself has no motorsport partnership on record.
- **No revenue figure** is used: none is public. The bookings-growth percentages are the company's
  own and are labelled so.
- **Product names beyond Galleon and Leviathan** (the fleet-management software) are not named, as
  they were not confirmed in an opened source; the copy says "Armada's software".
- **Deal size ($2–4M a year) is an ESTIMATE**, labelled as such.
- **Team choice.** Cadillac, the other American team, is ruled out by Core Scientific (official
  data-centre partner) and TWG AI (exclusive AI partner). Williams, Racing Bulls and Audi are open in
  the lane but lack the American-industrial pairing; Haas was chosen on the sponsor table, not on any
  other 1440 prospect (Crusoe N° 121 also points at Haas; per the operating rules that is not a
  placement and does not close the lane).
- **The one real clash-check** is the connectivity lane (CommScope, Ruckus): Armada manages
  Starlink terminals, so the category must be defined as edge compute and satellite backhaul and
  cleared with the team. It is the second risk row.
- **Score reset from 87 to 75.** The thin row's 87 was not supported: capacity is real but a $2B
  company without a marketing chief will not fund a top-tier fee, and urgency is soft (no hard
  deadline beyond Q4 rosters).
- **Grid Fit panel vs. this brief.** The rendered GRID FIT panel is the pipeline's automatic category
  read (`seeds/sponsor_categories.json`), which marks Mercedes open and Aston Martin taken by NetApp.
  The brief's own clash-check is the sponsor table by brand: CoreWeave (Aston Martin), Hewlett Packard
  Enterprise (Mercedes) and Core Scientific (Cadillac) are the rivals that matter. Trust the copy, and
  the ruled-out list on the app page, over the panel.

## Ledger as built (N° 218, 19 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Dan Wright, Co-Founder & CEO at Armada |
| decision_maker | person_role | yes | verified | Dan Wright, Co-Founder & CEO, Armada at Armada |
| key_facts | funding | yes | verified | $230M oversubscribed Series B at a $2B pre-money valuation, announced 19 May 2026 in a company release and reported by CNBC; total funding nearly $500M |
| deck | funding | yes | verified | Armada, the San Francisco builder of ruggedised, satellite-connected data centres that run on oil fields, mines and Navy sites, closed an oversubscribed $230M S |
| key_facts | funding | yes | verified | Series B co-led by Overmatch, BlackRock and 8090 Industries; Johnson Controls invested alongside the Galleon Forge One agreement; earlier backers include M12 (M |
| the_case_p1 | funding | yes | verified | On 19 May 2026 Armada announced a $230M oversubscribed Series B at a $2B pre-money valuation, co-led by Overmatch, BlackRock and 8090 Industries, taking total f |
| key_facts | date | yes | verified | $230M Series B at a $2B pre-money valuation plus a Johnson Controls agreement for Galleon Forge One, an up-to-400,000 sq ft Arizona factory, announced 19 May 20 |
| the_case_p1 | funding | yes | verified | The company says customer bookings grew 540% from FY25 to FY26. |
| key_facts | sponsorship | yes | verified | Core Scientific is Cadillac F1 Team's official data-centre partner (Mar 2026); CoreWeave is Aston Martin Aramco's Official AI Cloud Computing Partner; Hewlett P |
| bottom_line | funding | yes | verified | A $230M round at $2B pre-money, a factory in production this summer and a product that is literally a data centre for remote sites give Armada budget, story and |
| key_facts | other | yes | verified | Galleon and Leviathan are ruggedised, Starlink-connected modular data centres built for sites with no grid or fibre; Galleon Forge One starts continuous product |
| the_case_p2 | sponsorship | yes | verified | Hewlett Packard Enterprise at Mercedes. |
| key_facts | other | yes | verified | HQ San Francisco; Seattle-area hub of about 120 people (GeekWire, 2026); Arizona factory from summer 2026; US customers named by the company include the US Navy |
| extended | funding | no | verified | The company reports 540% customer bookings growth from FY25 to FY26 and a 2,000% year-on-year rise in Q1 FY27 bookings; |
| trigger | date | yes | verified | funding round |
| why_now_callout | event | yes | verified | The United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | The Miami GP |
| extended | event | no | verified | United States GP |
