"""Claim-level verification (build brief §3.1, §6.5).

Three layers, cheapest and most certain first:
1. **Calendar check** — any race/event mention is matched against ``calendar_events`` for
   the season. Not in the table → ``contradicted``. This is what catches Ramp N° 025's
   "F1 London race in August 2026" without asking a model anything.
2. **Sponsor-table check** — "Brand at Team" claims are matched against ``sponsors``
   (active/joined). Not in the table → ``contradicted`` (the table is a dated snapshot;
   a genuinely new deal therefore blocks the brief until an operator confirms it — the
   conservative direction the brief demands).
3. **Source check** — everything else goes to the verifier model (claude-opus-5 by
   default) which fetches the cited source and up to two independent ones and returns
   verified / unverified / contradicted with an evidence URL + excerpt.

Decision (§6.5): any contradicted load-bearing claim → blocked; any unverified
load-bearing claim → needs_review; all verified → verified.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.config import Settings, get_settings
from intel.llm import ModelTurnError, complete_text
from intel.models import (
    Brief,
    CalendarEvent,
    Claim,
    ClaimType,
    Series,
    Sponsor,
    SponsorStatus,
    Verification,
    VerificationMethod,
    VerificationResult,
    VerificationStatus,
)
from intel.normalise import company_norm
from intel.parse import ParseError, ScannedSignal, extract_json_object

# --- claim drafts ------------------------------------------------------------------------


@dataclass
class ClaimDraft:
    text: str
    section: str
    claim_type: ClaimType
    load_bearing: bool = True
    cited_source_url: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


# Sections whose claims are load-bearing per §6.5 (deck, THE CASE, WHY NOW, decision-maker,
# deal architecture, score cells). Everything from the scanner's key facts feeds those.
LOAD_BEARING_SECTIONS = {
    "key_facts",
    "trigger",
    "decision_maker",
    "deck",
    "headline_long",
    "the_case",
    "why_now",
    "deal_architecture",
    "score_rationale",
    "key_facts_proof_points",
    "value_to_team",
    "why_team",
}

_KEY_FACT_TYPES: dict[str, ClaimType] = {
    "funding": ClaimType.funding,
    "investors": ClaimType.funding,
    "revenue": ClaimType.revenue,
    "trigger": ClaimType.date,
    "competitor_signal": ClaimType.sponsorship,
    "strategic_hook": ClaimType.other,
    "us_presence": ClaimType.other,
    "alumni_match": ClaimType.person_role,
}
_EMPTY = {"", "n/a", "na", "none", "null", "unknown", "undisclosed", "not disclosed", "-", "—"}


def claims_from_signal(signal: ScannedSignal) -> list[ClaimDraft]:
    """Deterministic claim extraction from the scanner's structured output."""
    out: list[ClaimDraft] = []
    src = signal.source_url
    if signal.person:
        role = f", {signal.role}" if signal.role else ""
        out.append(
            ClaimDraft(
                f"{signal.person}{role} at {signal.company}",
                "decision_maker",
                ClaimType.person_role,
                True,
                src,
                {"person": signal.person, "role": signal.role, "company": signal.company},
            )
        )
    kf = signal.key_facts.model_dump()
    for key, ctype in _KEY_FACT_TYPES.items():
        val = kf.get(key)
        if not val or str(val).strip().lower() in _EMPTY:
            continue
        out.append(ClaimDraft(str(val).strip(), "key_facts", ctype, True, src, {"field": key}))
    trig = signal.trigger_reason
    if trig and trig.strip() and trig.strip() != (kf.get("trigger") or "").strip():
        out.append(ClaimDraft(trig.strip(), "trigger", ClaimType.date, True, src))
    out.extend(event_claims_in(out, src))
    return out


_NUMERIC = re.compile(
    r"(?:[$€£]\s?\d[\d.,]*\s?(?:[MBK]|bn|million|billion)?\+?)|(?:\d+(?:\.\d+)?%)",
    re.IGNORECASE,
)
_REVENUE_WORDS = re.compile(r"revenue|\barr\b|sales|turnover|run-?rate", re.IGNORECASE)
_SPONSOR_WORDS = re.compile(r"sponsor|partner|livery|title deal|signed", re.IGNORECASE)
_SENTENCE = re.compile(r"(?<=[.;])\s+")

# Claims in these written sections gate the brief (§6.5). why_team / value / risks are still
# verified but do not block on their own.
_WRITTEN_LOAD_BEARING = {
    "deck": True,
    "the_case_p1": True,
    "the_case_p2": True,
    "why_now_callout": True,
    "bottom_line": True,
    "deal_arch_para": True,
    "why_team_para": False,
    "value_content": False,
}


def claims_from_brief(written: Any) -> list[ClaimDraft]:
    """Deterministic claim extraction from the written brief text (stage B, after writing).

    - decision-maker name + role (person_role, load-bearing);
    - every sentence carrying a money / percentage figure in the load-bearing sections
      (funding or revenue by wording; figures in DEAL ARCHITECTURE are 1440's own deal
      proposal, not company facts, so they are skipped);
    - every race / event mention anywhere in the brief;
    - every 'Brand at Team' sponsorship pair in the landscape / team sections.
    A model-based extractor (``ClaimExtractor``) can add what the regexes miss.
    """
    from intel.brief_data import strip_markup

    out: list[ClaimDraft] = []
    name = getattr(written, "decision_maker_name", None)
    if name:
        role = getattr(written, "decision_maker_role", None) or ""
        out.append(
            ClaimDraft(
                f"{name}, {role} at {written.company}" if role else f"{name} at {written.company}",
                "decision_maker",
                ClaimType.person_role,
                True,
                None,
                {"person": name, "role": role, "company": written.company},
            )
        )
    for section, lb in _WRITTEN_LOAD_BEARING.items():
        text = strip_markup(getattr(written, section, "") or "")
        if not text:
            continue
        if section == "deal_arch_para":
            continue
        for sentence in _SENTENCE.split(text):
            if _NUMERIC.search(sentence):
                ctype = ClaimType.revenue if _REVENUE_WORDS.search(sentence) else ClaimType.funding
                out.append(ClaimDraft(sentence.strip(), section, ctype, lb))
    for section in ("the_case_p2", "why_team_para", "value_content"):
        text = strip_markup(getattr(written, section, "") or "")
        # Only sentences that talk about sponsorship carry 'Brand at Team' claims worth
        # checking; the bare pattern over-fires on ordinary prose.
        sponsor_sentences = " ".join(s for s in _SENTENCE.split(text) if _SPONSOR_WORDS.search(s))
        for brand, team in sponsorship_pairs(sponsor_sentences):
            out.append(
                ClaimDraft(
                    f"{brand} at {team}",
                    section,
                    ClaimType.sponsorship,
                    _WRITTEN_LOAD_BEARING.get(section, False),
                )
            )
    scan_sections = [
        "deck",
        "the_case_p1",
        "the_case_p2",
        "why_now_callout",
        "why_team_para",
        "value_content",
        "deal_arch_para",
        "bottom_line",
        "opening_angle_quote",
    ]
    texts = [
        ClaimDraft(strip_markup(getattr(written, s, "") or ""), s, ClaimType.other, True)
        for s in scan_sections
    ]
    for r in getattr(written, "risks", []) or []:
        texts.append(
            ClaimDraft(strip_markup(f"{r.detail} {r.counter}"), "risks", ClaimType.other, False)
        )
    # The app-page expansion (extended.*) is not load-bearing for the send decision, but its
    # figures and race mentions go through the same checks so nothing unverified reaches
    # the screen unmarked.
    ext = getattr(written, "extended", None)
    for text in ext.texts if ext else []:
        plain = strip_markup(text)
        if not plain:
            continue
        texts.append(ClaimDraft(plain, "extended", ClaimType.other, False))
        for sentence in _SENTENCE.split(plain):
            if _NUMERIC.search(sentence):
                ctype = ClaimType.revenue if _REVENUE_WORDS.search(sentence) else ClaimType.funding
                out.append(ClaimDraft(sentence.strip(), "extended", ctype, False))
    out.extend(event_claims_in([t for t in texts if t.text], None))
    return out


class ClaimExtractor(Protocol):
    def extract(self, written: Any) -> list[ClaimDraft]: ...


class NoExtractor:
    def extract(self, written: Any) -> list[ClaimDraft]:
        return []


def merge_claims(*groups: list[ClaimDraft]) -> list[ClaimDraft]:
    seen: set[str] = set()
    out: list[ClaimDraft] = []
    for g in groups:
        for d in g:
            key = re.sub(r"\W+", " ", d.text.lower()).strip()
            if key and key not in seen:
                seen.add(key)
                out.append(d)
    return out


# --- calendar check ----------------------------------------------------------------------

# Venue/city → the token that appears in the seeded round name. Geography only.
VENUE_ALIASES: dict[str, str] = {
    "silverstone": "british",
    "monza": "italian",
    "imola": "emilia",
    "spa": "belgian",
    "spa-francorchamps": "belgian",
    "suzuka": "japanese",
    "zandvoort": "dutch",
    "baku": "azerbaijan",
    "jeddah": "saudi",
    "sakhir": "bahrain",
    "melbourne": "australian",
    "albert park": "australian",
    "shanghai": "chinese",
    "montreal": "canadian",
    "montréal": "canadian",
    "barcelona": "spanish",
    "madrid": "spanish",
    "budapest": "hungarian",
    "hungaroring": "hungarian",
    "interlagos": "são paulo",
    "sao paulo": "são paulo",
    "austin": "us",
    "cota": "us",
    "united states": "us",
    "texas": "us",
    "mexico city": "mexico",
    "yas marina": "abu dhabi",
    "lusail": "qatar",
    "marina bay": "singapore",
    "monte carlo": "monaco",
    "spielberg": "austrian",
    "red bull ring": "austrian",
    "las vegas": "las vegas",
    "vegas": "las vegas",
    "miami": "miami",
}

# Keywords are case-insensitive (scoped (?i:...)); the place must be Capitalised words so
# that "hospitality at the British GP" yields "British", not the whole phrase.
_EVENT_RE = re.compile(
    r"(?:\b(?i:(F1|Formula\s*1|Formula\s*One|FE|Formula\s*E))\b[\s:,-]*)?"
    r"([A-Z][\w'’.-]*(?:\s+[A-Z][\w'’.-]*){0,3})\s+"
    r"(?i:(Grand\s+Prix|GP|E-?Prix|race|round))\b"
    r"(?:[^.;]{0,40}?\b(?i:((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{4})))?"
)
_STOP_PLACES = {"the", "a", "an", "this", "that", "next", "home", "first", "key", "each"}


def find_event_mentions(text: str) -> list[dict[str, str | None]]:
    """Race/event mentions in free text: [{'series','place','kind','when','span'}]."""
    found: list[dict[str, str | None]] = []
    for m in _EVENT_RE.finditer(text or ""):
        place = m.group(2).strip()
        # Drop sentence-initial articles / determiners ("The British GP" → "British").
        words = place.split()
        while len(words) > 1 and words[0].lower() in _STOP_PLACES:
            words = words[1:]
        place = " ".join(words)
        if place.lower() in _STOP_PLACES or len(place) < 3:
            continue
        series_raw = (m.group(1) or "").upper().replace(" ", "")
        kind = m.group(3).lower().replace("-", "")
        series: str | None = None
        if series_raw in {"F1", "FORMULA1", "FORMULAONE"}:
            series = "F1"
        elif series_raw in {"FE", "FORMULAE"} or kind == "eprix":
            series = "FE"
        elif kind in {"grand prix", "gp"}:
            series = "F1"
        found.append(
            {
                "series": series,
                "place": place,
                "kind": m.group(3),
                "when": m.group(4),
                "span": m.group(0).strip(),
            }
        )
    return found


def event_claims_in(drafts: list[ClaimDraft], src: str | None) -> list[ClaimDraft]:
    out: list[ClaimDraft] = []
    seen: set[str] = set()
    for d in drafts:
        for ev in find_event_mentions(d.text):
            key = (ev["span"] or "").lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(
                ClaimDraft(
                    ev["span"] or d.text,
                    d.section,
                    ClaimType.event,
                    d.load_bearing,
                    src,
                    {"event": ev},
                )
            )
    return out


def _season_for(when: str | None, run_date: dt.date) -> int:
    if when:
        m = re.search(r"(20\d\d)", when)
        if m:
            return int(m.group(1))
    return run_date.year


def check_event_claim(session: Session, draft: ClaimDraft, run_date: dt.date) -> Verification:
    ev = draft.meta.get("event") or {}
    place = (ev.get("place") or "").lower().strip()
    series = ev.get("series")
    kind = (ev.get("kind") or "").lower()
    if series is None:
        series = "FE" if "prix" in kind and kind.startswith("e") else "F1"
    season = _season_for(ev.get("when"), run_date)
    rows = session.scalars(
        select(CalendarEvent).where(
            CalendarEvent.series == Series(series), CalendarEvent.season == season
        )
    ).all()
    if not rows:
        return Verification(
            status=VerificationResult.unverified,
            method=VerificationMethod.calendar,
            notes=f"no {series} {season} calendar loaded; cannot check '{draft.text}'",
        )
    # Match on the alias, the full place, and each significant word of it ("British",
    # "Las Vegas", "Sao Paulo"), so wording variants still find the round.
    words = [w for w in re.split(r"[^a-z0-9]+", place) if len(w) >= 4 and w not in _STOP_PLACES]
    tokens = {VENUE_ALIASES.get(place, place), place, *words}
    tokens |= {VENUE_ALIASES[w] for w in words if w in VENUE_ALIASES}
    for r in rows:
        hay = " ".join(filter(None, [r.name, r.city, r.country])).lower()
        if any(t and t in hay for t in tokens):
            note = f"round {r.round}: {r.name}"
            if r.date_start is None:
                note += " (round exists; dates not yet verified — calendar is provisional)"
            return Verification(
                status=VerificationResult.verified,
                method=VerificationMethod.calendar,
                evidence_url=r.source,
                evidence_excerpt=note,
                notes=None,
            )
    return Verification(
        status=VerificationResult.contradicted,
        method=VerificationMethod.calendar,
        notes=(
            f"no {series} {season} round matches '{ev.get('place')}' in the fixed calendar "
            f"table ({len(rows)} rounds loaded)"
        ),
    )


# --- sponsor-table check -----------------------------------------------------------------

_PAIR_RE = re.compile(
    r"([A-Z][\w&.'-]*(?:\s+[A-Z][\w&.'-]*){0,2})\s+"
    r"(?:is\s+)?(?:at|with|sponsors?|partner(?:s|ed)?\s+with|signed\s+with|on)\s+"
    r"([A-Z][\w&.'-]*(?:\s+[A-Z][\w&.'-]*){0,3})"
)


def sponsorship_pairs(text: str) -> list[tuple[str, str]]:
    return [(m.group(1).strip(), m.group(2).strip()) for m in _PAIR_RE.finditer(text or "")]


def _team_tokens(team: str) -> set[str]:
    words = {w for w in re.split(r"[^a-z0-9]+", team.lower()) if len(w) > 2}
    return words - {"f1", "team", "racing", "formula", "the"}


def check_sponsorship_claim(session: Session, draft: ClaimDraft) -> Verification | None:
    pairs = sponsorship_pairs(draft.text)
    if not pairs:
        return None  # nothing structured to check; falls through to the source check
    live = (SponsorStatus.active, SponsorStatus.joined)
    unmatched: list[str] = []
    matched: list[str] = []
    for brand, team in pairs:
        rows = session.scalars(
            select(Sponsor).where(
                Sponsor.brand_norm == company_norm(brand), Sponsor.status.in_(live)
            )
        ).all()
        hit = None
        for r in rows:
            if r.team and _team_tokens(team) & _team_tokens(r.team):
                hit = r
                break
            if r.team is None and not _team_tokens(team):
                hit = r
                break
        if hit:
            matched.append(
                f"{brand} → {hit.team or 'championship'} ({hit.level.value}, {hit.status.value})"
            )
        else:
            unmatched.append(f"{brand} at {team}")
    if unmatched:
        return Verification(
            status=VerificationResult.contradicted,
            method=VerificationMethod.sponsor_db,
            notes="not in the sponsor table (snapshot dated 2026-05-20): " + "; ".join(unmatched),
        )
    return Verification(
        status=VerificationResult.verified,
        method=VerificationMethod.sponsor_db,
        evidence_excerpt="; ".join(matched),
        evidence_url="spec/active_sponsor_db.md",
    )


# --- source check (model) ------------------------------------------------------------------


class Verifier(Protocol):
    def verify(self, claim: ClaimDraft, company: str) -> Verification: ...


VERIFIER_SYSTEM = (
    "You are the 1440Sports fact verifier. You receive ONE claim about a company, drawn from a "
    "sponsorship-intelligence brief, plus the URL the brief cites. Fetch the cited URL and, if "
    "needed, search for up to two independent sources. Decide whether the claim is:\n"
    "- verified: a Tier 1 source (company press release, regulator/exchange filing, WSJ, "
    "Bloomberg, Reuters, FT, NYT, The Information, TechCrunch with named byline) directly "
    "supports it, including the specific figure, name, date or relationship;\n"
    "- contradicted: a credible source says something incompatible (different figure, different "
    "person in the role, the event or relationship does not exist);\n"
    "- unverified: you could not find a source that supports it.\n"
    "Never verify from memory. A claim without a supporting source is unverified, not verified. "
    "Quote the exact supporting or contradicting sentence as the excerpt.\n\n"
    'Return ONLY a JSON object: {"status": "verified|unverified|contradicted", '
    '"evidence_url": "..." or null, "excerpt": "..." or null, "reasoning": "one sentence"}'
)


class AnthropicVerifier:
    """claude-opus-5 + web_fetch/web_search; returns a Verification (never raises on model 'no')."""

    def __init__(self, client: Any | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self._client = client

    def verify(self, claim: ClaimDraft, company: str) -> Verification:
        user = (
            f"Company: {company}\nClaim ({claim.claim_type.value}, section {claim.section}): "
            f"{claim.text}\nCited source: {claim.cited_source_url or 'none given'}"
        )
        tools = [
            {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 3},
            {"type": "web_search_20260209", "name": "web_search", "max_uses": 3},
        ]
        try:
            text = complete_text(
                self._client,
                model=self.settings.verify_model,
                system=VERIFIER_SYSTEM,
                messages=[{"role": "user", "content": user}],
                tools=tools,
                max_tokens=16000,
                effort="high",
                label="verifier",
            ).text
            data = extract_json_object(text)
        except (ParseError, ModelTurnError) as exc:
            return Verification(
                status=VerificationResult.unverified,
                method=VerificationMethod.llm_source_fetch,
                model=self.settings.verify_model,
                notes=f"verifier output unparseable: {exc}",
            )
        status = str(data.get("status", "unverified")).lower()
        if status not in {"verified", "unverified", "contradicted"}:
            status = "unverified"
        return Verification(
            status=VerificationResult(status),
            method=VerificationMethod.llm_source_fetch,
            model=self.settings.verify_model,
            evidence_url=data.get("evidence_url") or None,
            evidence_excerpt=(data.get("excerpt") or None),
            notes=data.get("reasoning") or None,
        )


class NoVerifier:
    """Used when no model credential is configured: every source-check claim is unverified."""

    def verify(self, claim: ClaimDraft, company: str) -> Verification:
        return Verification(
            status=VerificationResult.unverified,
            method=VerificationMethod.llm_source_fetch,
            notes="no verifier configured (ANTHROPIC_API_KEY unset) — VERIFY BEFORE CIRCULATION",
        )


def default_verifier(settings: Settings | None = None) -> Verifier:
    settings = settings or get_settings()
    if settings.anthropic_api_key:
        return AnthropicVerifier(settings=settings)
    return NoVerifier()


# --- running the ledger ---------------------------------------------------------------------


@dataclass
class LedgerResult:
    status: VerificationStatus
    claims: list[Claim]
    counts: dict[str, int]
    blocking: list[str]  # texts of contradicted load-bearing claims
    review: list[str]  # texts of unverified load-bearing claims


def decide(pairs: list[tuple[Claim, Verification]]) -> VerificationStatus:
    lb = [(c, v) for c, v in pairs if c.load_bearing]
    if any(v.status == VerificationResult.contradicted for _, v in lb):
        return VerificationStatus.blocked
    if any(v.status == VerificationResult.unverified for _, v in lb):
        return VerificationStatus.needs_review
    return VerificationStatus.verified


def run_ledger(
    session: Session,
    brief: Brief,
    drafts: list[ClaimDraft],
    company: str,
    run_date: dt.date,
    verifier: Verifier,
) -> LedgerResult:
    """Store every claim + verification for ``brief`` and set its verification_status."""
    pairs: list[tuple[Claim, Verification]] = []
    for pos, d in enumerate(drafts):
        claim = Claim(
            brief_id=brief.id,
            position=pos,
            section=d.section,
            text=d.text,
            claim_type=d.claim_type,
            load_bearing=d.load_bearing,
            cited_source_url=d.cited_source_url,
        )
        session.add(claim)
        session.flush()
        if d.claim_type == ClaimType.event:
            v = check_event_claim(session, d, run_date)
        elif d.claim_type == ClaimType.sponsorship:
            v = check_sponsorship_claim(session, d) or verifier.verify(d, company)
        else:
            v = verifier.verify(d, company)
        v.claim_id = claim.id
        session.add(v)
        pairs.append((claim, v))
    session.flush()
    # The brief's status is decided over its WHOLE ledger (stage A key facts + stage B
    # brief text), using the latest verification of each claim.
    session.expire(brief, ["claims"])
    all_pairs = [
        (c, sorted(c.verifications, key=lambda x: (x.checked_at, x.id))[-1])
        for c in brief.claims
        if c.verifications
    ]
    status = decide(all_pairs or pairs)
    brief.verification_status = status
    counts: dict[str, int] = {}
    for _, v in pairs:
        counts[v.status.value] = counts.get(v.status.value, 0) + 1
    return LedgerResult(
        status,
        [c for c, _ in pairs],
        counts,
        [
            c.text
            for c, v in pairs
            if c.load_bearing and v.status == VerificationResult.contradicted
        ],
        [c.text for c, v in pairs if c.load_bearing and v.status == VerificationResult.unverified],
    )
