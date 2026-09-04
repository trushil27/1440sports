"""Draft outreach → Copy · Create Outlook draft (never sends) · Mark contacted (build brief §8)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from intel import outreach as outreach_mod
from intel import send as send_mod
from intel.config import get_settings
from intel.models import Brief, BriefAction, BriefActionLog, OutreachDraft
from intel_api.auth import SessionUser, current_user, get_db
from intel_api.routes.people import people_card

router = APIRouter(prefix="/api", tags=["outreach"])


def _brief(db: Session, number: int) -> Brief:
    brief = db.scalar(
        select(Brief)
        .options(selectinload(Brief.candidate), selectinload(Brief.claims))
        .where(Brief.brief_number == number)
    )
    if brief is None:
        raise HTTPException(status_code=404, detail="brief not found")
    return brief


def _draft(db: Session, row: OutreachDraft) -> dict[str, Any]:
    brief = db.get(Brief, row.brief_id)
    return {
        "id": row.id,
        "brief_number": brief.brief_number if brief else None,
        "subject": row.subject,
        "body": row.body,
        "created_at": row.created_at.isoformat(),
        "outlook_draft_id": row.outlook_draft_id,
    }


@router.post("/briefs/{number}/outreach", status_code=201)
def create_draft(
    number: int,
    request: Request,
    db: Session = Depends(get_db),
    user: SessionUser = Depends(current_user),
) -> dict[str, Any]:
    brief = _brief(db, number)
    card = people_card(db, brief)
    if not card["outreach_enabled"]:
        raise HTTPException(
            status_code=409, detail=card["warning"] or "decision-maker role is not verified"
        )
    writer = getattr(request.app.state, "outreach_writer", None)
    try:
        draft = outreach_mod.compose(brief, writer)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    row = OutreachDraft(brief_id=brief.id, subject=draft.subject, body=draft.body)
    db.add(row)
    db.flush()
    db.refresh(row)
    return {**_draft(db, row), "claim_ids": draft.claim_ids}


@router.get("/briefs/{number}/outreach")
def list_drafts(
    number: int, db: Session = Depends(get_db), _: SessionUser = Depends(current_user)
) -> list[dict]:
    brief = _brief(db, number)
    rows = db.scalars(
        select(OutreachDraft)
        .where(OutreachDraft.brief_id == brief.id)
        .order_by(OutreachDraft.id.desc())
    ).all()
    return [_draft(db, r) for r in rows]


@router.post("/outreach/{draft_id}/outlook-draft")
def create_outlook_draft(
    draft_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: SessionUser = Depends(current_user),
) -> dict[str, Any]:
    """Creates a Draft in the sender's mailbox via Graph. Never calls sendMail (§9.12)."""
    row = db.get(OutreachDraft, draft_id)
    if row is None:
        raise HTTPException(status_code=404, detail="draft not found")
    mailer = getattr(request.app.state, "mailer", None) or send_mod.mailer_for(get_settings())
    brief = db.get(Brief, row.brief_id)
    card = people_card(db, _brief(db, brief.brief_number))
    to = [card["contact"]["email"]] if card.get("contact") and card["contact"].get("email") else []
    row.outlook_draft_id = mailer.create_draft(
        send_mod.Outgoing(to=to, subject=row.subject, body_text=row.body)
    )
    db.flush()
    return _draft(db, row)


@router.post("/outreach/{draft_id}/contacted")
def mark_contacted(
    draft_id: int, db: Session = Depends(get_db), user: SessionUser = Depends(current_user)
) -> dict[str, Any]:
    row = db.get(OutreachDraft, draft_id)
    if row is None:
        raise HTTPException(status_code=404, detail="draft not found")
    db.add(
        BriefActionLog(
            brief_id=row.brief_id,
            action=BriefAction.contacted,
            by=user.email,
            at=dt.datetime.now(dt.UTC),
            note=f"outreach draft {row.id}",
        )
    )
    db.flush()
    return {"ok": True}
