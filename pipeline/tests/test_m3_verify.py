"""M3 regression suite — build brief §9 tests 1 and 2, plus the ledger decision rules."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import func, select

from intel import run_daily, verify
from intel.config import Settings
from intel.models import (
    Brief,
    Candidate,
    CandidateDecision,
    Claim,
    ClaimType,
    SurfacedLog,
    Verification,
    VerificationMethod,
    VerificationResult,
    VerificationStatus,
)
from intel.seed import load_seeds
from tests.fixtures import production_signals as ps


class FakeVerifier:
    """Returns a scripted status per claim text (default verified); records what it was asked."""

    def __init__(self, scripted: dict[str, str] | None = None, default: str = "verified") -> None:
        self.scripted = scripted or {}
        self.default = default
        self.asked: list[str] = []

    def verify(self, claim: verify.ClaimDraft, company: str) -> Verification:
        self.asked.append(claim.text)
        status = self.default
        for needle, s in self.scripted.items():
            if needle.lower() in claim.text.lower():
                status = s
        return Verification(
            status=VerificationResult(status),
            method=VerificationMethod.llm_source_fetch,
            model="fake",
            evidence_url="https://example.test/evidence" if status == "verified" else None,
            evidence_excerpt="scripted" if status == "verified" else None,
        )


def _settings(url: str, **overrides) -> Settings:
    return Settings(database_url=url, execution_mode="dry_run", **overrides)


def _scanner(*signals):
    return lambda _date: list(signals)


# --- §9.1 Ramp N° 025 phantom race ---------------------------------------------------------


def test_event_mentions_are_found_in_free_text():
    found = verify.find_event_mentions(ps.RAMP_PHANTOM_RACE["trigger_reason"])
    assert [(f["series"], f["place"], f["when"]) for f in found] == [
        ("F1", "London", "August 2026")
    ]
    brit = verify.find_event_mentions(
        "hospitality at the British GP at Silverstone (3-5 July 2026)"
    )
    assert brit[0]["place"] == "British" and brit[0]["series"] == "F1"
    assert verify.find_event_mentions("a Mexico City E-Prix activation")[0]["series"] == "FE"


def test_funding_rounds_are_not_race_rounds():
    # Fluidstack N° 127 (6 Sep 2026): "WHY NOW  The round was reported on 3 September" was
    # read as a race called "WHY NOW The" and contradicted by the calendar table.
    for text in (
        "WHY NOW  The round was reported on 3 September; budgets reset after a raise.",
        "a Series B round led by Jane Street at an $18B valuation",
        "The round closed in July at $7.5B.",
    ):
        assert verify.find_event_mentions(text) == [], text
    # A real round mention still counts.
    assert verify.find_event_mentions("the Austin round in October")[0]["place"] == "Austin"


def test_phantom_london_race_is_contradicted_by_the_calendar_table(session):
    load_seeds(session)
    draft = verify.ClaimDraft(
        "F1 London race August 2026",
        "trigger",
        ClaimType.event,
        meta={"event": {"series": "F1", "place": "London", "when": "August 2026"}},
    )
    v = verify.check_event_claim(session, draft, dt.date(2026, 5, 28))
    assert v.status == VerificationResult.contradicted
    assert v.method == VerificationMethod.calendar
    assert "London" in v.notes and "24 rounds" in v.notes


def test_real_round_is_found_by_venue_alias(session):
    load_seeds(session)
    draft = verify.ClaimDraft(
        "British GP at Silverstone",
        "deal_architecture",
        ClaimType.event,
        meta={"event": {"series": "F1", "place": "Silverstone", "when": None}},
    )
    v = verify.check_event_claim(session, draft, dt.date(2026, 6, 14))
    assert v.status == VerificationResult.verified
    assert "British GP" in v.evidence_excerpt
    assert "dates not yet verified" in v.evidence_excerpt  # calendar is provisional


def test_fe_event_without_a_loaded_calendar_is_unverified_not_contradicted(session):
    load_seeds(session)  # FE Seasons 12 + 13 are seeded (5 Sep 2026); 2029 is not
    draft = verify.ClaimDraft(
        "Mexico City E-Prix",
        "why_now",
        ClaimType.event,
        meta={"event": {"series": "FE", "place": "Mexico City", "when": "January 2029"}},
    )
    v = verify.check_event_claim(session, draft, dt.date(2028, 6, 14))
    assert v.status == VerificationResult.unverified
    # …and with the calendar loaded the same round verifies (Season 12, stored as 2026)
    ok = verify.ClaimDraft(
        "Mexico City E-Prix",
        "why_now",
        ClaimType.event,
        meta={"event": {"series": "FE", "place": "Mexico City", "when": None}},
    )
    assert verify.check_event_claim(session, ok, dt.date(2026, 6, 14)).status.value == "verified"


def test_ramp_025_is_blocked_before_any_brief_is_issued(session, migrated_database):
    load_seeds(session)
    s = _settings(migrated_database)
    fake = FakeVerifier()  # every other claim would verify; the race alone must block
    out = run_daily.run_day(
        dt.date(2026, 5, 28),
        s,
        _scanner(ps.with_breakdown(ps.RAMP_PHANTOM_RACE, series="F1")),
        session,
        verifier=fake,
    )
    assert out.status == "no_signal" and out.brief_id is None
    cand = session.scalar(select(Candidate))
    assert cand.decision == CandidateDecision.verification_blocked
    assert "London" in cand.decision_reason
    brief = session.scalar(select(Brief))
    assert brief.verification_status == VerificationStatus.blocked
    event = session.scalar(select(Claim).where(Claim.claim_type == ClaimType.event))
    assert event.load_bearing and event.verifications[0].status == VerificationResult.contradicted
    assert session.scalar(select(func.count()).select_from(SurfacedLog)) == 0  # never surfaced


def test_blocked_candidate_moves_on_to_the_next_eligible_one(session, migrated_database):
    load_seeds(session)
    s = _settings(migrated_database)
    out = run_daily.run_day(
        dt.date(2026, 5, 28),
        s,
        _scanner(
            ps.with_breakdown(ps.RAMP_PHANTOM_RACE, series="F1"),  # 87, blocked
            ps.with_breakdown(ps.PRIMER_B, series="F1"),  # 79, dated 2026-05-20: fresh, clean
        ),
        session,
        verifier=FakeVerifier(),
    )
    assert out.status == "success" and out.verification_status == "verified"
    issued = session.get(Brief, out.brief_id)
    assert issued.candidate.company_raw == "Primer"
    statuses = sorted(b.verification_status.value for b in session.scalars(select(Brief)))
    assert statuses == ["blocked", "verified"]
    surfaced = session.scalars(select(SurfacedLog)).all()
    assert [r.company_norm for r in surfaced] == ["primer"]
    assert surfaced[0].brief_id == issued.id


def test_max_three_attempts_then_no_signal(session, migrated_database):
    load_seeds(session)
    s = _settings(migrated_database, max_verification_attempts=1)
    out = run_daily.run_day(
        dt.date(2026, 5, 28),
        s,
        _scanner(
            ps.with_breakdown(ps.RAMP_PHANTOM_RACE, series="F1"),
            ps.with_breakdown(ps.PRIMER_B, series="F1"),
        ),
        session,
        verifier=FakeVerifier(),
    )
    assert out.status == "no_signal"
    decisions = {c.company_raw: c.decision for c in session.scalars(select(Candidate))}
    assert decisions["Ramp"] == CandidateDecision.verification_blocked
    assert decisions["Primer"] == CandidateDecision.not_selected


# --- §9.2 1Komma5° fabricated figures ------------------------------------------------------
# The specific wrong revenue figure and phantom investor from the May-2026 1Komma5° brief
# are not on record in this repository (the n8n PDF is not in spec/). The ledger test
# therefore uses explicitly labelled placeholders for those two claim texts; the decision
# logic under test does not depend on the figures themselves.


def _onekomma5_ledger(session, verifier):
    from intel.models import Run

    run = Run(run_date=dt.date(2026, 5, 26))
    session.add(run)
    session.flush()
    cand = Candidate(
        run_id=run.id,
        company_raw="1Komma5°",
        company_norm="1komma5",
        raw_json=dict(ps.ONEKOMMA5),
    )
    session.add(cand)
    session.flush()
    brief = Brief(candidate_id=cand.id, run_date=run.run_date)
    session.add(brief)
    session.flush()
    drafts = [
        verify.ClaimDraft(
            "Philipp Schröder, CEO & Co-Founder at 1Komma5°",
            "decision_maker",
            ClaimType.person_role,
        ),
        verify.ClaimDraft(
            "<revenue figure as stated in the May-2026 brief — not supported by any source>",
            "the_case",
            ClaimType.revenue,
        ),
        verify.ClaimDraft(
            "<investor named in the May-2026 brief — not on the cap table>",
            "the_case",
            ClaimType.funding,
        ),
    ]
    return brief, verify.run_ledger(session, brief, drafts, "1Komma5°", run.run_date, verifier)


def test_unsupported_revenue_and_investor_land_in_needs_review_never_verified(session):
    verifier = FakeVerifier({"revenue figure": "unverified", "investor named": "unverified"})
    brief, result = _onekomma5_ledger(session, verifier)
    assert result.status == VerificationStatus.needs_review
    assert brief.verification_status == VerificationStatus.needs_review
    assert len(result.review) == 2 and result.blocking == []


def test_contradicted_investor_blocks(session):
    verifier = FakeVerifier({"revenue figure": "unverified", "investor named": "contradicted"})
    brief, result = _onekomma5_ledger(session, verifier)
    assert result.status == VerificationStatus.blocked
    assert brief.verification_status == VerificationStatus.blocked


def test_all_verified_is_the_only_route_to_verified(session):
    _, result = _onekomma5_ledger(session, FakeVerifier())
    assert result.status == VerificationStatus.verified
    assert result.counts == {"verified": 3}


def test_without_a_model_credential_nothing_is_verified(session):
    _, result = _onekomma5_ledger(session, verify.NoVerifier())
    assert result.status == VerificationStatus.needs_review
    assert all(
        "VERIFY BEFORE CIRCULATION" in v.notes for c in result.claims for v in c.verifications
    )


# --- sponsor-table check -------------------------------------------------------------------


def test_sponsorship_claim_in_table_verifies_and_absent_one_contradicts(session):
    load_seeds(session)
    ok = verify.check_sponsorship_claim(
        session, verify.ClaimDraft("Splunk at McLaren", "key_facts", ClaimType.sponsorship)
    )
    assert ok.status == VerificationResult.verified and ok.method == VerificationMethod.sponsor_db
    absent = verify.check_sponsorship_claim(
        session, verify.ClaimDraft("Anduril at Cadillac", "key_facts", ClaimType.sponsorship)
    )
    assert absent.status == VerificationResult.contradicted
    assert "snapshot" in absent.notes


def test_claims_from_signal_cover_person_key_facts_trigger_and_events():
    sig = ps.with_breakdown(ps.RAMP_PHANTOM_RACE, series="F1")
    drafts = verify.claims_from_signal(sig)
    types = [d.claim_type for d in drafts]
    assert types[0] == ClaimType.person_role and "Eric Glyman" in drafts[0].text
    assert ClaimType.date in types  # the trigger text
    assert types[-1] == ClaimType.event and "London" in drafts[-1].text
    assert all(d.load_bearing for d in drafts)
