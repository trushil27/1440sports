"""1440 Sports - scoring + hero-selection logic.

Pure standard library. See engine/methodology.md for the model.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, List, Optional

PILLARS = ("timing", "capacity", "brand_fit", "urgency")
ELIGIBLE_SERIES = {"F1", "FE", "FE paddock"}
CROWDING_CAP = 100          # > this many inbound pitches => gated out of hero
SWEET_SPOT = (50, 100)      # client's target band


def opportunity_score(prospect: Dict[str, Any]) -> int:
    """Sum the four /25 pillars into a /100 Opportunity Score."""
    scores = prospect.get("scores", {})
    return int(sum(int(scores.get(p, 0)) for p in PILLARS))


def band(score: int) -> str:
    if score >= 80:
        return "HOT"
    if score >= 65:
        return "WARM"
    if score >= 50:
        return "DEVELOPING"
    return "PARK"


def crowding_label(est: Optional[int]) -> str:
    if est is None:
        return "unknown"
    if est < SWEET_SPOT[0]:
        return f"~{est} (EARLY - ahead of the noise)"
    if est <= SWEET_SPOT[1]:
        return f"~{est} (SWEET SPOT 50-100)"
    return f"~{est} (SATURATED >100 - gated out)"


def is_eligible_for_hero(prospect: Dict[str, Any], min_deal_years: int = 3) -> bool:
    """Apply the hard gates from methodology section 5/4."""
    if prospect.get("status") != "active":
        return False
    if prospect.get("series") not in ELIGIBLE_SERIES:
        return False
    if int(prospect.get("min_deal_years", 0)) < min_deal_years:
        return False
    est = prospect.get("est_inbound_pitches")
    if est is not None and int(est) > CROWDING_CAP:
        return False
    return True


def _days_since(date_str: Optional[str], today: _dt.date) -> Optional[int]:
    if not date_str:
        return None
    try:
        d = _dt.date.fromisoformat(date_str)
    except ValueError:
        return None
    return (today - d).days


def rank(prospects: List[Dict[str, Any]],
         today: Optional[_dt.date] = None,
         cooldown_days: int = 5,
         min_deal_years: int = 3,
         history: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """Return eligible prospects sorted best-first.

    history maps prospect id -> ISO date it was last used as hero, so a recent
    hero is pushed down (not removed) to keep the daily brief fresh.
    """
    today = today or _dt.date.today()
    history = history or {}
    ranked = []
    for p in prospects:
        if not is_eligible_for_hero(p, min_deal_years):
            continue
        score = opportunity_score(p)
        est = p.get("est_inbound_pitches")
        last = _days_since(history.get(p["id"]), today)
        on_cooldown = last is not None and last < cooldown_days
        signals = set(p.get("signals", []))
        priority_signal = int(bool(signals & {"exec_migration", "spinoff_unicorn"}))
        hot = int(p.get("timing_window") == "HOT")
        # Sort key: cooldown last; then score; then lower crowding; then HOT; then priority signal.
        sort_key = (
            0 if on_cooldown else 1,
            score,
            -(est if est is not None else 999),
            hot,
            priority_signal,
        )
        ranked.append((sort_key, score, p))
    ranked.sort(key=lambda t: t[0], reverse=True)
    return [p for _, _, p in ranked]


def select_hero(prospects: List[Dict[str, Any]], **kwargs) -> Optional[Dict[str, Any]]:
    r = rank(prospects, **kwargs)
    return r[0] if r else None


def enrich(prospect: Dict[str, Any]) -> Dict[str, Any]:
    """Attach computed fields used by the template."""
    p = dict(prospect)
    p["opportunity"] = opportunity_score(prospect)
    p["band"] = band(p["opportunity"])
    p["crowding_label"] = crowding_label(prospect.get("est_inbound_pitches"))
    return p
