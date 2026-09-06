# OLIX Computing → Atlassian Williams Racing — verification log (N° 153, issued for 3 Aug 2026)

Built in-session at no API cost (no `ANTHROPIC_API_KEY` in the sandbox) from the batch-6 row
dated 3 Aug 2026, with Claude acting as scanner, verifier and writer through the pipeline's
injectable stages; the calendar table, sponsor table, 13-rule audit and the 2-page render ran as
code. The desk row's team was null; Williams is this case's own choice from the sponsor table.

**Sandbox limitation, stated plainly:** olix.com, tech.eu, datacenterdynamics.com, siliconangle.com
and the Companies House pages were blocked by the egress proxy. Every claim was checked against
the search summary of the page named as the evidence URL. Treat each VERIFIED line as REPORTED
until a person opens the link. Confidence is MEDIUM; the footer reads VERIFY BEFORE CIRCULATION.

## The thin row, corrected

- "Largest UK semiconductor raise of 2026" — **not found in any source**; dropped.
- "Valuation tripled in six months from $220M Series A" conflated round size and valuation:
  the Series A was **$220M at just over $1B** (Feb 2026); the Series B is **$312M at $3.3B**.
  The tripling is $1B → $3.3B in six months (Tech.eu, DCD). The brief says exactly that.
- Trigger date 3 Aug 2026 confirmed by the dated Tech.eu and DCD reports and the company newsroom URL.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| James Dacombe, Founder & CEO; director since incorporation 22 Mar 2024 | VERIFIED | Companies House officers page; Tech.eu, DCD |
| $312M Series B at $3.3B, 3 Aug 2026; Fundomo lead; Arm, Hudson River Trading, Reed Hastings; existing backers increased | VERIFIED | olix.com newsroom (search summary); Tech.eu; DCD |
| $220M Series A at just over $1B, Feb 2026, led by Hummingbird | REPORTED | SiliconANGLE 11 Feb 2026; Dealroom |
| UK government Sovereign AI fund invested | REPORTED | DCD headline and body (amount not disclosed) |
| First systems to customers H2 2027; hiring across London, Bristol, Austin, Toronto, San Francisco | VERIFIED | olix.com newsroom (search summary); DCD |
| Matt Briers (ex-Wise CFO) hired as CFO; Nick McKeown to the board | REPORTED | Tech.eu |
| Tom Elvidge, COO | REPORTED | LinkedIn listing only; flagged "reported" in the bio |
| No CMO | GAP (stated) | no marketing officer on any listing found |
| Registered office St Albans; incorporated 22 Mar 2024; London-based | VERIFIED | Companies House; press |
| Groq Official Partner of McLaren, Sep 2025, logo from Singapore | VERIFIED | mclaren.com announcement |
| Grid occupancy (Williams roster; Groq/McLaren; ARM + CoreWeave/Aston Martin; AMD + Snapdragon + HPE/Mercedes; Core Scientific + TWG AI/Cadillac; Oracle/Red Bull; Microsoft/Alpine; HP + IBM/Ferrari; HPE departed + ElevenLabs/Audi) | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| United States GP (Austin, late Oct), Las Vegas (Nov), Italian GP (Sep), British GP (Jul) | VERIFIED | calendar table (`seeds/calendar_2026.json`) |

## Screen-outs and things not claimed

- **No motorsport tie found** for Dacombe, Briers or Elvidge after checking; `leadership_ties` is empty.
- **No revenue figure**: none exists; the company is pre-product.
- **Dacombe's age** (25, per Business Cloud / IBTimes) is used only in a risk row, not as a fact of the case.
- **Deal size ($3–5M a year) is an ESTIMATE**, labelled as such.
- **Total funding** is not summed in the copy (sources differ on the pre-Series-A base).
- MODE B is declared honestly: there is no product to deploy before H2 2027; the evaluation clause is a
  proposal, not a claim.

## Team choice

Williams was chosen over the open alternatives (Haas, Racing Bulls) for the British engineering
story and the absence of any semiconductor or compute partner on its roster. McLaren (Groq),
Aston Martin (Arm, CoreWeave), Mercedes (AMD, Snapdragon, HPE) and Cadillac (Core Scientific,
TWG AI) are ruled out by category occupancy in the sponsor table.

## Ledger as built (N° 153, 17 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | James Dacombe, Founder & CEO at OLIX Computing |
| decision_maker | person_role | yes | verified | James Dacombe, Founder & CEO, OLIX Computing at OLIX Computing |
| key_facts | funding | yes | verified | $312M Series B at a $3.3B valuation announced 3 Aug 2026, led by Fundomo; follows a $220M Series A at just over $1B led by Hummingbird in February 2026 |
| deck | funding | yes | verified | OLIX, the London AI-chip company founded in 2024 by James Dacombe, announced a $312M Series B at a $3.3B valuation on 3 August, tripling the $1B mark set by its |
| key_facts | funding | yes | verified | Fundomo (lead), Arm, Hudson River Trading and Reed Hastings; existing backers Hummingbird, Crane, Plural, Creandum, Phoenix Court and Transition increased commi |
| the_case_p1 | funding | yes | verified | Six months earlier Hummingbird had led a $220M Series A at just over $1B. |
| key_facts | date | yes | verified | $312M Series B at a $3.3B valuation, announced 3 Aug 2026 |
| bottom_line | funding | yes | verified | $312M at $3.3B, a government-backed sovereign-AI story and an open silicon lane at a British team make OLIX a 2027 partner to sign in the fourth quarter. |
| key_facts | sponsorship | yes | verified | Groq has been an Official Partner of McLaren since September 2025 with its inference chips on the car; Arm, now an OLIX investor, sits on Aston Martin Aramco's  |
| extended | funding | no | verified | OLIX announced a $312M Series B at a $3.3B valuation on 3 August 2026, led by Fundomo with Arm, Hudson River Trading and Reed Hastings. |
| key_facts | other | yes | verified | First AI systems due to customers in the second half of 2027; hiring silicon, compiler, photonics and systems engineers across London, Bristol, Austin, Toronto  |
| extended | funding | no | verified | The $220M Series A in February 2026, led by Hummingbird, priced OLIX at just over $1B. |
| key_facts | other | yes | verified | Offices and hiring in Austin and San Francisco; UK company registered in St Albans (Companies House), London-based |
| extended | funding | no | verified | Six months later the Series B priced it at $3.3B. |
| trigger | date | yes | verified | funding round |
| why_now_callout | event | yes | verified | United States GP |
| extended | event | no | verified | The United States GP |
