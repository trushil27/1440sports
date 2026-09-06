# EnergyX → Andretti Formula E — verification log (N° 166, issued for 6 Jul 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec: Claude did the research and writing; the pipeline's code stages ran the freshness window, the claims ledger with the calendar and sponsor-table checks, the 13-rule audit and the 2-page render. The row's source was Eni's own release; the primary source used is EnergyX's release of the same day on PR Newswire.

**Sandbox limitation, stated plainly:** direct fetches of energyx.com, eni.com, prnewswire.com, investors.gm.com, techcrunch.com, citybiz.co and pulse2.com were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

**$225M strategic equity investment from Eni for a minority stake in Project Black Giant, 6 Jul 2026** — company release, mirrored by Eni. VERIFIED (search summary). Project figures (52,500 tpa LCE over two phases; 100,000+ acres in the Domeyko Range near Salar de Punta Negra, Antofagasta; up to ~25% offtake to Eni; $690M EXIM LOI; total cost just below $1B) are from the same release.

**The row's "total capital raised exceeds $406M" was NOT confirmed** in the release and is not used; PitchBook lists ~$406M and CB Insights a different total, so the figure is left out.

## Decision path (from the company's own leadership page)

- **Teague Egan, Founder, Chairman & CEO** (founded 2018).
- Path: **Kellee Khalil, Chief Marketing Officer** (brand and marketing strategy — the real sponsorship owner), **Mayank Sharma, Chief Financial Officer**, **Juan Carlos Barrera, President of Lithium, South America**. Amit Patwardhan, CTO, is the technical counterpart; Kris Haber, Vice Chairman.

## Leadership ties

No motorsport or sponsorship-deal history was found for Egan, Khalil, Sharma or Barrera after searching; `leadership_ties` is empty.

## Team choice

No lithium, battery-materials or mining brand is on the FE grid. Andretti Formula E was chosen because its roster carries no energy partner, because it is the American team with home rounds in Austin (6 Feb 2027) and Miami (20 Feb 2027), and because of a verified ownership link: General Motors (EnergyX's Series B lead) and TWG Motorsports (Andretti's owner) both sit on the Cadillac F1 Team's 2026 roster in the sponsor table. The link is presented as an introduction path, not as an existing relationship. Eni itself is a BWT Alpine F1 partner (sponsor table) — noted, irrelevant to an FE case.

## Screen-outs and things not claimed

- **MODE B, stated in the copy**: Formula E runs a spec battery; no in-car workstream is claimed.
- **No revenue figure** is used; the company is pre-revenue and its offering filings report losses (Texarkana Today, from SEC filings — REPORTED; used only in the risk row).
- **Retail-investor figures** (about 40,000 investors; $75M Reg A+; $36.6M sold by Apr 2026) are REPORTED (TechCrunch, DealMaker, Texarkana Today) and labelled so.
- **Deal size ($1.5-3M a year) is an ESTIMATE**, labelled as such, and deliberately small: capacity is scored 13 because Eni's money is project equity, not brand budget.
- The score is held at 71; the thin row's 83 was not supported.

## Ledger as built (N° 166, 25 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Teague Egan, Founder, Chairman & CEO at EnergyX |
| decision_maker | person_role | yes | verified | Teague Egan, Founder, Chairman & CEO, EnergyX at EnergyX |
| key_facts | funding | yes | verified | $225M strategic equity investment from Eni for a minority stake in Project Black Giant, announced 6 Jul 2026; supplements a $690M debt-financing letter of inten |
| deck | funding | yes | verified | EnergyX, the Austin lithium-extraction company backed by General Motors and POSCO, announced a $225M strategic equity investment from Eni on 6 July 2026 for a m |
| key_facts | funding | yes | verified | Eni (2026, project-level); General Motors led a $50M Series B in Apr 2023 with Elohim Partners and IMM Investment Global (POSCO Holdings a major contributor to  |
| the_case_p1 | funding | yes | verified | On 6 July EnergyX announced a $225M equity investment from Eni for a minority stake in Project Black Giant, a lithium brine and refining project in Chile's Anto |
| key_facts | date | yes | verified | $225M strategic equity investment from Eni in Project Black Giant, announced 6 Jul 2026 |
| the_case_p1 | funding | yes | verified | It sits on top of a $690M debt letter of intent from the US EXIM Bank; |
| key_facts | sponsorship | yes | verified | No lithium, battery-materials or mining brand on the Formula E grid; energy majors sit on DS Penske (TotalEnergies), Lola Yamaha ABT (Shell) and Jaguar TCS (Cas |
| the_case_p1 | funding | yes | verified | total project cost is put just below $1B. |
| key_facts | other | yes | verified | General Motors, EnergyX's Series B lead, is the parent of the Cadillac F1 Team alongside TWG Motorsports, which also owns Andretti Formula E; Austin E-Prix on 6 |
| the_case_p1 | funding | yes | verified | General Motors led the $50M Series B in April 2023; |
| key_facts | other | yes | verified | HQ Austin, Texas; Project Lonestar 250-tonne-a-year DLE demonstration plant in the Smackover region of Texas and Arkansas commissioned Mar 2026; about 50,000 ac |
| the_case_p1 | funding | yes | verified | a $75M Regulation A+ raise built about 40,000 retail shareholders (reported). |
| trigger | date | yes | verified | strategic investment |
| bottom_line | funding | yes | verified | A $225M Eni investment plus a $690M EXIM letter of intent give EnergyX an energy major's endorsement at the moment the GEN4 era opens, with a home race in Austi |
| key_facts | event | yes | verified | Austin E-Prix on 6 Feb 2027 |
| extended | funding | no | verified | On 6 July 2026 EnergyX announced a $225M strategic equity investment from Eni for a minority stake in Project Black Giant in Chile, with Eni taking rights to up |
| extended | funding | no | verified | The equity sits alongside a $690M debt-financing letter of intent from the US EXIM Bank, and total project cost is estimated just below $1B including financing. |
| extended | funding | no | verified | For a company that has funded itself in part through a $75M Regulation A+ offering to about 40,000 retail investors, a supermajor's cheque changes how bankers,  |
| why_now_callout | event | yes | verified | London E-Prix |
| why_now_callout | event | yes | verified | The Austin E-Prix on 6 February 2027 |
| opening_angle_quote | event | yes | verified | Austin E-Prix |
| extended | event | no | verified | The Austin E-Prix is on 6 February 2027 |
| extended | event | no | verified | Miami E-Prix |
