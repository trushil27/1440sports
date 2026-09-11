"""What kind of moment is this signal? — the trigger taxonomy behind outreach.

A sponsorship conversation opens differently depending on why the company is in the news:
a funding round is "new money, new brand budget"; a spin-off is "a new name that needs a
stage"; a new CEO or CMO is "a new owner of the brand agenda in their first 100 days"; an
executive who arrives from a company that sponsored F1 or Formula E is "shared history".
The operator asked (11 Sep 2026) for an outreach sequence per trigger and for the desk to
SPOT these triggers on every signal, so the type is derived here, deterministically, from
the trigger text the ledger already verified, and shown on every row.

Priority when several apply: an executive move from a sponsor outranks a new-CMO or
new-CEO reading (the person is the opening), which outranks a spin-off, which outranks a
listing, which outranks a funding round.
"""

from __future__ import annotations

import re
from typing import Any

TYPES: dict[str, str] = {
    "exec_move": "Ex-sponsor executive",
    "new_cmo": "New CMO / commercial lead",
    "new_ceo": "New CEO",
    "spin_off": "Spin-off / carve-out",
    "listing": "Listing / IPO",
    "funding_round": "Funding round",
    "expansion": "Expansion",
    "other": "Other",
}

_APPOINT = (
    r"(appoint|appoints|appointed|names|named|hires|hired|joins|joined|promot|new |incoming|"
    r"takes over|steps up|succeed)"
)
_CMO = (
    r"(chief marketing|cmo\b|chief commercial|cco\b|chief revenue|cro\b|head of "
    r"marketing|marketing director|vp marketing|chief brand|chief growth|commercial director)"
)
_CEO = r"(chief executive|\bceo\b|managing director|president and ceo|group ceo)"
_SPIN = (
    r"(spin[- ]?off|spin[- ]?out|carve[- "
    r"]?out|demerger|de-merger|separation|standalone|stand-alone|split[- ]off|reverse morris)"
)
_LIST = (
    r"(\bipo\b|initial public offering|listing|lists on|listed "
    r"on|nasdaq|nyse|euronext|\bspac\b|begins trading|public debut|direct "
    r"listing|s-1\b|f-1\b|10-12b)"
)
_FUND = (
    r"(series [a-h]\b|seed round|growth round|funding "
    r"round|\braise[sd]?\b|\braising\b|\bround\b|valuation|led by|financing|investment "
    r"round|mega-?round)"
)
_EXPAND = (
    r"(opens? (an? )?(new "
    r")?(office|hq|headquarters|factory|plant|gigafactory)|expands? "
    r"(to|into)|launch(es)? in|enters? the (uk|us|european|german|japanese) "
    r"market|london office|european headquarters)"
)
_PRIOR = (
    r"(formerly|previously|ex-|prior(ly)? (at|with)|who "
    r"(led|ran|built|structured)|from (his|her|their) time at|left [A-Z])"
)


def _has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE) is not None


def classify(
    trigger: str | None,
    key_facts: dict[str, Any] | None = None,
    role: str | None = None,
    sponsor_brands: list[str] | None = None,
) -> str:
    """The trigger type for a signal, from its verified trigger text and key facts."""
    kf = key_facts or {}
    text = " ".join(
        str(x)
        for x in (
            trigger or "",
            kf.get("trigger") or "",
            kf.get("strategic_hook") or "",
            kf.get("alumni_match") or "",
        )
        if x
    )
    alumni = str(kf.get("alumni_match") or "").strip()
    lower = text.lower()
    # 1. an executive who arrives from a company that sponsored the grid
    if alumni and alumni.lower() not in ("none", "n/a", "no", "null", "-", "—"):
        return "exec_move"
    if _has(_PRIOR, text) and sponsor_brands:
        for brand in sponsor_brands:
            b = (brand or "").strip().lower()
            if len(b) >= 3 and re.search(r"\b" + re.escape(b) + r"\b", lower):
                return "exec_move"
    # 2. a new marketing / commercial owner, 3. a new chief executive
    if _has(_APPOINT, text) and _has(_CMO, text):
        return "new_cmo"
    if _has(_APPOINT, text) and _has(_CEO, text):
        return "new_ceo"
    # 4. identity events, 5. capital events
    if _has(_SPIN, text):
        return "spin_off"
    if _has(_LIST, text):
        return "listing"
    if _has(_FUND, text):
        return "funding_round"
    if _has(_EXPAND, text):
        return "expansion"
    return "other"


def label(kind: str | None) -> str:
    return TYPES.get(kind or "other", TYPES["other"])


def attach(
    entries: list[dict[str, Any]], sponsor_brands: list[str] | None = None
) -> dict[str, int]:
    """Set ``trigger_type`` + ``trigger_label`` on every app row. Returns a count by type."""
    counts: dict[str, int] = {}
    for e in entries:
        kind = classify(
            e.get("trigger"),
            (e.get("key_facts") if isinstance(e.get("key_facts"), dict) else None),
            e.get("role"),
            sponsor_brands,
        )
        # a Stage chip of "Spin-out" is the same statement as the text
        if kind in ("other", "funding_round") and (e.get("stage") or "") == "Spin-out":
            kind = "spin_off"
        e["trigger_type"] = kind
        e["trigger_label"] = label(kind)
        counts[kind] = counts.get(kind, 0) + 1
    return counts
