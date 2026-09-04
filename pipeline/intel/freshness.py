"""Freshness: reject stale triggers by date arithmetic, never by asking the model (§3.3, §6.2).

The scanner's ``signal_date`` is the trigger date. It arrives as an ISO day most of the
time, but real outputs have included month-only strings ("January 2026"). A month-only
date is resolved to the LAST day of that month — the most generous reading — so a
candidate is only called stale when it is stale under every reading of the date.
"""

from __future__ import annotations

import calendar
import datetime as dt
import re
from dataclasses import dataclass

_MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
_MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
_MONTHS["sept"] = 9

_ISO_DAY = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_ISO_MONTH = re.compile(r"^(\d{4})-(\d{2})$")
_DAY_MON_YEAR = re.compile(r"^(\d{1,2})\s+([A-Za-z]+)\.?\s+(\d{4})$")
_MON_DAY_YEAR = re.compile(r"^([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})$")
_MON_YEAR = re.compile(r"^([A-Za-z]+)\.?\s+(\d{4})$")


@dataclass(frozen=True)
class ParsedDate:
    date: dt.date | None
    precision: str | None  # "day" | "month" | None


def parse_trigger_date(value: str | dt.date | None) -> ParsedDate:
    if value is None:
        return ParsedDate(None, None)
    if isinstance(value, dt.datetime):
        return ParsedDate(value.date(), "day")
    if isinstance(value, dt.date):
        return ParsedDate(value, "day")
    s = str(value).strip()
    if not s:
        return ParsedDate(None, None)
    if m := _ISO_DAY.match(s):
        try:
            return ParsedDate(dt.date(int(m[1]), int(m[2]), int(m[3])), "day")
        except ValueError:
            return ParsedDate(None, None)
    if m := _ISO_MONTH.match(s):
        return _month(int(m[1]), int(m[2]))
    if m := _DAY_MON_YEAR.match(s):
        mon = _MONTHS.get(m[2].lower())
        if mon:
            try:
                return ParsedDate(dt.date(int(m[3]), mon, int(m[1])), "day")
            except ValueError:
                return ParsedDate(None, None)
    if m := _MON_DAY_YEAR.match(s):
        mon = _MONTHS.get(m[1].lower())
        if mon:
            try:
                return ParsedDate(dt.date(int(m[3]), mon, int(m[2])), "day")
            except ValueError:
                return ParsedDate(None, None)
    if m := _MON_YEAR.match(s):
        mon = _MONTHS.get(m[1].lower())
        if mon:
            return _month(int(m[2]), mon)
    return ParsedDate(None, None)


def _month(year: int, month: int) -> ParsedDate:
    if not 1 <= month <= 12:
        return ParsedDate(None, None)
    last = calendar.monthrange(year, month)[1]
    return ParsedDate(dt.date(year, month, last), "month")


@dataclass(frozen=True)
class FreshnessDecision:
    fresh: bool
    reason: str
    trigger_date: dt.date | None
    age_days: int | None


def check_freshness(
    trigger_value: str | dt.date | None, run_date: dt.date, window_days: int
) -> FreshnessDecision:
    """Deterministic: fresh iff 0 <= (run_date - trigger_date).days <= window_days.

    No parseable date → not fresh (we cannot prove it is inside the window).
    A trigger dated in the future is kept: it is an announced deadline, not stale news.
    """
    parsed = parse_trigger_date(trigger_value)
    if parsed.date is None:
        return FreshnessDecision(False, "no parseable trigger date", None, None)
    age = (run_date - parsed.date).days
    if age > window_days:
        return FreshnessDecision(
            False,
            f"trigger {parsed.date.isoformat()} ({parsed.precision}) is {age} days old; "
            f"window is {window_days}",
            parsed.date,
            age,
        )
    return FreshnessDecision(True, "within window", parsed.date, age)
