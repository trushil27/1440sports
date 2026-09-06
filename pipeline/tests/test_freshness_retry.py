"""When every candidate is outside the freshness window the run asks the scanner once more,
for the window only — and the log names each candidate with its date and decision."""

from __future__ import annotations

import datetime as dt

from intel import run_daily
from intel.config import Settings
from intel.models import Brief
from intel.parse import ScannedSignal
from intel.seed import load_seeds
from tests.fixtures import production_signals as ps
from tests.fixtures.ramp_brief import RAMP_WRITTEN
from tests.test_m3_verify import FakeVerifier
from tests.test_m4_pipeline import FakeWriter, _block

RUN_DATE = dt.date(2026, 6, 14)


def _sig(**over) -> ScannedSignal:
    row = dict(ps.RAMP_JUNE_ROUND)
    row["score_breakdown"] = ps.synthetic_split(row["score"])
    row.update(over)
    return ScannedSignal.model_validate(row)


def test_all_stale_triggers_one_dated_retry(session, migrated_database, tmp_path, capsys):
    load_seeds(session)
    calls: list[str | None] = []

    def scanner(run_date, addendum=None):
        calls.append(addendum)
        if addendum is None:  # first pass: well-known but old rounds
            return [
                _sig(company="Old Co A", signal_date="2026-04-01"),
                _sig(company="Old Co B", signal_date="2026-03-20"),
            ]
        return [_sig(signal_date="2026-06-12")]  # the retry finds this week's round

    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        anthropic_api_key="x",
    )
    stages = run_daily.Stages(
        verifier=FakeVerifier(),
        writer=FakeWriter([_block(RAMP_WRITTEN)]),
        font_stack="june",
        distribute=False,
    )
    out = run_daily.run_day(RUN_DATE, settings, scanner, session, stages=stages)
    assert out.status == "success", out.summary
    assert len(calls) == 2 and "between 2026-05-31 and 2026-06-14" in calls[1]
    assert "Old Co A (2026-04-01)" in calls[1]
    assert out.summary["freshness_retry"] is True
    assert out.summary["candidates"] == 3
    names = [c["company"] for c in out.summary["candidate_list"]]
    assert names[:2] == ["Old Co A", "Old Co B"] and names[2] == "Ramp"
    assert [c["decision"] for c in out.summary["candidate_list"]][:2] == ["stale", "stale"]
    brief = session.get(Brief, out.brief_id)
    assert brief.candidate.rank == 3  # ranks continue after the first pass
    log = capsys.readouterr().out
    assert "1. Old Co A · signal 2026-04-01 · stale" in log
    assert "all 2 candidates stale — retrying the scan for 2026-05-31..2026-06-14" in log
    assert "3. Ramp · signal 2026-06-12 · pending" in log and "Ramp: issued as brief" in log


def test_no_retry_when_the_scanner_cannot_take_an_addendum(session, migrated_database, tmp_path):
    load_seeds(session)
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        anthropic_api_key="x",
    )
    stages = run_daily.Stages(
        verifier=FakeVerifier(), writer=FakeWriter([]), font_stack="june", distribute=False
    )
    out = run_daily.run_day(
        dt.date(2026, 6, 15),
        settings,
        lambda d: [_sig(company="Old Co", signal_date="2026-04-01")],
        session,
        stages=stages,
    )
    assert out.status == "no_signal" and "freshness_retry" not in (out.summary or {})


def test_fallback_window_admits_an_older_trigger_labelled(session, migrated_database, tmp_path):
    """No retry possible (plain scanner), nothing inside 14 days: a 20-day-old round is admitted
    under the 30-day fallback, and the run says so."""
    load_seeds(session)
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        anthropic_api_key="x",
    )
    stages = run_daily.Stages(
        verifier=FakeVerifier(),
        writer=FakeWriter([_block(RAMP_WRITTEN)]),
        font_stack="june",
        distribute=False,
    )
    run_date = dt.date(2026, 6, 16)
    out = run_daily.run_day(
        run_date, settings, lambda d: [_sig(signal_date="2026-05-27")], session, stages=stages
    )
    assert out.status == "success", out.summary
    assert out.summary["fallback_window"] == 30
    rows = out.summary["candidate_list"]
    assert [r["decision"] for r in rows] == ["stale", "selected"]
    assert rows[1]["reason"].startswith("fallback window 30 days: trigger 20 days old")


def test_fallback_off_keeps_the_no_signal(session, migrated_database, tmp_path):
    load_seeds(session)
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        anthropic_api_key="x",
        freshness_fallback_days=0,
    )
    stages = run_daily.Stages(
        verifier=FakeVerifier(), writer=FakeWriter([]), font_stack="june", distribute=False
    )
    out = run_daily.run_day(
        dt.date(2026, 6, 17),
        settings,
        lambda d: [_sig(signal_date="2026-05-27")],
        session,
        stages=stages,
    )
    assert out.status == "no_signal" and "fallback_window" not in out.summary
