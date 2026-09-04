"""Today, history/search, brief detail, actions, highlights (build brief §8)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session, selectinload

from intel.models import (
    Blocklist,
    BlocklistStatus,
    Brief,
    BriefAction,
    BriefActionLog,
    Candidate,
    Highlight,
    Run,
    VerificationStatus,
)
from intel_api.auth import SessionUser, current_user, get_db
from intel_api.serializers import brief_card, brief_detail

router = APIRouter(prefix="/api", tags=["briefs"])

_LOAD = (selectinload(Brief.candidate), selectinload(Brief.claims), selectinload(Brief.actions))


def _brief_or_404(db: Session, number: int) -> Brief:
    brief = db.scalar(select(Brief).options(*_LOAD).where(Brief.brief_number == number))
    if brief is None:
        raise HTTPException(status_code=404, detail="brief not found")
    return brief


@router.get("/today")
def today(db: Session = Depends(get_db), _: SessionUser = Depends(current_user)) -> dict[str, Any]:
    """The most recent issued (non-blocked, non-historical) brief + its highlights + run context."""
    brief = db.scalar(
        select(Brief)
        .options(*_LOAD)
        .where(Brief.verification_status != VerificationStatus.blocked, Brief.historical.is_(False))
        .order_by(Brief.run_date.desc(), Brief.id.desc())
    )
    if brief is None:
        latest_run = db.scalar(select(Run).order_by(Run.run_date.desc(), Run.attempt.desc()))
        return {
            "brief": None,
            "message": "No verified signal yet.",
            "last_run": {"date": latest_run.run_date.isoformat(), "status": latest_run.status.value}
            if latest_run
            else None,
        }
    run = db.get(Run, brief.candidate.run_id)
    others = db.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.run_id == run.id, Candidate.id != brief.candidate_id)
    )
    highlights = db.scalars(
        select(Highlight).where(Highlight.brief_id == brief.id).order_by(Highlight.id)
    ).all()
    return {
        "brief": brief_card(brief),
        "highlights": [{"text": h.text, "claim_ids": h.claim_ids} for h in highlights],
        "run": {
            "id": run.id,
            "date": run.run_date.isoformat(),
            "status": run.status.value,
            "others_not_chosen": others,
        },
        "is_today": brief.run_date == dt.date.today(),
    }


@router.get("/briefs")
def list_briefs(
    db: Session = Depends(get_db),
    _: SessionUser = Depends(current_user),
    q: str | None = None,
    series: str | None = None,
    tier: str | None = None,
    track: int | None = None,
    status: str | None = None,
    date_from: dt.date | None = Query(default=None, alias="from"),
    date_to: dt.date | None = Query(default=None, alias="to"),
    include_historical: bool = True,
    include_blocked: bool = False,
    cursor: str | None = None,
    limit: int = Query(default=30, le=100),
) -> dict[str, Any]:
    """History (newest first) with search + filters. ``cursor`` = "<date>|<id>" of the last row."""
    stmt = select(Brief).options(*_LOAD).join(Candidate, Candidate.id == Brief.candidate_id)
    if not include_blocked:
        stmt = stmt.where(Brief.verification_status != VerificationStatus.blocked)
    if not include_historical:
        stmt = stmt.where(Brief.historical.is_(False))
    if status:
        stmt = stmt.where(Brief.verification_status == VerificationStatus(status))
    if track in (1, 2):
        stmt = stmt.where(Candidate.track == track)
    if series:
        stmt = stmt.where(
            or_(
                cast(Brief.brief_data["series_label"].astext, String).ilike(series),
                cast(Candidate.series, String) == series.upper(),
            )
        )
    if date_from:
        stmt = stmt.where(Brief.run_date >= date_from)
    if date_to:
        stmt = stmt.where(Brief.run_date <= date_to)
    if q:
        needle = f"%{q}%"
        bd = Brief.brief_data
        stmt = stmt.where(
            or_(
                Candidate.company_raw.ilike(needle),
                Candidate.recommended_team.ilike(needle),
                Candidate.trigger_reason_raw.ilike(needle),
                bd["company"].astext.ilike(needle),
                bd["decision_maker_name"].astext.ilike(needle),
                bd["team_label"].astext.ilike(needle),
                bd["industry_meta"].astext.ilike(needle),
                bd["deck"].astext.ilike(needle),
                bd["the_case_p1"].astext.ilike(needle),
            )
        )
    if cursor:
        try:
            c_date, c_id = cursor.split("|")
            cd, ci = dt.date.fromisoformat(c_date), int(c_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="bad cursor") from exc
        stmt = stmt.where(or_(Brief.run_date < cd, (Brief.run_date == cd) & (Brief.id < ci)))
    stmt = stmt.order_by(Brief.run_date.desc(), Brief.id.desc()).limit(limit + 1)
    rows = db.scalars(stmt).all()
    cards = [brief_card(b) for b in rows[:limit]]
    if tier:
        cards = [c for c in cards if (c["tier"] or "").upper() == tier.upper()]
    next_cursor = (
        f"{rows[limit - 1].run_date.isoformat()}|{rows[limit - 1].id}"
        if len(rows) > limit
        else None
    )
    return {"items": cards, "next_cursor": next_cursor}


@router.get("/briefs/{number}")
def get_brief(
    number: int, db: Session = Depends(get_db), _: SessionUser = Depends(current_user)
) -> dict[str, Any]:
    return brief_detail(_brief_or_404(db, number))


@router.get("/briefs/{number}/pdf")
def get_pdf(
    number: int, db: Session = Depends(get_db), _: SessionUser = Depends(current_user)
) -> FileResponse:
    brief = _brief_or_404(db, number)
    if not brief.pdf_path or not Path(brief.pdf_path).exists():
        raise HTTPException(status_code=404, detail="no PDF stored for this brief")
    company = (brief.brief_data or {}).get("company", "brief").replace(" ", "_")
    return FileResponse(
        brief.pdf_path,
        media_type="application/pdf",
        filename=f"1440_Intelligence_Brief_{company}.pdf",
    )


@router.get("/briefs/{number}/highlights")
def get_highlights(
    number: int, db: Session = Depends(get_db), _: SessionUser = Depends(current_user)
) -> list[dict]:
    brief = _brief_or_404(db, number)
    rows = db.scalars(
        select(Highlight).where(Highlight.brief_id == brief.id).order_by(Highlight.id)
    ).all()
    return [
        {"text": h.text, "claim_ids": h.claim_ids, "generated_at": h.generated_at.isoformat()}
        for h in rows
    ]


class ActionBody(BaseModel):
    action: str  # pursuing | snoozed | killed | contacted
    note: str | None = None


@router.post("/briefs/{number}/actions")
def post_action(
    number: int,
    body: ActionBody,
    db: Session = Depends(get_db),
    user: SessionUser = Depends(current_user),
) -> dict[str, Any]:
    """Log the action; Snooze (30 d) and Kill also write the cooling list (pipeline respects it)."""
    brief = _brief_or_404(db, number)
    try:
        action = BriefAction(body.action)
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail="action must be pursuing|snoozed|killed|contacted"
        ) from exc
    cand = brief.candidate
    now = dt.datetime.now(dt.UTC)
    db.add(BriefActionLog(brief_id=brief.id, action=action, by=user.email, at=now, note=body.note))
    if action in (BriefAction.snoozed, BriefAction.killed):
        row = db.scalar(select(Blocklist).where(Blocklist.company_norm == cand.company_norm))
        if row is None:
            row = Blocklist(
                company_raw=cand.company_raw,
                company_norm=cand.company_norm,
                status=BlocklistStatus.cooling,
            )
            db.add(row)
        if action == BriefAction.snoozed:
            row.status = BlocklistStatus.cooling
            row.cooling_until = (now + dt.timedelta(days=30)).date()
            row.reason = f"snoozed 30 days in the app by {user.email}"
        else:
            row.status = BlocklistStatus.closed_lost
            row.cooling_until = None  # indefinite until an operator lifts it
            row.reason = f"killed in the app by {user.email}"
        row.added_by = user.email
        row.notes = body.note
    if action == BriefAction.pursuing:
        # Pursuing = an active pursuit: never re-pitch cold while it is open.
        row = db.scalar(select(Blocklist).where(Blocklist.company_norm == cand.company_norm))
        if row is None:
            row = Blocklist(
                company_raw=cand.company_raw,
                company_norm=cand.company_norm,
                status=BlocklistStatus.active,
            )
            db.add(row)
        row.status = BlocklistStatus.active
        row.cooling_until = None
        row.reason = f"pursuing (set in the app by {user.email})"
        row.added_by = user.email
    db.flush()
    db.refresh(brief)
    return {"actions": brief_detail(brief)["actions"]}
