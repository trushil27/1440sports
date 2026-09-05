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


def _slot(argv: list[str]) -> tuple[dt.time, dt.time]:
    """``--slot HH:MM`` moves both the run and the send to that London time (test runs)."""
    if "--slot" in argv:
        raw = argv[argv.index("--slot") + 1]
        h, m = (int(x) for x in raw.split(":"))
        return dt.time(h, m), dt.time(h, m)
    return RUN_AT, SEND_AT


SLOT_TOLERANCE = dt.timedelta(minutes=20)


def london_now(now_utc: dt.datetime | None = None) -> dt.datetime:
    now_utc = now_utc or dt.datetime.now(dt.UTC)
    return now_utc.astimezone(LONDON)


def is_run_slot(now_utc: dt.datetime | None = None, run_at: dt.time = RUN_AT) -> bool:
    """True when the local London time is within tolerance of the slot (either UTC firing)."""
    local = london_now(now_utc)
    target = local.replace(hour=run_at.hour, minute=run_at.minute, second=0, microsecond=0)
    return abs(local - target) <= SLOT_TOLERANCE


def seconds_until_send(now_utc: dt.datetime | None = None, send_at: dt.time = SEND_AT) -> float:
    local = london_now(now_utc)
    target = local.replace(hour=send_at.hour, minute=send_at.minute, second=0, microsecond=0)
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
    run_at, send_at = _slot(argv)
    if not force and not is_run_slot(run_at=run_at):
        print(f"not the {run_at:%H:%M} Europe/London slot (local {london_now():%H:%M}); exiting")
        return 0
    settings = get_settings()
    run_date = london_now().date()
    stages = run_daily.Stages(distribute=False)  # distribute at 06:00, below
    outcome = run_daily.run_day(run_date, settings, stages=stages)
    print(outcome)

    wait = 0.0 if no_wait else seconds_until_send(send_at=send_at)
    if wait > 0:
        print(f"waiting {int(wait)}s until {send_at:%H:%M} Europe/London")
        time.sleep(wait)
    with session_scope() as session:
        run = session.get(Run, outcome.run_id)
        brief = session.get(Brief, outcome.brief_id) if outcome.brief_id else None
        sends = send.distribute(session, run, settings, send.mailer_for(settings), brief)
        for s in sends:
            print(
                f"sent {s.kind.value} → {s.recipient} [{s.status.value}] {s.message_id or s.error}"
            )
    # "Build the full case" requests from the app (Netlify form) → full rebuilds, then the
    # static app: export every brief + the sponsor grid; deploy when configured. Neither may
    # fail the run — the brief has already been stored and sent.
    try:
        from intel import rebuild_queue

        for rec in rebuild_queue.process(settings):
            print("rebuilt:", rec)
        for rec in rebuild_queue.backlog(settings, limit=settings.rebuild_backlog_per_run):
            print("backlog:", rec)
    except Exception as exc:  # noqa: BLE001 — best effort by design
        print(f"rebuild queue skipped: {exc}")
    try:
        from intel import site_export

        print("site:", site_export.publish(settings))
    except Exception as exc:  # noqa: BLE001 — best effort by design
        print(f"site export skipped: {exc}")
    # A failed run has already been reported by email; exiting 0 keeps the cron service
    # from showing as "Crashed" for a data problem the next run will retry as attempt N+1.
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
