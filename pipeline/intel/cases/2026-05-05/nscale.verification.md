# Nscale → Atlassian Williams Racing — verification log (N° 231, row dated 5 May 2026)

Built in-session on 6 Sep 2026 at no API cost for the desk row dated 5 May 2026 (batch 21). Claude acted as researcher, verifier and writer; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code via `intel.session_case`.

**Sandbox limitation, stated plainly:** direct fetches of nscale.com, prnewswire.com, datacenterdynamics.com and wikipedia.org were blocked by the egress proxy. Every claim below was checked against the search summary of the primary page named as the evidence URL (Nscale's own press releases; CNBC, Sifted and DCD as secondaries). Treat each VERIFIED line as REPORTED until a person opens the link; confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

The thin row's trigger holds: the $2B Series C at $14.6B was announced by the company on **9 Mar 2026** (the thin row said 'reported Mar 2026' with 1 Mar as a placeholder), 57 days before the row's date — inside the 90-day window. The thin row's source (Crunchbase News round-up) is secondary; the primary source is `nscale.com/press-releases/nscale-series-c` (also PR Newswire), with CNBC (9 Mar 2026) as the credible secondary.

**The thin row's person was wrong.** 'Aliaksei Smirnou, CEO & Co-Founder' is not an Nscale executive on any leadership page or release found; Nscale's Founder and CEO is Josh Payne (with co-founder Nathan Townsend). Corrected.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Josh Payne, Founder & CEO; formed May 2024 out of Arkon Energy; HQ London | VERIFIED (search summary) | nscale.com/about; Wikipedia; Computer Weekly |
| $2B Series C led by Aker ASA and 8090 Industries at $14.6B; investor list; 9 Mar 2026 | VERIFIED (search summary) | Nscale release; CNBC; Sifted |
| IPO planned H2 2026; Goldman Sachs and JPMorgan hired | REPORTED | DCD / BeBeez, Feb 2026 |
| $1.1B Series B, 25 Sep 2025; Aker $285M, 9.3%; Microsoft $6.2B five-year Narvik contract | VERIFIED (search summary) | Nscale release; Aker release; DCD |
| Stargate UK; Loughton 23,040 GB300 GPUs from Q1 2027; 58,640 UK GPUs; 300,000 global | VERIFIED (search summary) | Nscale release 16 Sep 2025; NVIDIA newsroom |
| Texas: Cedarvale 234MW lease with Ionic Digital, ~104,000 GB300s for Microsoft from Q3 2026; lease value ~$2B | VERIFIED / value REPORTED | DCD; KSST; Blockspace |
| Lauren Hurwitz COO (28 Apr 2026); Alice Takhtajan CFO (26 Dec 2025); Nidhi Chappell President of AI Infrastructure (4 Dec 2025); no CMO | VERIFIED (search summary) | Nscale press releases; DCD |
| Williams roster; no cloud/GPU partner; conflicts at Aston Martin, Cadillac, Red Bull, Mercedes, Alpine, McLaren, Ferrari, Audi | VERIFIED | sponsor table |
| Claude Official Thinking Partner at Williams (Feb 2026); CoreWeave at Aston Martin (May 2025) | VERIFIED (search summary) | williamsf1.com; astonmartinf1.com |
| British GP (July), United States GP (Austin), Las Vegas GP | VERIFIED | calendar table |

## Screen-outs and things not claimed

- **Leadership ties: none found** for Payne, Hurwitz, Takhtajan or Chappell.
- **Not a placement.** N° 127 Fluidstack (6 Sep 2026) also recommends Williams' open compute lane; per the operating rules, both may point there — the human layer decides.
- **No revenue figure** is used: none is public.
- **Deal size ($5-8M a year) is an ESTIMATE**, labelled as such.
- The Cedarvale lease value (~$2B) is press-reported and used only on the ledger/app page as reported.
- Fortune (3 Jun 2026) questioned whether Nscale's build-out can match its funding; after the row date, noted here for the MD, not used in the score.

## Ledger as built (N° 231, 19 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Josh Payne, Founder & CEO at Nscale |
| decision_maker | person_role | yes | verified | Josh Payne, Founder & CEO, Nscale at Nscale |
| key_facts | funding | yes | verified | $2B Series C led by Aker ASA and 8090 Industries at a $14.6B valuation, announced 9 Mar 2026, the largest Series C in European history (company statement) |
| deck | funding | yes | verified | Nscale, the London-based AI-infrastructure builder behind Stargate UK and Microsoft's Norwegian and Texan capacity, closed a $2B Series C led by Aker ASA and 80 |
| key_facts | funding | yes | verified | Aker ASA, 8090 Industries (leads); Astra Capital Management, Citadel, Dell, Jane Street, Lenovo, Linden Advisors, Nokia, NVIDIA, Point72 |
| the_case_p1 | funding | yes | verified | On 9 March 2026 Nscale announced a $2B Series C led by Aker ASA and 8090 Industries at a $14.6B valuation, with Astra Capital Management, Citadel, Dell, Jane St |
| key_facts | date | yes | verified | $2B Series C at a $14.6B valuation announced 9 Mar 2026; Goldman Sachs and JPMorgan hired for an IPO planned for the second half of 2026 (DCD, reported) |
| the_case_p1 | funding | yes | verified | It follows a $1.1B Series B in September 2025, the month Microsoft signed a $6.2B, five-year capacity contract at Narvik. |
| key_facts | sponsorship | yes | verified | CoreWeave at Aston Martin (Official AI Cloud Computing Partner); Core Scientific and TWG AI at Cadillac; Oracle at Red Bull; Microsoft at Mercedes and at Alpine |
| bottom_line | funding | yes | verified | A $2B Series C at $14.6B, Microsoft, OpenAI and NVIDIA as anchor partners and a reported second-half listing put Nscale at peak brand-investment authority with  |
| key_facts | other | yes | verified | Microsoft signed a $6.2B five-year capacity contract at Narvik, Norway (Sep 2025) and holds capacity agreements in the UK, Texas and Portugal; Stargate UK with  |
| extended | funding | no | verified | On 9 March 2026 Nscale announced a $2B Series C led by Aker ASA and 8090 Industries at a $14.6B valuation, which the company calls the largest Series C in Europ |
| key_facts | other | yes | verified | Cedarvale, Texas: a 10-year lease on Ionic Digital's 234MW facility (Oct 2025, reported at about $2B) to deploy about 104,000 NVIDIA GB300 GPUs for Microsoft fr |
| extended | funding | no | verified | The $1.1B Series B of 25 September 2025, led by Aker with Dell, Fidelity, Nokia, NVIDIA and Point72, was itself the largest in UK and European history; |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | A company that has raised more than $3B in half a year, from a standing start in May 2024, is building a public-company brand whether it has planned one or not. |
| why_now_callout | event | yes | verified | The British GP |
| deal_arch_para | event | yes | verified | British GP |
| extended | event | no | verified | United States GP |
