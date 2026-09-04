"""'Recent & insightful' (build brief §8 Home): two or three sentences generated at brief
time from VERIFIED claims only — what changed in the last 14 days and why it matters.

Deterministic composition (no model needed): the verified trigger claim, then up to two
verified figures, then the bottom line's team verdict. Every sentence carries the ids of
the claims it came from (``highlights.claim_ids`` must reference verified claims only).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from intel.brief_data import strip_markup
from intel.models import Brief, ClaimType, Highlight, VerificationResult


def _verified(brief: Brief):
    for c in sorted(brief.claims, key=lambda c: (c.position, c.id)):
        if not c.verifications:
            continue
        v = sorted(c.verifications, key=lambda x: (x.checked_at, x.id))[-1]
        if v.status == VerificationResult.verified:
            yield c


def compose_highlights(brief: Brief) -> list[tuple[str, list[int]]]:
    claims = list(_verified(brief))
    out: list[tuple[str, list[int]]] = []
    trigger = next(
        (c for c in claims if c.section == "trigger" or c.claim_type == ClaimType.date), None
    )
    if trigger:
        out.append((strip_markup(trigger.text).rstrip(".") + ".", [trigger.id]))
    figures = [
        c
        for c in claims
        if c.claim_type in (ClaimType.funding, ClaimType.revenue) and c is not trigger
    ][:2]
    if figures:
        out.append(
            (
                " ".join(strip_markup(c.text).rstrip(".") + "." for c in figures),
                [c.id for c in figures],
            )
        )
    d = brief.brief_data or {}
    team = d.get("team_label")
    if team and out:
        # The verdict is 1440's own judgement, not a fact claim; it cites the claims above.
        out.append(
            (
                f"Why it matters: the moment lines up with {team}, "
                "where the category lane is open today.",
                [c for _, ids in out for c in ids],
            )
        )
    return out[:3]


def store_highlights(session: Session, brief: Brief) -> list[Highlight]:
    rows = [
        Highlight(brief_id=brief.id, text=t, claim_ids=ids) for t, ids in compose_highlights(brief)
    ]
    for r in rows:
        session.add(r)
    session.flush()
    return rows
