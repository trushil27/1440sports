"""Parallel backlog runs: shards split the same newest-first queue without overlap, and the
daily hero numbering ignores the reserved backlog blocks."""

from __future__ import annotations

from sqlalchemy import text

from intel import backfill, rebuild_queue
from intel.run_daily import RunOutcome

SWEEP = backfill.BACKFILL_DIR / "fe_sweep_signals_2026-09-05.json"


class Recorder:
    def __init__(self):
        self.built: list[str] = []

    def __call__(self, company, date, settings):
        self.built.append(company)
        return RunOutcome(1, date, "success", None, 1, "verified", "pass", None)


def test_shards_partition_the_queue_without_overlap(session, tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_STORAGE_DIR", str(tmp_path / "s"))
    from intel.config import reset_settings

    reset_settings()
    backfill.import_daily_signals(session, SWEEP)
    from intel.config import get_settings

    settings = get_settings()
    built = {}
    for k in range(3):
        rec = Recorder()
        monkeypatch.setenv("PDF_STORAGE_DIR", str(tmp_path / f"s{k}"))  # separate done-files
        reset_settings()
        rebuild_queue.backlog(
            get_settings(), limit=100, runner=rec, session=session, shard=k, shards=3
        )
        built[k] = rec.built
    sets = [set(v) for v in built.values()]
    assert all(sets[i].isdisjoint(sets[j]) for i in range(3) for j in range(i + 1, 3))
    total = sum(len(v) for v in built.values())
    assert total >= 20  # the sweep has 24 rows, a few are screened/merged
    assert abs(len(built[0]) - len(built[2])) <= 1  # round-robin split
    reset_settings()
    del settings


def test_daily_sequence_ignores_backlog_blocks(session):
    before = session.execute(text("SELECT last_value FROM brief_number_seq")).scalar()
    backfill._bump_sequence(session, 10712)
    assert session.execute(text("SELECT last_value FROM brief_number_seq")).scalar() == before
    backfill._bump_sequence(session, 130)
    assert session.execute(text("SELECT last_value FROM brief_number_seq")).scalar() >= 130
