# Modal Labs → Atlassian Williams Racing — verification log (N° 215, issued for 21 May 2026)

Built in-session on 6 Sep 2026 at no API cost (batch 18): Claude did the research, verification and writing; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code. The brief is issued for the desk row's date, 21 May 2026; the trigger is dated the same day.

**Sandbox limitation, stated plainly:** direct fetches of modal.com, generalcatalyst.com, williamsf1.com, astonmartinf1.com and the calendar sites were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## What the thin row got right and wrong

- **Person and trigger are correct**: Erik Bernhardsson, CEO; $355M Series C led by General Catalyst with Redpoint, Bain Capital Ventures, Menlo and Accel; ARR from $60M (Sep 2025) to $300M. The row cited SiliconANGLE; the primary source is Modal's own blog post of 21 May 2026, with the Reuters exclusive as the credible secondary. The row omitted the valuation ($4.65B post-money) and the two-tranche structure.
- **Score.** The row carried 85. Re-scored at 78: capacity and ops fit are strong; brand fit is a developer-first infrastructure brand with little consumer reach, and there is no listing signal.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $355M Series C at $4.65B post-money; General Catalyst + Redpoint lead; Menlo, Bain Capital Ventures, Accel; 21 May 2026 | VERIFIED (company post) + REPORTED (Reuters) | modal.com/blog/modal-series-c; Reuters via Yahoo Finance |
| Two tranches, first at $2.5B; talks reported Feb 2026 | REPORTED | Reuters; TechCrunch 11 Feb 2026 |
| Annualised revenue > $300M, fivefold from ~$60M in Sep 2025 | VERIFIED (company-stated) + REPORTED (Reuters) | Modal blog; Reuters |
| $87M Series B led by Lux at $1.1B, Sep 2025; total then $111M | VERIFIED | Modal Series B post; Built In NYC 1 Oct 2025 |
| Disclosed funding $466M; valuation quadrupled | DERIVED (111 + 355; 4.65 / 1.1) | the two announcements |
| Customers DoorDash, Cognition, Decagon, Suno, Physical Intelligence, Chai Discovery; >1B sandboxes; Lovable 1M+ sandboxes in a weekend | VERIFIED (company post) | Modal blog |
| Bernhardsson CEO (ex-Spotify, Better.com CTO); Bubna CTO; founded 2021 | VERIFIED | General Catalyst investment note; Modal company page |
| David Dorman VP Marketing and Growth; Justin Dignelli VP Sales; no CMO/CFO/COO listed | REPORTED (LinkedIn) / VERIFIED (absence) | LinkedIn profiles; no leadership page lists a C-level marketing or finance role |
| HQ New York; offices San Francisco and Stockholm | VERIFIED | Built In NYC |
| Claude Official Thinking Partner at Williams (2026) | VERIFIED | williamsf1.com |
| CoreWeave Official AI Cloud Computing Partner, Aston Martin Aramco, May 2025 | VERIFIED | astonmartinf1.com |
| Grid occupancy (Williams roster; CoreWeave + Cognition / Aston Martin; Core Scientific + TWG AI / Cadillac; Oracle / Red Bull; Microsoft + HPE + AMD / Mercedes; Microsoft / Alpine; Google Cloud + Dell + Groq / McLaren; HP + IBM / Ferrari; HPE / Audi departed) | VERIFIED | sponsor table `seeds/sponsors.json` |
| Canadian GP 22-24 May; Monaco 5-7 Jun; Spanish 12-14 Jun; Austrian 26-28 Jun; British 3-5 Jul; US GP Oct; Las Vegas Nov | VERIFIED | calendar table + formula1.com dates via ESPN / F1 Experiences |

## Screen-outs and things not claimed

- **Employee count** is not used: sources disagree (122 vs ~153 in spring 2026).
- **No motorsport tie found** for Bernhardsson, Bubna, Dorman or Dignelli after checking; `leadership_ties` is empty.
- **Modal is not a partner of any F1 or FE team** (sponsor table; live search of 2026 AI partnerships).
- **Cold-start timing** is stated as "seconds" because sources differ (sub-second vs under three seconds).
- **Deal size ($3-5M a year) is an ESTIMATE**, labelled as such.
- **Fluidstack (N° 127, 6 Sep 2026) also recommends Williams.** Our signals are not placements: team fit is judged only against real grid occupancy, and the compute lane at Williams was open on 21 May 2026 as it is today.

## Decision path

Erik Bernhardsson (Co-Founder & CEO) is the sponsorship owner. Path: David Dorman (VP Marketing and Growth) and Justin Dignelli (VP Sales). Technical counterpart: Akshat Bubna (Co-Founder & CTO). No CMO or CFO is listed.

## Ledger as built (N° 215, 26 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Erik Bernhardsson, Co-Founder & CEO at Modal Labs |
| decision_maker | person_role | yes | verified | Erik Bernhardsson, Co-Founder & CEO, Modal Labs at Modal Labs |
| key_facts | funding | yes | verified | $355M Series C at a $4.65B post-money valuation led by General Catalyst and Redpoint, with Menlo Ventures, Bain Capital Ventures and Accel, announced 21 May 202 |
| deck | funding | yes | verified | Modal Labs, the New York serverless AI-compute platform, announced a $355M Series C at a $4.65B valuation on 21 May 2026, led by General Catalyst and Redpoint. |
| key_facts | funding | yes | verified | General Catalyst and Redpoint (co-leads); Menlo Ventures, Bain Capital Ventures, Accel (new); Lux Capital led the $87M Series B at $1.1B in September 2025 |
| deck | revenue | yes | verified | Annualised revenue has passed $300M, up fivefold since September, and the valuation has quadrupled from the $1.1B Lux Capital set then. |
| key_facts | revenue | yes | verified | More than $300M annualised revenue, up fivefold from about $60M in September 2025 (company-stated; Reuters) |
| the_case_p1 | funding | yes | verified | On 21 May Modal announced $355M at a $4.65B post-money valuation, led by General Catalyst and Redpoint with Menlo, Bain Capital Ventures and Accel joining. |
| key_facts | date | yes | verified | $355M Series C at $4.65B led by General Catalyst and Redpoint, announced 21 May 2026 |
| the_case_p1 | funding | yes | verified | Reuters reports the round closed in two tranches, the first at $2.5B, as AI-coding demand surged. |
| key_facts | sponsorship | yes | verified | CoreWeave is Official AI Cloud Computing Partner of Aston Martin Aramco (May 2025); Core Scientific and TWG AI sit on Cadillac's roster; the cloud lanes of Red  |
| the_case_p1 | revenue | yes | verified | Annualised revenue has passed $300M, fivefold the roughly $60M of September 2025, when Lux Capital led an $87M Series B at $1.1B. |
| key_facts | other | yes | verified | Modal customer Cognition joined Aston Martin Aramco for 2026; Williams runs VAST Data and Claude but has no cloud or GPU-compute partner |
| bottom_line | revenue | yes | verified | A $355M round at $4.65B, revenue past $300M and growing fivefold, and a product the engineers write to directly give Modal the budget, the motive and a real wor |
| key_facts | other | yes | verified | HQ New York; offices in San Francisco and Stockholm; founded 2021 |
| extended | funding | no | verified | On 21 May 2026 Modal announced a $355M Series C at a $4.65B post-money valuation led by General Catalyst and Redpoint, with Menlo Ventures, Bain Capital Venture |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | Reuters reports the round closed in two tranches, the first at $2.5B, as investor demand grew; |
| extended | funding | no | verified | TechCrunch had reported talks at $2.5B in February. |
| extended | revenue | no | verified | Annualised revenue has passed $300M, up fivefold from about $60M in September 2025, when Lux Capital led an $87M Series B at $1.1B. |
| why_now_callout | event | yes | verified | Canadian GP |
| why_now_callout | event | yes | verified | British GP |
| extended | event | no | verified | Monaco GP |
| extended | event | no | verified | Spanish GP |
| extended | event | no | verified | Austrian GP |
| extended | event | no | verified | Las Vegas GP |
