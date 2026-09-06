# ThreatLocker → Cadillac F1 Team — verification log (N° 158, brief dated 29 Jul 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec: Claude did the research and writing; the pipeline's calendar and sponsor-table checks, 13-rule audit and 2-page render ran as code. The brief is issued for the date the signal sits on in the desk (29 Jul 2026); one development after that date (the IndyCar trial, 4 Sep 2026) is reported on the app page under an explicit "Update since this date" label and is not used in the 2-page brief.

**Sandbox limitation, stated plainly:** direct fetches of threatlocker.com, prnewswire.com, securityweek.com, theorg.com, craft.co, wikipedia.org, tracksideonline.com and indycar.com were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## The trigger

Company-announced: ThreatLocker's own press release of 29 Jul 2026 (mirrored on PR Newswire, Yahoo Finance, AOL) states the $190M Series F led by Elephant, with D. E. Shaw Ventures and Arthur Ventures continuing and Koch Disruptive Technologies new, and names the uses (AI-risk controls, the Zero Trust Platform, a Reading, UK office). The thin row's source (Yahoo Finance) was a syndication of this release; the primary is now the evidence URL. Trigger date = row date, inside the 90-day window.

## Corrections to the thin row

- The thin row scored ThreatLocker 87 (HOT TOP TIER). That is inflated: no valuation is stated by the company, revenue is not public, the category is the most crowded on the grid, and the brand is channel-led. Re-scored 74 (HOT) with the holds written into the score cells and risks.
- "Launched UK Reading office and EMEA expansion simultaneously": the release says the capital will fund expansion *beginning with the opening* of a Reading office; the European headquarters has been in Dublin since 2021. Copy adjusted.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $190M Series F, Elephant lead, D. E. Shaw / Arthur Ventures / Koch Disruptive Technologies; 29 Jul 2026; Reading office | VERIFIED (company release via search summary) | threatlocker.com press release; PR Newswire |
| HQ Orlando; offices Dublin, Dubai, Brisbane; protects over 70,000 organisations | VERIFIED (company release) | same |
| Prior rounds $20M B, $100M C, $115M D (24 Apr 2024), $60M E (Apr 2025); total nearly $500M | REPORTED | SecurityWeek 29 Jul 2026; GlobeNewswire 24 Apr 2024 |
| Pre-round valuation $1.6B | REPORTED, conflicting | SecurityWeek says $1.6B; Capital Asset Ventures put the Apr 2025 Series E at $1.2B. The brief says "reported" and the risk row says the company has not stated a figure |
| Founded 2017 by Danny and Sami Jenkins and John Carolan; Danny Jenkins previously co-founded MXSweep (Dublin) | VERIFIED | threatlocker.com company / leadership pages (search summaries) |
| Leadership: Danny Jenkins CEO; Sami Jenkins COO; Rob Allen CPO; Shane Deegan CRO; Michael Jenkins CTO; Martin Olivo CIO; no CMO listed; CFO not named on public listings | VERIFIED / GAP | The Org leadership team; LinkedIn listings. A CFO exists per LinkedIn but is not named on any leadership page found — recorded as a gap, not guessed |
| Products: Allowlisting, Ringfencing, Elevation Control; MSP channel | VERIFIED | threatlocker.com |
| UCF Athletics sponsorship | VERIFIED (company release, undated in summary) | threatlocker.com press release |
| Juncos Hollinger Racing, IndyCar finale at Laguna Seca, one race, Jenkins quote | REPORTED (team release via TrackSideOnline, 4 Sep 2026) | tracksideonline.com; indycar.com previews |
| Cadillac: Fishers campus ($200M, ~400,000 sq ft), Charlotte, Silverstone; Core Scientific Official Data Center Partner building the Indianapolis data hub (10 Mar 2026); IFS technology partner; no title sponsor sought | VERIFIED | Core Scientific investor release; motorsport.com; team profile |
| Cadillac roster and cybersecurity lanes across the grid | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| United States GP (October) and Las Vegas GP (November) 2026 | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Screen-outs and things not claimed

- **Leadership ties:** no senior ThreatLocker leader found with prior F1/FE employment or sponsorship history; `leadership_ties` is empty after checking. The company's own sports spend (UCF Athletics; the IndyCar one-race deal) is a habit, not a tie.
- **Revenue:** third-party estimates range from $29M to $125M and disagree; none is used.
- **3M** was reported as Cadillac's material-science partner (30 Jun 2026) but is not in the sponsor table, so it is not named in the copy.
- **Aston Martin / SentinelOne:** the table lists SentinelOne as departed while SentinelOne's own site reports a multi-year extension (Feb 2024). Ruled out either way as a direct endpoint rival; the conflict is flagged for the sponsor-table maintainer.
- **Deal size $3-5M a year** is a 1440 ESTIMATE, labelled as such.

## Ledger as built (N° 158, 21 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Danny Jenkins, CEO & Co-Founder at ThreatLocker |
| decision_maker | person_role | yes | verified | Danny Jenkins, CEO & Co-Founder, ThreatLocker at ThreatLocker |
| key_facts | funding | yes | verified | $190M Series F led by Elephant, with D. E. Shaw Ventures and Arthur Ventures returning and Koch Disruptive Technologies new (company release, 29 Jul 2026); prio |
| deck | funding | yes | verified | ThreatLocker, the Orlando zero-trust endpoint company protecting more than 70,000 organisations, closed a $190M Series F led by Elephant on 29 July 2026, with K |
| key_facts | funding | yes | verified | Elephant (lead), D. E. Shaw Ventures, Arthur Ventures, Koch Disruptive Technologies |
| the_case_p1 | funding | yes | verified | ThreatLocker announced a $190M Series F on 29 July 2026, led by Elephant, with D. |
| key_facts | date | yes | verified | $190M Series F led by Elephant announced 29 Jul 2026, funding AI-risk controls and a first UK office in Reading |
| the_case_p1 | funding | yes | verified | It follows a $20M Series B, $100M Series C, $115M Series D (April 2024) and $60M Series E (April 2025): nearly $500M in total. |
| key_facts | sponsorship | yes | verified | CrowdStrike at Mercedes, Bitdefender at Ferrari, Keeper at Williams, 1Password (Red Bull), Cato Networks at Alpine, NinjaOne at Audi; Cadillac carries no cybers |
| the_case_p1 | funding | yes | verified | SecurityWeek puts the pre-round valuation at $1.6B (reported); |
| key_facts | other | yes | verified | Zero-trust endpoint controls (allowlisting, Ringfencing) for a debut team building a greenfield IT estate across Fishers, Charlotte and Silverstone, with Core S |
| bottom_line | funding | yes | verified | A $190M Series F closed on 29 July, a first European office and a platform protecting 70,000 organisations put ThreatLocker at peak spend authority. |
| key_facts | other | yes | verified | HQ Orlando, Florida; offices in Dublin, Dubai and Brisbane; Reading, UK office opening |
| extended | funding | no | verified | ThreatLocker announced on 29 July 2026 that it had secured $190M in Series F funding led by Elephant, with D. |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | The Series F follows a $20M Series B, $100M Series C, $115M Series D in April 2024 and $60M Series E in April 2025, taking total funding to nearly $500M. |
| extended | funding | no | verified | SecurityWeek reports the previous round valued the company at $1.6B; |
| extended | funding | no | verified | Cadillac is building an entire Formula 1 operation from scratch: a $200M, roughly 400,000 sq ft campus in Fishers next to Indianapolis Metropolitan Airport, a C |
| why_now_callout | event | yes | verified | The United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | United States GP |
