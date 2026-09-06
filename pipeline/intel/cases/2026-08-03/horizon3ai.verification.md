# Horizon3.ai → Cadillac F1 Team — verification log (N° 154, issued for 3 Aug 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from the batch-6 row
dated 3 Aug 2026, with Claude acting as scanner, verifier and writer through the pipeline's
injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as
code. The desk row's team was null; Cadillac is this case's own choice from the sponsor table.

**Sandbox limitation, stated plainly:** horizon3.ai, businesswire.com, techcrunch.com,
securityweek.com, mclaren.com and forbes.com were blocked by the egress proxy. Every claim was
checked against the search summary of the page named as the evidence URL. Treat each VERIFIED
line as REPORTED until a person opens the link. Confidence is MEDIUM; the footer reads VERIFY
BEFORE CIRCULATION.

## The thin row, corrected

- The row's figures (\$250M Series E, \$2B valuation, ~\$100M ARR, 120% growth, 7,200+ customers,
  four Fortune 10) all check out against the company release and TechCrunch. "ARR ~\$100M" is
  TechCrunch's figure, not the company's, and is labelled *reported*; the company states 120%
  ARR growth and "more than 7,000 organisations".
- "Opened Amsterdam European HQ" — the Amsterdam office opened in June 2026 (TechCrunch); the
  "European HQ" label is not used in the copy.
- **Decision-maker changed** from the row's Snehal Antani (CEO) to **Andres Botero, CMO**,
  appointed 7 Jan 2026: the real sponsorship owner. Antani is the C-level sponsor in the path.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Andres Botero, CMO, appointed 7 Jan 2026; ex-CMO Rubrik (from June 2023; IPO April 2024) | VERIFIED | horizon3.ai press release (search summary); Rubrik release |
| \$250M Series E at >\$2B, 3 Aug 2026, co-led by NightDragon and NEA, oversubscribed | VERIFIED | horizon3.ai / Business Wire release (search summary); TechCrunch; SecurityWeek |
| New and returning investors (Acrew, Blue Cloud, Demeter, EDBI, PSG, SAIC, Sapphire; Craft, Prosperity7, Qualcomm Ventures, Ridge, SignalFire) | VERIFIED | company release via SecurityWeek |
| 120% YoY ARR growth; >7,000 organisations; four Fortune 10 | VERIFIED | company release |
| ARR approaching \$100M; ~7,200–7,300 customers | REPORTED | TechCrunch, 3 Aug 2026 |
| Series D \$100M led by NEA, June 2025, at \$650M | REPORTED (\$650M) / VERIFIED (round) | TechCrunch; Business Wire 10 Jun 2025 |
| Founders met at JSOC; Antani ex-CTO USSOCOM, ex-Splunk CTO; HQ San Francisco | VERIFIED | TechCrunch; Cybersecurity Summit profile |
| Amsterdam (June 2026), Australia, Singapore offices; partner-network investment | VERIFIED | TechCrunch |
| Holly Grey CFO (19 Aug 2025); Matt Hartley CRO; Jill Passalacqua CLO; no president/COO listed | VERIFIED | horizon3.ai release; company listings |
| Rubrik–McLaren multi-year partnership announced 28 Jan 2026 (F1 + IndyCar) | VERIFIED | mclaren.com announcement |
| Cadillac: no cybersecurity partner; TWG AI exclusive AI partner (4 Feb 2026); Core Scientific data centre (10 Mar 2026); IFS technology partner | VERIFIED | sponsor table; Business Wire; Cadillac F1 |
| Cadillac commercial team (Epp, Teixeira, Dinger, Iqbal); 'fewer, bigger, better'; Fishers / Charlotte / Silverstone | VERIFIED | Forbes 17 Nov 2025; Sportcal; team profile |
| Grid occupancy of the cybersecurity lane (CrowdStrike, Bitdefender, 1Password, Keeper, Okta/Cisco/Rubrik, Cato/SEALSQ, NinjaOne/Extreme, SentinelOne departed) | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| F1 threat context (deepfakes, phishing, telemetry theft; FIA loophole June 2025) | REPORTED | CloudSEK; Panda Security |
| United States GP (Austin, late Oct), Mexico City, São Paulo, Las Vegas (Nov) | VERIFIED | calendar table |

## Leadership ties

- **Andres Botero (CMO)** was Rubrik's CMO from June 2023 until his move was announced on
  7 Jan 2026; Rubrik's McLaren partnership was announced on 28 Jan 2026. The overlap is real;
  his personal role in the deal is **not confirmed** by any source, and the brief says so twice.
  Recorded as a *probable* tie, not a confirmed one.
- Snehal Antani, Holly Grey, Matt Hartley: **none found** after checking.

## Screen-outs and things not claimed

- **Total funding** is not summed in the copy.
- **No listing date** is claimed; "plausible listing window" is framed as such.
- **Deal size (\$4–6M a year) is an ESTIMATE**, labelled as such.
- **Aston Martin** is not treated as open: the sponsor table marks SentinelOne departed within the
  last 12 months, but no end to the partnership was found live, so the lane is treated as occupied.
- Zenity (N° 155 in this batch) is also recommended to Cadillac, in the AI-agent-security lane.
  Both recommendations are judged against real grid occupancy only, as the operating rules require;
  neither is a placement.

## Ledger as built (N° 154, 24 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Andres Botero, Chief Marketing Officer at Horizon3.ai |
| decision_maker | person_role | yes | verified | Andres Botero, Chief Marketing Officer, Horizon3.ai at Horizon3.ai |
| key_facts | funding | yes | verified | $250M Series E at a valuation above $2B, announced 3 Aug 2026, co-led by NightDragon and NEA; triples the $650M Series D valuation of June 2025 (reported) |
| deck | funding | yes | verified | Horizon3, the San Francisco security company whose NodeZero platform attacks customers' networks the way an adversary would, announced a $250M Series E at a val |
| key_facts | funding | yes | verified | NightDragon and NEA (co-leads); new: Acrew Capital, Blue Cloud Ventures, Demeter Group, EDBI, PSG, SAIC, Sapphire Ventures; returning: Craft Ventures, Prosperit |
| the_case_p1 | revenue | yes | verified | The company reports 120% year-on-year ARR growth and more than 7,000 organisations protected, four of them Fortune 10; |
| key_facts | revenue | yes | verified | ARR approaching $100M with 120% year-on-year ARR growth (company release; TechCrunch, reported) |
| the_case_p1 | revenue | yes | verified | TechCrunch puts ARR near $100M (reported). |
| key_facts | date | yes | verified | $250M Series E at a valuation above $2B, announced 3 Aug 2026 |
| the_case_p2 | funding | yes | verified | A $2B category leader with no seat, and a marketer who has watched one taken. |
| key_facts | sponsorship | yes | verified | CrowdStrike at Mercedes, Bitdefender at Ferrari, Keeper at Williams, Okta and Rubrik at McLaren, Cato Networks at Alpine, and Red Bull's 1Password; Cadillac car |
| bottom_line | revenue | yes | verified | $250M at more than $2B, 120% ARR growth, a CMO who has seen an F1 deal built and an open cybersecurity lane at the American debutant put Horizon3 at peak author |
| key_facts | other | yes | verified | CMO Andres Botero joined on 7 Jan 2026 from Rubrik, whose multi-year McLaren partnership was announced on 28 Jan 2026; international expansion with offices in A |
| extended | funding | no | verified | Horizon3 announced a $250M Series E at a valuation above $2B on 3 August 2026, co-led by NightDragon and NEA, with seven new investors including Sapphire Ventur |
| key_facts | other | yes | verified | Headquartered in San Francisco; founders from Joint Special Operations Command; SAIC among new investors |
| extended | funding | no | verified | The June 2025 Series D, $100M led by NEA, valued the company at $650M (reported). |
| trigger | date | yes | verified | funding round |
| extended | revenue | no | verified | Fourteen months later the price is above $2B, on 120% year-on-year ARR growth and more than 7,000 organisations protected, four of them Fortune 10. |
| extended | revenue | no | verified | Cadillac's hospitality reaches CISOs, CIOs and federal buyers at Austin and Las Vegas, the audience a $100M-ARR security company selling to Fortune 10 accounts  |
| extended | funding | no | verified | Open but not chosen: neither offers the American greenfield estate and premium positioning that match a $2B company. |
| why_now_callout | event | yes | verified | The United States GP |
| extended | event | no | verified | Las Vegas GP |
| extended | event | no | verified | Miami GP |
| extended | event | no | verified | United States GP |
