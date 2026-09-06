"""The desk's build service — the endpoint behind the app's *Build the full case* button.

A static app cannot run the models, and the team will not sign in anywhere to ask for a case.
This tiny public service (same image and variables as the daily job) takes the click, queues
it in ``rebuild_requests``, runs the full pipeline for that one company straight away in a
background thread (``intel.rebuild``), then re-exports and republishes the app so the case
appears on the site. The daily job drains anything left in the queue.

    uvicorn intel.desk_api:app --host 0.0.0.0 --port $PORT      # Railway "desk-api" service

Only companies that already exist as signals can be requested (no free text), one build at a
time, at most ``DESK_MAX_BUILDS_PER_HOUR`` an hour — enough to stop abuse of a public URL.
"""

from __future__ import annotations

import datetime as dt
import threading
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func, select

from intel.config import Settings, get_settings
from intel.db import session_scope
from intel.models import Brief, RebuildRequest, RebuildStatus

_lock = threading.Lock()
_running = {"active": False}


class BuildIn(BaseModel):
    number: int | None = None
    company: str | None = None


def _serialise(r: RebuildRequest) -> dict[str, Any]:
    return {
        "id": r.id,
        "company": r.company,
        "date": r.date.isoformat(),
        "status": r.status.value,
        "requested_at": r.requested_at.isoformat() if r.requested_at else None,
        "started_at": r.started_at.isoformat() if r.started_at else None,
        "finished_at": r.finished_at.isoformat() if r.finished_at else None,
        "result_number": r.result_number,
        "error": r.error,
    }


def work_one(settings: Settings, request_id: int, runner=None) -> dict[str, Any]:
    """Run one queued request to completion (used by the thread and by the daily job)."""
    from intel import rebuild as rebuild_mod
    from intel import site_export

    run = runner or rebuild_mod.rebuild
    with session_scope(settings.database_url) as session:
        req = session.get(RebuildRequest, request_id)
        if req is None or req.status != RebuildStatus.queued:
            return {"id": request_id, "status": "skipped"}
        req.status = RebuildStatus.running
        req.started_at = dt.datetime.now(dt.UTC)
        company, date = req.company, req.date
    try:
        out = run(company, date, settings)
        ok = out.status == "success"
        with session_scope(settings.database_url) as session:
            req = session.get(RebuildRequest, request_id)
            req.status = RebuildStatus.done if ok else RebuildStatus.failed
            req.finished_at = dt.datetime.now(dt.UTC)
            req.result_brief_id = out.brief_id
            if out.brief_id:
                brief = session.get(Brief, out.brief_id)
                req.result_number = brief.brief_number if brief else None
            if not ok:
                req.error = f"pipeline status {out.status}: {out.verification_status or ''}"[:500]
    except Exception as exc:  # noqa: BLE001 — recorded, never raised into the server
        with session_scope(settings.database_url) as session:
            req = session.get(RebuildRequest, request_id)
            req.status = RebuildStatus.failed
            req.finished_at = dt.datetime.now(dt.UTC)
            req.error = f"{type(exc).__name__}: {exc}"[:500]
        return {"id": request_id, "status": "failed", "error": str(exc)[:200]}
    try:
        site_export.publish(settings)
    except Exception as exc:  # noqa: BLE001 — the case exists; the next run republishes
        print(f"desk api: site publish after build skipped: {exc}")
    return {"id": request_id, "status": "done" if ok else "failed"}


def drain(settings: Settings, limit: int = 3, runner=None) -> list[dict[str, Any]]:
    """Work off queued requests, oldest first (the daily job calls this too)."""
    with session_scope(settings.database_url) as session:
        ids = list(
            session.scalars(
                select(RebuildRequest.id)
                .where(RebuildRequest.status == RebuildStatus.queued)
                .order_by(RebuildRequest.requested_at)
                .limit(limit)
            )
        )
    return [work_one(settings, i, runner) for i in ids]


def _worker(settings: Settings, runner=None) -> None:
    with _lock:
        if _running["active"]:
            return
        _running["active"] = True
    try:
        while True:
            done = drain(settings, limit=1, runner=runner)
            if not done:
                break
    finally:
        with _lock:
            _running["active"] = False


def create_app(settings: Settings | None = None, runner=None, start_worker: bool = True) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="1440 desk build service", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "building": _running["active"]}

    @app.post("/build")
    def build(body: BuildIn, request: Request) -> dict[str, Any]:
        with session_scope(settings.database_url) as session:
            brief = None
            if body.number is not None:
                brief = session.scalar(select(Brief).where(Brief.brief_number == body.number))
            elif body.company:
                brief = session.scalar(
                    select(Brief)
                    .where(Brief.brief_data["company"].astext.ilike(body.company.strip()))
                    .order_by(Brief.run_date.desc())
                )
            if brief is None:
                raise HTTPException(404, "no such signal")
            company = (brief.brief_data or {}).get("company") or brief.candidate.company_raw
            if brief.web_html_path:
                raise HTTPException(
                    409, f"{company} already has a full case (N° {brief.brief_number})"
                )
            open_req = session.scalar(
                select(RebuildRequest).where(
                    RebuildRequest.company == company,
                    RebuildRequest.status.in_([RebuildStatus.queued, RebuildStatus.running]),
                )
            )
            if open_req is not None:
                return {"queued": False, "request": _serialise(open_req)}
            hour_ago = dt.datetime.now(dt.UTC) - dt.timedelta(hours=1)
            recent = session.scalar(
                select(func.count())
                .select_from(RebuildRequest)
                .where(RebuildRequest.requested_at >= hour_ago)
            )
            if recent is not None and recent >= settings.desk_max_builds_per_hour:
                raise HTTPException(429, "build limit reached for this hour; try again later")
            req = RebuildRequest(
                brief_number=brief.brief_number,
                company=company,
                date=brief.run_date,
                status=RebuildStatus.queued,
                requested_at=dt.datetime.now(dt.UTC),
                requester=(request.client.host if request.client else None),
            )
            session.add(req)
            session.flush()
            payload = _serialise(req)
        if start_worker:
            threading.Thread(target=_worker, args=(settings, runner), daemon=True).start()
        return {"queued": True, "request": payload}

    @app.get("/build/{request_id}")
    def status(request_id: int) -> dict[str, Any]:
        with session_scope(settings.database_url) as session:
            req = session.get(RebuildRequest, request_id)
            if req is None:
                raise HTTPException(404, "unknown request")
            return _serialise(req)

    @app.get("/queue")
    def queue() -> list[dict[str, Any]]:
        with session_scope(settings.database_url) as session:
            rows = session.scalars(
                select(RebuildRequest).order_by(RebuildRequest.requested_at.desc()).limit(50)
            ).all()
            return [_serialise(r) for r in rows]

    return app


app = None


def get_app() -> FastAPI:
    global app
    if app is None:
        app = create_app()
    return app
