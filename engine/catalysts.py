"""Catalyst radar — the 'born-big' overnight-unicorn watchlist.

A spin-off / merger / acquisition / carve-out / take-private that creates a
$1B+ entity overnight is the highest-priority signal class in the mandate
(methodology #5): fresh capital, a brand-identity reckoning, no existing
sponsorships, budget authority being set NOW. These are easy to miss because the
company did not exist in its current form yesterday — so we log every such event
in data/catalysts.json the moment it surfaces, then promote the promising ones
into data/prospects.json as scored prospects.

This module loads that radar, scores freshness (shared with engine/scoring.py),
and prints a desk view:

    python3 engine/catalysts.py            # full radar
    python3 engine/catalysts.py --open     # only events not yet promoted
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scoring  # noqa: E402  (shares CATALYST_FRESH_DAYS + freshness logic)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CATALYSTS = os.path.join(_ROOT, "data", "catalysts.json")


def load_catalysts(path: str = _CATALYSTS) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    data = json.load(open(path, encoding="utf-8"))
    return data.get("events", []) if isinstance(data, dict) else list(data)


def assess(event: Dict[str, Any], today: Optional[_dt.date] = None) -> Dict[str, Any]:
    """Freshness for a radar event, reusing the same rule scoring.py applies to a
    prospect's catalyst (status announced/imminent, or within CATALYST_FRESH_DAYS)."""
    today = today or _dt.date.today()
    status = str(event.get("status", "")).lower()
    days = scoring._days_since(event.get("event_date"), today)
    fresh = (status in {"announced", "imminent"}
             or (days is not None and abs(days) <= scoring.CATALYST_FRESH_DAYS))
    return {
        "fresh": bool(fresh),
        "days": days,
        "promoted": bool(event.get("promoted_to")),
        "excluded": bool(event.get("already_present")),
    }


def radar(today: Optional[_dt.date] = None, open_only: bool = False) -> List[Dict[str, Any]]:
    """Return radar events (freshest first), each annotated with assessment."""
    today = today or _dt.date.today()
    out = []
    for ev in load_catalysts():
        a = assess(ev, today)
        if open_only and (a["promoted"] or a["excluded"]):
            continue
        out.append({**ev, "_assess": a})
    out.sort(key=lambda e: (e["_assess"]["fresh"], not e["_assess"]["promoted"]),
             reverse=True)
    return out


def _print(events: List[Dict[str, Any]]) -> None:
    if not events:
        print("Catalyst radar: no events.")
        return
    print("\n1440 Sports — Catalyst radar (born-big / overnight-unicorn events)")
    print("-" * 72)
    for e in events:
        a = e["_assess"]
        flag = "🔥 FRESH" if a["fresh"] else "·  aged "
        if a["excluded"]:
            where = "EXCLUDED — already_present on a grid (proof example)"
        elif a["promoted"]:
            where = f"→ prospect '{e['promoted_to']}'"
        else:
            where = "ON RADAR (not yet promoted)"
        print(f"{flag}  {e.get('type','?').upper():12} {e.get('name','?')}")
        print(f"          {e.get('new_valuation','?')}  ·  {e.get('series_hint','?')}"
              f"  ·  {e.get('confidence','?')}  ·  {where}")
        if not a["promoted"]:
            print(f"          TRIAGE: {e.get('triage','—')}")
    n_open = sum(1 for e in events
                 if not e["_assess"]["promoted"] and not e["_assess"]["excluded"])
    n_fresh = sum(1 for e in events if e["_assess"]["fresh"])
    print("-" * 72)
    print(f"— {len(events)} event(s): {n_fresh} fresh, {n_open} awaiting promotion —\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="1440 catalyst radar")
    ap.add_argument("--open", action="store_true",
                    help="show only events not yet promoted to a prospect")
    args = ap.parse_args()
    _print(radar(open_only=args.open))
