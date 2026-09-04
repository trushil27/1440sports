"""Render the 2-page brief in the June-2026 production format (build brief §3.4, §6.8).

Ported from this repo's ``engine/generate_brief.py`` + ``engine/templates/brief.html.j2``
(the builder that produced Ramp N° 007 / 017). Three things are computed here and never
written by a model:
- PROOF POINTS and SOURCES come from the claims ledger; the header says "every figure
  verified" only when every shown figure is, otherwise figures carry † and the footer
  reads VERIFY BEFORE CIRCULATION;
- the decision-maker VERIFIED tag comes from the person/role claim's verification;
- GRID FIT rows (PRIME LANE / OPEN / CROWDED / CONFLICT per team) come from the
  ``sponsors`` table plus the team profiles mirrored from data/teams.json.

Strictly two pages: ``render_pdf`` raises on overflow.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.brief_data import BriefData, GridRow, ProofPoint, WrittenBrief, strip_markup
from intel.models import (
    Brief,
    Claim,
    ClaimType,
    Series,
    Sponsor,
    SponsorStatus,
    VerificationResult,
    VerificationStatus,
)
from intel.score import tier_for

HERE = Path(__file__).parent
ASSETS = HERE / "assets"
TEMPLATES = HERE / "templates"
LOGO = ASSETS / "1440_logo.png"

MODE_CAPTIONS = {
    "A": "tech in the car / championship",
    "B": "tech serves the team operation",
    "C": "audience / brand pipeline",
}

_STOP = {
    "the",
    "and",
    "of",
    "for",
    "with",
    "tech",
    "technology",
    "technologies",
    "enterprise",
    "software",
    "platform",
    "management",
    "services",
    "solutions",
    "company",
    "inc",
    "group",
    "global",
    "digital",
    "systems",
    "system",
    "ai",
    "data",
    "cloud",
}
_MONEY = re.compile(
    r"(?:[$€£]\s?\d[\d.,]*\s?(?:[MBK]|bn|million|billion|m|b)?\+?)|(?:\d+(?:\.\d+)?%)|(?:\b\d[\d,]*\+)",
    re.IGNORECASE,
)


class PageOverflow(RuntimeError):
    pass


# --- value-section mode (production_roadmap §2.1.8) --------------------------------------

_MODE_B_INDUSTRY = re.compile(r"fintech|payment|insur|treasury|banking|spend|finance", re.I)
_MODE_C_INDUSTRY = re.compile(r"consumer|lifestyle|media|b2c|retail|fitness|wearable|apparel", re.I)


def value_mode_for(ops_fit: int | None, industry_meta: str | None) -> str:
    """MODE A operational (OF ≥ 14); MODE B back-office (OF 11-13 or fintech/payments/
    insurance); MODE C audience/brand pipeline (OF ≤ 10 + consumer/lifestyle/media/B2C)."""
    industry = industry_meta or ""
    of = ops_fit if ops_fit is not None else 0
    if _MODE_B_INDUSTRY.search(industry) and of < 14:
        return "B"
    if of >= 14:
        return "A"
    if of >= 11:
        return "B"
    if _MODE_C_INDUSTRY.search(industry):
        return "C"
    return "B"


# --- ledger-derived panels -----------------------------------------------------------------


def _verified(claim: Claim) -> bool:
    return any(v.status == VerificationResult.verified for v in claim.verifications)


def proof_points_from_ledger(claims: list[Claim], limit: int = 6) -> list[ProofPoint]:
    """Numeric / dated facts from the ledger as PROOF POINT cards, verified ones first."""
    pts: list[ProofPoint] = []
    for c in claims:
        if c.claim_type not in (ClaimType.funding, ClaimType.revenue, ClaimType.date):
            continue
        text = strip_markup(c.text)
        m = _MONEY.search(text)
        if not m:
            continue
        value = m.group(0).strip()
        fact = text if len(text) <= 110 else text[:107].rstrip() + "…"
        pts.append(
            ProofPoint(
                value=value,
                fact=fact,
                source_url=c.cited_source_url,
                verified=_verified(c),
                claim_id=c.id,
            )
        )
    pts.sort(key=lambda p: not p.verified)
    return pts[:limit]


def sources_from_ledger(claims: list[Claim], limit: int = 8) -> list[str]:
    urls: list[str] = []
    for c in claims:
        for v in c.verifications:
            if v.status == VerificationResult.verified and v.evidence_url:
                urls.append(v.evidence_url)
    for c in claims:
        if c.cited_source_url:
            urls.append(c.cited_source_url)
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        u = u.strip()
        if u and u not in seen and u.startswith("http"):
            seen.add(u)
            out.append(u)
    return out[:limit]


def decision_maker_verified(claims: list[Claim]) -> bool:
    for c in claims:
        if c.claim_type == ClaimType.person_role and c.section == "decision_maker":
            return _verified(c)
    return False


def ledger_counts(claims: list[Claim]) -> tuple[int, int]:
    lb = [c for c in claims if c.load_bearing]
    return sum(1 for c in lb if _verified(c)), len(lb)


# --- GRID FIT from the sponsors table -----------------------------------------------------


def _tokens(text: str | None) -> set[str]:
    return {
        t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if len(t) > 2 and t not in _STOP
    }


def _team_key(name: str | None) -> set[str]:
    return _tokens(name) - {"team", "racing", "formula"}


def load_team_profiles() -> list[dict]:
    try:
        from intel.seed import load_team_profiles as _load

        return _load()
    except Exception:  # pragma: no cover - profiles are optional
        path = HERE / "seeds" / "team_profiles.json"
        return json.loads(path.read_text()) if path.exists() else []


def build_gridfit(
    session: Session,
    series: str,
    recommended_team: str,
    lane_tokens: set[str],
    domain_tokens: set[str],
    max_rows: int = 4,
) -> tuple[list[GridRow], str]:
    """OPEN / CROWDED / CONFLICT per team from ``sponsors`` (+ team profile openings)."""
    live = (SponsorStatus.active, SponsorStatus.joined)
    rows = session.scalars(
        select(Sponsor).where(
            Sponsor.series == Series(series), Sponsor.status.in_(live), Sponsor.team.isnot(None)
        )
    ).all()
    by_team: dict[str, list[Sponsor]] = {}
    for r in rows:
        by_team.setdefault(r.team or "", []).append(r)
    profiles = {p["team"]: p for p in load_team_profiles() if p.get("series") == series}
    rec_key = _team_key(recommended_team)
    categorised = sum(1 for r in rows if r.category)
    out: list[tuple[int, GridRow]] = []
    for team, partners in by_team.items():
        conflicts: list[str] = []
        crowded: list[str] = []
        for p in partners:
            blob = " ".join(filter(None, [p.category, p.notes])).lower()
            ptoks = _tokens(blob)
            if not ptoks:
                continue
            if ptoks & lane_tokens:
                conflicts.append(p.brand)
            elif ptoks & domain_tokens:
                crowded.append(p.brand)
        prof = profiles.get(team, {})
        openings = [
            o for o in prof.get("open_categories", []) if _tokens(o) & (lane_tokens | domain_tokens)
        ]
        greenfield = (
            "debut" in str(prof.get("note", "")).lower()
            or "inaugural" in str(prof.get("note", "")).lower()
        )
        recommended = bool(rec_key and rec_key & _team_key(team))
        if conflicts:
            status, label, detail = "conflict", "TAKEN", ", ".join(sorted(set(conflicts))[:3])
        elif recommended and (greenfield or openings) and not crowded:
            status, label = "prime", "PRIME LANE"
            detail = (
                "greenfield entry — partner roster being built from zero"
                if greenfield
                else "documented open category: " + ", ".join(openings[:2])
            )
        elif crowded:
            status, label, detail = "crowded", "CROWDED", ", ".join(sorted(set(crowded))[:3])
        else:
            status, label, detail = "open", "OPEN", "no rival in this category lane"
        weight = len(conflicts) * 2 + len(crowded)
        out.append(
            (
                weight,
                GridRow(
                    team=team, recommended=recommended, status=status, label=label, detail=detail
                ),
            )
        )
    rec_rows = [r for _, r in out if r.recommended]
    others = [
        r
        for _, r in sorted(
            (t for t in out if not t[1].recommended), key=lambda t: t[0], reverse=True
        )
    ]
    note = f"{categorised} of {len(rows)} partner rows categorised"
    return (rec_rows + others)[:max_rows], note


# --- assembling BriefData -------------------------------------------------------------------


def _date_long(date: dt.date) -> str:
    return date.strftime("%d %b %Y").upper()


def assemble(
    session: Session,
    brief: Brief,
    written: WrittenBrief,
    run_date: dt.date,
    industry_tokens_extra: set[str] | None = None,
    discovery: str = "scan",
) -> BriefData:
    """Fill the computed fields from the ledger + sponsors table around the written text."""
    claims = list(brief.claims)
    verified_n, total_n = ledger_counts(claims)
    lane = _tokens(written.industry_meta)
    domain = lane | (industry_tokens_extra or set())
    grid, note = build_gridfit(session, written.series_label, written.team_label, lane, domain)
    pts = proof_points_from_ledger(claims)
    data = BriefData(
        **written.model_dump(),
        proof_points=pts,
        all_proof_points_verified=bool(pts) and all(p.verified for p in pts),
        gridfit=grid,
        gridfit_note=note,
        sources=sources_from_ledger(claims),
        decision_maker_verified=decision_maker_verified(claims),
        verification_status=brief.verification_status.value,
        claims_verified=verified_n,
        claims_total=total_n,
        discovery=discovery,
        date_long=_date_long(run_date),
    )
    return data


# --- HTML / PDF --------------------------------------------------------------------------------


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_html(data: BriefData, font_stack: str = "brand") -> str:
    ctx = data.render_context()
    tier = tier_for(data.score)
    needs_review = (
        data.verification_status == "needs_review" or data.confidence_level.upper() == "MEDIUM"
    )
    ctx.update(
        tier=tier,
        mode_caption=MODE_CAPTIONS.get(data.value_mode or "", ""),
        footer_left="1440 SPORTS · LONDON · VERIFY BEFORE CIRCULATION"
        if needs_review
        else "1440 SPORTS · LONDON",
        logo_src=LOGO.as_uri(),
        fonts_dir=(ASSETS / "fonts").as_uri(),
        font_stack=font_stack,
        page_font="Lora" if font_stack == "brand" else 'Georgia, "Liberation Serif", serif',
    )
    return _env().get_template("brief.html.j2").render(**ctx)


def render_pdf(html: str, out_path: Path) -> int:
    """Write the PDF and return its page count. Raises PageOverflow if it is not exactly 2 pages."""
    from weasyprint import HTML

    doc = HTML(string=html, base_url=str(TEMPLATES)).render()
    n = len(doc.pages)
    if n != 2:
        raise PageOverflow(f"brief renders to {n} pages; the 1440 standard is strictly 2")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.write_pdf(str(out_path))
    return n


def render_brief(
    data: BriefData, out_dir: Path, slug: str, font_stack: str = "brand"
) -> dict[str, str | int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    html = render_html(data, font_stack)
    html_path = out_dir / f"{slug}.html"
    html_path.write_text(html, encoding="utf-8")
    pdf_path = out_dir / f"{slug}.pdf"
    pages = render_pdf(html, pdf_path)
    return {"html": str(html_path), "pdf": str(pdf_path), "pages": pages}


def brief_status_for_md(brief: Brief) -> bool:
    """§7: MD-eligible only when verified AND audit pass / pass_after_retry."""
    from intel.models import AuditStatus

    return brief.verification_status == VerificationStatus.verified and brief.audit_status in (
        AuditStatus.passed,
        AuditStatus.pass_after_retry,
    )
