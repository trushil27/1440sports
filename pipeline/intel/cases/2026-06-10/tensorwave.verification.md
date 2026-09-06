# TensorWave → TGR Haas F1 Team — verification log (N° 196, issued for 10 Jun 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox), with Claude acting as scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code from the case spec `tensorwave.case.json`.

**Sandbox limitation, stated plainly:** businesswire.com, tensorwave.com, morningstar.com and nasdaq.com were blocked by the egress proxy. Every claim below was checked against the search summary of the primary page named as the evidence URL. Treat VERIFIED lines as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

The row's trigger holds and is dated to the row: **$350M Series B at a $1.55B valuation, co-led by Magnetar and AMD Ventures, Business Wire release of 10 Jun 2026** (URL stamp 20260610). The row's "~$100M ARR confirmed" does not: the figure traces to the 14 May 2025 Series A release ("on track to close the year with a revenue run rate exceeding $100 million"), a 2025 projection. The brief says "reported" and the capacity score is 14, not the row's implied 18+; the total is 72 against the row's 87.

## The team, chosen

The row carried no team. Compute-lane incumbents in the sponsor table: CoreWeave (Aston Martin), Core Scientific and TWG AI (Cadillac), Google Cloud and Dell (McLaren), Oracle (Red Bull; group incumbent for Racing Bulls), Microsoft and HPE (Mercedes), Microsoft (Alpine), HP and IBM (Ferrari). Open: Haas, Williams, Audi. **TGR Haas F1 Team** is chosen for the US thread (Las Vegas company, American team, three US rounds) and because compute in kind is worth most to the leanest team. AMD is a Mercedes partner; that is named as a risk, not hidden. Case N° 193 (UiPath) in this batch also recommends Haas: our signals are not placements, and each is judged against the real roster only. Two 2026 Haas additions sit outside the sponsor table and are not written as "Brand at Team" in the copy: Emburse (travel and expense, 3 Jun 2026) and Exein (physical AI security); neither is a compute rival.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Darrick Horton, Co-Founder & CEO | VERIFIED | Crunchbase; company LinkedIn post; company blog |
| $350M Series B at $1.55B; Magnetar and AMD Ventures co-leads; Maverick Silicon, Nexus, Western Frontier; MI355X clusters; 8,192-GPU MI325X cluster; >2 GW secured; ~4x the $400M Series A price | VERIFIED | Business Wire 10 Jun 2026 (mirrored on tensorwave.com); HPCwire, DCD |
| $100M Series A, 14 May 2025, same co-leads plus Prosperity7; run-rate above $100M by end-2025 (projection) | VERIFIED (figure REPORTED as a projection) | Business Wire 14 May 2025; DCD |
| Founded 2023, HQ Las Vegas | VERIFIED | DCD; Crunchbase |
| Piotr Tomasik, Co-Founder, President & COO; Jeff Tatarchuk, Co-Founder & Chief Growth Officer; Navi Ganancial, VP Marketing; no CMO/CFO listed | REPORTED | LinkedIn; CB Insights; RocketReach |
| Haas: Kannapolis HQ, Banbury and Maranello; TGR title from 2026; roster (Mphasis, Ruckus, CommScope, Haas Automation) | VERIFIED | Ruckus release Jan 2026; formula1.com Dec 2025; sponsor table |
| CoreWeave at Aston Martin (May 2025); Core Scientific at Cadillac; Google Cloud/Dell at McLaren; Oracle at Red Bull; Microsoft at Mercedes and Alpine; HP/IBM at Ferrari; AMD at Mercedes | VERIFIED | sponsor table (`seeds/sponsors.json`, `seeds/sponsor_categories.json`) |
| Miami GP (May), United States GP (Austin, late Oct), Las Vegas GP (Nov) | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Decision path

Sponsorship owner: **Darrick Horton, Co-Founder & CEO** (founder-led; no CMO exists). Path: **Piotr Tomasik, Co-Founder, President & COO** (partnerships) and **Jeff Tatarchuk, Co-Founder & Chief Growth Officer**; marketing sits with **Navi Ganancial, VP Marketing and Communications**. No CFO is listed on any leadership listing found.

## Leadership ties

`leadership_ties: []` — Horton, Tomasik and Tatarchuk searched against F1/FE/motorsport; none found. TensorWave's announced partnerships are AMD, Fermi America and UNLV; none with any team, series or race.

## Update after the row date

On 10 Aug 2026 Fermi America announced a binding 15-year lease with TensorWave as anchor tenant at Project Matador (Carson County, Texas): an initial 222 MW from the second half of 2027 with expansion rights to 650 MW, about $6.5B of revenue to Fermi over the term (prior signal check). Not used in the brief, which is issued for 10 June; it strengthens the capacity story for a re-dated approach.

## Screen-outs and things not claimed

- **No 2026 revenue figure**: none disclosed; the 2025 run-rate projection is labelled reported.
- **Deal size ($2-4M a year) is an ESTIMATE**, part in compute credits, labelled as such.
- **The F1 workstream is 1440's proposal**; no motorsport customer exists.
- **Score 72, not 87**: capacity is sub-scale for the archetype and the brand is B2B infrastructure.

## Ledger as built (N° 196, 20 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Darrick Horton, Co-Founder & CEO at TensorWave |
| decision_maker | person_role | yes | verified | Darrick Horton, Co-Founder & CEO, TensorWave at TensorWave |
| key_facts | funding | yes | verified | $350M Series B at a $1.55B valuation, co-led by Magnetar and AMD Ventures, announced 10 Jun 2026; prior $100M Series A (14 May 2025) co-led by the same two |
| deck | funding | yes | verified | TensorWave, the Las Vegas-based all-AMD GPU cloud, announced on 10 June 2026 a $350M Series B at a $1.55B valuation co-led by Magnetar and AMD Ventures, almost  |
| key_facts | funding | yes | verified | Magnetar and AMD Ventures (co-leads); Maverick Silicon, Nexus Venture Partners, Western Frontier; Prosperity7 in the Series A |
| the_case_p1 | funding | yes | verified | On 10 June TensorWave announced a $350M Series B at a $1.55B valuation, co-led by Magnetar and AMD Ventures with Maverick Silicon, Nexus Venture Partners and We |
| key_facts | revenue | yes | verified | Reported only: the May 2025 Series A release said TensorWave was on track to close 2025 with a revenue run rate exceeding $100M; no 2026 figure disclosed |
| the_case_p1 | funding | yes | verified | the same leads backed the $100M Series A of May 2025 at a reported $400M. |
| key_facts | date | yes | verified | $350M Series B at a $1.55B valuation, announced 10 Jun 2026 |
| the_case_p1 | revenue | yes | verified | Revenue is reported only: the 2025 release projected a run rate above $100M by year-end. |
| key_facts | sponsorship | yes | verified | CoreWeave is Official AI Cloud Computing Partner of Aston Martin Aramco; Core Scientific sits with Cadillac; Google Cloud and Dell with McLaren; Oracle with Red |
| bottom_line | funding | yes | verified | A $350M round at $1.55B on 10 June, a live 8,192-GPU cluster and 2 GW of secured capacity put TensorWave at peak brand-investment authority; |
| key_facts | other | yes | verified | The largest all-AMD GPU cloud: an 8,192-GPU Instinct MI325X training cluster live and more than 2 GW of long-term data-centre capacity secured; MI355X clusters  |
| extended | funding | no | verified | On 10 June 2026 TensorWave announced a $350M Series B at a $1.55B valuation, co-led by Magnetar and AMD Ventures with Maverick Silicon, Nexus Venture Partners a |
| key_facts | other | yes | verified | HQ Las Vegas, Nevada; founded 2023; US data-centre capacity |
| extended | funding | no | verified | The $100M Series A of May 2025 valued the company at a reported $400M; |
| trigger | date | yes | verified | funding round |
| why_now_callout | event | yes | verified | The United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | United States GP |
