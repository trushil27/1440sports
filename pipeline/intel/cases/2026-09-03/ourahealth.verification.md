# Oura Health → Andretti Formula E — verification log (N° 233, 3 Sep 2026)

An n8n-engine row (24 Aug 2026, score 86, "HOT TOP TIER", person Tom Hale) rebuilt as a full case at
no model-API cost. Nothing n8n recorded was carried over: the score, the tier, the person and the
trigger were all re-derived from live search. n8n also surfaced Oura on 21 May 2026 at 84 — that
was the *confidential* draft registration statement (CNBC, 21 May 2026), which is 105 days before
today and outside the 90-day window. The public S-1 of 3 September is the live trigger, so the
signal sits on 3 Sep 2026.

**Sandbox limitation, stated plainly:** direct fetches of sec.gov, mobihealthnews.com,
the5krunner.com, ouraring.com, ussoccer.com, usta.com, la28.org, cnbc.com and techcrunch.com were
blocked by the egress proxy. Every claim below was checked against the search summary of the
primary page named as the evidence URL. Treat each VERIFIED line as REPORTED until a person opens
the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## What n8n got wrong, and what replaced it

| n8n recorded | Checked | Used |
|---|---|---|
| Score 86, HOT TOP TIER | Not supportable | 78, HOT — see "what holds it back" |
| Person: Tom Hale, CEO | Correct but not the sponsorship owner | Doug Sweeny, CMO, who owns the Team USA / U.S. Soccer / USTA portfolio; Hale is the path |
| Date 24 Aug 2026 | That is the TechCrunch *reported* IPO-valuation story | 3 Sep 2026, the public S-1 filing |
| "2026 capital trigger" unspecified | — | Public Form S-1, SEC, 3 Sep 2026, Nasdaq: OURA |

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Public Form S-1 filed 3 Sep 2026; Nasdaq, ticker OURA; Goldman Sachs, Morgan Stanley, JPMorgan, Allen & Company, Jefferies leading | VERIFIED | SEC EDGAR accession 0001193125-26-381855; Bloomberg 3 Sep 2026 |
| Confidential draft registration statement 21 May 2026 | REPORTED | CNBC, 21 May 2026 |
| $1.21B revenue, nine months to 30 Jun 2026, +74% from $697.6M | VERIFIED (from the filing, via press summaries) | Yahoo Finance / Bloomberg / the5krunner S-1 coverage |
| $1.4B trailing-twelve-month revenue, $59M net profit | VERIFIED (same) | as above |
| 5.0m paid members vs 2.5m; 3.6m rings sold over twelve months | VERIFIED (same) | as above |
| $924.3M nine-month loss attributable to common stockholders, driven by a $985.0M deemed dividend on preferred | VERIFIED (same) | as above — stated in the app page so the loss headline is not read as trading performance |
| $900M+ Series E at $11B led by Fidelity, with ICONIQ, Whale Rock, Atreides (Oct 2025); Series D at $5B (Dec 2024) | VERIFIED | CNBC, 14 Oct 2025 |
| Listing could value Oura above $16B | REPORTED — labelled "reported" in the copy | TechCrunch, 24 Aug 2026 |
| Official Wearable of Team USA and the LA28 Games, 6 Feb 2026 | VERIFIED | la28.org newsroom; Business Wire 20260206641709 |
| Official Wearable of U.S. Soccer, 27 national teams, 22 Apr 2026 | VERIFIED | ussoccer.com; Business Wire 20260422929732 |
| Five-year USTA / US Open partnership, Aug 2026 | VERIFIED | usta.com announcement |
| Team Finland partnership to the 2030 Winter Olympics | REPORTED | press summaries; not used in the 2-page brief |
| HQ San Francisco, founded in Oulu, offices in Finland, 900+ employees | VERIFIED | MobiHealthNews IPO coverage |
| Doug Sweeny, CMO (successor to Karina Kogan); Tom Hale CEO since 1 Mar 2022, ex-president of Momentive (public 2018); Sean Brecker CFO; Michael A. Chapp COO since Apr 2019; no president listed | VERIFIED | Oura blog, Adweek, Modern Retail, The Org |
| WHOOP joined Scuderia Ferrari; Eight Sleep joined Aston Martin Aramco; Optimum Nutrition at McLaren; no wearable or health-technology partner on any 2026 FE roster; Andretti roster = TWG AI, Quest Global, Crowe UK, Reflo, TWG Motorsports, Nissan powertrain from S13; Chase at Jaguar; TDK at Porsche | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Season 13: 21 races, 13 cities; Jeddah opener 18 Dec 2026; Austin E-Prix 6 Feb 2027; Miami E-Prix 20 Feb 2027 | VERIFIED | calendar table (`seeds/calendar_fe.json`) |
| Aston Martin Red Bull Racing named Oura its first Official Health Technology Partner in Nov 2020, rings issued to drivers and pit crew | VERIFIED | ouraring.com/blog/redbull |

## The screen-out that was considered and rejected

**"Already an F1/FE partner"** was the live question. Oura ran an Official Health Technology
partnership with Aston Martin Red Bull Racing from November 2020. It is **not** on Red Bull
Racing's 2026 roster in the sponsor table, no renewal announcement was found, and the 2026
portfolio analyses of the team do not list it. Grid occupancy is judged only against the sponsor
table (CLAUDE.md), so Oura is not a current F1 or FE partner and the case is buildable. The lapse
is not buried: it is the second risk row on page 2, a ruled-out reason for Red Bull, and its own
paragraph on the app page.

## Honest score — what holds it back (78, not the 86 n8n recorded)

- **Brand fit 14/20.** Oura is a consumer wellness brand; motorsport is not where its buyer sits,
  and Formula E's audience is smaller than the Olympic and national-team properties it already owns.
- **Urgency 12/20.** There is no hard deadline. The listing is the moment, not a cliff, and a
  company in a live offering can defer a sponsorship decision by two quarters at no cost.
- **Ops fit 15/20.** The workstream is real but it is a people programme, not a car programme; it
  will never be worth Formula 1 money and it is easy for a team to accept in kind.
- **On-camera 3/4.** A ring is a small logo. The value is the designation and the content, not the
  livery.

## Leadership ties

`leadership_ties`: **none found**. Tom Hale (Momentive, HomeAway, Linden Lab, Macromedia, Adobe),
Doug Sweeny (Levi's, Nest, One Medical), Sean Brecker and Michael Chapp show no F1 or Formula E
role in any listing checked. The company-level tie is the 2020 Red Bull Racing deal, which was
signed under a previous chief executive.

## Not claimed

- **No price range or offer size**: the S-1 does not set one, so the brief does not imply one.
- **Deal size ($2-4M a year) is an ESTIMATE** and is labelled as such.
- **No Formula E audience figures** are used: none were verified in this session.
- **TAG Heuer sits at championship level in Formula E** and at Oracle Red Bull Racing in Formula 1.
  It is a timepiece brand, not a health wearable, so it is not treated as a category clash — but it
  is named in the Red Bull rule-out so the reader can judge for themselves.

## Ledger as built (N° 233, 25 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Doug Sweeny, Chief Marketing Officer at Oura Health |
| decision_maker | person_role | yes | verified | Doug Sweeny, Chief Marketing Officer, Oura Health at Oura Health |
| key_facts | funding | yes | verified | $900M Series E led by Fidelity at an $11B valuation (Oct 2025), double the $5B Series D mark of Dec 2024; a listing above $16B is reported, not confirmed |
| deck | revenue | yes | verified | Oura filed a public Form S-1 with the SEC on 3 September for a Nasdaq listing under the ticker OURA, disclosing $1.4B of trailing-twelve-month revenue at $59M o |
| key_facts | funding | yes | verified | Fidelity Management & Research (lead), ICONIQ, Whale Rock and Atreides in the Series E; the offering is led by Goldman Sachs, Morgan Stanley, JPMorgan, Allen &  |
| the_case_p1 | revenue | yes | verified | The filing shows $1.21B of revenue for the nine months to 30 June 2026, up 74% from $697.6M, five million paid members against 2.5 million a year earlier, and $ |
| key_facts | revenue | yes | verified | $1.21B for the nine months to 30 June 2026, up 74% from $697.6M; $1.4B of trailing-twelve-month revenue at $59M net profit |
| the_case_p1 | funding | yes | verified | TechCrunch reported on 24 August that the listing could value the company above $16B, against $11B at last October's Series E. |
| key_facts | date | yes | verified | Public Form S-1 filed with the SEC on 3 September 2026 for a Nasdaq listing under the ticker OURA |
| bottom_line | revenue | yes | verified | A public S-1 on 3 September, $1.4B of trailing revenue and a reported listing above $16B put Oura at the point where a newly listed consumer brand writes its ne |
| key_facts | sponsorship | yes | verified | WHOOP has joined Scuderia Ferrari's roster and Eight Sleep has joined Aston Martin Aramco's; no wearable or health-technology partner appears on any 2026 Formul |
| extended | revenue | no | verified | Revenue of $1.21B for the nine months to 30 June 2026, up 74% from $697.6M a year earlier. |
| key_facts | other | yes | verified | Official Wearable of Team USA and the LA28 Games (6 Feb 2026), of U.S. Soccer and its 27 national teams (22 Apr 2026) and, on a five-year USTA agreement, of the |
| extended | revenue | no | verified | Trailing-twelve-month revenue of $1.4B at $59M of net profit. |
| key_facts | other | yes | verified | Headquarters in San Francisco with offices in Finland, more than 900 employees, and a Nasdaq listing filed |
| extended | funding | no | verified | The nine-month loss attributable to common stockholders of $924.3M is an accounting artefact of a $985.0M deemed dividend to preferred holders, not trading perf |
| trigger | date | yes | verified | IPO filing |
| extended | funding | no | verified | The Series E in October 2025 raised more than $900M at an $11B valuation, led by Fidelity with ICONIQ, Whale Rock and Atreides - double the $5B set at the Serie |
| extended | funding | no | verified | TechCrunch reported on 24 August that the listing could value Oura above $16B. |
| why_now_callout | event | yes | verified | Jeddah E-Prix |
| why_now_callout | event | yes | verified | Austin E-Prix and the Miami E-Prix land in February 2027 |
| opening_angle_quote | event | yes | verified | Austin E-Prix |
| opening_angle_quote | event | yes | verified | Miami E-Prix |
| extended | event | no | verified | Jeddah E-Prix on 18 December 2026 |
| extended | event | no | verified | Austin E-Prix on 6 February 2027 |
