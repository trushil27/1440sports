"""The stage of the capital event behind a signal — and whether it is the kind the desk
wants to be FIRST to.

Operator, 8 Sep 2026: "instead of being 50th agency, we can be … very early to approach the
tech company who got fundings recently from Series C, D, E or spin out." Growth-stage rounds
and spin-outs are the moment a company gets both the budget and the brand-building motive
at once, and the window in which nobody else has called yet is short. So the desk names the
stage on every signal, asks its scanner for those first, and — at equal score — ranks the
newest growth-stage trigger ahead of the rest.

This is a sourcing priority and a tie-break. It does not change the five-dimension score or
the gates, which are the MD's (build brief §0.5).
"""

from __future__ import annotations

import re

_SERIES = re.compile(r"\bseries\s+([a-h])\b", re.I)
_SPIN = re.compile(r"\b(spin[- ]?(?:off|out)|carve[- ]?out|demerger|separation)\b", re.I)
_IPO = re.compile(r"\b(ipo|initial public offering|listing|listed|s-1|f-1|direct listing)\b", re.I)
_PRE_IPO = re.compile(r"\bpre[- ]ipo\b", re.I)
_MEGA = re.compile(r"\b(mega[- ]?round|growth round|late[- ]stage)\b", re.I)

#: Stages the desk wants to be first to. Series C and later, and a company being born big.
GROWTH_STAGES = frozenset(
    {
        "Series C",
        "Series D",
        "Series E",
        "Series F",
        "Series G",
        "Series H",
        "Spin-out",
        "Pre-IPO",
        "IPO",
    }
)


def round_stage(text: str | None) -> str | None:
    """'Series D', 'Spin-out', 'IPO', 'Pre-IPO', 'Growth round', or None if the text does
    not say. Never inferred from the amount: a $200m round with no letter stays unnamed."""
    t = text or ""
    if _SPIN.search(t):
        return "Spin-out"
    if _PRE_IPO.search(t):
        return "Pre-IPO"
    m = _SERIES.search(t)
    if m:
        return f"Series {m.group(1).upper()}"
    if _IPO.search(t):
        return "IPO"
    if _MEGA.search(t):
        return "Growth round"
    return None


def is_growth_stage(stage: str | None) -> bool:
    return bool(stage) and (stage in GROWTH_STAGES or stage == "Growth round")
