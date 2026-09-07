"""Has today's signal already gone out? — answered from the repo, before any database.

GitHub's scheduled workflows are best-effort: on this repo they have arrived four to five
hours after the cron time, every day (5 Sep 09:10Z for an 04:30Z cron, 6 Sep 08:45Z and
09:32Z, 7 Sep 09:34Z and 10:32Z). The daily job used to gate on "is it 05:xx in London?",
so every one of those late firings was discarded and no signal was produced.

The fix is to stop trusting the clock and fire several times, which needs a reliable answer
to "is today already done?" — otherwise a second firing sends the MD a second email. That
answer lives in the repo: the daily job commits its case record to
``pipeline/intel/cases/<run date>/<company>.run.json`` and a record whose run summary is NOT
a rebuild is the day's live brief.

    python -m intel.day_status            # prints done/pending for today, exit 0 either way
    python -m intel.day_status --date 2026-09-07 --github-output "$GITHUB_OUTPUT"
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

CASES_DIR = Path(__file__).resolve().parent / "cases"


def live_case_for(day: dt.date, cases_dir: Path | str | None = None) -> Path | None:
    """The record of a signal issued for ``day``, or None.

    Any case record with a real brief number counts, however it was produced — the daily job,
    or a case built by hand. If a signal already exists for today the desk is showing it, and
    a second run would issue a second brief and email the operator twice.

    The trade-off, stated so it is not a surprise: a backlog case that happens to carry
    today's date would also block the day. Backlog rebuilds use the original signal's date,
    so that is rare, and the Actions tab's force run overrides it."""
    folder = Path(cases_dir or CASES_DIR) / day.isoformat()
    if not folder.is_dir():
        return None
    for record in sorted(folder.glob("*.run.json")):
        try:
            data = json.loads(record.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        number = (data.get("brief") or {}).get("number")
        if isinstance(number, int) and number > 0:
            return record
    return None


def london_today() -> dt.date:
    """Stdlib only, deliberately: this runs in the workflow's gate step BEFORE pip install,
    so it must not reach for intel.config (pydantic) or anything else third-party."""
    from zoneinfo import ZoneInfo

    return dt.datetime.now(ZoneInfo("Europe/London")).date()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.day_status", description=__doc__)
    parser.add_argument("--date", type=dt.date.fromisoformat, default=None)
    parser.add_argument("--cases", default=None)
    parser.add_argument(
        "--github-output",
        default=os.environ.get("GITHUB_OUTPUT"),
        help="append 'done=true|false' for a workflow step output",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    day = args.date or london_today()
    record = live_case_for(day, args.cases)
    done = record is not None
    print(
        f"{day}: today's signal is already saved ({record.name})"
        if done
        else f"{day}: no signal saved yet — the run should proceed"
    )
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"done={'true' if done else 'false'}\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
