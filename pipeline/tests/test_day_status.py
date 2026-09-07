"""intel.day_status — the daily job asks the repo, not the clock, whether today is done."""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import textwrap
from pathlib import Path

from intel import day_status

CASES = Path(__file__).resolve().parents[1] / "intel" / "cases"


def _record(folder: Path, stem: str, number: int) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"{stem}.run.json"
    p.write_text(json.dumps({"run": {}, "brief": {"number": number}}), encoding="utf-8")
    return p


def test_a_saved_signal_marks_the_day_done(tmp_path):
    day = dt.date(2026, 9, 7)
    assert day_status.live_case_for(day, tmp_path) is None
    _record(tmp_path / "2026-09-07", "acme", 300)
    assert day_status.live_case_for(day, tmp_path).name == "acme.run.json"


def test_an_import_placeholder_does_not_count(tmp_path):
    # historical imports carry NEGATIVE numbers; only a real issued brief closes the day
    _record(tmp_path / "2026-09-07", "old", -42)
    assert day_status.live_case_for(dt.date(2026, 9, 7), tmp_path) is None


def test_todays_real_repo_state_is_readable():
    # 6 Sep 2026 shipped N° 127 Fluidstack, so that day reads as done from the repo itself
    assert day_status.live_case_for(dt.date(2026, 9, 6), CASES) is not None


def test_the_gate_runs_without_any_third_party_package():
    """The workflow calls this BEFORE pip install, so it must be stdlib-only. A stray
    `from intel.config import …` here would make every scheduled run fail at the gate."""
    code = textwrap.dedent("""
        import sys
        sys.path = [p for p in sys.path if 'site-packages' not in p and 'dist-packages' not in p]
        sys.path.insert(0, %r)
        import runpy
        sys.argv = ['day_status', '--date', '2026-09-06']
        runpy.run_module('intel.day_status', run_name='__main__')
    """) % str(CASES.parents[1])
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "already saved" in r.stdout


def test_github_output_is_written_for_the_workflow_step(tmp_path):
    out = tmp_path / "out"
    day_status.main(["--date", "2026-09-07", "--cases", str(tmp_path), "--github-output", str(out)])
    assert out.read_text(encoding="utf-8").split() == ["done=false", "hold=false"]
    _record(tmp_path / "2026-09-07", "acme", 301)
    day_status.main(["--date", "2026-09-07", "--cases", str(tmp_path), "--github-output", str(out)])
    text = out.read_text(encoding="utf-8")
    assert "done=true" in text and "hold=true" in text


def test_a_firing_before_five_london_is_held_not_run(tmp_path, monkeypatch):
    """The routine fires at a fixed UTC time; in winter that same instant is an hour earlier
    in London. The gate — not the trigger — is what keeps the signal landing at 06:00."""
    from zoneinfo import ZoneInfo

    london = ZoneInfo("Europe/London")
    assert day_status.too_early(dt.datetime(2026, 11, 2, 4, 48, tzinfo=london)) is True
    assert day_status.too_early(dt.datetime(2026, 11, 2, 5, 48, tzinfo=london)) is False

    out = tmp_path / "out"
    winter_dawn = dt.datetime(2026, 11, 2, 4, 48, tzinfo=london)
    monkeypatch.setattr(day_status, "london_now", lambda: winter_dawn)
    day_status.main(["--cases", str(tmp_path), "--github-output", str(out)])
    text = out.read_text(encoding="utf-8")
    assert "done=false" in text and "hold=true" in text  # nothing saved, but not yet its hour
