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

# --- Catalyst signal: a "born-big" overnight $1B+ unicorn event (methodology #5).
# A spin-off, merger, acquisition, carve-out or take-private that mints a
# billion-dollar entity overnight -> fresh balance sheet, a brand-identity
# reckoning, no existing sponsorships, and budget authority being set NOW. The
# single highest-value class in the mandate, so a FRESH one outranks peers at the
# same score. Detection radar: data/catalysts.json + engine/catalysts.py.
CATALYST_SIGNALS = {
    "spinoff_unicorn", "merger_unicorn", "acquisition_unicorn",
    "carveout_unicorn", "take_private_unicorn", "overnight_unicorn",
    "spinoff",  # back-compat with older tags
}
CATALYST_TYPES = ("spinoff", "merger", "acquisition", "carveout", "take_private")
CATALYST_FRESH_DAYS = 548   # ~18 months: how long the born-big brand-reckoning window stays open


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


def catalyst_status(prospect: Dict[str, Any],
                    today: Optional[_dt.date] = None) -> Dict[str, Any]:
    """Detect a 'born-big' overnight-unicorn catalyst on a prospect.

    Prefers the structured `catalyst` field
    ``{type, counterparty, event_date, status, new_valuation, source}``; falls
    back to a catalyst *signal* tag (e.g. ``spinoff_unicorn``). Returns
    ``{has, fresh, type, label}`` where ``fresh`` means the brand-reckoning
    window is still open: status announced/imminent, or the event is within
    ``CATALYST_FRESH_DAYS`` of today (past OR upcoming).
    """
    today = today or _dt.date.today()
    cat = prospect.get("catalyst")
    signals = set(prospect.get("signals", []))
    sig_hit = bool(signals & CATALYST_SIGNALS)

    if isinstance(cat, dict) and (cat.get("type") or cat.get("event_date")):
        status = str(cat.get("status", "")).lower()
        days = _days_since(cat.get("event_date"), today)
        fresh = (status in {"announced", "imminent"}
                 or (days is not None and abs(days) <= CATALYST_FRESH_DAYS))
        ctype = cat.get("type", "event")
        val = cat.get("new_valuation", "")
        label = f"{ctype}{(' ' + val) if val else ''}".strip()
        return {"has": True, "fresh": bool(fresh), "type": ctype, "label": label}

    if sig_hit:
        # signal-only (no structured event): a catalyst, freshness assumed open
        return {"has": True, "fresh": True, "type": "signal",
                "label": "born-big / overnight unicorn"}
    return {"has": False, "fresh": False, "type": None, "label": None}


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
        cat = catalyst_status(p, today)
        exec_tie = int(bool(p.get("leadership_ties")) or "exec_migration" in signals)
        hot = int(p.get("timing_window") == "HOT")
        sort_key = (
            0 if on_cooldown else 1,
            score,
            int(cat["fresh"]),     # a FRESH born-big catalyst outranks peers at the same score
            exec_tie,              # a senior leader with prior F1/FE or deal-structuring history
            -(est if est is not None else 999),
            hot,
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
    cat = catalyst_status(prospect)
    p["has_catalyst"] = cat["has"]
    p["catalyst_fresh"] = cat["fresh"]
    p["catalyst_label"] = cat["label"]
    p["has_leadership_tie"] = bool(prospect.get("leadership_ties")) or \
        "exec_migration" in set(prospect.get("signals", []))
    return p
