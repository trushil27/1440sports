"""People panel (build brief §8): decision-maker card with verified role, provider contact
details (only when a licensed provider returned them), alumni tag, re-verify, role drift."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from intel import contacts as contacts_mod
from intel import verify
from intel.config import get_settings
from intel.models import Alumni, Brief, Claim, ClaimType, Contact, Verification, VerificationResult
from intel.normalise import company_norm
from intel_api.auth import SessionUser, current_user, get_db
from intel_api.serializers import latest_verification

router = APIRouter(prefix="/api/briefs", tags=["people"])


def _brief(db: Session, number: int) -> Brief:
    brief = db.scalar(
        select(Brief)
        .options(selectinload(Brief.candidate), selectinload(Brief.claims))
        .where(Brief.brief_number == number)
    )
    if brief is None:
        raise HTTPException(status_code=404, detail="brief not found")
    return brief


def _role_claim(brief: Brief) -> Claim | None:
    for c in brief.claims:
        if c.claim_type == ClaimType.person_role and c.section == "decision_maker":
            return c
    return None


def role_status(brief: Brief) -> dict[str, Any]:
    claim = _role_claim(brief)
    v = latest_verification(claim) if claim else None
    return {
        "claim_id": claim.id if claim else None,
        "status": v.status.value if v else "unverified",
        "verified_on": v.checked_at.date().isoformat()
        if v and v.status == VerificationResult.verified
        else None,
        "source": v.evidence_url if v else (claim.cited_source_url if claim else None),
        "excerpt": v.evidence_excerpt if v else None,
        "drifted": bool(v and v.status == VerificationResult.contradicted),
    }


def people_card(db: Session, brief: Brief) -> dict[str, Any]:
    d = brief.brief_data or {}
    company = d.get("company") or brief.candidate.company_raw
    name = d.get("decision_maker_name")
    title = d.get("decision_maker_role")
    role = role_status(brief)
    contact: Contact | None = contacts_mod.find_contact(db, name, company) if name else None
    alumni = db.scalar(
        select(Alumni).where(Alumni.company_norm == company_norm(company), Alumni.active.is_(True))
    )
    drifted = role["drifted"] or bool(
        contact and contact.role_verification_id and _contradicted(db, contact)
    )
    outreach_enabled = (
        role["status"] == "verified" and not drifted and not (contact and contact.opted_out)
    )
    return {
        "name": name,
        "title": title,
        "company": company,
        "bio": d.get("decision_maker_bio"),
        "role": {**role, "drifted": drifted},
        "contact": (
            {
                "linkedin_url": contact.linkedin_url,
                "email": contact.email,
                "phone": contact.phone,
                "provider": contact.source_provider,
                "retrieved_at": contact.retrieved_at.isoformat() if contact.retrieved_at else None,
                "opted_out": contact.opted_out,
                "consent_basis": contact.consent_basis,
            }
            if contact
            else None
        ),
        "contact_provider": get_settings().__dict__.get("contact_provider", None) or "none",
        "alumni": (
            {
                "name": alumni.name,
                "tier": alumni.tier.value,
                "prior_deal": alumni.deal_involvement,
                "boost": alumni.boost_applied,
            }
            if alumni and name and alumni.name.lower() == name.lower()
            else None
        ),
        "co_decision_makers": [],
        "outreach_enabled": outreach_enabled,
        "warning": "Role check failed after the brief was issued — re-verify before outreach."
        if drifted
        else None,
    }


def _contradicted(db: Session, contact: Contact) -> bool:
    v = db.get(Verification, contact.role_verification_id) if contact.role_verification_id else None
    return bool(v and v.status == VerificationResult.contradicted)


@router.get("/{number}/people")
def get_people(
    number: int, db: Session = Depends(get_db), _: SessionUser = Depends(current_user)
) -> dict[str, Any]:
    return people_card(db, _brief(db, number))


@router.post("/{number}/people/reverify")
def reverify_role(
    number: int, db: Session = Depends(get_db), _: SessionUser = Depends(current_user)
) -> dict[str, Any]:
    """Re-run the role check now (§8 'Re-verify'). A contradiction disables outreach."""
    brief = _brief(db, number)
    claim = _role_claim(brief)
    if claim is None:
        raise HTTPException(status_code=409, detail="this brief has no decision-maker claim")
    verifier = getattr(db, "_verifier_override", None) or verify.default_verifier(get_settings())
    draft = verify.ClaimDraft(
        claim.text, claim.section, claim.claim_type, claim.load_bearing, claim.cited_source_url
    )
    company = (brief.brief_data or {}).get("company") or brief.candidate.company_raw
    v = verifier.verify(draft, company)
    v.claim_id = claim.id
    v.checked_at = dt.datetime.now(dt.UTC)
    db.add(v)
    db.flush()
    name = (brief.brief_data or {}).get("decision_maker_name")
    contact = contacts_mod.find_contact(db, name, company) if name else None
    if contact is not None:
        contact.role_verified_at = v.checked_at
        contact.role_verification_id = v.id
        db.flush()
    db.refresh(brief)
    return people_card(db, brief)


@router.post("/{number}/people/lookup")
def lookup_contact(
    number: int, db: Session = Depends(get_db), _: SessionUser = Depends(current_user)
) -> dict[str, Any]:
    """Fetch contact details from the licensed provider (none approved yet → 409)."""
    brief = _brief(db, number)
    settings = get_settings()
    provider = contacts_mod.provider_for(getattr(settings, "contact_provider", None))
    name = (brief.brief_data or {}).get("decision_maker_name")
    company = (brief.brief_data or {}).get("company") or brief.candidate.company_raw
    if not name:
        raise HTTPException(status_code=409, detail="no decision-maker on this brief")
    rec = provider.lookup(name, company)
    if rec is None:
        raise HTTPException(
            status_code=409,
            detail="no contact provider approved yet (§11.7) — nothing fetched, nothing guessed",
        )
    contacts_mod.store_contact(db, rec, company)
    return people_card(db, brief)
