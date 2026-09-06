"""The desk build service: one click queues a build for an existing signal, runs it, records the
result, and the daily job drains whatever is left."""

from __future__ import annotations

import datetime as dt

from fastapi.testclient import TestClient
from sqlalchemy import select

from intel import backfill, desk_api
from intel.config import Settings
from intel.models import RebuildRequest, RebuildStatus
from intel.run_daily import RunOutcome

SWEEP = backfill.BACKFILL_DIR / "fe_sweep_signals_2026-09-05.json"


class FakeRunner:
    def __init__(self, status="success"):
        self.calls = []
        self.status = status

    def __call__(self, company, date, settings):
        self.calls.append((company, date))
        return RunOutcome(1, date, self.status, None, None, "verified", "pass", None)


def _settings(url, tmp_path):
    return Settings(
        database_url=url, pdf_storage_dir=str(tmp_path / "s"), site_dir=str(tmp_path / "site")
    )


def test_build_queues_runs_and_reports(session, migrated_database, tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_STORAGE_DIR", str(tmp_path / "s"))
    from intel.config import reset_settings

    reset_settings()
    backfill.import_daily_signals(session, SWEEP)
    session.commit()
    number = session.scalar(select(RebuildRequest.id))  # none yet
    assert number is None
    from intel.models import Brief

    antora = session.scalar(
        select(Brief).where(Brief.brief_data["company"].astext == "Antora Energy")
    )
    settings = _settings(migrated_database, tmp_path)
    runner = FakeRunner()
    app = desk_api.create_app(settings, runner=runner, start_worker=False)
    client = TestClient(app)

    assert client.get("/health").json()["ok"] is True
    r = client.post("/build", json={"number": antora.brief_number})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["queued"] is True and body["request"]["status"] == "queued"
    rid = body["request"]["id"]
    # a second click while queued returns the same request
    again = client.post("/build", json={"number": antora.brief_number}).json()
    assert again["queued"] is False and again["request"]["id"] == rid
    assert client.post("/build", json={"number": 999999}).status_code == 404

    # the worker (here: the daily job's drain) runs it
    done = desk_api.drain(settings, runner=runner)
    assert done and done[0]["status"] == "done"
    assert runner.calls == [("Antora Energy", dt.date(2026, 7, 30))]
    st = client.get(f"/build/{rid}").json()
    assert st["status"] == "done" and st["finished_at"]
    session.expire_all()
    row = session.get(RebuildRequest, rid)
    assert row.status == RebuildStatus.done

    # the failure path is recorded, not raised
    r = client.post("/build", json={"company": "BYD"})
    assert r.status_code == 200
    bad = desk_api.drain(settings, runner=FakeRunner(status="no_signal"))
    assert bad[0]["status"] == "failed"
    assert client.get("/queue").json()[0]["status"] == "failed"


def test_rate_limit(session, migrated_database, tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_STORAGE_DIR", str(tmp_path / "s"))
    from intel.config import reset_settings

    reset_settings()
    backfill.import_daily_signals(session, SWEEP)
    session.commit()
    from sqlalchemy import delete

    session.execute(delete(RebuildRequest))  # rows from other tests persist in the shared DB
    session.commit()
    settings = _settings(migrated_database, tmp_path).model_copy(
        update={"desk_max_builds_per_hour": 1}
    )
    client = TestClient(desk_api.create_app(settings, runner=FakeRunner(), start_worker=False))
    assert client.post("/build", json={"company": "Base Power"}).status_code == 200
    assert client.post("/build", json={"company": "Lyten"}).status_code == 429
