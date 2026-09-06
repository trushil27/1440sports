# Exa → Atlassian Williams Racing — verification log (N° 213, issued for 22 May 2026)

Built in-session on 6 Sep 2026 at no API cost (batch 18): Claude did the research, verification and writing; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code (`python -m intel.session_case exa.case.json build`). The brief is issued for the desk row's date, 22 May 2026; the trigger is dated 20 May 2026 (2 days before the row, inside the 90-day window).

**Sandbox limitation, stated plainly:** direct fetches of exa.ai, a16z.com, bloomberg.com, williamsf1.com and the calendar sites were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## What the thin row got wrong

- **Person.** The row named *Jeff Wang, CEO & Co-founder*. Exa's own Series C post is signed by **Will Bryk, CEO & Co-founder**; a16z's investment note and Lightspeed's profiles name Bryk as CEO and Jeff Wang as co-founder. Dan McArdle is Co-Founder & CTO. The brief is addressed to Bryk.
- **Source.** The row cited Bloomberg; the primary source is the company's blog post of 20 May 2026 (Bloomberg confirms the same figures the same day).
- **Score.** The row carried 84. Re-scored at 72: the workstream is lighter than a compute or data partner, the brand is a developer API with little consumer reach, and there is no listing signal.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $250M Series C led by Andreessen Horowitz at $2.2B, 20 May 2026 | VERIFIED (company post) + REPORTED (Bloomberg) | exa.ai/blog/announcing-series-c; Bloomberg 20 May 2026 |
| $85M Series B at $700M led by Benchmark, Sep 2025; $22M Series A led by Lightspeed, Jul 2024; YC and NVentures | VERIFIED | Exa Series B post / SiliconANGLE 3 Sep 2025; TechCrunch 16 Jul 2024 |
| $357M across three rounds | DERIVED (22 + 85 + 250) | the three announcements above |
| >5,000 companies, 400,000 developers; Cursor, Cognition, HubSpot | VERIFIED (company post) | exa.ai blog; Bloomberg |
| Marcus Holm joins as CRO from LaunchDarkly (President) | VERIFIED | exa.ai blog, 20 May 2026 |
| Will Bryk CEO; Jeff Wang co-founder; Dan McArdle CTO; founded 2021; Harvard | VERIFIED | exa.ai blog; a16z announcement; Lightspeed profile |
| No CMO, CFO or COO listed; finance reports to Jeff Wang | VERIFIED (absence) | Exa VP Finance posting (Ashby, dated Jun 2026, after the brief date; the absence also holds at 22 May) |
| HQ San Francisco | VERIFIED | Bloomberg; California filing (430 Shotwell St) |
| Exa is a native Claude connector / MCP server | VERIFIED | claude.com/connectors/exa; exa.ai/mcp |
| Claude is Williams' Official Thinking Partner (multi-year, 2026) | VERIFIED | williamsf1.com |
| Grid occupancy (Google Cloud/McLaren, Microsoft/Mercedes+Alpine, Meta AI/Mercedes, TWG AI/Cadillac, Cognition+CoreWeave/Aston Martin, Oracle/Red Bull, HP+IBM/Ferrari, ElevenLabs/Audi; Williams roster) | VERIFIED | sponsor table `seeds/sponsors.json` |
| Monaco GP 5-7 Jun, Spanish GP 12-14 Jun, Austrian GP 26-28 Jun, British GP 3-5 Jul | VERIFIED | calendar table + formula1.com dates via ESPN / F1 Experiences |

## Screen-outs and things not claimed

- **No revenue figure** is used: Exa has not disclosed revenue (Bloomberg). Third-party estimates (Sacra) are not used.
- **No motorsport tie found** for Bryk, Wang, McArdle or Holm after checking; `leadership_ties` is empty.
- **Exa is not a partner of any F1 or FE team** (checked against the sponsor table and a live search of 2026 AI partnerships).
- **Employee count** (Tracxn: 121 at Jan 2026) is not used in the brief.
- **Deal size ($2-4M a year) is an ESTIMATE**, labelled as such.
- **MODE A is claimed with a caveat:** the workstream (live retrieval for the Claude-based agents Williams already runs) is real but lighter than compute or data; ops fit is scored 14/20 and the first risk row says so.

## Decision path

Will Bryk (Co-Founder & CEO) is the sponsorship owner. Path: Marcus Holm (incoming CRO, go-to-market) and Jeff Wang (co-founder; finance reports to him). Technical counterpart: Dan McArdle (Co-Founder & CTO). No CMO is listed.

## Ledger as built (N° 213, 21 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Will Bryk, Co-Founder & CEO at Exa |
| decision_maker | person_role | yes | verified | Will Bryk, Co-Founder & CEO, Exa at Exa |
| key_facts | funding | yes | verified | $250M Series C led by Andreessen Horowitz at a $2.2B valuation, announced 20 May 2026 (Exa blog; Bloomberg) |
| deck | funding | yes | verified | Exa, the search engine built for AI agents, announced a $250M Series C led by Andreessen Horowitz at a $2.2B valuation on 20 May 2026, more than tripling the $7 |
| key_facts | funding | yes | verified | Andreessen Horowitz (lead, Series C); Benchmark led the $85M Series B at $700M in September 2025; Lightspeed led the $22M Series A in July 2024; Y Combinator an |
| the_case_p1 | funding | yes | verified | On 20 May Exa announced a $250M Series C led by Andreessen Horowitz at a $2.2B valuation, confirmed by Bloomberg the same day. |
| key_facts | date | yes | verified | $250M Series C led by Andreessen Horowitz at a $2.2B valuation, announced 20 May 2026 |
| the_case_p1 | funding | yes | verified | It follows an $85M Series B led by Benchmark at $700M in September 2025 and a $22M Series A led by Lightspeed in July 2024. |
| key_facts | sponsorship | yes | verified | Google Cloud at McLaren and Microsoft at Mercedes and Alpine are the search incumbents on the grid; Meta AI at Mercedes, TWG AI at Cadillac and Cognition at Ast |
| the_case_p2 | revenue | yes | verified | A challenger with a $250M war chest and a new revenue chief has a story to tell against them. |
| key_facts | other | yes | verified | Exa is a native Claude connector and MCP server; Claude is Atlassian Williams Racing's Official Thinking Partner from 2026 |
| bottom_line | revenue | yes | verified | A $250M round at $2.2B, a new revenue chief with a go-to-market mandate, and a native connection to the Claude programme already on the Williams give Exa the bu |
| key_facts | other | yes | verified | HQ San Francisco; founded 2021 out of Y Combinator |
| extended | funding | no | verified | On 20 May 2026 Exa announced a $250M Series C led by Andreessen Horowitz at a $2.2B valuation, on its own blog and confirmed by Bloomberg the same day. |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | The valuation has more than tripled since the $85M Series B at $700M led by Benchmark in September 2025. |
| why_now_callout | event | yes | verified | Monaco GP |
| why_now_callout | event | yes | verified | British GP |
| extended | event | no | verified | Spanish GP |
| extended | event | no | verified | Austrian GP |
| extended | event | no | verified | The British GP |
