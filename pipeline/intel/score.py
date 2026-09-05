"""Gate + dimension bookkeeping, alumni boost, pre-flight, FE rotation, selection (§6.4).

The V2.1 scanner (spec/v21_prompt.md, spec/n8n_v21_prompts.md NODE 1) does the judgement:
it applies the six gates and scores five dimensions /20. This module does NOT re-score;
it records what the model claimed, re-derives the arithmetic deterministically, applies
the rules that belong in code (OF gate, alumni boost from the ``alumni`` table, sponsor
identity pre-flight, tier thresholds, FE rotation, MD threshold) and refuses candidates
whose numbers do not add up. No weight or gate here differs from the spec; changing one
needs MD approval (build brief §0.5).
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.models import Alumni, AlumniTier, Sponsor, SponsorStatus
from intel.normalise import company_norm
from intel.parse import ScannedSignal

# spec/v21_prompt.md — Score Tier Thresholds (Phase 2.1)
TIER_THRESHOLDS: tuple[tuple[int, str], ...] = (
    (85, "HOT TOP TIER"),
    (70, "HOT"),
    (55, "WARM"),
    (40, "VERIFY"),
    (25, "PLANT"),
    (0, "DISCARD"),
)

# spec/v21_prompt.md Gate 0 + NODE 1 gate (1): Tier 1 = company press release, SEC/Companies
# House filing, named mainstream business press, verified LinkedIn. Domain heuristics only;
# the claim-level verifier (M3) is what actually checks the source.
TIER1_DOMAINS = {
    "sec.gov",
    "find-and-update.company-information.service.gov.uk",
    "wsj.com",
    "bloomberg.com",
    "reuters.com",
    "ft.com",
    "nytimes.com",
    "theinformation.com",
    "techcrunch.com",
    "theverge.com",
    "businesswire.com",
    "prnewswire.com",
    "globenewswire.com",
    "linkedin.com",
    "cnbc.com",
}
TIER3_DOMAINS = {"reddit.com", "x.com", "twitter.com", "facebook.com", "quora.com", "4chan.org"}
_PRESS_PATH = re.compile(r"/(press|newsroom|news-releases?|investors?|ir)\b")


def source_tier(url: str | None) -> int | None:
    if not url:
        return None
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return None
    host = host[4:] if host.startswith("www.") else host
    if any(host == d or host.endswith("." + d) for d in TIER3_DOMAINS):
        return 3
    if any(host == d or host.endswith("." + d) for d in TIER1_DOMAINS):
        return 1
    if _PRESS_PATH.search(urlparse(url).path or ""):
        return 1  # a company's own press/newsroom page
    return 2


def tier_for(score: int) -> str:
    for floor, name in TIER_THRESHOLDS:
        if score >= floor:
            return name
    return "DISCARD"


# --- alumni boost (spec/v22_alumni.md) -------------------------------------------------

_SENIORITY = (
    (re.compile(r"\b(ceo|chief executive|founder|co-?founder|managing director)\b", re.I), 1.0),
    (re.compile(r"\b(cmo|chief marketing|president)\b", re.I), 0.9),
    (re.compile(r"\b(cro|chief revenue|vp|vice president|svp|evp)\b", re.I), 0.7),
)
_TIER_BASE = {AlumniTier.strict: 12, AlumniTier.medium: 8}


def _recency_multiplier(move_date: dt.date | None, today: dt.date) -> float:
    if move_date is None:
        return 0.85  # unknown tenure: treat as 6-12 months, the middle of the table
    months = (today - move_date).days / 30.4
    if months <= 3:
        return 1.0
    if months <= 6:
        return 0.95
    if months <= 12:
        return 0.85
    if months <= 24:
        return 0.7
    return 0.5


def alumni_boost_for(session: Session, norm: str, today: dt.date) -> tuple[int, dict | None]:
    """Gate 6: a confirmed alumnus at this company → (+boost, match record). None otherwise.

    Boost = tier base (strict 12 / medium 8) × seniority × recency, per the v22 modifier
    tables. The capacity modifier needs a valuation we do not trust from the scanner, so it
    is not applied here; the match record says so.
    """
    row = session.scalar(
        select(Alumni)
        .where(Alumni.company_norm == norm, Alumni.active.is_(True))
        .order_by(Alumni.id)
    )
    if row is None:
        return 0, None
    seniority = 0.5
    for pat, mult in _SENIORITY:
        if row.current_role and pat.search(row.current_role):
            seniority = mult
            break
    recency = _recency_multiplier(row.move_date, today)
    boost = round(_TIER_BASE[row.tier] * seniority * recency)
    if row.tier == AlumniTier.strict:
        boost = max(9, min(12, boost)) if boost >= 9 else boost
    return boost, {
        "alumni_id": row.id,
        "name": row.name,
        "tier": row.tier.value,
        "current_role": row.current_role,
        "move_date": row.move_date.isoformat() if row.move_date else None,
        "seniority_multiplier": seniority,
        "recency_multiplier": recency,
        "capacity_adjustment": "not applied (valuation not trusted from scanner)",
        "boost": boost,
    }


# --- pre-flight sponsor check (spec/active_sponsor_db.md §6) ----------------------------


def preflight(session: Session, signal: ScannedSignal) -> dict:
    """Steps 1 (identity) and 3/4 (already on the recommended team) from the sponsors table.

    Category lock (step 2) and category density (step 5) need a category per sponsor row;
    the spec only categorises championship-level partners, so those steps are reported as
    'not evaluated' rather than guessed.
    """
    norm = company_norm(signal.company)
    live = (SponsorStatus.active, SponsorStatus.joined)
    rows = session.scalars(
        select(Sponsor).where(Sponsor.brand_norm == norm, Sponsor.status.in_(live))
    ).all()
    identity = [
        {"series": r.series.value, "level": r.level.value, "team": r.team, "brand": r.brand}
        for r in rows
    ]
    rec = (signal.recommended_team or "").lower()
    on_team = [i for i in identity if i["team"] and rec and _team_matches(rec, i["team"])]
    if on_team:
        outcome = "CONFLICTED"
    elif identity:
        outcome = "CONSTRAINED"
    else:
        outcome = "CLEAN"
    return {
        "identity_check": identity,
        "team_slot_check": on_team,
        "category_lock_check": "not evaluated (no per-sponsor category data)",
        "category_density": "not evaluated",
        "outcome": outcome,
    }


def _team_matches(recommended_lower: str, team_name: str) -> bool:
    words = {w for w in re.split(r"[^a-z0-9]+", team_name.lower()) if len(w) > 2}
    words -= {"f1", "team", "racing", "formula"}
    return any(w in recommended_lower for w in words)


# --- scoring bookkeeping ---------------------------------------------------------------


@dataclass
class Scored:
    ok: bool
    reason: str | None
    gate_results: dict = field(default_factory=dict)
    score_breakdown: dict = field(default_factory=dict)
    base_score: int | None = None
    alumni_boost: int = 0
    score_total: int | None = None
    ranking_score: int | None = None
    tier: str | None = None


def score_signal(session: Session, signal: ScannedSignal, run_date: dt.date) -> Scored:
    """Re-derive the arithmetic and record every gate. Refuses candidates whose numbers lie."""
    gates: dict = {}
    tier_src = source_tier(signal.source_url)
    gates["gate0_source"] = {"url": signal.source_url, "tier": tier_src, "pass": tier_src in (1, 2)}
    if tier_src == 3 or not signal.source_url:
        return Scored(False, "gate 0: no Tier 1/2 source URL", gates)

    bd = signal.score_breakdown
    if bd is None:
        return Scored(False, "no score_breakdown from scanner", gates)
    dims = {
        "timing": bd.timing,
        "capacity": bd.capacity,
        "brand_fit": bd.brand_fit,
        "urgency": bd.urgency,
        "ops_fit": bd.ops_fit if bd.ops_fit is not None else 0,
    }
    if bd.ops_fit_subscores is not None and bd.ops_fit is not None:
        subs = bd.ops_fit_subscores
        parts = [subs.product_to_need, subs.slot_availability, subs.on_camera, subs.lock_in]
        if all(p is not None for p in parts) and sum(parts) != bd.ops_fit:  # type: ignore[arg-type]
            gates["ops_fit_subscore_mismatch"] = {"sum": sum(parts), "ops_fit": bd.ops_fit}  # type: ignore[arg-type]
    if bd.legacy_scale:
        gates["scanner_scale"] = "legacy 4×25 shape rescaled to /20; ops_fit unknown"
    base = sum(dims.values())
    of_gate = bd.brand_fit >= 12
    gates["of_gate"] = {"brand_fit": bd.brand_fit, "applied": of_gate}
    ranking_base = base if of_gate else base - dims["ops_fit"]

    norm = company_norm(signal.company)
    boost, match = alumni_boost_for(session, norm, run_date)
    gates["gate6_alumni"] = {
        "boost": boost,
        "match": match,
        "scanner_alumni_match": signal.key_facts.alumni_match,
    }

    pf = preflight(session, signal)
    gates["preflight"] = pf
    cap = None
    if pf["identity_check"]:
        cap = 70  # NODE 1 gate (5): existing F1/FE programme of similar character → cap at 70
        gates["gate5_saturation"] = {"existing_sponsor": True, "cap": cap}
    else:
        gates["gate5_saturation"] = {"existing_sponsor": False, "cap": None}

    total = base + boost
    ranking = ranking_base + boost
    if cap is not None:
        total = min(total, cap)
        ranking = min(ranking, cap)
    total = max(0, min(100, total))
    ranking = max(0, min(100, ranking))

    gates["scanner_score"] = signal.score
    gates["recomputed_total"] = total
    gates["scanner_vs_recomputed_delta"] = signal.score - total

    breakdown = {
        **dims,
        "base": base,
        "alumni_boost": boost,
        "of_gate_applied": of_gate,
        "total": total,
        "ranking": ranking,
        "cap": cap,
    }
    if bd.ops_fit_subscores is not None:
        breakdown["ops_fit_subscores"] = bd.ops_fit_subscores.model_dump()
    return Scored(True, None, gates, breakdown, base, boost, total, ranking, tier_for(total))


# --- selection -------------------------------------------------------------------------


def fe_rotation_day(run_date: dt.date) -> bool:
    """Phase 2.1.8: Tuesdays and Fridays force-select the top eligible FE candidate."""
    return run_date.weekday() in (1, 4)


def select_top(eligible: list[tuple[int, str | None, object]], run_date: dt.date) -> object | None:
    """eligible: (ranking_score, series, payload) — returns the payload to brief today.

    Tue/Fri → highest FE if any FE is eligible; other days (incl. Sat/Sun, per the
    operator's weekend decision: run every day, score-only) → highest score.
    """
    if not eligible:
        return None
    ordered = sorted(eligible, key=lambda t: t[0], reverse=True)
    if fe_rotation_day(run_date):
        fe = [t for t in ordered if t[1] == "FE"]
        if fe:
            return fe[0][2]
    return ordered[0][2]
