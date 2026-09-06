# Anduril Industries → Cadillac F1 Team — verification log (N° 220, issued for 15 May 2026)

Built in-session on 6 Sep 2026 at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from a case spec
(`andurilindustries.case.json`) with Claude doing the research, verification and writing; the calendar
table, sponsor table, 13-rule audit and the 2-page render ran as code via `python -m intel.session_case`.
The row came from a thin scan dated 15 May 2026 (score 86, no team, person Palmer Luckey); the trigger
was corrected, the sponsorship owner re-identified and the score re-set.

**Sandbox limitation, stated plainly:** direct fetches of anduril.com, techcrunch.com, bloomberg.com,
army.mil, hendrickmotorsports.com, nascar.com, gmdefensellc.com, theorg.com and cadillacf1team.com were
blocked by the egress proxy. Each claim below was checked against the search summary of the primary page
named as the evidence URL. Treat every VERIFIED line as REPORTED until a person opens the link.
Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger, corrected

The thin row said "$5B financing round; prior $4B round Mar 2026 at a reported $60B valuation". The
round is real but the shape was wrong: **$5B Series H at a $61B valuation, announced 13 May 2026** (not
15 May), led by Thrive Capital and Andreessen Horowitz; the **prior round was $2.5B at $30.5B in June
2025** — there was no $4B March 2026 round. The "$20B US Army contract" is confirmed as a ten-year
enterprise contract with a **$20B ceiling** (army.mil, 13 Mar 2026), a maximum rather than an obligated
amount. `signal_date` is 13 May; the row date 15 May is the run date. Inside the 90-day window.

## The finding the thin row missed

**Anduril already buys motorsport.** It is Official Defense Partner of NASCAR and presenting sponsor of
the NASCAR San Diego weekend (NASCAR, 14 Aug 2025); the Anduril 250 "Race the Base" Cup Series street
race ran at Naval Base Coronado on 21 June 2026; and it is a primary sponsor of Hendrick Motorsports'
William Byron for two Cup races a season 2026–2028 (Hendrick, 22 Oct 2025). None of this is F1 or FE,
so Anduril is not an existing grid partner, but it is the warmest signal class: a marketing chief who
has structured motorsport deals. `leadership_ties` therefore records **Jeff Miller — built the NASCAR
and Hendrick programmes (2025)**. No F1/FE tie was found for Schimpf, Steckman, Grimm, Stephens or
Luckey after checking.

## Ledger (all load-bearing claims covered; see the table appended by the build)

| Claim | Status | Evidence |
|---|---|---|
| Jeff Miller, marketing chief since May 2024 (ex-Cruise VP marketing) | VERIFIED | O'Dwyer's PR News, 15 May 2024 |
| Miller's title: chief marketing officer | REPORTED (2026 'CMO Insider' interview; Cannes Lions 2026 coverage); The Org still shows VP of Marketing | note in bio |
| $5B Series H, $61B, Thrive + a16z, >$11B over eight rounds, 13 May 2026 | VERIFIED (company announcement via TechCrunch / Bloomberg / GovConWire) | evidence URL |
| Prior round $2.5B at $30.5B, June 2025 | REPORTED | Yahoo Finance / TechCrunch |
| US Army enterprise contract, $20B ceiling, 13 Mar 2026 | VERIFIED | army.mil |
| Arsenal-1: $1B, Columbus, Ohio, production target July 2026 | VERIFIED | Breaking Defense / Ohio Governor's office |
| NASCAR Official Defense Partner; San Diego weekend; Coronado race 21 Jun 2026 | VERIFIED | NASCAR / Hendrick / Wikipedia |
| Hendrick primary sponsor of William Byron, two Cup races a season, 2026–2028 | VERIFIED | hendrickmotorsports.com |
| GM Defense–Anduril teaming agreement, Oct 2023 | VERIFIED | gmdefensellc.com; PR Newswire |
| Leadership: Schimpf CEO, Stephens chairman, Steckman President & CBO, Grimm COO, Luckey co-founder; HQ Costa Mesa | VERIFIED | OCBJ; company promotions release; Wikipedia |
| Cadillac roster (TWG AI exclusive AI, Core Scientific, IFS, Tenneco, Jim Beam, Tommy Hilfiger, Claro); GM works entry; no title sponsor sought | VERIFIED | cadillacf1team.com partners; sponsor table |
| Boeing at Alpine; Zoox at Williams | VERIFIED | alpinef1.com; sponsor table |
| IPO expected 2027 or later; no S-1 | REPORTED (expectation, labelled) | Forge Global; Investing.com |
| United States GP (Austin), Las Vegas GP, Miami GP in 2026 | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Decision path

**Jeff Miller** (chief marketing officer; Anduril's first marketing hire, May 2024) owns brand spend and
built the NASCAR and Hendrick programmes, so he is the sponsorship owner rather than Palmer Luckey.
Path: Matthew Steckman (President & Chief Business Officer), Matt Grimm (Co-Founder & COO), Brian
Schimpf (CEO); Palmer Luckey is the brand principal. No CFO is named in the sources opened.

## Screen-outs and things not claimed

- **Revenue is not used.** Pre-IPO market sites report ~$2.2B for 2025 and ~$4.3B 2026 guidance; these
  are not company disclosures and are left out of the brief.
- **No Lattice-on-the-pit-wall workstream is claimed.** TWG AI is Cadillac's primary and exclusive AI
  partner; the value section is an honest MODE B with named mechanics, and the second risk row is the
  category definition.
- **Brand safety is the first risk row**, not a footnote: a weapons maker on an F1 car will be tested by
  a European fan base and by team and promoter policies in a way NASCAR did not test. The Boeing-at-Alpine
  precedent and Cadillac's American identity are the counters; activation rules on product imagery must
  be agreed up front.
- **Team choice.** Alpine (Boeing) and Williams (Zoox) are ruled out on category; Aston Martin on the
  Aramco title; Haas is open but lacks the GM Defense path; Red Bull, Racing Bulls and the European
  heritage teams have no US identity. Cadillac was chosen on the sponsor table and the GM relationship.
- **Grid Fit panel vs. this brief.** The rendered GRID FIT panel is the pipeline's automatic category read
  (`seeds/sponsor_categories.json`), which has no defence category; trust the ruled-out list on the app
  page over the panel.
- **Deal size ($8–12M a year) is an ESTIMATE**, labelled as such.
- **Score reset from 86 to 79.** Capacity and timing are at the ceiling; brand fit and ops fit are held
  back by defence sensitivities and by the absence of a real operational workstream.

## Ledger as built (N° 220, 23 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Jeff Miller, Chief Marketing Officer at Anduril Industries |
| decision_maker | person_role | yes | verified | Jeff Miller, Chief Marketing Officer, Anduril Industries at Anduril Industries |
| key_facts | funding | yes | verified | $5B Series H at a $61B valuation, announced 13 May 2026, led by Thrive Capital and Andreessen Horowitz; total raised more than $11B over eight rounds (company a |
| deck | funding | yes | verified | Anduril, the Costa Mesa defence-technology company that already sponsors NASCAR and Hendrick Motorsports, announced a $5B Series H at a $61B valuation on 13 May |
| key_facts | funding | yes | verified | Thrive Capital and Andreessen Horowitz (returning leads); the prior round was $2.5B at a $30.5B valuation in June 2025 |
| the_case_p1 | funding | yes | verified | On 13 May 2026 Anduril announced a $5B Series H led by Thrive Capital and Andreessen Horowitz at a $61B valuation, double the $30.5B set in June 2025, taking to |
| key_facts | date | yes | verified | $5B Series H at a $61B valuation, doubling the $30.5B set in June 2025, announced 13 May 2026 |
| the_case_p1 | funding | yes | verified | The demand behind it is public: the US Army awarded a ten-year enterprise contract with a $20B ceiling on 13 March 2026, and Arsenal-1, a $1B factory in Columbu |
| key_facts | sponsorship | yes | verified | No defence-technology partner on any F1 team; Boeing is a BWT Alpine team partner (aerospace and defence prime); Zoox sits at Williams (autonomous vehicles); An |
| bottom_line | funding | yes | verified | A $5B round at $61B, a $20B Army contract ceiling, a factory starting in July and a NASCAR programme already running put Anduril at peak brand-investment author |
| key_facts | other | yes | verified | GM Defense and Anduril signed a teaming agreement in October 2023 on autonomy, battery electrification and propulsion; Cadillac F1 Team is General Motors' works |
| extended | funding | no | verified | On 13 May 2026 Anduril announced a $5B Series H led by Thrive Capital and Andreessen Horowitz at a $61B valuation, double the $30.5B set by the $2.5B round of J |
| key_facts | other | yes | verified | HQ Costa Mesa, California; Arsenal-1, a $1B hyperscale factory in Columbus, Ohio, targeting production from July 2026; US Army enterprise contract with a $20B c |
| extended | funding | no | verified | total funding is now more than $11B over eight rounds. |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | The US Army awarded Anduril a ten-year enterprise contract with a $20B ceiling on 13 March 2026, consolidating more than 120 procurement actions into one framew |
| extended | funding | no | verified | Arsenal-1, the $1B hyperscale factory in Columbus, Ohio, targets production from July 2026. |
| extended | funding | no | verified | For a brand that spends on two Cup races a season with Hendrick, the step up to a three-year F1 seat is proportionate to a $5B raise. |
| extended | funding | no | verified | Anduril's guest list is Pentagon, Congressional, allied-government and prime-contractor audiences, plus the venture and public-market investors who priced the $ |
| why_now_callout | event | yes | verified | The United States GP |
| why_now_callout | event | yes | verified | Las Vegas GP |
| extended | event | no | verified | The Miami GP |
| extended | event | no | verified | United States GP |
