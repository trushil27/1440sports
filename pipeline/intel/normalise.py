"""Deterministic normalisers used as database keys.

``company_norm`` is the structural dedup key (build brief §5):
lowercase → strip parenthetical content first → strip corporate suffixes →
strip non-alphanumerics. "Lime" and "Lime (Neutron Holdings)" MUST map to the
same key; that is the production bug this exists to make impossible.

Note: the retired n8n normaliser also stripped the token "ai". The build brief's
suffix list does not include it, so neither does this one ("Factory AI" keeps
its "ai"; a future change here is a dedup-policy change and needs a test).
"""

from __future__ import annotations

import re
import unicodedata

SUFFIXES: tuple[str, ...] = (
    "inc",
    "ltd",
    "llc",
    "plc",
    "corp",
    "holdings",
    "technologies",
    "technology",
    "the",
)

_PARENS = re.compile(r"\([^)]*\)")
_SUFFIX = re.compile(r"\b(?:" + "|".join(SUFFIXES) + r")\b")
_NON_ALNUM = re.compile(r"[^a-z0-9]")
_NON_ALNUM_KEEP_SPACE = re.compile(r"[^a-z0-9 ]")
_WS = re.compile(r"\s+")


def _ascii_lower(text: str) -> str:
    """Lowercase and fold accents (Citroën → citroen, 1Komma5° → 1komma5)."""
    folded = unicodedata.normalize("NFKD", text or "")
    return folded.encode("ascii", "ignore").decode("ascii").lower()


def company_norm(name: str | None) -> str:
    """Normalise a company name into its dedup key.

    >>> company_norm("Lime (Neutron Holdings)") == company_norm("Lime")
    True
    >>> company_norm("The Trade Desk Inc.")
    'tradedesk'
    """
    s = _ascii_lower(name or "")
    s = _PARENS.sub(" ", s)
    s = _SUFFIX.sub(" ", s)
    return _NON_ALNUM.sub("", s)


def trigger_norm(trigger: str | None) -> str:
    """Normalise a trigger reason: lowercase, accent-fold, punctuation → space, collapse."""
    s = _ascii_lower(trigger or "")
    s = _NON_ALNUM_KEEP_SPACE.sub(" ", s)
    return _WS.sub(" ", s).strip()
