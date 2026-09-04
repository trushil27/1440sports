"""Operator pages (build brief §8 `/ops`): runs, candidate reasons, review queue, editable
blocklist / alumni / sponsors, provider usage, config. Operator role only."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from intel.config import get_settings
from intel.models import (
    Alumni,
    AuditStatus,
    Blocklist,
    BlocklistStatus,
    Brief,
    Contact,
    Run,
    Series,
    Sponsor,
    SponsorLevel,
    SponsorStatus,
    VerificationStatus,
)
from intel.normalise import company_norm
from intel.send import candidate_reasons
from intel_api.auth import SessionUser, get_db, require_operator
from intel_api.serializers import brief_card

router = APIRouter(prefix="/api/ops", tags=["ops"], dependencies=[Depends(require_operator)])


@router.get("/runs")
def runs(
    db: Session = Depends(get_db), limit: int = Query(default=30, le=200)
) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(Run)
        .options(selectinload(Run.candidates))
        .order_by(Run.run_date.desc(), Run.attempt.desc())
        .limit(limit)
    ).all()
    return [
        {
            "id": r.id,
            "date": r.run_date.isoformat(),
            "attempt": r.attempt,
            "status": r.status.value,
            "mode": r.execution_mode.value,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "models": r.model_versions,
            "candidates": len(r.candidates),
            "summary": r.summary,
            "error": r.error,
        }
        for r in rows
    ]


@router.get("/runs/{run_id}/candidates")
def run_candidates(run_id: int, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return candidate_reasons(run)


@router.get("/queue")
def review_queue(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Blocked / needs-review / audit-failed briefs (non-historical), newest first."""
    rows = db.scalars(
        select(Brief)
        .options(selectinload(Brief.candidate), selectinload(Brief.claims))
        .where(
            Brief.historical.is_(False),
            (
                Brief.verification_status.in_(
                    [VerificationStatus.needs_review, VerificationStatus.blocked]
                )
            )
            | (Brief.audit_status.in_([AuditStatus.failed, AuditStatus.pending])),
        )
        .order_by(Brief.run_date.desc(), Brief.id.desc())
    ).all()
    return [brief_card(b) for b in rows]


# --- blocklist -----------------------------------------------------------------------------


class BlocklistBody(BaseModel):
    company: str
    status: str = "active"
    reason: str | None = None
    cooling_until: dt.date | None = None
    notes: str | None = None


def _bl(row: Blocklist) -> dict[str, Any]:
    return {
        "id": row.id,
        "company": row.company_raw,
        "company_norm": row.company_norm,
        "status": row.status.value,
        "reason": row.reason,
        "added_at": row.added_at.isoformat(),
        "cooling_until": row.cooling_until.isoformat() if row.cooling_until else None,
        "added_by": row.added_by,
        "notes": row.notes,
    }


@router.get("/blocklist")
def blocklist(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return [
        _bl(r)
        for r in db.scalars(
            select(Blocklist).order_by(Blocklist.status, Blocklist.company_raw)
        ).all()
    ]


@router.post("/blocklist", status_code=201)
def add_blocklist(
    body: BlocklistBody,
    db: Session = Depends(get_db),
    user: SessionUser = Depends(require_operator),
) -> dict:
    norm = company_norm(body.company)
    row = db.scalar(select(Blocklist).where(Blocklist.company_norm == norm))
    if row is None:
        row = Blocklist(
            company_raw=body.company,
            company_norm=norm,
            status=BlocklistStatus(body.status),
            added_at=dt.date.today(),
        )
        db.add(row)
    row.status = BlocklistStatus(body.status)
    row.reason, row.cooling_until, row.notes, row.added_by = (
        body.reason,
        body.cooling_until,
        body.notes,
        user.email,
    )
    db.flush()
    return _bl(row)


@router.delete("/blocklist/{row_id}", status_code=204)
def delete_blocklist(row_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(Blocklist, row_id)
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    db.delete(row)
    db.flush()


# --- alumni --------------------------------------------------------------------------------


class AlumniBody(BaseModel):
    current_role: str | None = None
    current_company: str | None = None
    move_date: dt.date | None = None
    tier: str | None = None
    outreach_status: str | None = None
    active: bool | None = None
    notes: str | None = None


def _alumni(a: Alumni) -> dict[str, Any]:
    return {
        "id": a.id,
        "name": a.name,
        "previous_role": a.previous_role,
        "previous_company": a.previous_company,
        "deal_involvement": a.deal_involvement,
        "current_role": a.current_role,
        "current_company": a.current_company,
        "move_date": a.move_date.isoformat() if a.move_date else None,
        "tier": a.tier.value,
        "boost_applied": a.boost_applied,
        "final_score": a.final_score,
        "complications": a.complications,
        "outreach_status": a.outreach_status,
        "active": a.active,
        "notes": a.notes,
    }


@router.get("/alumni")
def alumni(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return [_alumni(a) for a in db.scalars(select(Alumni).order_by(Alumni.id)).all()]


@router.put("/alumni/{alumni_id}")
def update_alumni(
    alumni_id: int, body: AlumniBody, db: Session = Depends(get_db)
) -> dict[str, Any]:
    from intel.models import AlumniTier

    a = db.get(Alumni, alumni_id)
    if a is None:
        raise HTTPException(status_code=404, detail="not found")
    for field_name, value in body.model_dump(exclude_none=True).items():
        if field_name == "tier":
            a.tier = AlumniTier(value)
        else:
            setattr(a, field_name, value)
    if body.current_company:
        a.company_norm = company_norm(body.current_company)
    db.flush()
    return _alumni(a)


# --- sponsors ------------------------------------------------------------------------------


class SponsorBody(BaseModel):
    series: str
    level: str
    team: str | None = None
    brand: str
    category: str | None = None
    status: str = "active"
    season: str | None = None
    notes: str | None = None
    source: str | None = None


def _sponsor(s: Sponsor) -> dict[str, Any]:
    return {
        "id": s.id,
        "series": s.series.value,
        "level": s.level.value,
        "team": s.team,
        "brand": s.brand,
        "category": s.category,
        "status": s.status.value,
        "season": s.season,
        "notes": s.notes,
        "source": s.source,
        "verified_at": s.verified_at.isoformat() if s.verified_at else None,
    }


@router.get("/sponsors")
def sponsors(
    db: Session = Depends(get_db),
    series: str | None = None,
    team: str | None = None,
    q: str | None = None,
    limit: int = Query(default=200, le=1000),
) -> list[dict[str, Any]]:
    stmt = select(Sponsor)
    if series:
        stmt = stmt.where(Sponsor.series == Series(series.upper()))
    if team:
        stmt = stmt.where(Sponsor.team.ilike(f"%{team}%"))
    if q:
        stmt = stmt.where(Sponsor.brand.ilike(f"%{q}%") | Sponsor.category.ilike(f"%{q}%"))
    stmt = stmt.order_by(Sponsor.series, Sponsor.team, Sponsor.brand).limit(limit)
    return [_sponsor(s) for s in db.scalars(stmt).all()]


@router.post("/sponsors", status_code=201)
def add_sponsor(body: SponsorBody, db: Session = Depends(get_db)) -> dict[str, Any]:
    s = Sponsor(
        series=Series(body.series.upper()),
        level=SponsorLevel(body.level),
        team=body.team,
        brand=body.brand,
        brand_norm=company_norm(body.brand),
        category=body.category,
        status=SponsorStatus(body.status),
        season=body.season,
        notes=body.notes,
        source=body.source or "added in the app",
        verified_at=dt.date.today(),
    )
    db.add(s)
    db.flush()
    return _sponsor(s)


@router.put("/sponsors/{sponsor_id}")
def update_sponsor(
    sponsor_id: int, body: SponsorBody, db: Session = Depends(get_db)
) -> dict[str, Any]:
    s = db.get(Sponsor, sponsor_id)
    if s is None:
        raise HTTPException(status_code=404, detail="not found")
    s.series, s.level = Series(body.series.upper()), SponsorLevel(body.level)
    s.team, s.brand, s.brand_norm = body.team, body.brand, company_norm(body.brand)
    s.category, s.status, s.season, s.notes = (
        body.category,
        SponsorStatus(body.status),
        body.season,
        body.notes,
    )
    if body.source:
        s.source = body.source
    s.verified_at = dt.date.today()
    db.flush()
    return _sponsor(s)


# --- provider usage + config ------------------------------------------------------------------


@router.get("/provider-usage")
def provider_usage(db: Session = Depends(get_db)) -> dict[str, Any]:
    rows = db.execute(
        select(Contact.source_provider, func.count(), func.max(Contact.retrieved_at)).group_by(
            Contact.source_provider
        )
    ).all()
    return {
        "providers": [
            {
                "provider": p or "none",
                "records": n,
                "last_retrieved": (t.isoformat() if t else None),
            }
            for p, n, t in rows
        ],
        "note": (
            "Cost is reported by the provider's own dashboard; records here are what the app "
            "stored (§11.7)."
        ),
    }


@router.get("/config")
def config() -> dict[str, Any]:
    s = get_settings()
    return {
        "execution_mode": s.execution_mode,
        "models": {"scan": s.scan_model, "writer": s.writer_model, "verify": s.verify_model},
        "md_threshold": s.md_threshold,
        "freshness_days_track1": s.freshness_days_track1,
        "freshness_days_alumni": s.freshness_days_alumni,
        "dedup_window_days": s.dedup_window_days,
        "max_verification_attempts": s.max_verification_attempts,
        "timezone": s.timezone,
        "anthropic_key_configured": bool(s.anthropic_api_key),
        "graph_configured": bool(s.graph_tenant_id and s.graph_client_id and s.graph_sender),
        "md_email_configured": bool(s.md_email),
    }
