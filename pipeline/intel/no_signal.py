"""Record a morning that found nothing — so the next firing does not scan again.

11 Sep 2026: the 04:40 run scanned, found 0 eligible of 11 and sent the operator a
"no signal" note; the 05:40 routine firing and the 09:20 cron then did the whole scan
again, because the gate (intel.day_status) only knows a day is done when a case record is
saved, and a no-signal day saves nothing. Three scans, one honest answer, about $3.60.

The daily job now writes ``pipeline/intel/cases/<date>/no_signal.json`` from the run record
when a run ends without a brief, and commits it with the cases. The gate reads it as "done":
one scan per day unless someone ticks the force box. It is a stdlib-only module because it
runs inside the workflow next to the gate, and it is NOT a case record — nothing in the
backfill, the site export or merge_cases globs this filename.

    python -m intel.no_signal                    # today, storage/briefs/runs → cases/
    python -m intel.no_signal --date 2026-09-11 --runs storage/briefs/runs \
        --cases pipeline/intel/cases
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from intel.day_status import CASES_DIR, live_case_for, london_today

MARKER = "no_signal.json"


def run_records(day: dt.date, runs_dir: Path | str) -> list[Path]:
    folder = Path(runs_dir)
    if not folder.is_dir():
        return []
    return sorted(folder.glob(f"{day.isoformat()}-run*.json"))


def write_marker(
    day: dt.date, runs_dir: Path | str, cases_dir: Path | str | None = None
) -> Path | None:
    """Write the marker for ``day`` if a run ended without a brief and no case exists.

    Returns the marker path, or None when there is a live case (the day is done anyway),
    no run record, or the run did produce a brief (then the case record is the answer)."""
    cases = Path(cases_dir or CASES_DIR)
    if live_case_for(day, cases) is not None:
        return None
    outcome = None
    for rec in run_records(day, runs_dir):
        try:
            data = json.loads(rec.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if data.get("status") == "no_signal" and not data.get("brief_id"):
            outcome = data
    if outcome is None:
        return None
    summary = outcome.get("summary") or {}
    marker = {
        "date": day.isoformat(),
        "status": "no_signal",
        "candidates": summary.get("candidates"),
        "decisions": summary.get("decisions"),
        "sources": summary.get("sources"),
        "usage": summary.get("usage"),
        "candidate_list": summary.get("candidate_list"),
        "recorded_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "note": "The morning run scanned and found no eligible signal; the gate holds further "
        "firings for the day. Tick 'force' on the Daily run workflow to scan again.",
    }
    folder = cases / day.isoformat()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / MARKER
    path.write_text(json.dumps(marker, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.no_signal", description=__doc__)
    parser.add_argument("--date", type=dt.date.fromisoformat, default=None)
    parser.add_argument("--runs", default="storage/briefs/runs")
    parser.add_argument("--cases", default=None)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    day = args.date or london_today()
    path = write_marker(day, args.runs, args.cases)
    if path is None:
        print(f"{day}: nothing to record (a case exists, or no run ended without a brief)")
    else:
        print(f"{day}: no-signal marker written → {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
