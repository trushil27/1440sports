# groundcover → TGR Haas F1 Team — verification log (N° 157, issued for 29 Jul 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from the batch-6 row
dated 29 Jul 2026, with Claude acting as scanner, verifier and writer through the pipeline's
injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as
code. The desk row's team was null; Haas is this case's own choice from the sponsor table.

**Sandbox limitation, stated plainly:** businesswire.com, hpcwire.com, calcalistech.com,
siliconangle.com, theorg.com and haasf1team.com were blocked by the egress proxy. Every claim was
checked against the search summary of the page named as the evidence URL. Treat each VERIFIED line
as REPORTED until a person opens the link. Confidence is MEDIUM; the footer reads VERIFY BEFORE
CIRCULATION.

## The thin row, corrected

- **The row's person was wrong.** "Shahar Fogel" does not exist at groundcover; the CEO and
  co-founder is **Shahar Azulay** (company release, Calcalist, The Org). Corrected throughout.
- "Doubled headcount; global expansion mandate activated same day" — headcount doubled to about
  140 (Calcalist); the release speaks of growth and the US offices, not a "mandate". The copy says
  "US push".
- Round, lead, investors and the \$160M total check out against the release.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Shahar Azulay, Co-founder & CEO; Yechezkel Rabinovich, CTO; founded 2021; PMO cyber unit | VERIFIED | Calcalist 29 Jul 2026; The Org |
| Azulay ex-Apple machine-learning manager | REPORTED | Tech Funding News |
| \$100M Series C led by One Peak, 29 Jul 2026; Morgan Stanley Expansion Capital; Zeev, Angular, Heavybit, Jibe; total \$160M | VERIFIED | Business Wire release (search summary); Axios; SiliconANGLE |
| ARR tripled; headcount doubled; > 250 paying customers; Fortune 5; seven-figure contracts | VERIFIED | company release |
| Valuation ≈ \$500M, ~4× prior round; 140 staff, ~80 in Israel, rest Boston and San Francisco | REPORTED | Calcalist |
| \$35M Series B led by Zeev, April 2025; total then \$60M | VERIFIED | SiliconANGLE 10 Apr 2025; PR Newswire |
| eBPF + bring-your-own-cloud; data stays in the customer environment | VERIFIED | company release |
| Chris Churilo, VP Marketing (SF); Ran Ziskovich, VP Finance; no CMO/CFO titled | REPORTED | The Org; RocketReach; release media contact |
| Haas: TGR title partner 2026; Kannapolis + Banbury; Mphasis, CommScope, Ruckus, Infobip, Fix Network; no observability partner | VERIFIED | haasf1team.com; sponsor table; team profile |
| Splunk/Cisco at McLaren; Dynatrace and Confluent at Racing Bulls; other lanes | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Italian GP, United States GP (Austin), Las Vegas GP | VERIFIED | calendar table |

## Leadership ties

- Shahar Azulay, Yechezkel Rabinovich, Chris Churilo: **none found** after checking.

## Screen-outs and things not claimed

- **No absolute ARR** is claimed; only the tripling the company states.
- **Deal size (\$1.5–3M a year) is an ESTIMATE**, labelled as such.
- The cost cap is mentioned as context only; no figure is claimed for it.
- Cadillac's open observability lane is acknowledged and ruled out on price, transparently.

## Ledger as built (N° 157, 23 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Shahar Azulay, Co-founder & CEO at groundcover |
| decision_maker | person_role | yes | verified | Shahar Azulay, Co-founder & CEO, groundcover at groundcover |
| key_facts | funding | yes | verified | $100M Series C led by One Peak, announced 29 Jul 2026; total funding $160M; valuation about $500M, roughly four times the prior round (Calcalist, reported) |
| deck | funding | yes | verified | groundcover, the Tel Aviv observability company that says it wants to replace Datadog, announced a $100M Series C led by One Peak on 29 July, with Morgan Stanle |
| key_facts | funding | yes | verified | One Peak (lead); Morgan Stanley Expansion Capital; existing investors Zeev Ventures, Angular Ventures, Heavybit and Jibe |
| deck | funding | yes | verified | Total funding is $160M; |
| key_facts | revenue | yes | verified | Annual recurring revenue tripled over the past year; several seven-figure contracts signed (company release; no absolute figure public) |
| deck | funding | yes | verified | Calcalist puts the valuation at about $500M, roughly four times the last round (reported). |
| key_facts | date | yes | verified | $100M Series C led by One Peak, announced 29 Jul 2026 |
| the_case_p1 | funding | yes | verified | the $35M Series B, led by Zeev, closed in April 2025. |
| key_facts | sponsorship | yes | verified | Splunk sits with McLaren through Cisco and Dynatrace at Racing Bulls; Haas carries no observability partner |
| bottom_line | revenue | yes | verified | A $100M Series C led by One Peak, tripled ARR and a doubled team give groundcover the budget and the motive to be seen beside Splunk and Dynatrace; |
| key_facts | other | yes | verified | Headcount doubled to about 140, roughly 80 in Israel and the rest in Boston and San Francisco; more than 250 paying customers from startups to Fortune 5 enterpr |
| the_case_p2 | sponsorship | yes | verified | Dynatrace at Racing Bulls |
| key_facts | other | yes | verified | Offices in Boston and San Francisco; VP Marketing based in San Francisco |
| extended | funding | no | verified | groundcover announced a $100M Series C led by One Peak on 29 July 2026, with Morgan Stanley Expansion Capital and existing investors Zeev Ventures, Angular Vent |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | Calcalist reports a valuation of about $500M, roughly four times the prior round. |
| extended | funding | no | verified | Cadillac's observability lane is open but its 'fewer, bigger, better' policy is priced above a $500M company; |
| extended | funding | no | verified | Observability lane open, but the 'fewer, bigger, better' partner policy is priced above a $500M company. |
| extended | event | no | verified | The Italian GP |
| extended | event | no | verified | United States GP |
| extended | event | no | verified | Las Vegas GP |
