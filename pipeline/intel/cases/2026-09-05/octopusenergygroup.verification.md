# Octopus Energy Group → Jaguar TCS Racing — verification log (N° 139, row of 5 Sep 2026)

Built in-session at no API cost on 6 Sep 2026 (batch 3) with Claude as scanner, verifier and writer through `intel.session_case`; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code.

**Sandbox limitation, stated plainly:** octopus.energy, globenewswire.com, uplight.com, sifted.eu and theorg.com are egress-blocked. Every claim was checked against the search summary of the primary page named as the evidence URL. Treat each VERIFIED line as REPORTED until a person opens the link. Confidence MEDIUM; footer VERIFY BEFORE CIRCULATION.

## The trigger

Octopus Energy Group's release of 1 Sep 2026 (GlobeNewswire, datelined Houston / Boulder) states the investment in Uplight has closed; Schneider Electric continues as an investor alongside Octopus's new majority stake; Nick Chaset is CEO of Uplight alongside Octopus Energy US; targets $1bn customer savings and 20 GW flexible capacity in five years; Uplight manages 8.5 GW across 85+ utilities. The definitive agreement was announced 24 Mar 2026 (Uplight press page, octopus.energy). Secondary: Renewable Energy Magazine (4 Sep 2026), Daily Energy Insider. The deal value is not disclosed and is not claimed.

## Corrections to the thin row

- The row said "raising up to £500M of new equity (reported Mar 2026)". The only report found is ION Analytics, June 2025 (working with KPMG on a minority-stake raise). No 2026 confirmation exists, so the brief does not use it.
- The row said "valued ~$5B". The latest valuation is $9B (7 May 2024, company release). Used instead.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Greg Jackson, Founder & CEO | VERIFIED | octopus.energy leadership page (summary); WRI profile |
| Rebecca Dibb-Simkin, Chief Product and Marketing Officer; Stuart Jackson, Co-Founder & CFO; no separate CMO | REPORTED | Crunchbase, LinkedIn, The Drum, Board Intelligence (company page blocked) |
| Uplight investment completed 1 Sep 2026; Chaset; Schneider minority; 8.5 GW / 85+ utilities; $1bn / 20 GW targets | VERIFIED | company release via GlobeNewswire (summary) |
| $9B valuation, May 2024; Generation IM 13%, CPP 12% | VERIFIED | octopus.energy release, 7 May 2024 (summary); Generation IM newsroom |
| Kraken $1B round at $8.65B; $850M to Octopus; D1 lead; 13.7% retained; mid-2026 separation target | REPORTED | CNBC 30 Dec 2025; Sifted; Ontario Teachers' release. Completion of the separation not confirmed as of 5 Sep 2026 |
| FY25 revenue £13.7bn (+10%), 10m customers, 7.6m UK homes, £255m net loss, £1.5bn net assets | REPORTED | Sifted on the filed annual report (octopusenergy.group PDF) |
| Arsenal official energy partner since Oct 2016 | VERIFIED | arsenal.com; Octopus Group newsroom |
| Ford integrated Electroverse, 2 Sep 2025 | VERIFIED | Ford of Europe media centre |
| Electroverse 1m+ chargers, 40+ countries | VERIFIED | octopus.energy release (summary) |
| 653k smart EV-tariff customers (Ofgem, Jul 2025), more than half with Octopus | REPORTED | octopus.energy Intelligent Octopus Go page citing Ofgem |
| Octopus Energy US in Houston; Uplight in Boulder | VERIFIED | octopusenergy.com press page; 1 Sep release dateline |
| Jaguar electric-only relaunch 2026; Bond Street; three new cars | REPORTED | electrive, 3 Nov 2025 |
| Jaguar TCS Racing roster (TCS, Castrol, Jaguar); Envision Group, Shell, TotalEnergies positions; Andretti roster | VERIFIED | sponsor table `seeds/sponsors.json` |
| Jeddah 18-19 Dec 2026; Austin 6 Feb; Miami 20 Feb; London 29-30 May 2027 | VERIFIED | calendar table `seeds/calendar_fe.json` |

## Decision path

Greg Jackson (Founder & CEO) is the decision maker: a founder-led group whose partnerships (Arsenal, Ford, the investor rounds) are fronted by him. Path: Rebecca Dibb-Simkin (Chief Product and Marketing Officer, the brand owner), Stuart Jackson (Co-Founder & CFO), Nick Chaset (CEO Octopus Energy US and Uplight) for a US extension. No separate CMO title exists; the CPMO holds marketing.

## Leadership ties

Searched Greg Jackson against Formula E / Formula 1 / motorsport: none found. Rebecca Dibb-Simkin's background is British Gas (Hive, Dyno-Rod), not motorsport. `leadership_ties` = none found.

## Screen-outs and things not claimed

- **Kraken (spin-out) is on `data/approached.json`** — the first risk row and the ask both require coordination before contact. This case is the consumer-brand parent, not Kraken.
- **No Octopus motorsport partnership found** (Formula E, Electroverse, Greg Jackson searches); Valencia CF sustainability partnership reported but not used.
- **Jaguar TCS Racing's real-world partners** reported by Jaguar media (Dow, Chase, Schaeffler) are not in the sponsor table and are not named in the copy; none is an energy retailer or charging brand. Castrol (a BP brand) is lubricants, flagged as a check, not a lock.
- **Deal size (£1.5–3M a season) is an ESTIMATE**, labelled as such.
- The Uplight transaction value, Octopus Energy US customer numbers and the status of the Kraken separation are not stated because they are not sourced.

## Ledger as built (N° 139, 22 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Greg Jackson, Founder & CEO at Octopus Energy Group |
| decision_maker | person_role | yes | verified | Greg Jackson, Founder & CEO, Octopus Energy Group at Octopus Energy Group |
| key_facts | funding | yes | verified | Valued at $9B in May 2024 when Generation Investment Management (13%) and CPP Investments (12%) increased their stakes; $850M of the $1B Kraken stake sale (Dec  |
| deck | revenue | yes | verified | Octopus Energy, Britain's largest household supplier with £13.7bn of revenue and 10 million customers, closed its majority investment in US grid-flexibility com |
| key_facts | funding | yes | verified | Generation Investment Management, CPP Investments, Origin Energy, Tokyo Gas; Kraken round led by D1 Capital with Fidelity International, Durable Capital and Ont |
| the_case_p1 | funding | yes | verified | It caps a year of capital re-shaping: $850M of the $1B Kraken stake sale (December 2025, $8.65B valuation) went to Octopus, on top of a $9B valuation set by Gen |
| key_facts | revenue | yes | verified | £13.7bn revenue in the year to 30 April 2025, up 10%, with 10 million customers, a £255m net loss and £1.5bn net assets (filed annual report, reported by Sifted |
| the_case_p1 | revenue | yes | verified | The year to 30 April 2025 brought £13.7bn of revenue, up 10%, and 10 million customers. |
| key_facts | date | yes | verified | Completed its majority investment in Uplight on 1 Sep 2026 (Schneider Electric stays a minority partner); Nick Chaset becomes Uplight CEO alongside Octopus Ener |
| bottom_line | funding | yes | verified | A $9B energy brand whose product is electric driving, fresh from the Uplight close and the Kraken proceeds, with a proven ten-year sports partnership and no pre |
| key_facts | sponsorship | yes | verified | No energy retailer, EV-charging or home-energy brand on the Jaguar TCS Racing roster (TCS, Castrol, Jaguar); Envision Group titles Envision Racing, Shell sits w |
| extended | funding | no | verified | The stated targets are $1 billion of customer savings and more than doubling flexible capacity to 20 GW over five years. |
| key_facts | other | yes | verified | Octopus already runs a long-term sports partnership: Arsenal's official energy partner since October 2016, with the Emirates Stadium on renewable supply and a f |
| extended | funding | no | verified | In December 2025 Octopus sold a $1B stake in Kraken at an $8.65B valuation, with $850M of the proceeds going to the group, and set a mid-2026 target for full se |
| key_facts | other | yes | verified | Octopus Energy US is based in Houston, Texas; Uplight in Boulder, Colorado, manages 8.5 GW of flexible load across more than 85 utilities |
| extended | funding | no | verified | The group itself was valued at $9B in May 2024 when Generation Investment Management and CPP Investments increased their stakes. |
| trigger | date | yes | verified | acquisition completed |
| extended | revenue | no | verified | In the year to 30 April 2025 Octopus recorded £13.7bn of revenue, up 10%, and grew to 10 million customers, including 7.6m UK homes. |
| extended | funding | no | verified | It reported a £255m net loss after one-off items, which is why the brief sizes the entry at partner level and includes an in-kind supply component. |
| why_now_callout | event | yes | verified | London E-Prix in May 2027 |
| deal_arch_para | event | yes | verified | London E-Prix |
| extended | event | no | verified | Austin E-Prix on 6 February 2027 |
