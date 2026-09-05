"""JSON shapes shared by the routes."""

from __future__ import annotations

from typing import Any

from intel.models import (
    AuditStatus,
    Brief,
    BriefActionLog,
    Candidate,
    Claim,
    Verification,
    VerificationResult,
    VerificationStatus,
)
from intel.score import tier_for


def latest_verification(claim: Claim) -> Verification | None:
    if not claim.verifications:
        return None
    return sorted(claim.verifications, key=lambda v: (v.checked_at, v.id))[-1]


def md_eligible(brief: Brief) -> bool:
    return brief.verification_status == VerificationStatus.verified and brief.audit_status in (
        AuditStatus.passed,
        AuditStatus.pass_after_retry,
    )


def brief_label(brief: Brief) -> str:
    d = brief.brief_data or {}
    if brief.historical and d.get("historical_label"):
        return str(d["historical_label"])
    if brief.historical:
        return "historical"
    return f"N° {brief.brief_number:03d}"


def verification_badge(brief: Brief) -> str:
    return {
        VerificationStatus.verified: "Verified",
        VerificationStatus.needs_review: "Review",
        VerificationStatus.blocked: "Blocked",
        VerificationStatus.pending: "Pending",
    }[brief.verification_status]


def brief_card(brief: Brief) -> dict[str, Any]:
    d = brief.brief_data or {}
    cand: Candidate = brief.candidate
    score = d.get("score", cand.score_total)
    return {
        "number": brief.brief_number,
        "label": brief_label(brief),
        "date": brief.run_date.isoformat(),
        "company": d.get("company") or cand.company_raw,
        "score": score,
        "tier": tier_for(int(score)) if score is not None else None,
        "series": d.get("series_label") or (cand.series.value if cand.series else None),
        "team": d.get("team_label") or cand.recommended_team,
        "person": d.get("decision_maker_name"),
        "role": d.get("decision_maker_role"),
        "take": d.get("deck"),
        "verification": brief.verification_status.value,
        "badge": verification_badge(brief),
        "audit": brief.audit_status.value,
        "track": 2 if cand.track == 2 else 1,
        "track_label": "Alumni Intelligence" if cand.track == 2 else "",
        "historical": brief.historical,
        "has_pdf": bool(brief.pdf_path),
        "md_eligible": md_eligible(brief),
        "industry": d.get("industry_meta"),
    }


def claim_row(claim: Claim) -> dict[str, Any]:
    v = latest_verification(claim)
    return {
        "id": claim.id,
        "text": claim.text,
        "section": claim.section,
        "type": claim.claim_type.value,
        "load_bearing": claim.load_bearing,
        "cited_source_url": claim.cited_source_url,
        "status": v.status.value if v else "unverified",
        "method": v.method.value if v else None,
        "evidence_url": v.evidence_url if v else None,
        "excerpt": v.evidence_excerpt if v else None,
        "notes": v.notes if v else None,
        "checked_at": v.checked_at.isoformat() if v and v.checked_at else None,
        "model": v.model if v else None,
    }


def verification_panel(brief: Brief) -> dict[str, Any]:
    rows = [claim_row(c) for c in sorted(brief.claims, key=lambda c: (c.position, c.id))]
    lb = [r for r in rows if r["load_bearing"]]
    verified = sum(1 for r in lb if r["status"] == VerificationResult.verified.value)
    return {
        "status": brief.verification_status.value,
        "badge": verification_badge(brief),
        "summary": f"{verified} of {len(lb)} load-bearing claims verified",
        "load_bearing_total": len(lb),
        "load_bearing_verified": verified,
        "claims": rows,
    }


def action_row(a: BriefActionLog) -> dict[str, Any]:
    return {
        "id": a.id,
        "action": a.action.value,
        "by": a.by,
        "at": a.at.isoformat(),
        "note": a.note,
    }


def brief_detail(brief: Brief) -> dict[str, Any]:
    cand: Candidate = brief.candidate
    return {
        **brief_card(brief),
        "brief_data": brief.brief_data,
        "mode": brief.mode.value if brief.mode else None,
        "page_count": brief.page_count,
        "pdf_url": f"/api/briefs/{brief.brief_number}/pdf" if brief.pdf_path else None,
        "page_url": f"/api/briefs/{brief.brief_number}/page" if brief.web_html_path else None,
        "verification_panel": verification_panel(brief),
        "score_composition": {
            "cells": (brief.brief_data or {}).get("score_cells", []),
            "breakdown": cand.score_breakdown,
            "gate_results": cand.gate_results,
            "alumni_boost": cand.alumni_boost,
        },
        "audit_result": {
            "status": brief.audit_status.value,
            "attempts": brief.audit_attempts,
            "violations": brief.audit_violations or [],
        },
        "candidate": {
            "id": cand.id,
            "decision": cand.decision.value,
            "reason": cand.decision_reason,
            "trigger": cand.trigger_reason_raw,
            "trigger_date": cand.trigger_date.isoformat() if cand.trigger_date else None,
            "source_url": cand.source_url,
            "resurfaced": cand.resurfaced,
        },
        "actions": [action_row(a) for a in sorted(brief.actions, key=lambda a: a.at)],
    }
