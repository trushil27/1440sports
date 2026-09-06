# Zenity → Cadillac F1 Team — verification log (N° 155, issued for 3 Aug 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from the batch-6 row
dated 3 Aug 2026, with Claude acting as scanner, verifier and writer through the pipeline's
injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as
code. The desk row's team was null; Cadillac is this case's own choice from the sponsor table.

**Sandbox limitation, stated plainly:** zenity.io, businesswire.com, fortune.com, calcalistech.com,
theorg.com and forbes.com were blocked by the egress proxy. Every claim was checked against the
search summary of the page named as the evidence URL. Treat each VERIFIED line as REPORTED until a
person opens the link. Confidence is MEDIUM; the footer reads VERIFY BEFORE CIRCULATION.

## The thin row, corrected

- Round, lead, investors and the Gartner report all check out. Total funding: the company says
  approximately \$185M, Fortune says \$180M; the brief uses "about \$185M" and the ledger records both.
- "APAC/Europe expansion mandate active" — the release says "expand globally"; the copy says
  "global expansion" and nothing more specific.
- **Valuation was not disclosed** (the CEO declined, per Fortune); the brief says so in the deck,
  the ticker line and the score.
- No CMO or CRO exists on any source found; marketing is led at director level (Andrew Silberman,
  Director of Marketing, per The Org). The decision path therefore runs CEO → CTO → VP Finance.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| Ben Kliger, CEO & Co-founder; Michael Bargury, CTO; founded 2021; Unit 8200; ex-Microsoft | VERIFIED | Calcalist 3 Aug 2026; Crunchbase (Kliger in New York) |
| \$125M Series C led by Norwest, 3 Aug 2026; new and returning investors | VERIFIED | zenity.io / Business Wire release (search summary); Fortune; Calcalist |
| Total funding ≈ \$185M (company) / \$180M (Fortune) | VERIFIED (both figures recorded) | company release; Fortune |
| Valuation not disclosed | VERIFIED | Fortune |
| \$38M Series B, 29 Oct 2024, Third Point + DTCP, M12; total then > \$55M | VERIFIED | zenity.io Series B release |
| Gartner 'company to beat' report, 17 Apr 2026 | VERIFIED | Business Wire 23 Apr 2026 |
| > 230 employees, ~150 in Israel; New York commercial base; Fortune 500 / Global 2000 customers; SoftBank Corp | VERIFIED | Calcalist; company release |
| Keren Herscovici, VP Finance & Corporate Development | VERIFIED | CTech, Jan 2025 |
| Andrew Silberman, Director of Marketing; no CMO/CRO | REPORTED / GAP stated | The Org |
| Cadillac: no cybersecurity partner; TWG AI exclusive AI partner; Core Scientific; IFS; 'fewer, bigger, better'; Fishers / Charlotte / Silverstone | VERIFIED | sponsor table; Business Wire; Forbes; team profile |
| Grid occupancy of the cybersecurity lane; no AI-agent security partner on any team | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| United States GP (Austin), Las Vegas GP | VERIFIED | calendar table |

## Leadership ties

- Ben Kliger, Michael Bargury, Keren Herscovici: **none found** after checking.

## Screen-outs and things not claimed

- **No revenue figure**: none is public.
- **No valuation** is claimed anywhere.
- **Deal size (\$2–4M a year) is an ESTIMATE**, labelled as such.
- **Aston Martin** is not treated as open (SentinelOne: table says departed within 12 months; no end
  found live).
- Horizon3 (N° 154 in this batch) is also recommended to Cadillac, in the autonomous-pentesting lane.
  Both are judged against real grid occupancy only; neither is a placement. Onyx Security (N° 156),
  a direct Zenity rival, was screened out of this batch at 64/100.

## Ledger as built (N° 155, 17 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Ben Kliger, CEO & Co-founder at Zenity |
| decision_maker | person_role | yes | verified | Ben Kliger, CEO & Co-founder, Zenity at Zenity |
| key_facts | funding | yes | verified | $125M Series C led by Norwest, announced 3 Aug 2026; total funding about $185M (company; Fortune reports $180M); valuation not disclosed |
| deck | funding | yes | verified | Zenity, the AI-agent security company founded in Tel Aviv and run commercially from New York, announced a $125M Series C led by Norwest on 3 August, with SoftBa |
| key_facts | funding | yes | verified | Norwest (lead); new: Qumra Capital, SoftBank Vision Fund 2, Hitachi Ventures, LG Technology Ventures; returning: Vertex Ventures, Third Point Ventures, DTCP, In |
| deck | funding | yes | verified | Total funding is about $185M; |
| key_facts | date | yes | verified | $125M Series C led by Norwest, announced 3 Aug 2026 |
| the_case_p1 | funding | yes | verified | The $38M Series B, co-led by Third Point and DTCP with Microsoft's M12, closed in October 2024. |
| key_facts | sponsorship | yes | verified | CrowdStrike at Mercedes, Bitdefender at Ferrari, Keeper at Williams, Okta and Rubrik at McLaren, Cato Networks at Alpine, and Red Bull's 1Password; no team carr |
| bottom_line | funding | yes | verified | A $125M Series C led by Norwest, with SoftBank, Hitachi and LG, Gartner's 'company to beat' verdict and an untouched agent-security lane at the American debutan |
| key_facts | other | yes | verified | Gartner named Zenity 'the company to beat' in AI agent governance in a 17 Apr 2026 report; more than 230 employees, about 150 in Israel; sales, marketing and op |
| extended | funding | no | verified | Zenity announced a $125M Series C led by Norwest on 3 August 2026, with Qumra Capital, SoftBank Vision Fund 2, Hitachi Ventures and LG Technology Ventures joini |
| key_facts | other | yes | verified | Sales, marketing and operations run from New York; CEO based in New York; R&D in Tel Aviv |
| why_now_callout | event | yes | verified | The United States GP |
| trigger | date | yes | verified | funding round |
| extended | event | no | verified | Las Vegas GP |
| extended | event | no | verified | United States GP |
