# Odyssey → Audi Revolut F1 Team — verification log (N° 175, row of 30 Jun 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec: Claude did the research and writing; the pipeline's code stages (freshness, dedup, scoring, the claims ledger with calendar and sponsor-table checks, the 13-rule audit, the 2-page render, the app page) ran unchanged via `python -m intel.session_case`. Rebuild of a historical row: the desk showed this signal on 30 Jun 2026 with a thin scan (score 72, team hint Alpine, source TechCrunch).

**Sandbox limitation, stated plainly:** direct fetches of businesswire.com, odyssey.ml, techcrunch.com, hpcwire.com, morningstar.com, audi.com and media.alpinecars.com were blocked by the egress proxy. Each claim was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, re-verified

The thin row's trigger holds. Odyssey's own Business Wire release of 17 Jun 2026 announces the $310M Series B at a $1.45B valuation led by Natural Capital, with Amazon, AMD Ventures, GV, EQT and IQT participating, and AWS as preferred cloud provider; TechCrunch, SiliconANGLE and HPCwire carried it the same day. 13 days before the row's date — inside the window. The thin row's person (Oliver Cameron, Co-Founder & CEO) is correct.

## Team choice: Audi, not the hinted Alpine

The thin row hinted Alpine. The sponsor table shows IndraMind (Indra Group's sovereign-AI platform) joined Alpine for 2026, and Alpine's own media site says it runs across trackside engineering, simulation and performance analysis — the exact lane Odyssey would take. Alpine is ruled out. Audi Revolut F1 Team has no simulation, vehicle-dynamics or AI-modelling partner in the table, Additive Industries and HPE left within the last 12 months, and Odyssey's Zurich office sits next to Audi's Hinwil chassis base. Investor-linked teams (AMD at Mercedes, GV/Google at McLaren) are named as warm paths but ruled out on crowding and price.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Oliver Cameron, Co-Founder & CEO; Jeff Hawke, Co-Founder & CTO; James Grieve, VP Engineering; Jessica Inman, VP GTM & Operations; no CMO or CFO listed | VERIFIED (search summary) | odyssey.ml |
| $310M Series B at $1.45B, led by Natural Capital; Amazon, AMD Ventures, GV, EQT, IQT; 17 Jun 2026 | VERIFIED (company release) | Business Wire |
| Total funding $337M | REPORTED | Crunchbase / TechCrunch |
| NVentures backed the Series A, Feb 2026; ~$27M raised before the B | REPORTED | TechCrunch |
| AWS preferred cloud provider; Trainium; Odyssey-2 Max, Odyssey-2 Pro (API), Starchild-1 | VERIFIED (company release) | Business Wire |
| Founded 2023; Cameron (Voyage founder, Cruise VP product); Hawke (Wayve) | REPORTED | TechCrunch |
| HQ Palo Alto; offices London and Zurich; ~50 staff | REPORTED (counts vary 46–55) | odyssey.ml careers, Built In |
| Audi works entry 2026; Hinwil chassis, Neuburg power unit, Bicester tech centre; Revolut title (Jul 2025); Binotto CEO/TP | VERIFIED (search summary) | audi.com |
| IndraMind at Alpine across engineering and simulation | VERIFIED (search summary) | media.alpinecars.com |
| Grid occupancy (Audi roster; Red Bull Ansys/Siemens; Mercedes G42/AMD/Microsoft; McLaren Google Cloud/Groq/Dell; Williams Claude/Zoox; Cadillac TWG AI; Aston CoreWeave/ServiceNow/Cognizant; Ferrari HP/IBM; Haas TGR/Mphasis) | VERIFIED | sponsor table |
| British, Dutch, Italian, US, Las Vegas GPs on the 2026 calendar | VERIFIED | calendar table (dates are not seeded; month placements are stated approximately) |

## Screen-outs and things not claimed

- **No motorsport tie found** for Cameron, Hawke, Grieve or Inman after checking; `leadership_ties` is empty.
- **No revenue figure** is used: none is public.
- **Deal size ($2–4M a year) is an ESTIMATE**, labelled as such.
- **The MODE A workstream is a pilot, not a proven deployment**: no F1 team is known to run a generative world model in its simulator. The first risk row says so and the ask is a paid pilot.
- **Score 70, not the thin scan's 72 or higher**: capacity is mid-tier (a $1.45B company with ~50 staff), brand fit is B2B and not yet a public name, and the ops fit is unproven in a race team.

## Ledger as built (N° 175, 21 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Oliver Cameron, Co-Founder & CEO at Odyssey |
| decision_maker | person_role | yes | verified | Oliver Cameron, Co-Founder & CEO, Odyssey at Odyssey |
| key_facts | funding | yes | verified | $310M Series B at a $1.45B valuation led by Natural Capital, announced 17 Jun 2026 (Business Wire release; TechCrunch) |
| deck | funding | yes | verified | Odyssey, the Palo Alto world-model lab founded by the Voyage and Wayve autonomy veterans, closed a $310M Series B at a $1.45B valuation on 17 June 2026, led by  |
| key_facts | funding | yes | verified | Natural Capital (lead); Amazon, AMD Ventures, GV, EQT, IQT; NVentures backed the Series A in February 2026; total funding $337M (Crunchbase) |
| the_case_p1 | funding | yes | verified | Odyssey announced on 17 June a $310M Series B at a $1.45B valuation, led by Natural Capital with Amazon, AMD Ventures, GV, EQT and IQT participating; |
| key_facts | date | yes | verified | $310M Series B at $1.45B on 17 Jun 2026; AWS named Odyssey's preferred cloud provider in the same announcement |
| the_case_p1 | funding | yes | verified | total funding stands at $337M (Crunchbase). |
| key_facts | sponsorship | yes | verified | Red Bull carries Ansys and Siemens in engineering simulation; IndraMind joined Alpine for 2026 across trackside engineering and simulation; Claude sits at Willi |
| the_case_p2 | funding | yes | verified | Odyssey has a Zurich office on Hinwil's doorstep, a founding team fluent in vehicles, and a fresh $310M that will be spent on being known to enterprise buyers. |
| key_facts | other | yes | verified | Odyssey has a Zurich office on the doorstep of Audi's Hinwil chassis base; Audi's first F1 season has a roster built from scratch with no simulation partner |
| why_now_callout | funding | yes | verified | a lab that has just taken $310M from Amazon, AMD and GV spends the next two quarters becoming visible to buyers. |
| key_facts | other | yes | verified | HQ Palo Alto, California; offices in London and Zurich |
| bottom_line | funding | yes | verified | A $310M round at $1.45B backed by Amazon, AMD and GV, an AWS compute deal, and a Zurich office beside Formula 1's newest works team put Odyssey at peak authorit |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | On 17 June 2026 Odyssey announced a $310M Series B at a $1.45B valuation, led by Natural Capital with Amazon, AMD Ventures, GV, EQT and IQT participating, and n |
| extended | funding | no | verified | total funding is $337M per Crunchbase. |
| extended | funding | no | verified | four months later the Series B priced the company at $1.45B. |
| extended | funding | no | verified | Audi offers the open lane at a price a $310M company can carry. |
| extended | event | no | verified | Las Vegas GP |
| extended | event | no | verified | Italian GP |
