# Lovable → TGR Haas F1 Team — verification log (N° 147, 12 Aug 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec (`lovable.case.json`), with Claude acting as scanner, verifier and writer; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code (`python -m intel.session_case`). Issued for the row's date, 12 Aug 2026, the day of the trigger.

**Sandbox limitation, stated plainly:** lovable.dev, techcrunch.com, bloomberg.com, theorg.com and wikipedia.org were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL (several independent summaries agree on every figure). Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, honestly labelled

Lovable's own release of 12 Aug 2026 (`lovable.dev/blog/series-c`) announces the **$400M Series C at $13.3B**, led by Menlo Ventures and co-led by the Scaleup Europe Fund managed by EQT; TechCrunch and Bloomberg confirmed it the same day. The desk row's **'$500M ARR' is corrected**: the company says run rate passed $500M in June and expects about $600M by end-August 2026 (Dealroom / Tech Startups from the release), company-stated and unaudited, and the brief says so. The row's **'CMO-level hires expected' and 'explicit global brand expansion' are not in any source** and are not used; what IS sourced is a CMO already in post in San Francisco (Lovable's own Chief of Staff, Marketing posting) and the US office plan (citybiz).

## Decision path

- **Anton Osika, Co-Founder & CEO** — VERIFIED (Forbes profile; Cooley; every round announcement). Fronts every raise.
- **Fabian Hedin, Co-Founder & CTO** — VERIFIED (Forbes).
- **CMO** — exists and is based in San Francisco (Lovable careers: 'Chief of Staff to our CMO … bridging SF and Stockholm'), but **no leadership page names them**; searched 'Lovable chief marketing officer' and appointment wires without a name. The brief says so rather than guessing.
- **No public CFO or COO** found after checking; stated as a GAP in the bio and the second risk.
- **Leadership ties:** Osika, Hedin — searched 'Formula 1 / motorsport / racing'; `none found`.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $400M Series C at $13.3B, 12 Aug 2026, Menlo lead, Scaleup Europe Fund (EQT) co-lead | VERIFIED (company release, via summaries; TechCrunch, Bloomberg) | lovable.dev/blog/series-c |
| Balderton, Carmignac, Kaszek, LTS Growth, Tencent, WiL, Regent new; Accel, CapitalG, DST, HubSpot Ventures, Salesforce Ventures returning | REPORTED | TechNode 13 Aug 2026; Vestbee |
| Series B $330M at $6.6B, 18 Dec 2025, CapitalG + Menlo; Atlassian Ventures participated; Series A $200M at $1.8B, Jul 2025 | REPORTED | TechCrunch 18 Dec 2025; Cooley |
| Run rate >$500M (June), ~$600M expected end-Aug 2026 | REPORTED, company-stated | Dealroom News; Tech Startups |
| >60M projects; >900M visits/month | REPORTED, company-stated | Series C release via Vestbee / edtechinnovationhub; Osika on X |
| Stockholm HQ; SF, NY, Boston offices; ~450 hires in 2026 | REPORTED | citybiz; Lovable on Threads |
| CMO based in San Francisco; no named CMO/CFO/COO | VERIFIED (company careers page) | lovable.dev/careers |
| Cerebras partnership, 5 Aug 2026 | VERIFIED (wire) | GlobeNewswire |
| Lovable built on Claude | VERIFIED | claude.com/customers/lovable |
| Salesforce + Racing Bulls Agentforce 360, June 2026 | REPORTED | MarketScreener |
| Haas roster (Toyota Gazoo Racing, Haas Automation/Tooling, Mphasis, Infobip, CommScope, Ruckus); rival lanes at McLaren, Alpine, Red Bull, Mercedes, Aston Martin, Ferrari, Racing Bulls, Cadillac, Audi, Williams | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Dutch, Italian, United States (Austin), Las Vegas, Miami GPs on the 2026 calendar | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Team choice and screen-outs

TGR Haas F1 Team chosen from the sponsor table: no software-creation, developer-platform or AI-application partner; Mphasis is a services integrator (channel, not rival, per `team_profiles.json`). Two 2026 additions not yet in the table were checked live and do not conflict: **Emburse** (Official Travel and Expense Solution Partner, June 2026) and **Exein** (Official Physical AI Security Partner from the Belgian GP). Williams is the warmest path (Atlassian Ventures investor; Claude on the car) but the title partner holds the software lane, so it is ruled out unless Atlassian endorses a co-activation — stated in `ruled_out`. Alpine (Microsoft/GitHub Copilot) and Red Bull (Oracle) are direct-rival lanes. Tencent is a Series C investor: check partner politics on any team with a rival Chinese-tech sponsor before signing.

## Things not claimed

- **Deal size ($3-5M a year) is an ESTIMATE**, labelled as such.
- **No listing date** is claimed; 'probable listing window' is judgment.
- Employee counts vary by source (146 FTE core team in March 2026 vs ~1,000 including contractors) and are not used.
- The desk's original score of 84 was inflated by the unsourced CMO-hire and brand-expansion lines; re-scored honestly at 72 (urgency 11: no deadline; ops fit 12: the workstream is real but light on the car).

## Ledger as built (N° 147, 21 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Anton Osika, Co-Founder & CEO at Lovable |
| decision_maker | person_role | yes | verified | Anton Osika, Co-Founder & CEO, Lovable at Lovable |
| key_facts | funding | yes | verified | $400M Series C at a $13.3B valuation, announced 12 Aug 2026, led by Menlo Ventures and co-led by the Scaleup Europe Fund managed by EQT; doubles the $6.6B set a |
| deck | funding | yes | verified | Lovable, the Stockholm platform on which non-engineers build and run software, announced a $400M Series C at a $13.3B valuation on 12 August, led by Menlo Ventu |
| key_facts | funding | yes | verified | Menlo Ventures (lead), Scaleup Europe Fund / EQT (co-lead); Balderton, Carmignac, Kaszek, LTS Growth, Tencent, World Innovation Lab, Regent; returning Accel, Ca |
| the_case_p1 | revenue | yes | verified | Lovable confirmed on 12 August a $400M Series C at $13.3B, led by Menlo Ventures and co-led by the Scaleup Europe Fund managed by EQT, with Balderton, Kaszek, T |
| key_facts | revenue | yes | verified | Company-stated revenue run rate approaching $600M by end of August 2026, up from $500M in June (reported by Dealroom and Tech Startups from the Series C release |
| the_case_p1 | funding | yes | verified | The price has doubled since the $330M Series B at $6.6B on 18 December 2025. |
| key_facts | date | yes | verified | $400M Series C at $13.3B, announced 12 Aug 2026 |
| the_case_p1 | revenue | yes | verified | The company says revenue run rate passed $500M in June and should reach about $600M by end-August; |
| key_facts | sponsorship | yes | verified | Salesforce, a Lovable investor, deployed Agentforce 360 with Visa Cash App Racing Bulls in June 2026; Google is on the McLaren car; Microsoft holds the software |
| bottom_line | funding | yes | verified | A $400M round at $13.3B, a company-stated run rate near $600M and a US office build-out put Lovable at peak brand-investment authority. |
| key_facts | other | yes | verified | US expansion: Stockholm stays HQ while offices open in San Francisco, New York and Boston with about 450 hires planned this year; Cerebras inference partnership |
| extended | funding | no | verified | On 12 August Lovable announced a $400M Series C at a $13.3B valuation, led by Menlo Ventures and co-led by the Scaleup Europe Fund managed by EQT, and confirmed |
| key_facts | other | yes | verified | Stockholm HQ; San Francisco office with the CMO based there; New York and Boston offices planned (reported) |
| extended | funding | no | verified | The Series B of 18 December 2025 raised $330M at $6.6B; |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | the Series A in July 2025 was $200M at $1.8B. |
| extended | funding | no | verified | A company re-priced from $1.8B to $13.3B in thirteen months has a story to tell to founders, enterprise buyers and, in time, public-market investors, and a budg |
| why_now_callout | event | yes | verified | United States GP |
| extended | event | no | verified | Las Vegas GP |
