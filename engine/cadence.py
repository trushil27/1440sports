"""Weekly cadence for the 1440 daily brief.

The MD asked for a rhythm rather than an undifferentiated daily pick:
  - 3 days/week on Formula E (FE) signals
  - 3 days/week on Formula 1 (F1) signals
  - 1 day/week a DECISION day: review the week's contenders across BOTH series
    and surface the single company we SHOULD proceed with.

Default rota (Mon=0 ... Sun=6), Europe/London. Override per-run with
`--series` / `--decision` on run_daily, or change PLAN here.
"""
from __future__ import annotations

import datetime as _dt
from typing import Dict

FE, F1, DECISION = "FE", "F1", "DECISION"

# weekday index -> plan
PLAN: Dict[int, str] = {
    0: FE,        # Monday
    1: FE,        # Tuesday
    2: FE,        # Wednesday
    3: F1,        # Thursday
    4: F1,        # Friday
    5: F1,        # Saturday
    6: DECISION,  # Sunday
}

LABEL = {FE: "Formula E", F1: "Formula 1", DECISION: "Decision day"}


def plan_for(date: _dt.date) -> str:
    """Return FE, F1, or DECISION for the given date."""
    return PLAN[date.weekday()]


def week_bounds(date: _dt.date):
    """Monday..Sunday window containing `date` (for the decision-day review)."""
    monday = date - _dt.timedelta(days=date.weekday())
    return monday, monday + _dt.timedelta(days=6)
