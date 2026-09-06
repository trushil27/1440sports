# Saronic → Cadillac F1 Team — verification log (N° 230, row dated 5 May 2026)

Built in-session on 6 Sep 2026 at no API cost for the desk row dated 5 May 2026 (batch 21). Claude acted as researcher, verifier and writer; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as code via `intel.session_case`.

**Sandbox limitation, stated plainly:** direct fetches of prnewswire.com, saronic.com and cnbc.com were blocked by the egress proxy. Every claim below was checked against the search summary of the primary page named as the evidence URL (Saronic's PR Newswire release; Naval News, WorkBoat, gCaptain, Defense News and GovCon Wire as secondaries). Treat each VERIFIED line as REPORTED until a person opens the link; confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

The thin row's trigger holds in full: the $1.75B Series D at a $9.25B post-money valuation was announced by the company on **31 Mar 2026**, 35 days before the row's date. The thin row's CNBC source is a credible secondary; the primary is the PR Newswire release. The '$300M shipyard expansion' is the Franklin, Louisiana project announced in December 2025, and 'Port Alpha Texas site search' was accurate on the row date; Brownsville was announced on 16 Jul 2026 (after the row; used only where labelled).

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Dino Mavrookas, Co-Founder & CEO (Navy SEAL; Vista Equity Partners) | VERIFIED (search summary) | saronic.com/team; The Org |
| $1.75B Series D led by Kleiner Perkins at $9.25B post-money; investor list; 31 Mar 2026 | VERIFIED (search summary) | PR Newswire release; Sullivan & Cromwell; CNBC |
| $600M Series C at $4B (2025) | VERIFIED (search summary) | Series D release; CNBC |
| $392M Navy Corsair production contract, Dec 2025; <12 months prototype to production | VERIFIED (search summary) | Naval News; WorkBoat; gCaptain |
| $300M Franklin, LA expansion; 300,000 sq ft; 1,500 jobs; Marauder 180 ft | VERIFIED (search summary) | Naval News Dec 2025; WorkBoat |
| Port Alpha: 20-plus vessels a year by 2027; 10,000 direct jobs over a decade | VERIFIED (company statement) | Series D release |
| Port Alpha in Brownsville, TX; $3.2B; 16 Jul 2026 | VERIFIED (search summary) — after row date | Saronic (Medium); Defense News; MyRGV |
| HQ Austin, TX; Corsair plant in central Texas | VERIFIED (search summary) | GovCon Wire; Series D release |
| Rob Lehman Co-Founder & CCO (owns marketing, sales); Emily Shanklin CMO (ex-SpaceX); Patrick Depriest CFO; Vibhav Altekar CTO | VERIFIED (search summary) | saronic.com/team; LinkedIn |
| No defence/maritime brand on the F1 grid; Boeing at Alpine; Zoox at Williams; Cadillac roster inaugural | VERIFIED | sponsor table |
| Cadillac engineered at Silverstone; Fishers campus under construction | VERIFIED (search summary) | GM News 19 Jan 2026 |
| Miami GP 3 May 2026; United States GP (Austin) late Oct; Las Vegas Nov | VERIFIED | calendar table |

## Screen-outs and things not claimed

- **Leadership ties: none found** for Mavrookas, Lehman, Shanklin or Depriest; Shanklin's SpaceX brand-building record is the nearest thing to a sponsorship pedigree and is noted, not scored.
- **Score is honest.** Capacity is near the top of the scale (19) and the category is clean, but this is a halo (ops fit 10) and a defence brand on a car carries reputational care (brand fit 13). 71, not the thin row's 83.
- **Deal size ($4-6M a year) is an ESTIMATE**, labelled as such.
- **The engineering-exchange and recruiting programme is a proposal**, not an existing arrangement.
- Headcount for the company as a whole is not public and is not used; only the Franklin workforce figures and the stated job targets are.

## Ledger as built (N° 230, 22 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Dino Mavrookas, Co-Founder & CEO at Saronic |
| decision_maker | person_role | yes | verified | Dino Mavrookas, Co-Founder & CEO, Saronic at Saronic |
| key_facts | funding | yes | verified | $1.75B Series D led by Kleiner Perkins at a $9.25B post-money valuation, announced 31 Mar 2026; follows a $600M Series C at a $4B valuation in 2025 |
| deck | funding | yes | verified | Saronic, the Austin-based builder of autonomous naval vessels, closed a $1.75B Series D led by Kleiner Perkins at a $9.25B post-money valuation on 31 March 2026 |
| key_facts | funding | yes | verified | Kleiner Perkins (lead); Advent International, Bessemer Venture Partners, DFJ Growth, BAM Elevate (new); 8VC, Caffeinated Capital, Andreessen Horowitz, Elad Gil, |
| the_case_p1 | funding | yes | verified | On 31 March 2026 Saronic announced a $1.75B Series D led by Kleiner Perkins at a $9.25B post-money valuation, with Advent International, Bessemer Venture Partne |
| key_facts | date | yes | verified | $1.75B Series D at a $9.25B post-money valuation announced 31 Mar 2026, with capital earmarked for shipbuilding capacity including Port Alpha, the planned Texas |
| the_case_p1 | funding | yes | verified | a $600M Series C had valued it at $4B in 2025. |
| key_facts | sponsorship | yes | verified | No defence, maritime-autonomy or shipbuilding brand on the F1 grid; the nearest adjacencies are Boeing at Alpine and Zoox at Williams |
| the_case_p1 | funding | yes | verified | In December the US Navy awarded a $392M production contract for its 24-foot Corsair, prototype to production in under 12 months. |
| key_facts | other | yes | verified | US Navy $392M Corsair production contract (Dec 2025), prototype to production in under 12 months; $300M expansion of the Franklin, Louisiana shipyard adding 300 |
| bottom_line | funding | yes | verified | A $1.75B Series D at $9.25B, a $392M Navy production contract and two shipyards to staff give Saronic the budget and the motive for a national platform. |
| key_facts | other | yes | verified | Headquartered in Austin, Texas; Corsair plant in central Texas; Marauder shipyard in Franklin, Louisiana; Port Alpha sited in Brownsville, Texas (announced Jul  |
| extended | funding | no | verified | A $600M Series C had valued the company at $4B in 2025, so the price more than doubled in about a year. |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | In December 2025 the US Navy awarded Saronic a $392M production contract for the 24-foot Corsair, announced at the Reagan National Defense Forum, with the Navy  |
| extended | funding | no | verified | The same month Saronic announced a $300M expansion of its Franklin, Louisiana shipyard, adding more than 300,000 square feet and 1,500 jobs, where the 180-foot  |
| why_now_callout | event | yes | verified | United States GP |
| extended | event | no | verified | The Miami GP ran on 3 May 2026 |
| extended | event | no | verified | The United States GP |
| extended | event | no | verified | Austin. The United States GP |
| extended | event | no | verified | Austin round |
