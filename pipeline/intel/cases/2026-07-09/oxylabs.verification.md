# Oxylabs → Audi Revolut F1 Team — verification log (N° 164, issued for 9 Jul 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec: Claude did the research and writing; the pipeline's code stages ran the freshness window, the claims ledger with the calendar and sponsor-table checks, the 13-rule audit and the 2-page render. The row came from a thin scan (SiliconANGLE); the primary source is the company release on GlobeNewswire, mirrored on warburgpincus.com.

**Sandbox limitation, stated plainly:** direct fetches of globenewswire.com, warburgpincus.com, oxylabs.io, finance.yahoo.com, thenextweb.com, proxyway.com and lb.lt were blocked by the egress proxy. Each claim below was checked against the search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The row was wrong about the person

The thin row named "Julius Irmantas Karosas, Co-founder & CEO". No such person appears in any source. Oxylabs was founded by **Julius Černiauskas**, who was CEO until the group's leadership change announced on 25 March 2026, when **Vytautas Savickas** became CEO and Černiauskas moved to Chairman of the Board. Savickas is the CEO quoted in the 9 July release and is the decision-maker here.

## The trigger, honestly labelled

- **$130M from Warburg Pincus (Capital Solutions Founders Fund), 9 Jul 2026** — company release. VERIFIED (search summary).
- **~$3.6B valuation** — reported by SiliconANGLE, TNW, IBTimes, Dealroom; not in the release headline. REPORTED, labelled so in the copy.
- **$350M ARR** — IBTimes / Dealroom citing the company. REPORTED, labelled so in the copy and in the second risk row.
- **First outside capital since 2015** — release. VERIFIED.
- **350,000+ customers** — release. VERIFIED.
- **HQ New York / 15+ offices** — release boilerplate via search summary; other listings still say Vilnius. Written as "describes itself as headquartered in New York" (REPORTED).

## Decision path

- **Vytautas Savickas, Chief Executive Officer** (group CEO from Q2 2026).
- Path: **Julius Černiauskas, founder and Chairman of the Board**; **Tomas Montvilas, Chief Commercial Officer**. **No chief marketing officer is listed**; the careers site advertises a Head of Marketing role. Vytautas Kirjazovas is Head of Communications.

## Leadership ties

No motorsport or sponsorship-deal history was found for Savickas, Černiauskas or Montvilas after searching; `leadership_ties` is empty.

## Team choice

No web-data, proxy or scraping brand is on the 2026 grid (searched Bright Data, Zyte, Decodo/Smartproxy: none found). Audi was chosen over Williams (VAST + Claude), Cadillac (TWG AI + Core Scientific), Racing Bulls (Confluent), McLaren (Alteryx + Google Cloud), Aston Martin (NetApp) and Haas (Mphasis) because its roster carries no data partner and because Revolut, its title partner, runs its European bank from Vilnius (Revolut Bank UAB, Bank of Lithuania register), which gives a real introduction path. The Revolut link is presented as an introduction, not as a relationship that exists.

## Screen-outs and things not claimed

- **Profitability** is not asserted with a figure; "profitable, bootstrapped" rests on the release's statement that the company took no outside capital in eleven years and the reported ARR.
- **Deal size ($2-4M a year) is an ESTIMATE**, labelled as such.
- The brand-protection workstream is described as a standard platform use case, not as something Audi has asked for.
- The score is held at 71: brand fit is 12 because the proxy heritage needs positioning, and ops fit is MODE B.

## Ledger as built (N° 164, 21 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Vytautas Savickas, Chief Executive Officer at Oxylabs |
| decision_maker | person_role | yes | verified | Vytautas Savickas, Chief Executive Officer, Oxylabs at Oxylabs |
| key_facts | funding | yes | verified | $130M investment from Warburg Pincus (Warburg Pincus Capital Solutions Founders Fund) at about $3.6B valuation, announced 9 Jul 2026; the company's first outsid |
| deck | funding | yes | verified | Oxylabs, the Vilnius-born web-data platform now headquartered in New York, took its first outside capital on 9 July 2026: $130M from Warburg Pincus at a reporte |
| key_facts | funding | yes | verified | Warburg Pincus (sole outside investor, via the Capital Solutions Founders Fund, 2026); bootstrapped before that |
| the_case_p1 | funding | yes | verified | On 9 July Oxylabs announced a $130M investment from the Warburg Pincus Capital Solutions Founders Fund; |
| key_facts | revenue | yes | verified | $350M annual recurring revenue, as reported by Dealroom and IBTimes citing the company (not in the release headline) |
| the_case_p1 | funding | yes | verified | the release does not print a valuation, and the $3.6B figure is reported by SiliconANGLE, TNW and Dealroom. |
| key_facts | date | yes | verified | $130M investment from Warburg Pincus at about $3.6B valuation, announced 9 Jul 2026 |
| the_case_p1 | revenue | yes | verified | The business serves over 350,000 customers across cybersecurity, e-commerce and finance, and Dealroom and IBTimes report $350M of annual recurring revenue, citi |
| key_facts | sponsorship | yes | verified | No web-data, proxy or scraping brand on the 2026 grid; adjacent data lanes are held by VAST (Williams), TWG AI (Cadillac), Confluent (Racing Bulls), Alteryx (Mc |
| bottom_line | funding | yes | verified | A $130M first outside round from Warburg Pincus at a reported $3.6B, a new chief executive with an international mandate, and a title partner whose European ban |
| key_facts | other | yes | verified | Revolut, Audi's 2026 title partner, runs its European bank from Vilnius (Revolut Bank UAB, licensed by the Bank of Lithuania and the ECB), the city where Oxylab |
| extended | funding | no | verified | On 9 July 2026 Oxylabs announced a $130M investment from the Warburg Pincus Capital Solutions Founders Fund, its first outside capital since it was founded in V |
| key_facts | other | yes | verified | Release issued from New York and Vilnius; the company describes itself as headquartered in New York with more than 15 offices globally (reported); serves over 3 |
| extended | funding | no | verified | SiliconANGLE, TNW, IBTimes and Dealroom report about $3.6B, and the brief labels that figure as reported. |
| trigger | date | yes | verified | funding round |
| why_now_callout | event | yes | verified | The Dutch GP |
| why_now_callout | event | yes | verified | Italian GP |
| extended | event | no | verified | Las Vegas GP |
| extended | event | no | verified | Dutch GP |
