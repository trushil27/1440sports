"""1440 Sports - scoring + hero-selection logic (Ramp-standard, v2).

Mirrors the Ramp Intelligence Brief (N 025) scorecard:
FIVE pillars, each /20 -> Opportunity /100.
  Timing, Capacity, Brand Fit, Urgency, Ops Fit.

MODE classification (shown on the brief):
  MODE A = the tech genuinely belongs in the car / is used by the championship
           (e.g. AVEVA digital twin, Oracle compute, JFrog software supply chain).
  MODE B = the tech serves the team's back-office / commercial operation
           (e.g. Ramp corporate spend management).

See engine/methodology.md for the full model.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, List, Optional

PILLARS = ("timing", "capacity", "brand_fit", "urgency", "ops_fit")
PILLAR_MAX = 20
ELIGIBLE_SERIES = {"F1", "FE", "FE paddock"}
CROWDING_CAP = 100          # > this many inbound pitches => gated out of hero
SWEET_SPOT = (50, 100)      # client's target band


def opportunity_score(prospect: Dict[str, Any]) -> int:
    """Sum the five /20 pillars into a /100 Opportunity Score."""
    scores = prospect.get("scores", {})
    return int(sum(int(scores.get(p, 0)) for p in PILLARS))


def tier(score: int) -> str:
    """Overall header tag, matching the Ramp 'HOT TOP TIER' convention."""
    if score >= 85:
        return "HOT · TOP TIER"
    if score >= 75:
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
    """Hard gates from methodology sections 4-5.

    Includes the 'already present' exclusion: a company already on an F1/FE grid
    (directly OR via a subsidiary/parent) is not a prospect.
    """
    if prospect.get("status") != "active":
        return False
    if prospect.get("already_present"):
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


def in_series(prospect: Dict[str, Any], series: Optional[str]) -> bool:
    """Series filter. 'F1' matches F1; 'FE' matches FE and FE-paddock; None/'all'
    matches everything."""
    if not series or series == "all":
        return True
    s = str(prospect.get("series", ""))
    if series == "FE":
        return s.startswith("FE")
    if series == "F1":
        return s == "F1"
    return s == series


def rank(prospects: List[Dict[str, Any]],
         today: Optional[_dt.date] = None,
         cooldown_days: int = 5,
         min_deal_years: int = 3,
         history: Optional[Dict[str, str]] = None,
         series: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return eligible prospects sorted best-first.

    history maps prospect id -> ISO date last used as hero, so a recent hero is
    pushed down (not removed) to keep the daily brief fresh. `series` optionally
    restricts to one championship ('F1' or 'FE').
    """
    today = today or _dt.date.today()
    history = history or {}
    ranked = []
    for p in prospects:
        if not is_eligible_for_hero(p, min_deal_years):
            continue
        if not in_series(p, series):
            continue
        score = opportunity_score(p)
        est = p.get("est_inbound_pitches")
        last = _days_since(history.get(p["id"]), today)
        on_cooldown = last is not None and last < cooldown_days
        signals = set(p.get("signals", []))
        priority_signal = int(bool(signals & {"exec_migration", "spinoff_unicorn"}))
        hot = int(p.get("timing_window") == "HOT")
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
    p["tier"] = tier(p["opportunity"])
    p["crowding_label"] = crowding_label(prospect.get("est_inbound_pitches"))
    return p
