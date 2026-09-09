"""intel.pool — the day's runner-ups and blocked candidates feed the app, not the bin.

"When we pick the best of 3, the other 2 don't have to be scrapped. It needs to feed into
the app still if they are relevant." (operator, 8 Sep 2026)"""

from __future__ import annotations

import datetime as dt
import json

from sqlalchemy import select

from intel import pool, run_daily
from intel.config import Settings
from intel.models import Brief, Candidate, CandidateDecision, Run
from intel.scan import ScanFailed
from intel.seed import load_seeds
from tests.fixtures.ramp_brief import RAMP_WRITTEN
from tests.test_m3_verify import FakeVerifier
from tests.test_m4_pipeline import RUN_DATE, FakeWriter, _block, _ramp_signal


def _second(company, score, trigger="raised a $250m Series D on 1 Jun 2026", date="2026-06-01"):
    """A second candidate; the desk rescores from the breakdown, so a weak one is weak there."""
    s = _ramp_signal()
    weak = score < 70
    update = {
        "company": company,
        "score": score,
        "trigger_reason": trigger,
        "signal_date": date,
        "source_url": f"https://news.test/{company.lower()}",
    }
    if weak:
        update["score_breakdown"] = s.score_breakdown.model_copy(
            update={"timing": 8, "capacity": 8, "brand_fit": 8, "urgency": 8, "ops_fit": 8}
        )
    return s.model_copy(update=update)


def _run_day(session, migrated_database, tmp_path, signals):
    load_seeds(session)
    stages = run_daily.Stages(
        verifier=FakeVerifier(),
        writer=FakeWriter([_block(RAMP_WRITTEN)]),
        font_stack="june",
    )
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        outbox_dir=str(tmp_path / "outbox"),
    )
    out = run_daily.run_day(RUN_DATE, settings, lambda _d: signals, session, stages=stages)
    session.flush()
    return out, settings


def test_runner_ups_are_written_with_the_case_and_come_back_as_thin_rows(
    session, migrated_database, tmp_path
):
    out, settings = _run_day(
        session,
        migrated_database,
        tmp_path,
        [_ramp_signal(), _second("Acme Grid", 78), _second("Tiny Co", 55)],
    )
    assert out.status == "success"
    run = session.get(Run, out.run_id)
    records = pool.pool_records(session, run, threshold=70)
    # Ramp won; Acme Grid cleared the bar and was not chosen; Tiny Co did not clear it
    assert [(r["company"], r["decision"]) for r in records] == [("Acme Grid", "runner_up")]
    assert records[0]["stage"] == "Series D" and records[0]["source"] == "scanner"

    cases = tmp_path / "cases"
    written = pool.sync_pool(session, cases, threshold=70)
    assert written == [str(cases / RUN_DATE.isoformat() / "pool.json")]
    data = json.loads((cases / RUN_DATE.isoformat() / "pool.json").read_text(encoding="utf-8"))
    assert data["candidates"][0]["company"] == "Acme Grid"

    # a fresh start imports it as a thin, unverified, historical row — and only once
    before = session.scalar(
        select(Brief).join(Candidate).where(Candidate.company_norm == "acmegrid")
    )
    assert before is None
    assert pool.import_pool(session, cases) == {"source": "pool", "created": 1, "skipped": 0}
    row = session.scalar(select(Brief).join(Candidate).where(Candidate.company_norm == "acmegrid"))
    assert row is not None and row.historical and row.brief_number < 0
    assert row.verification_status.value == "needs_review"
    assert row.brief_data["historical_label"] == f"Runner-up, {RUN_DATE.isoformat()}"
    assert row.candidate.decision == CandidateDecision.not_selected
    assert pool.import_pool(session, cases) == {"source": "pool", "created": 0, "skipped": 1}


def test_a_blocked_candidate_becomes_a_screen_out_with_its_reason(tmp_path):
    cases = tmp_path / "cases" / "2026-09-08"
    cases.mkdir(parents=True)
    (cases / "pool.json").write_text(
        json.dumps(
            {
                "date": "2026-09-08",
                "candidates": [
                    {
                        "company": "Nscale",
                        "decision": "blocked",
                        "reason": "contradicted load-bearing claim: pre-IPO round | IPO round",
                        "series": "F1",
                        "source_url": "https://techcrunch.com/nscale",
                        "score": 81,
                    },
                    {"company": "Acme Grid", "decision": "runner_up", "score": 78},
                ],
            }
        ),
        encoding="utf-8",
    )
    rows = pool.blocked_rows(tmp_path / "cases")
    assert [r["company"] for r in rows] == ["Nscale"]
    rv = rows[0]["review"]
    assert rv["status"] == "screened_out" and rv["reason_code"] == "case_screen"
    assert rv["reason"].startswith("contradicted: contradicted load-bearing")
    assert rv["sources"] == ["https://techcrunch.com/nscale"] and rv["screened_at"] == "2026-09-08"


def test_the_scan_is_tried_twice_before_the_day_fails_and_not_when_the_mailbox_delivered():
    calls = []

    def flaky(day):
        calls.append(day)
        if len(calls) == 1:
            raise ScanFailed("first try: cut off")
        return ["ok"]

    assert run_daily._scan_with_retry(flaky, RUN_DATE, Settings(), []) == ["ok"]
    assert len(calls) == 2

    calls.clear()

    def always(day):
        calls.append(day)
        raise ScanFailed("no")

    try:
        run_daily._scan_with_retry(always, RUN_DATE, Settings(), [])
        raise AssertionError("should have raised")
    except ScanFailed:
        pass
    assert len(calls) == 2  # exactly scan_full_attempts

    calls.clear()
    try:
        run_daily._scan_with_retry(always, RUN_DATE, Settings(), ["a lead from the mailbox"])
        raise AssertionError("should have raised")
    except ScanFailed:
        pass
    assert len(calls) == 1  # the mailbox delivered: no second paid attempt


def test_two_runner_ups_on_one_day_import_under_one_run(session, migrated_database, tmp_path):
    """9 Sep 2026: the importer gave every runner-up its own run with the same fixed attempt
    number, and (run_date, attempt) is unique — the second one on a day failed the whole
    backfill, which is what every start of the desk runs first."""
    from intel.seed import load_seeds as _seeds

    _seeds(session)
    cases = tmp_path / "cases" / "2026-09-09"
    cases.mkdir(parents=True)
    (cases / "pool.json").write_text(
        json.dumps(
            {
                "date": "2026-09-09",
                "candidates": [
                    {"company": "Alpha Grid", "decision": "runner_up", "score": 78, "rank": 2},
                    {"company": "Beta Cells", "decision": "runner_up", "score": 74, "rank": 3},
                ],
            }
        ),
        encoding="utf-8",
    )
    assert pool.import_pool(session, tmp_path / "cases") == {
        "source": "pool",
        "created": 2,
        "skipped": 0,
    }
    runs = session.scalars(select(Run).where(Run.run_date == dt.date(2026, 9, 9))).all()
    assert len(runs) == 1 and runs[0].attempt == 1
    # importing again on the same memory changes nothing, and a fresh date takes attempt 1 too
    assert pool.import_pool(session, tmp_path / "cases") == {
        "source": "pool",
        "created": 0,
        "skipped": 2,
    }
