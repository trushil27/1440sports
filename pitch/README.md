# Pitch — The Origination Desk (for Ricky Paugh, MD)

The internal proposal that pitches the signals engine to 1440's MD as a funded
**origination desk** — framed in his own CEB / insight-led-selling language.

## The narrative (10 slides)
1. **Cover** — The Origination Desk: insight-led origination for 1440.
2. **The problem** — partner time is the scarce asset; the bottleneck is *finding*, not closing.
3. **What I've built** — the SENSE → SCORE → MATCH → VERIFY pipeline.
4. **The trust layer** — claim-level citations + the hard verification gate (the real moat).
5. **Proof · 01 — F1** — Cohesity → Cadillac F1 Team (82/100), engine-generated, verified.
6. **Proof · 02 — FE** — Glean → Mahindra Racing (72/100), same standard.
7. **The pipeline** — eleven scored, team-matched prospects live now.
8. **The full potential** — signal → meeting-ready → full transaction-ready proposal.
9. **The ask** — a defined role + a small budget + a performance kicker; measured on
   qualified briefs and meetings booked.
10. **First 90 days** — prove → build the next rung → systematise.

## Build it
```bash
python3 pitch/build_deck.py        # -> pitch/1440-origination-desk.pdf (+ .html)
```
Landscape A4, brand-locked to the Intelligence Brief system (navy `#191a48` /
gold `#d1ae7a`, Georgia serif, 1440 masthead). Logos are embedded as base64, so
the PDF is fully portable. Uses the same WeasyPrint toolchain as `engine/`.

## Walk into the room with
- `pitch/1440-origination-desk.pdf` — the deck.
- `briefs/2026-05-29/cohesity.pdf` — the F1 proof brief (the live demo).
- `briefs/2026-05-30/glean.pdf` — the FE proof brief.

Both briefs were generated, fact-verified and 2-page-locked by the engine itself —
they *are* the demo, not mock-ups.
