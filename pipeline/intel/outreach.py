"""Outreach drafts (build brief §8): brand voice, built from the opening angle and VERIFIED
claims only, ending with the 25-minute ask. §9.12: a draft contains no claim absent from the
brief's verified claims, and creating an Outlook draft never sends.

Without a model credential the draft is composed deterministically from verified claim
text; with one, the writer model drafts in ``spec/brand_voice.md`` voice and the same safety
check gates the result.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from intel.brief_data import strip_markup
from intel.models import Brief, Claim, ClaimType, VerificationResult

_FIGURE = re.compile(
    r"(?:[$€£]\s?\d[\d.,]*\s?(?:[MBK]|bn|million|billion)?\+?)|(?:\d+(?:\.\d+)?%)|(?:\b(?:19|20)\d{2}\b)",
    re.IGNORECASE,
)
BRAND_VOICE = Path(__file__).resolve().parents[2] / "spec" / "brand_voice.md"


@dataclass
class Draft:
    subject: str
    body: str
    claim_ids: list[int]


def verified_claims(brief: Brief) -> list[Claim]:
    out = []
    for c in brief.claims:
        if not c.verifications:
            continue
        v = sorted(c.verifications, key=lambda x: (x.checked_at, x.id))[-1]
        if v.status == VerificationResult.verified:
            out.append(c)
    return out


def figures_in(text: str) -> set[str]:
    return {m.group(0).replace(" ", "").lower() for m in _FIGURE.finditer(text or "")}


def check_draft(body: str, claims: list[Claim]) -> list[str]:
    """§9.12 safety: every figure/year in the draft must appear in a verified claim.

    Returns the offending figures (empty list = safe)."""
    allowed: set[str] = set()
    for c in claims:
        allowed |= figures_in(strip_markup(c.text))
    return sorted(f for f in figures_in(body) if f not in allowed)


def compose_deterministic(brief: Brief) -> Draft:
    d = brief.brief_data or {}
    company = d.get("company", "")
    name = (d.get("decision_maker_name") or "").split(" ")[0]
    claims = verified_claims(brief)
    numeric = [
        c for c in claims if c.claim_type in (ClaimType.funding, ClaimType.revenue, ClaimType.date)
    ][:2]
    team = d.get("team_label") or ""
    lines = [f"{name}," if name else "Hello,", ""]
    if numeric:
        lines.append(" ".join(strip_markup(c.text).rstrip(".") + "." for c in numeric))
    angle = strip_markup(d.get("opening_angle_intro") or "")
    if angle:
        lines.append(angle)
    if team:
        lines.append(
            "1440 places companies at exactly this moment with one F1 or Formula E team — "
            f"for {company} the fit we have mapped is {team}, with a category lane that is "
            "open today."
        )
    lines += [
        "",
        "Would 25 minutes this week or next work to walk you through it?",
        "",
        "Best,",
        "1440 Sports",
    ]
    body = "\n".join(lines)
    return Draft(
        subject=f"{company} × {team or 'F1 / Formula E'} — 25 minutes?",
        body=body,
        claim_ids=[c.id for c in numeric],
    )


def compose(brief: Brief, model_writer=None) -> Draft:
    """Model-written in brand voice when a writer is available; deterministic otherwise.
    Either way the §9.12 check must pass, else fall back to the deterministic draft."""
    claims = verified_claims(brief)
    if model_writer is not None:
        d = brief.brief_data or {}
        voice = BRAND_VOICE.read_text(encoding="utf-8") if BRAND_VOICE.exists() else ""
        system = (
            "You write first-contact outreach emails for 1440Sports, a London "
            "motorsport-sponsorship agency. Use ONLY the verified facts listed; do not add any "
            "figure, date, investor, or event that is not listed. End with a specific 25-minute "
            'ask. Return JSON {"subject": ..., "body": ...}.\n\n' + voice
        )
        facts = "\n".join(f"- {strip_markup(c.text)}" for c in claims)
        user = (
            f"Company: {d.get('company')}\n"
            f"Recipient: {d.get('decision_maker_name')}, {d.get('decision_maker_role')}\n"
            f"Recommended team: {d.get('team_label')}\n"
            f"Opening angle: {strip_markup(d.get('opening_angle_quote') or '')}\n"
            f"Verified facts:\n{facts}"
        )
        try:
            from intel.config import get_settings
            from intel.parse import extract_json_object

            raw = model_writer.write(model=get_settings().writer_model, system=system, user=user)
            data = extract_json_object(raw)
            body = str(data.get("body", ""))
            if body and not check_draft(body, claims):
                return Draft(str(data.get("subject", "")), body, [c.id for c in claims])
        except Exception:
            pass  # fall through to the deterministic draft
    draft = compose_deterministic(brief)
    offenders = check_draft(draft.body, claims)
    if offenders:  # cannot happen by construction, but never ship an unverified figure
        raise ValueError(f"draft contains unverified figures: {offenders}")
    return draft
