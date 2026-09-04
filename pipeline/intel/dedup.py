"""Blocklist + dedup as DATABASE rules (§3.2, §6.3).

Dedup key = (company_norm, trigger_reason_norm). Two real lessons shaped the trigger key:
- The retired n8n dedup was company-only, which produced the "Primer duplicate" and the
  "Lime vs Lime (Neutron Holdings)" bugs (the latter is fixed by ``company_norm``).
- The scanner never words the same trigger the same way twice ("S-1 filed 8 May 2026"
  vs "Filed Nasdaq S-1 — first micromobility IPO attempt"). So the trigger key is a
  deterministic CLASS of the trigger text (funding round, IPO filing, IPO roadshow, ...)
  chosen by keyword-hit counting. Same company + same class within the window →
  ``dedup_suppressed``; same company + different class → passes, tagged RESURFACED.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.models import Blocklist, BlocklistStatus, SurfacedLog
from intel.normalise import trigger_norm

# Priority order breaks ties (first wins). Patterns are matched against the lowercased text.
TRIGGER_CLASSES: list[tuple[str, list[str]]] = [
    (
        "funding_round",
        [
            r"\bseries [a-h]\b(?:[- ]\d)?",
            r"\braise[sd]?\b",
            r"\braising\b",
            r"funding round",
            r"\bround\b",
            r"valuation",
            r"\bled by\b",
            r"\bpre money\b",
            r"\bpost money\b",
        ],
    ),
    (
        # NB: patterns see the NORMALISED text: "S-1" arrives as "s 1", "F-1" as "f 1".
        "ipo_filing",
        [
            r"\bs[ -]?1\b",
            r"\bf 1\b",
            r"\bform 10\b",
            r"ipo filing",
            r"\bfiled\b",
            r"\bfiles? for\b",
            r"\bconfidential",
            r"prospectus",
        ],
    ),
    (
        "ipo_roadshow",
        [
            r"roadshow",
            r"nasdaq debut",
            r"listing",
            r"\bbell\b",
            r"ipo priced",
            r"\blists?\b",
        ],
    ),
    (
        "acquisition",
        [
            r"acqui",
            r"\bmerger\b",
            r"\bbuyout\b",
            r"takeover",
            r"spin-?o(?:ff|ut)",
            r"demerger",
            r"separation",
        ],
    ),
    (
        "leadership_change",
        [
            r"appoint",
            r"\bhire[sd]?\b",
            r"\bnamed\b",
            r"\bjoins? as\b",
            r"\bnew (?:ceo|cmo|cro|cfo|coo|president)\b",
            r"steps? down",
            r"\bdeparts?\b",
            r"\bsucceed",
        ],
    ),
    (
        "expansion",
        [
            r"expan",
            r"launch(?:es|ed|ing)? in\b",
            r"enter(?:s|ed|ing)? (?:the )?\w+ market",
            r"new (?:office|hq|headquarters)",
            r"opens? (?:an? )?(?:office|hq)",
            r"onboarding",
        ],
    ),
    ("product_launch", [r"\blaunch", r"unveil", r"\breleases?\b", r"\bships?\b", r"\bproduct\b"]),
    ("partnership", [r"partner", r"sponsor", r"\bdeal with\b", r"agreement", r"\bcontract\b"]),
    ("regulatory", [r"regulat", r"approval", r"licen[cs]e", r"clearance", r"\bmandate\b"]),
    (
        "results",
        [r"earnings", r"\bresults\b", r"revenue (?:up|grew|rose)", r"\bquarter\b", r"\bfy20\d\d\b"],
    ),
]

_COMPILED = [(name, [re.compile(p) for p in pats]) for name, pats in TRIGGER_CLASSES]


def trigger_class(text: str | None) -> str:
    """Deterministic trigger class by keyword-hit count; ties → priority order; none → 'other'."""
    s = trigger_norm(text)
    if not s:
        return "other"
    best, best_hits = "other", 0
    for name, pats in _COMPILED:
        hits = sum(1 for p in pats if p.search(s))
        if hits > best_hits:
            best, best_hits = name, hits
    return best


def trigger_key(text: str | None) -> str:
    """The dedup key for a trigger: its class, or the normalised text when unclassifiable."""
    cls = trigger_class(text)
    if cls != "other":
        return cls
    return ("other:" + trigger_norm(text))[:120] or "other"


@dataclass(frozen=True)
class BlocklistDecision:
    blocked: bool
    reason: str | None
    entry_id: int | None


def check_blocklist(session: Session, company_norm: str, today: dt.date) -> BlocklistDecision:
    """Blocked while ACTIVE, or COOLING / CLOSED_LOST with cooling_until >= today (or unset)."""
    rows = session.scalars(select(Blocklist).where(Blocklist.company_norm == company_norm)).all()
    for row in rows:
        if row.status == BlocklistStatus.active:
            return BlocklistDecision(
                True, f"blocklist: active pursuit ({row.reason or 'no reason'})", row.id
            )
        if row.cooling_until is None or row.cooling_until >= today:
            return BlocklistDecision(
                True,
                f"blocklist: {row.status.value} until {row.cooling_until or 'further notice'}",
                row.id,
            )
    return BlocklistDecision(False, None, None)


@dataclass(frozen=True)
class DedupDecision:
    suppressed: bool
    resurfaced: bool
    reason: str | None
    prior_id: int | None


def check_dedup(
    session: Session, company_norm: str, trig_key: str, now: dt.datetime, window_days: int
) -> DedupDecision:
    cutoff = now - dt.timedelta(days=window_days)
    rows = session.scalars(
        select(SurfacedLog).where(
            SurfacedLog.company_norm == company_norm, SurfacedLog.last_surfaced_at >= cutoff
        )
    ).all()
    same = [r for r in rows if r.trigger_reason_norm == trig_key]
    if same:
        r = same[0]
        return DedupDecision(
            True,
            False,
            f"dedup: {r.company_display or company_norm} surfaced on {r.last_surfaced_at.date()} "
            f"with the same trigger ({trig_key}); window {window_days}d",
            r.id,
        )
    if rows:
        r = rows[0]
        return DedupDecision(
            False,
            True,
            f"resurfaced: {r.company_display or company_norm} last surfaced "
            f"{r.last_surfaced_at.date()} ({r.trigger_reason_norm}); new trigger {trig_key}",
            r.id,
        )
    return DedupDecision(False, False, None, None)


def record_surfaced(
    session: Session,
    company_norm: str,
    trig_key: str,
    display: str | None,
    now: dt.datetime,
    brief_id: int | None = None,
) -> SurfacedLog:
    row = session.scalar(
        select(SurfacedLog).where(
            SurfacedLog.company_norm == company_norm, SurfacedLog.trigger_reason_norm == trig_key
        )
    )
    if row is None:
        row = SurfacedLog(
            company_norm=company_norm,
            trigger_reason_norm=trig_key,
            company_display=display,
            first_surfaced_at=now,
            last_surfaced_at=now,
            times_surfaced=1,
            brief_id=brief_id,
        )
        session.add(row)
    else:
        row.last_surfaced_at = now
        row.times_surfaced += 1
        if brief_id is not None:
            row.brief_id = brief_id
        if display:
            row.company_display = display
    session.flush()
    return row
