# Divergent Technologies → McLaren Mastercard F1 Team — verification log (N° 177, row of 27 Jun 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec: Claude did the research and writing; the pipeline's code stages (freshness, dedup, scoring, the claims ledger with calendar and sponsor-table checks, the 13-rule audit, the 2-page render, the app page) ran unchanged via `python -m intel.session_case`. Rebuild of a historical row: the desk showed this signal on 27 Jun 2026 with a thin scan (score 78, team hint McLaren, source Los Angeles Business Journal).

**Sandbox limitation, stated plainly:** direct fetches of prnewswire.com, tctmagazine.com, lbpost.com, breakingdefense.com, automotiveworld.com and mclaren.com were blocked by the egress proxy. Each claim was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, corrected

The thin row's trigger — "Series E reported to value Divergent at $2.3B" — is real but stale: the round closed on 15 September 2025, 285 days before the row. The row is kept because a fresh, company-announced inflection exists inside the window: on 17 June 2026 Divergent unveiled Monolith One and a 430,000 sq ft second factory in Long Beach for an 8X rise in output, with a COO (1 Jun), CTO (8 Jun) and Chief Commercial Officer (15 Jun) named the same month. `signal_date` is 17 Jun 2026 and the brief says the Series E is nine months old. The thin row's person (Lukas Czinger) is correct; his title on Divergent's releases is President & Chief Executive Officer and Co-Founder.

## Team choice

The thin row hinted McLaren; the sponsor table supports it. McLaren Racing carries no additive or digital-manufacturing partner; Stratasys, McLaren's polymer-printing supplier, is not in the table as active and was reported still active in March 2026 — the brief names it and treats it as a different lane (polymer parts, not metal structures), which is stated honestly rather than hidden. McLaren Automotive's W1 uses Divergent-printed titanium suspension, and McLaren Racing is a separate company (Mumtalakat majority, CYVN non-controlling, operationally separate) — the brief says so and the second risk row is about exactly that. Alpine (3D Systems) and Haas (Haas Automation) are ruled out by name; Audi, Aston Martin, Mercedes, Cadillac and the Red Bull teams are addressed on the app page.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Lukas Czinger, President & CEO, Co-Founder; Kevin Czinger, Founder & Executive Chairman; Cooper Keller COO (1 Jun 2026); Brian Erhartic CTO (8 Jun 2026); Ben Nicholson CCO (15 Jun 2026); no CMO or CFO listed | VERIFIED (company releases via search summaries) | PR Newswire |
| Monolith One: twelve 2kW lasers (24kW), 700 x 700 x 835 mm; Long Beach factory 430,000 sq ft, 64 printers, ~1,000 jobs, 8X output, production H1 2027; 17 Jun 2026 | VERIFIED (company release) + REPORTED (jobs, printer count, timeline via Breaking Defense / Long Beach Post) | PR Newswire; Breaking Defense |
| $290M Series E ($250M equity, $40M debt) at $2.3B, led by Rochefort ($120M), 15 Sep 2025 | VERIFIED (company release) | PR Newswire; SiliconANGLE |
| $230M Series D, Nov 2023; ~$1.1B total raised | VERIFIED / REPORTED (total via Tracxn, Crunchbase) | PR Newswire |
| McLaren W1 front suspension (titanium upper and lower wishbones, upright) printed by Divergent; multi-year collaboration | VERIFIED (McLaren Automotive release) | Automotive World |
| Founded 2014; HQ Torrance; 600+ parts; Lockheed Martin, RTX, McLaren, Aston Martin, General Atomics, Bugatti, Saab, Triumph Group; Mercedes-AMG a customer | VERIFIED (company boilerplate) / REPORTED (Mercedes-AMG via Series E coverage) | PR Newswire |
| Tomahawk structure at Long Beach from 2027; 30,000 airframes or 60,000 warhead casings capacity | REPORTED | Breaking Defense |
| Czinger 21C production-car lap records (Laguna Seca, COTA), Goodwood hillclimb record | REPORTED | Wikipedia (Czinger 21C) |
| CYVN owns McLaren Automotive and a non-controlling stake in McLaren Racing; Mumtalakat majority; operationally separate | VERIFIED (search summary) | mclaren.com |
| Grid occupancy (McLaren roster; Alpine 3D Systems; Audi Additive Industries departed; Haas Automation; Red Bull Siemens/Ansys; Cadillac GM/Tenneco) | VERIFIED | sponsor table |
| British, Dutch, Italian, US, Las Vegas GPs on the 2026 calendar | VERIFIED | calendar table (dates not seeded; month placements approximate) |

## Screen-outs and things not claimed

- **No revenue figure** is used: private estimates (Craft, Latka) conflict and are not company-stated.
- **No IPO claim**: no filing or company statement found; the deal paragraph says "probable listing window" as an assessment only.
- **Leadership ties**: Lukas and Kevin Czinger run Czinger Vehicles (hypercar records at COTA, Laguna Seca, Goodwood) — a motorsport-adjacent tie, recorded; no F1/FE sponsorship-structuring tie found for any leader.
- **Deal size ($3–5M a year) is an ESTIMATE**, labelled as such.
- **Score 71, not the thin scan's 78**: the fresh trigger is a capacity expansion, not a raise; the defence identity dilutes brand fit; McLaren Racing prices at the top of the grid.

## Ledger as built (N° 177, 17 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Lukas Czinger, President & CEO, Co-Founder at Divergent Technologies |
| decision_maker | person_role | yes | verified | Lukas Czinger, President & CEO, Co-Founder, Divergent Technologies at Divergent Technologies |
| key_facts | funding | yes | verified | $290M Series E ($250M equity, $40M debt) led by Rochefort Asset Management at a $2.3B valuation, closed 15 Sep 2025 (company release); $230M Series D in Nov 202 |
| deck | funding | yes | verified | Divergent, the Torrance digital-manufacturing company whose printed titanium suspension sits on the McLaren W1, unveiled Monolith One, a twelve-laser metal prin |
| key_facts | funding | yes | verified | Rochefort Asset Management (Series E lead, $120M of the round); total raised more than $1B (Tracxn, reported) |
| the_case_p1 | funding | yes | verified | It follows the $290M Series E closed on 15 September 2025 at a $2.3B valuation, led by Rochefort Asset Management, after a $230M Series D in November 2023. |
| key_facts | date | yes | verified | 17 Jun 2026: Divergent unveils Monolith One, a 12-laser (24kW) metal printer, and a second factory in Long Beach, California (430,000 sq ft) for an 8X rise in a |
| bottom_line | funding | yes | verified | A $2.3B company that already prints the McLaren W1's suspension has just announced a twelve-laser printer and a 430,000 sq ft factory it must fill. |
| key_facts | sponsorship | yes | verified | 3D Systems is Alpine's additive partner; Additive Industries departed Audi within the last 12 months; Haas Automation (machine tools) is the Haas F1 owner's bra |
| extended | funding | no | verified | The $290M Series E closed on 15 September 2025 at a $2.3B valuation, led by Rochefort Asset Management with $120M of the round, on top of a $230M Series D in No |
| key_facts | other | yes | verified | McLaren Automotive already builds the W1's front suspension on Divergent's DAPS: titanium upper and lower wishbones and the front upright, printed by Divergent |
| extended | funding | no | verified | total funding is reported at about $1.1B. |
| key_facts | other | yes | verified | HQ Torrance, California; second factory in Long Beach, California |
| extended | event | no | verified | The British GP |
| trigger | date | yes | verified | second factory and new production system |
| extended | event | no | verified | Las Vegas GP |
| extended | event | no | verified | British GP |
