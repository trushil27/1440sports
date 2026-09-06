# Quantinuum → Aston Martin Aramco F1 Team — verification log (N° 201, 7 Jun 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) with Claude acting as
scanner, verifier and writer through the pipeline's injectable stages; the calendar table, sponsor
table, 13-rule audit and the 2-page render ran as code. The case sits on the row's date, 7 Jun 2026,
in rebuild mode; `quantinuum.run.json` is the case record `python -m intel.backfill --cases` imports.

**Sandbox limitation, stated plainly:** direct fetches of quantinuum.com, ir.quantinuum.com, sec.gov,
cnbc.com and wikipedia.org were blocked by the egress proxy. Each claim below was checked against the
search summary of the primary page named as the evidence URL. Treat every VERIFIED line as REPORTED
until a person opens the link. Confidence is MEDIUM and the footer reads VERIFY BEFORE CIRCULATION.

## The trigger

Quantinuum's own pricing release: an upsized IPO of 28,000,000 Class A shares at $60.00, Nasdaq
Global Market, ticker QNT, trading from 4 Jun 2026; $1.68B raised (Reuters/CNBC, Bloomberg, The
Quantum Insider). The row date is 7 Jun; the trigger is three days earlier, inside the 90-day
window. The valuation (~$15B) is REPORTED and varies by outlet ($14.6B-$15.6B); the brief says
"roughly $15B" and labels it reported.

## Ledger (claims verified against search summaries of the primary pages)

| Claim | Status | Evidence |
|---|---|---|
| Rajeeb Hazra, President & CEO; ex-Intel (25 yrs), ex-Micron | VERIFIED | quantinuum.com CEO release; About page |
| IPO: 28M shares at $60, above $53-55; $1.68B; QNT; 4 Jun 2026; JPM/MS leads; closed flat | VERIFIED (company + CNBC) | quantinuum.com pricing release; CNBC 4 Jun |
| Valuation ~$15B | REPORTED | The Quantum Insider, IBTimes, Seeking Alpha (range) |
| $600M at $10B pre-money, Sep 2025; Kapur chairs the board | VERIFIED | quantinuum.com / Honeywell release, 4 Sep 2025 |
| 2025 revenue $30.9M, bookings $79.3M, net loss $192.6M; Honeywell ~48.1% voting power | REPORTED (S-1 via coverage) | The Quantum Insider 26 May; Quantum Zeitgeist; The Next Web |
| Nitesh Sharan CFO from 6 Apr 2026 (ex-SoundHound AI) | VERIFIED | quantinuum.com release |
| HQ Broomfield, Colorado; European HQ Cambridge; offices London, Oxford, Munich, Tokyo; formed 2021 from Honeywell Quantum Solutions + Cambridge Quantum | VERIFIED | quantinuum.com launch release / About |
| Helios, Nov 2025, 98 physical qubits, 99.921% fidelity, 48 logical qubits; Sol 2027, Apollo 2029; InQuanto chemistry | VERIFIED / REPORTED (roadmap) | quantinuum.com Helios release; S-1 coverage |
| Grid occupancy (Aston Martin roster; IBM, Google Cloud, Microsoft, Oracle, Core Scientific/TWG AI, Claude/VAST) | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Austrian GP 28 Jun; British GP 5 Jul 2026; Austin and Las Vegas in the autumn | VERIFIED | calendar table + silverstone.co.uk / RacingNews365 |

## Screen-outs and things not claimed

- **No chief marketing officer is claimed.** A search summary asserted a "President and Chief Marketing Officer" at Quantinuum but no source page confirmed it and the IR leadership page was blocked; the brief says none is confirmed rather than naming one.
- **No motorsport tie found** for Hazra, Sharan or Kapur; `leadership_ties` is empty after checking.
- **No lock-up period, share-count or free-float figure** is used beyond what the pricing release states.
- **Deal size ($3-5M a year) is an ESTIMATE**, labelled as such.
- **The workstream is labelled exploratory.** No claim that quantum beats classical solvers on race problems.
- **The score is 73, not the thin row's 76.** What holds it back: $30.9M revenue against a $192.6M loss (capacity 17 despite the raise), a B2B investor-facing brand (14), no hard deadline (13) and a research-only workstream (ops fit 12).

## Decision path

CEO Raj Hazra (owner) → CFO Nitesh Sharan → chairman Vimal Kapur (Honeywell). Ask on the first call who owns marketing.

## Ledger as built (N° 201, 24 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Rajeeb Hazra, President & Chief Executive Officer at Quantinuum |
| decision_maker | person_role | yes | verified | Rajeeb Hazra, President & CEO, Quantinuum at Quantinuum |
| key_facts | funding | yes | verified | IPO: 28 million Class A shares at $60 (above the $53-55 range), $1.68B raised, Nasdaq QNT, first trade 4 Jun 2026; valuation reported at roughly $15B; $600M rai |
| deck | funding | yes | verified | Quantinuum, the Honeywell-controlled trapped-ion quantum computer maker formed from Honeywell Quantum Solutions and Cambridge Quantum, priced an upsized IPO at  |
| key_facts | funding | yes | verified | Honeywell (about 48% of voting power after the offering) and Cambridge Quantum Holdings as founding shareholders; J.P. Morgan and Morgan Stanley led the IPO boo |
| the_case_p1 | funding | yes | verified | Quantinuum sold 28 million Class A shares at $60, above the $53-55 range, raising $1.68B; |
| key_facts | revenue | yes | verified | 2025 revenue $30.9M, bookings $79.3M, net loss $192.6M (S-1, as reported) |
| the_case_p1 | funding | yes | verified | Reports put the valuation at roughly $15B, up from the $10B pre-money at which Honeywell led a $600M raise in September 2025. |
| key_facts | date | yes | verified | Upsized IPO priced at $60 a share; Nasdaq debut as QNT on 4 Jun 2026, $1.68B raised |
| the_case_p1 | revenue | yes | verified | The S-1 shows the scale of the bet: 2025 revenue of $30.9M, bookings of $79.3M and a net loss of $192.6M, with Honeywell keeping about 48% of the voting power. |
| key_facts | sponsorship | yes | verified | IBM (Ferrari), Google Cloud (McLaren), Microsoft (Mercedes, Alpine) and Oracle (Red Bull) each run quantum programmes at parent level; no quantum-computing comp |
| bottom_line | funding | yes | verified | A $1.68B IPO at roughly $15B, Honeywell's backing and a grid where every quantum rival is locked to another team give Quantinuum a clean lane at Aston Martin, w |
| key_facts | other | yes | verified | Helios, launched Nov 2025 with 98 physical qubits at 99.921% two-qubit gate fidelity, and the InQuanto chemistry platform give a race team research workstreams  |
| bottom_line | revenue | yes | verified | Revenue of $30.9M against a $192.6M loss is what holds the score back. |
| key_facts | other | yes | verified | Headquarters Broomfield, Colorado; European headquarters Cambridge, UK; offices in London, Oxford, Munich and Tokyo |
| extended | funding | no | verified | Quantinuum priced an upsized IPO of 28 million Class A shares at $60, above the $53-55 range, and began trading on Nasdaq as QNT on 4 June 2026, raising $1.68B  |
| trigger | date | yes | verified | IPO |
| extended | funding | no | verified | Reports put the valuation at roughly $15B, up from the $10B pre-money valuation of the $600M raise Honeywell led in September 2025. |
| extended | funding | no | verified | Honeywell keeps about 48% of the voting power and its chairman and CEO, Vimal Kapur, chairs the Quantinuum board: a first sports partnership would be read as a  |
| extended | revenue | no | verified | The S-1 discloses 2025 revenue of $30.9M, bookings of $79.3M and a net loss of $192.6M. |
| why_now_callout | event | yes | verified | The British GP |
| value_content | event | yes | verified | British GP |
| extended | event | no | verified | United States GP |
| extended | event | no | verified | Las Vegas GP |
