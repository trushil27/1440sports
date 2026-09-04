"""Scheduling in Europe/London (build brief §4): run at 05:30, send at 06:00, BST/GMT-safe.

Cloud cron runs in UTC. Rather than editing the cron twice a year, the schedule fires at
BOTH 04:30 and 05:30 UTC and this module decides which firing is the real 05:30 London
slot (the other exits immediately). The daily job then:

1. runs the pipeline (scan → … → render) and stores everything;
2. waits until 06:00 London;
3. distributes (§7) — sends are recorded, so a retry after a crash never double-sends.

``python -m intel.schedule`` is the cron entry point (Railway cron / GitHub Actions).
"""

from __future__ import annotations

import datetime as dt
import sys
import time
from zoneinfo import ZoneInfo

from intel.config import get_settings

LONDON = ZoneInfo("Europe/London")
RUN_AT = dt.time(5, 30)
SEND_AT = dt.time(6, 0)
SLOT_TOLERANCE = dt.timedelta(minutes=20)


def london_now(now_utc: dt.datetime | None = None) -> dt.datetime:
    now_utc = now_utc or dt.datetime.now(dt.UTC)
    return now_utc.astimezone(LONDON)


def is_run_slot(now_utc: dt.datetime | None = None) -> bool:
    """True when the local London time is within tolerance of 05:30 (either UTC firing)."""
    local = london_now(now_utc)
    target = local.replace(hour=RUN_AT.hour, minute=RUN_AT.minute, second=0, microsecond=0)
    return abs(local - target) <= SLOT_TOLERANCE


def seconds_until_send(now_utc: dt.datetime | None = None) -> float:
    local = london_now(now_utc)
    target = local.replace(hour=SEND_AT.hour, minute=SEND_AT.minute, second=0, microsecond=0)
    if target < local:
        return 0.0
    return (target - local).total_seconds()


def main(argv: list[str] | None = None) -> int:
    """Cron entry point. ``--force`` skips the slot check (manual runs); ``--no-wait`` sends now."""
    from intel import run_daily, send
    from intel.db import session_scope
    from intel.models import Brief, Run

    argv = sys.argv[1:] if argv is None else argv
    force = "--force" in argv
    no_wait = "--no-wait" in argv
    if not force and not is_run_slot():
        print(f"not the 05:30 Europe/London slot (local {london_now():%H:%M}); exiting")
        return 0
    settings = get_settings()
    run_date = london_now().date()
    stages = run_daily.Stages(distribute=False)  # distribute at 06:00, below
    outcome = run_daily.run_day(run_date, settings, stages=stages)
    print(outcome)

    wait = 0.0 if no_wait else seconds_until_send()
    if wait > 0:
        print(f"waiting {int(wait)}s until 06:00 Europe/London")
        time.sleep(wait)
    with session_scope() as session:
        run = session.get(Run, outcome.run_id)
        brief = session.get(Brief, outcome.brief_id) if outcome.brief_id else None
        sends = send.distribute(session, run, settings, send.mailer_for(settings), brief)
        for s in sends:
            print(
                f"sent {s.kind.value} → {s.recipient} [{s.status.value}] {s.message_id or s.error}"
            )
    return 0 if outcome.status != "failed" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
