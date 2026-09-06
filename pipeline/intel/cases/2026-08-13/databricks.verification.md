# Databricks → Nissan Formula E Team — verification log (N° 235, 13 Aug 2026)

An n8n-engine row (27 Aug 2026, score 87, "HOT TOP TIER", person Ali Ghodsi) rebuilt as a full case
at no model-API cost. n8n surfaced Databricks four times — 7 May at 84, 4 Jun at 76, 27 Jul at 89,
27 Aug at 87 — without ever pinning a trigger. Nothing it recorded was carried over.

**Sandbox limitation, stated plainly:** direct fetches of databricks.com, cnbc.com, qz.com,
global.nissannews.com and allied.vc were blocked by the egress proxy. Every claim below was checked
against the search summary of the primary page named as the evidence URL. Treat each VERIFIED line
as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE
CIRCULATION.

## The trigger, and the three candidates that lost

| Candidate | Date | Verdict |
|---|---|---|
| Series L, >$4B at $134B | Dec 2025 – early 2026 | **Stale** — outside the 90-day window |
| "In talks at $165–175B" | mid-2026 | **Rejected** — talks, not a closed round |
| IPO | — | **Rejected** — no S-1; Ghodsi said in June 2026 this is a poor year to list |
| **$5B closed at $190B** | **13 Aug 2026** | **Used** — company-announced, 24 days before today |

The used trigger carries on **Databricks' own newsroom** ("Databricks Grows >80% YoY, Surpasses $7B
Revenue Run-Rate, Scales Lakebase, Genie, and Unity AI Gateway") and on CNBC the same day, so it is
company-confirmed rather than press-reported. The signal therefore sits on 13 Aug 2026, not on the
27 Aug row date n8n recorded.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $5B closed at a $190B valuation, announced 13 Aug 2026 | VERIFIED | databricks.com newsroom; CNBC 13 Aug 2026; Quartz |
| Coatue lead; Blackstone, MGX, T. Rowe Price accounts; new: Sixth Street Growth, BOND, Clearlake, Point72, Premji Invest, TPG; existing: a16z, Dragoneer, Goldman Sachs Alternatives, Thrive | VERIFIED | same |
| 42% above the $134B Series L mark of six months earlier | VERIFIED | same |
| Revenue run-rate past $7B, growth above 80% YoY | VERIFIED as the company's own stated figures — the copy says "its own release puts" | Databricks newsroom, 13 Aug 2026 |
| Proceeds to Unity AI Gateway, Lakebase, Genie | VERIFIED | Databricks newsroom |
| Ghodsi: a poor year to go public; no S-1 filed as of mid-Aug 2026; listing expected 2027+ | REPORTED — labelled "has said publicly" and "reported" | Allied Venture Partners IPO analysis; Forge |
| Rick Schultz, CMO since March 2017, previously marketing lead at Alteryx through its listing | VERIFIED | The Org, Crunchbase, Bloomberg profile, databricks.com speaker page |
| Ali Ghodsi, co-founder and CEO since 2016; Ion Stoica, co-founder and executive chair; Hatim Shafique, COO; HQ San Francisco | VERIFIED | company listings, The Org, Craft |
| Oliver Rowland won the Season 11 drivers' world championship; stays for Season 13 with Zane Maloney; Alpine Tech renewed and helped develop the e-4ORCE 05 powertrain; Nissan supplies the GEN4 powertrain to Andretti Formula E from Season 13 | VERIFIED | global.nissannews.com releases |
| F1 occupancy: Oracle (Red Bull), SAP + Microsoft + HPE (Mercedes), Splunk + Dell + Google Cloud + Mastercard (McLaren), HP + IBM (Ferrari), Atlassian + VAST + Keeper + Zoox + Claude (Williams), CoreWeave (Aston Martin), Microsoft (Alpine), TWG AI + Core Scientific (Cadillac), AWS + Salesforce (championship) | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| FE occupancy: Google Cloud (championship), TWG AI (Andretti), Sand Technologies (Envision), Tech Mahindra (Mahindra), TCS (Jaguar), TDK (Porsche); six of ten entries carry no data, AI or software partner; Nissan's non-parent rows all marked unverified | VERIFIED | sponsor table |
| Season 13: first GEN4 season, 21 races, 13 cities, Jeddah opener 18 Dec 2026, Austin 6 Feb 2027, Miami 20 Feb 2027, Tokyo finale 24-25 Jul 2027 | VERIFIED | calendar table (`seeds/calendar_fe.json`) |
| Databricks is not a partner of any F1 or FE team or of either championship | VERIFIED | sponsor table; live partner-list search found nothing |

## Why Formula E, on the evidence rather than on preference

The Formula 1 answer was tested first and it fails on occupancy. Every Formula 1 team a brand at
this valuation would want already carries a data, cloud or enterprise-software partner — the table
rows are in the ledger above — so entering Formula 1 means displacing an incumbent, taking a
second-tier designation beside one, or buying a team without an engineering story. The two Formula 1
rosters with room are the ones a $190B company would not choose for reach.

Formula E is the opposite: six of ten entries carry no data partner at all, and the operational case
is genuinely stronger there. Formula E is an energy-management formula — fixed energy per race,
attack mode, regeneration, slipstream — decided by modelling rather than by aerodynamic development,
and it has no aerodynamic-testing restriction shaping where a team may spend effort. Season 13 is the
first GEN4 season, so every energy and tyre model is rebuilt from a small base of data. That is a
real Mode A workstream, not a halo.

## Honest score — what holds it back (81, not the 87 n8n recorded)

- **Brand fit 15/20.** The category is proven in motorsport, but Formula E's reach is a fraction of
  Formula 1's for a company that could pay Formula 1 prices. This is the first objection the brief
  will meet internally and it is the first risk row on page 2.
- **Urgency 13/20.** There is no listing to time against. Ghodsi has deferred it, which removes the
  quiet-period pressure that usually drives this desk's HOT TOP TIER scores. The GEN4 reset is a
  window, not a deadline.
- **Capacity 19/20, not 20.** The money is unquestionable; the constraint is that a works-OEM entry
  means the partner sits behind the Nissan marque rather than beside it.
- **On-camera 3/4.** A works Formula E car is a manufacturer's canvas first.

## Leadership ties

`leadership_ties`: **none found**. Ali Ghodsi, Ion Stoica, Rick Schultz and Hatim Shafique show no
Formula 1 or Formula E role in any listing checked, and no prior motorsport sponsorship structured by
any of them was found. Schultz's relevant experience is taking a data-analytics brand through a
listing at Alteryx, which is the pattern, not a tie.

## Not claimed

- **No CFO is named.** No Databricks CFO was confirmed in this session, so the decision path stops at
  the executive chair rather than inventing one. The brief says who is listed and no more.
- **No total-funding or ARR figure** beyond the company's own run-rate statement, which is attributed
  as such.
- **Deal size ($3-6M a year) is an ESTIMATE**, labelled as such on the app page.
- **Andy Kofoid** appears in one secondary listing as President, Global Field Operations. A single
  unconfirmed source is not enough for a decision path, so he is not in the brief.
- **Google Cloud is Formula E's championship cloud and technology partner.** Databricks runs on the
  hyperscalers rather than against them, so this is treated as an adjacency to be scoped and cleared,
  named as the second risk row, with the McLaren precedent (Splunk and Google Cloud on one car) as
  the counter — not as a hard clash.

## Ledger as built (N° 235, 23 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Rick Schultz, Chief Marketing Officer at Databricks |
| decision_maker | person_role | yes | verified | Rick Schultz, Chief Marketing Officer, Databricks at Databricks |
| key_facts | funding | yes | verified | $5B strategic round closed at a $190B valuation, announced 13 August 2026 — 42% above the $134B Series L mark set six months earlier |
| deck | revenue | yes | verified | Databricks closed $5B at a $190B valuation on 13 August, 42% above its $134B Series L mark six months earlier, on a revenue run-rate past $7B growing more than  |
| key_facts | funding | yes | verified | Coatue leading, with Blackstone, MGX and accounts advised by T. Rowe Price; new investors Sixth Street Growth, BOND, Clearlake Capital, Point72, Premji Invest a |
| the_case_p1 | funding | yes | verified | Databricks announced on 13 August that it had closed a $5B strategic round at a $190B valuation, led by Coatue, with Blackstone, MGX and T. |
| key_facts | revenue | yes | verified | Revenue run-rate past $7B growing more than 80% year on year, per the company's own announcement |
| the_case_p1 | revenue | yes | verified | Its own release puts the revenue run-rate past $7B at more than 80% growth. |
| key_facts | date | yes | verified | $5B round closed at a $190B valuation, announced by the company on 13 August 2026 |
| the_case_p1 | funding | yes | verified | The mark is 42% above the $134B Series L of six months earlier. |
| key_facts | sponsorship | yes | verified | Enterprise data brands hold a seat at almost every Formula 1 team — Oracle at Oracle Red Bull Racing, SAP at Mercedes-AMG Petronas F1 Team, Splunk at McLaren F1 |
| bottom_line | revenue | yes | verified | A $5B round closed at $190B on 13 August, a revenue run-rate past $7B growing more than 80% a year, and no listing to wait for. |
| key_facts | other | yes | verified | Nissan supplies its GEN4 Formula E powertrain to Andretti Formula E from Season 13 under a multi-year agreement, so a data partnership at the works team spans t |
| extended | funding | no | verified | Databricks closed a $5B strategic funding round at a $190B valuation, announced on 13 August 2026. |
| key_facts | other | yes | verified | Headquarters in San Francisco, California; the round's proceeds go to the Unity AI Gateway, Lakebase and Genie enterprise-agent products |
| extended | revenue | no | verified | Databricks put its revenue run-rate past $7B with more than 80% year-on-year growth, and directed the capital at the Unity AI Gateway, Lakebase and Genie - the  |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | The $190B mark is about 42% above the $134B Series L set six months earlier. |
| why_now_callout | event | yes | verified | Jeddah E-Prix |
| extended | event | no | verified | Jeddah E-Prix on 18 December 2026 |
| extended | event | no | verified | Austin E-Prix on 6 February 2027 |
| extended | event | no | verified | Miami E-Prix |
| extended | event | no | verified | Tokyo E-Prix closing on 24-25 July 2027 |
