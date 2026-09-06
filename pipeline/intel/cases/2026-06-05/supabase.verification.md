# Supabase → Atlassian Williams Racing — verification log (N° 202, 5 Jun 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) with Claude acting as
scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor
table, 13-rule audit and the 2-page render ran as code. The case sits on the row's date, 5 Jun 2026,
in rebuild mode; `supabase.run.json` is the case record `python -m intel.backfill --cases` imports.

**Sandbox limitation, stated plainly:** direct fetches of supabase.com, prnewswire.com, cnbc.com,
techcrunch.com and williamsf1.com were blocked by the egress proxy. Each claim below was checked
against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line
as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE
CIRCULATION.

## The trigger

Supabase announced the **$500M Series F led by GIC at a $10.5B post-money valuation** on its own
blog on 4 Jun 2026 (company-announced, not merely reported); CNBC (4 Jun) and TechCrunch (5 Jun)
carry the same figures. The thin row's "$10B" is TechCrunch's rounding; the brief uses the company's
$10.5B. The row's date is 5 Jun; the trigger is one day earlier, inside the 90-day window.

## Ledger (claims verified against search summaries of the primary pages)

| Claim | Status | Evidence |
|---|---|---|
| Paul Copplestone, Co-Founder & CEO | VERIFIED | The Org, Supabase posts |
| Ant Wilson CTO; Scott Buxton CFO; Rory Wilding COO/CCO; Tracy Lane GC; no CMO listed | VERIFIED | The Org, LinkedIn |
| $500M Series F, GIC lead, $10.5B post-money, 4 Jun 2026; investors as listed; total > $1B | VERIFIED (company) | supabase.com/blog/supabase-series-f; CNBC; TechCrunch |
| Series E $100M at $5B (Oct 2025); Series D $200M at $2B (Apr 2025) | VERIFIED (company) | PR Newswire Series E release; Series D coverage |
| 250,000+ customers; 9M+ developers; database launches +600% in a year; >60% via AI tools; Claude Code largest contributor since Jan 2026; Multigres preview | REPORTED (company figures via coverage) | Series F post as summarised by TechCrunch, TipRanks, Elets CIO |
| Founded 2020; San Francisco; remote-first | VERIFIED | Crunchbase, Craft (some profiles list Singapore) |
| Claude Official Thinking Partner of Williams (multi-year, 2026) | VERIFIED | williamsf1.com |
| Grid occupancy (Williams roster; Oracle, Google Cloud/Dell, Confluent/Dynatrace, Microsoft, NetApp, IBM, Core Scientific/TWG AI) | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Austrian GP 28 Jun; British GP 5 Jul 2026; Austin and Las Vegas in the autumn | VERIFIED | calendar table + silverstone.co.uk / RacingNews365 |

## Screen-outs and things not claimed

- **No motorsport tie found** for Copplestone, Wilson, Wilding or Buxton; `leadership_ties` is empty after checking.
- **No revenue or ARR figure** is used: none is public.
- **Headquarters** is given as San Francisco (Supabase Inc.); the company is fully remote and some profiles list Singapore. Not load-bearing.
- **Deal size ($3-5M a year) is an ESTIMATE**, labelled as such.
- **The score is 75, not the thin row's 83.** What holds it back: no chief marketing officer and a developer-led, community marketing culture (brand fit 14); no hard deadline (urgency 12); the operational workstream is the team's application layer, not race data (ops fit 14).

## Decision path

CEO Paul Copplestone (owner of a first sports partnership) → Rory Wilding, COO & Chief Commercial Officer → Scott Buxton, CFO. No CMO exists on the leadership listings found; say so on the first call rather than guessing a marketing counterpart.

## Ledger as built (N° 202, 24 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Paul Copplestone, Co-Founder & CEO at Supabase |
| decision_maker | person_role | yes | verified | Paul Copplestone, Co-Founder & CEO, Supabase at Supabase |
| key_facts | funding | yes | verified | $500M Series F led by GIC at a $10.5B post-money valuation, announced 4 Jun 2026; Series E $100M at $5B (Oct 2025); Series D $200M at $2B (Apr 2025) |
| deck | funding | yes | verified | Supabase, the open-source Postgres backend that more than 9 million developers build on, closed a $500M Series F led by GIC at a $10.5B post-money valuation on  |
| key_facts | funding | yes | verified | GIC (lead); Accel, Y Combinator, Craft, Felicis, Peak XV and Coatue returning; Stripe (second investment) and Salesforce Ventures; total raised over $1B |
| the_case_p1 | revenue | yes | verified | Supabase announced on 4 June a $500M Series F led by GIC, with Accel, Y Combinator, Craft, Felicis, Peak XV and Coatue returning, a second investment from Strip |
| key_facts | date | yes | verified | $500M Series F at a $10.5B post-money valuation, announced 4 Jun 2026 (company blog; CNBC, TechCrunch) |
| the_case_p1 | funding | yes | verified | The post-money valuation is $10.5B, up from $5B at the October 2025 Series E and $2B at the April 2025 Series D; |
| key_facts | sponsorship | yes | verified | Oracle (Red Bull), Google Cloud and Dell (McLaren), Confluent and Dynatrace (Racing Bulls) occupy the database, cloud and data lanes; no open-source database or |
| the_case_p1 | funding | yes | verified | total capital raised now exceeds $1B. |
| key_facts | other | yes | verified | Supabase says Claude Code has been the largest contributor to new databases on its platform since the start of 2026; Claude is Official Thinking Partner of Atla |
| the_case_p1 | funding | yes | verified | The company reports more than 250,000 customers and over 9 million developers, and says database launches grew 600% in the past year, with over 60% created by A |
| key_facts | other | yes | verified | US company (Supabase Inc., San Francisco), remote-first; founded 2020 |
| bottom_line | funding | yes | verified | A $500M raise at $10.5B, more than 9 million developers, and Claude Code as the top creator of Supabase databases put Supabase at peak brand-investment capacity |
| trigger | date | yes | verified | funding round |
| extended | revenue | no | verified | On 4 June 2026 Supabase announced a $500M Series F led by GIC at a $10.5B post-money valuation, with Accel, Y Combinator, Craft, Felicis, Peak XV and Coatue ret |
| extended | funding | no | verified | The Series E in October 2025 priced the company at $5B; |
| extended | funding | no | verified | the Series D in April 2025 at $2B. |
| extended | funding | no | verified | A company re-priced from $2B to $10.5B inside fourteen months has a story to tell enterprise buyers and, eventually, public markets, and now has the budget to t |
| extended | funding | no | verified | Supabase says database launches on its platform grew 600% in the past year and that over 60% of new databases are created by AI tools, with Claude Code the larg |
| why_now_callout | event | yes | verified | The British GP |
| value_content | event | yes | verified | British GP |
| extended | event | no | verified | United States GP |
| extended | event | no | verified | Las Vegas GP |
