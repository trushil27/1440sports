# Glow → TGR Haas F1 Team — verification log (N° 160, brief dated 22 Jul 2026)

Built in-session on 6 Sep 2026 at no API cost from a case spec: Claude did the research and writing; the pipeline's calendar and sponsor-table checks, 13-rule audit and 2-page render ran as code. The brief is issued for the date the signal sits on in the desk (22 Jul 2026), which is also the trigger date.

**Sandbox limitation, stated plainly:** direct fetches of glow.io, globenewswire.com, techcrunch.com, securityweek.com and calcalistech.com were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## The trigger

Company-announced: Glow's release of 22 Jul 2026 (GlobeNewswire, mirrored on glow.io, Yahoo Finance; TechCrunch, SecurityWeek and Help Net Security coverage) states $180M in funding at a $1.2B valuation, the leads and participants, paying customers and the use of funds. The thin row's source (GlobeNewswire) is the same release; the company newsroom copy is now the evidence URL.

## Corrections to the thin row

- The row called it a "$180M Series A". The company release gives only the $180M total; CTech reports three rounds (seed, Series A, Series B). The brief says "$180M raised" and labels the split as reported.
- The row scored Glow 87 (HOT TOP TIER). That is inflated for a year-old company with about 100 staff and no disclosed revenue. Re-scored 71 (HOT): capacity 13 and ops fit 14 hold it back, and the first risk row says so. Brand fit 15 rests on the six security vendors already buying F1 to reach CISOs, a precedent the sponsor table documents.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $180M at $1.2B; leads Sequoia, Cyberstarts, Greenoaks, Redpoint; participants Index, Swish, Lux, Operator Collective, Holly; 22 Jul 2026; use of funds (US go-to-market, Glow Labs) | VERIFIED (company release via search summary) | glow.io newsroom; GlobeNewswire |
| Three rounds: $20M seed, $60M Series A at $400M, $100M Series B; ~100 staff, ~65 in Israel | REPORTED | CTech 22 Jul 2026; SecurityWeek |
| Founded 2025; Tel Aviv and Palo Alto | VERIFIED / REPORTED | SecurityWeek; TechCrunch |
| Leadership: Roi Tiger CEO (Meta VP Eng, Onavo founder); Omer Singer CTO; Ophir Arie VP R&D; Arnon Joseph CPO; Emily Heath COO (Wiz board through the $32B Google acquisition, ex-Cyberstarts partner); Patti Degnan CISO; no CMO listed | VERIFIED | company release and about page (search summaries); Pulse2 on the Degnan appointment |
| Product: prevention-first control of software, AI agents and developer tools; blocked malicious npm packages; flagged devices with missing or degraded EDR; customers in healthcare, retail, financial services | VERIFIED (company release) | glow.io; Help Net Security |
| Haas: Kannapolis HQ, Banbury, Maranello; TGR title 2026; Mphasis, CommScope/Ruckus, Orion180; cybersecurity (product) open | VERIFIED | haasf1team.com; team profile |
| Haas roster and security lanes across the grid | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| United States GP (Oct), Las Vegas GP (Nov), Miami GP; 24 rounds | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Screen-outs and things not claimed

- **Leadership ties:** no Glow leader found with prior F1/FE employment or sponsorship history; `leadership_ties` empty after checking. Emily Heath's Wiz board seat is a marketing-playbook signal, not a motorsport tie, and is described as such.
- **Revenue:** none disclosed; none used. The "28-day average resolution" and "living asset inventory" metrics appear in coverage but are not load-bearing here.
- **The Haas deployment** in VALUE is a proposal, written as one; Glow has no motorsport customer.
- **Deal size $2-4M a year** is a 1440 ESTIMATE, labelled as such.

## Ledger as built (N° 160, 21 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Roi Tiger, CEO & Co-Founder at Glow |
| decision_maker | person_role | yes | verified | Roi Tiger, CEO & Co-Founder, Glow at Glow |
| key_facts | funding | yes | verified | $180M raised at a $1.2B valuation, led by Sequoia, Cyberstarts, Greenoaks and Redpoint Ventures with Index Ventures, Swish Ventures, Lux Capital, Operator Colle |
| deck | funding | yes | verified | Glow, the Tel Aviv and Palo Alto endpoint-security company founded in 2025 by former Meta engineering VP Roi Tiger, emerged from stealth on 22 July 2026 with $1 |
| key_facts | funding | yes | verified | Sequoia, Cyberstarts, Greenoaks, Redpoint Ventures (leads); Index Ventures, Swish Ventures, Lux Capital, Operator Collective, Holly Ventures |
| the_case_p1 | funding | yes | verified | Glow's release states $180M in funding at a $1.2B valuation, led by Sequoia, Cyberstarts, Greenoaks and Redpoint Ventures, with Index, Swish, Lux, Operator Coll |
| key_facts | date | yes | verified | Emerged from stealth on 22 Jul 2026 with $180M in funding at a $1.2B valuation; funds a US go-to-market team and Glow Labs |
| the_case_p1 | funding | yes | verified | CTech reports it as three rounds in about a year, a $20M seed, a $60M Series A at $400M and a $100M Series B. |
| key_facts | sponsorship | yes | verified | CrowdStrike at Mercedes, Bitdefender at Ferrari, Keeper at Williams, 1Password (Red Bull), Cato Networks at Alpine, NinjaOne at Audi; Haas carries no cybersecur |
| the_case_p2 | funding | yes | verified | Glow's leadership has run that playbook from inside: COO Emily Heath sat on Wiz's board through its $32B sale to Google and was a Cyberstarts partner. |
| key_facts | other | yes | verified | Prevention-first control of software, AI agents and developer tools on employee devices; COO Emily Heath sat on the Wiz board through its $32B sale to Google (c |
| the_case_p2 | funding | yes | verified | A stealth exit with $180M is when a company buys its stage. |
| key_facts | other | yes | verified | Offices in Tel Aviv and Palo Alto, California; about 100 staff, roughly 65 in Israel (reported); the raise funds a US go-to-market team |
| bottom_line | revenue | yes | verified | A $180M stealth exit at $1.2B, a Sequoia and Cyberstarts syndicate, paying customers and a funded US sales build put Glow at the start of its brand-spend cycle. |
| trigger | date | yes | verified | stealth exit with funding |
| extended | funding | no | verified | On 22 July 2026 Glow emerged from stealth with $180M in funding at a $1.2B valuation. |
| extended | funding | no | verified | CTech reports the $180M as a $20M seed led by Sequoia and Cyberstarts, a $60M Series A led by Index Ventures with Greenoaks at a $400M valuation, and a $100M Se |
| extended | funding | no | verified | Its partner tier is one a year-old company with $180M can carry without distorting its budget, and product can form part of the consideration. |
| why_now_callout | event | yes | verified | The United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | United States GP |
