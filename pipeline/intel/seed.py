"""Reference-data seeds: mirror the spec files into the database (build brief §5).

Loads ``intel/seeds/*.json`` into ``sponsors``, ``alumni``, ``blocklist`` and
``calendar_events``. Every seed row was copied from a spec file and carries a
``source`` pointing at the file and section; nothing here is invented.

Idempotent: each table has a natural key and rows are upserted on it, so
running the loader twice leaves the row counts unchanged.

    python -m intel.seed            # load into $DATABASE_URL
"""

from __future__ import annotations

import datetime as dt
import json
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.models import (
    Alumni,
    AlumniTier,
    Blocklist,
    BlocklistStatus,
    CalendarEvent,
    EventStatus,
    Series,
    Sponsor,
    SponsorLevel,
    SponsorStatus,
)
from intel.normalise import company_norm

SEEDS_DIR = Path(__file__).resolve().parent / "seeds"

SPONSORS_FILE = "sponsors.json"
ALUMNI_FILE = "alumni.json"
BLOCKLIST_FILE = "blocklist.json"
CALENDAR_FILE = "calendar_2026.json"


def _date(value: str | None) -> dt.date | None:
    return dt.date.fromisoformat(value) if value else None


def _read(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _upsert(
    session: Session,
    model: type,
    rows: Iterable[dict[str, Any]],
    key_of: Callable[[dict[str, Any]], dict[str, Any]],
) -> int:
    """Insert or update each row, keyed on the columns returned by ``key_of``."""
    count = 0
    for row in rows:
        key = key_of(row)
        stmt = select(model)
        for column, value in key.items():
            stmt = stmt.where(getattr(model, column) == value)
        existing = session.execute(stmt).scalars().first()
        if existing is None:
            session.add(model(**row))
        else:
            for column, value in row.items():
                setattr(existing, column, value)
        count += 1
    session.flush()
    return count


# --- per-table row builders --------------------------------------------------------------


def _sponsor_row(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "series": Series(raw["series"]),
        "level": SponsorLevel(raw["level"]),
        "team": raw.get("team"),
        "brand": raw["brand"],
        "brand_norm": company_norm(raw["brand"]),
        "category": raw.get("category"),
        "status": SponsorStatus(raw["status"]),
        "season": raw.get("season"),
        "notes": raw.get("notes"),
        "source": raw.get("source"),
        "verified_at": _date(raw.get("verified_at")),
    }


def _alumni_row(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": raw["name"],
        "previous_role": raw.get("previous_role"),
        "previous_company": raw.get("previous_company"),
        "deal_involvement": raw.get("deal_involvement"),
        "current_role": raw.get("current_role"),
        "current_company": raw.get("current_company"),
        "company_norm": company_norm(raw.get("current_company")) or None,
        "move_date": _date(raw.get("move_date")),
        "tier": AlumniTier(raw["tier"]),
        "boost_applied": raw.get("boost_applied"),
        "base_score": raw.get("base_score"),
        "final_score": raw.get("final_score"),
        "complications": raw.get("complications"),
        "verification": raw.get("verification"),
        "outreach_status": raw.get("outreach_status"),
        "active": True,
        # The ORM has no ``source`` column on alumni: keep provenance in notes.
        "notes": _join(raw.get("notes"), f"Source: {raw['source']}" if raw.get("source") else None),
    }


def _blocklist_row(raw: dict[str, Any]) -> dict[str, Any]:
    added_at = _date(raw.get("added_at"))
    if added_at is None:
        raise ValueError(f"blocklist seed {raw['company_raw']!r} has no added_at")
    return {
        "company_raw": raw["company_raw"],
        "company_norm": company_norm(raw["company_raw"]),
        "status": BlocklistStatus(raw["status"]),
        "reason": raw.get("reason"),
        "added_at": added_at,
        "cooling_until": _date(raw.get("cooling_until")),
        "added_by": raw.get("added_by"),
        # The ORM has no ``source`` column on blocklist: keep provenance in notes.
        "notes": _join(raw.get("notes"), f"Source: {raw['source']}" if raw.get("source") else None),
    }


def _calendar_row(raw: dict[str, Any]) -> dict[str, Any]:
    # calendar_events has no ``notes`` column; the spec's remark on the title
    # sponsor (e.g. "(historically Qatar Airways)") is folded into ``source`` so
    # the verification stage can still see the caveat.
    source = raw.get("source")
    if raw.get("notes"):
        source = _join(source, f"note: {raw['notes']}")
    return {
        "series": Series(raw["series"]),
        "season": int(raw["season"]),
        "round": int(raw["round"]),
        "name": raw["name"],
        "city": raw.get("city"),
        "country": raw.get("country"),
        "date_start": _date(raw.get("date_start")),
        "date_end": _date(raw.get("date_end")),
        "title_sponsor": raw.get("title_sponsor"),
        "status": EventStatus(raw["status"]),
        "source": source,
        "verified_at": _date(raw.get("verified_at")),
    }


def _join(*parts: str | None) -> str | None:
    kept = [p for p in parts if p]
    return " | ".join(kept) if kept else None


# --- loaders -----------------------------------------------------------------------------


def load_sponsors(session: Session, seeds_dir: Path = SEEDS_DIR) -> int:
    rows = (_sponsor_row(r) for r in _read(seeds_dir / SPONSORS_FILE))
    return _upsert(
        session,
        Sponsor,
        rows,
        lambda r: {
            "series": r["series"],
            "level": r["level"],
            "team": r["team"],
            "brand_norm": r["brand_norm"],
            "status": r["status"],
        },
    )


def load_alumni(session: Session, seeds_dir: Path = SEEDS_DIR) -> int:
    rows = (_alumni_row(r) for r in _read(seeds_dir / ALUMNI_FILE))
    return _upsert(
        session,
        Alumni,
        rows,
        lambda r: {"name": r["name"], "current_company": r["current_company"]},
    )


def load_blocklist(session: Session, seeds_dir: Path = SEEDS_DIR) -> int:
    rows = (_blocklist_row(r) for r in _read(seeds_dir / BLOCKLIST_FILE))
    return _upsert(session, Blocklist, rows, lambda r: {"company_norm": r["company_norm"]})


def load_calendar(session: Session, seeds_dir: Path = SEEDS_DIR) -> int:
    data = _read(seeds_dir / CALENDAR_FILE)
    events = data["events"] if isinstance(data, dict) else data
    rows = (_calendar_row(r) for r in events)
    return _upsert(
        session,
        CalendarEvent,
        rows,
        lambda r: {"series": r["series"], "season": r["season"], "round": r["round"]},
    )


def load_seeds(session: Session, seeds_dir: Path | str | None = None) -> dict[str, int]:
    """Upsert every seed file. Returns the number of seed rows processed per table."""
    base = Path(seeds_dir) if seeds_dir else SEEDS_DIR
    return {
        "sponsors": load_sponsors(session, base),
        "alumni": load_alumni(session, base),
        "blocklist": load_blocklist(session, base),
        "calendar_events": load_calendar(session, base),
    }


def main() -> None:
    from intel.db import session_scope

    with session_scope() as session:
        counts = load_seeds(session)
    for table, n in counts.items():
        print(f"{table}: {n} rows upserted")


if __name__ == "__main__":
    main()
