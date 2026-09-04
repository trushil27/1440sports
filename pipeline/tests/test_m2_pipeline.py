"""M2 regression suite — build brief §9 tests 3, 4, 5, 6 and 8, on the real production cases."""

from __future__ import annotations

import datetime as dt
import json

import pytest
from sqlalchemy import func, select

from intel import dedup, freshness, run_daily, score
from intel.config import Settings
from intel.models import Blocklist, BlocklistStatus, Candidate, CandidateDecision, Run
from intel.parse import ParseError, extract_json_array, parse_scan_output
from tests.fixtures import production_signals as ps


def _settings(url: str, **overrides) -> Settings:
    return Settings(database_url=url, execution_mode="dry_run", **overrides)


def _scanner(*signals):
    return lambda _date: list(signals)


# --- §9.6 stray-bracket output -------------------------------------------------------------


def test_stray_bracket_inside_string_and_prose_still_parses():
    row = dict(ps.PRIMER_A)
    row["score_breakdown"] = ps.synthetic_split(row["score"])
    row["key_facts"] = {"strategic_hook": "US expansion [50 hires", "investors": "Sofina]"}
    text = (
        "Here are today's signals [ranked best first]:\n```json\n"
        + json.dumps([row], ensure_ascii=False)
        + "\n```\nNote: scores are out of 100]. Sources checked [Tier 1]."
    )
    signals = parse_scan_output(text)
    assert len(signals) == 1
    assert signals[0].company == "Primer"
    assert signals[0].key_facts.strategic_hook == "US expansion [50 hires"


def test_truncated_output_raises_parse_error_with_feedback():
    text = '[{"company": "Primer", "score": 85, "signal_date": "2026-05-20"'
    with pytest.raises(ParseError, match="no JSON array"):
        extract_json_array(text)


def test_validation_error_names_the_item_and_field():
    text = json.dumps([{"company": "Primer", "score": 850, "track": 1}])
    with pytest.raises(ParseError, match=r"item 0 \(Primer\): score"):
        parse_scan_output(text)


# --- §9.5 stale triggers — date arithmetic, before scoring -------------------------------


@pytest.mark.parametrize(
    ("trigger", "run_date"),
    [
        (ps.STRAVA["signal_date"], dt.date(2026, 5, 19)),  # logged 2026-01-01, surfaced in May
        ("January 2026", dt.date(2026, 5, 19)),  # the wording in Strava's logged trigger
        (ps.ONEKOMMA5["signal_date"], dt.date(2026, 5, 26)),  # "July 2025", surfaced 26 May 2026
    ],
)
def test_stale_triggers_are_rejected_by_arithmetic(trigger, run_date):
    d = freshness.check_freshness(trigger, run_date, window_days=14)
    assert not d.fresh
    assert d.age_days is not None and d.age_days > 14


def test_month_precision_uses_last_day_of_month():
    parsed = freshness.parse_trigger_date("July 2025")
    assert parsed == freshness.ParsedDate(dt.date(2025, 7, 31), "month")


def test_fresh_trigger_passes_and_missing_date_does_not():
    assert freshness.check_freshness("2026-05-08", dt.date(2026, 5, 9), 14).fresh
    assert not freshness.check_freshness(None, dt.date(2026, 5, 9), 14).fresh
    assert freshness.check_freshness("2026-05-08", dt.date(2026, 5, 22), 14).fresh
    assert not freshness.check_freshness("2026-05-08", dt.date(2026, 5, 23), 14).fresh


def test_stale_candidates_never_reach_scoring(session, migrated_database):
    s = _settings(migrated_database)
    out = run_daily.run_day(
        dt.date(2026, 5, 26),
        s,
        _scanner(ps.with_breakdown(ps.STRAVA), ps.with_breakdown(ps.ONEKOMMA5)),
        session,
    )
    assert out.status == "no_signal"
    rows = session.scalars(select(Candidate)).all()
    assert {r.decision for r in rows} == {CandidateDecision.stale}
    assert all(r.score_total is None for r in rows)  # scoring never ran


# --- §9.3 Lime / "Lime (Neutron Holdings)" ---------------------------------------------


def test_trigger_classes_for_the_real_lime_and_primer_wordings():
    assert dedup.trigger_key(ps.LIME_S1_A["trigger_reason"]) == "ipo_filing"
    assert dedup.trigger_key(ps.LIME_S1_B["trigger_reason"]) == "ipo_filing"
    assert dedup.trigger_key(ps.LIME_ROADSHOW["trigger_reason"]) == "ipo_roadshow"
    assert {
        dedup.trigger_key(r["trigger_reason"]) for r in (ps.PRIMER_A, ps.PRIMER_B, ps.PRIMER_C)
    } == {"funding_round"}
    assert dedup.trigger_key(ps.RAMP_PHANTOM_RACE["trigger_reason"]) == "funding_round"


def test_lime_neutron_holdings_is_suppressed_within_30_days(session, migrated_database):
    s = _settings(migrated_database)
    day1 = run_daily.run_day(
        dt.date(2026, 5, 8), s, _scanner(ps.with_breakdown(ps.LIME_S1_A)), session
    )
    assert day1.status == "success"

    day2 = run_daily.run_day(
        dt.date(2026, 5, 9), s, _scanner(ps.with_breakdown(ps.LIME_S1_B)), session
    )
    assert day2.status == "no_signal"
    cand = session.scalar(select(Candidate).where(Candidate.run_id == day2.run_id))
    assert cand.company_norm == "lime"
    assert cand.decision == CandidateDecision.dedup_suppressed
    assert "same trigger" in cand.decision_reason


def test_same_company_new_trigger_passes_tagged_resurfaced(session, migrated_database):
    """Lime's real second trigger (IPO roadshow, 22 Jun) is a different class from the S-1."""
    s = _settings(migrated_database)
    run_daily.run_day(dt.date(2026, 5, 8), s, _scanner(ps.with_breakdown(ps.LIME_S1_A)), session)

    # 45 days later, outside the 30-day window: passes, not tagged.
    day3 = run_daily.run_day(
        dt.date(2026, 6, 22), s, _scanner(ps.with_breakdown(ps.LIME_ROADSHOW)), session
    )
    assert day3.status == "success"
    c3 = session.get(Candidate, day3.selected_candidate_id)
    assert c3.decision == CandidateDecision.selected and c3.resurfaced is False


def test_new_trigger_inside_the_window_is_tagged_resurfaced(session, migrated_database):
    wide = _settings(migrated_database, dedup_window_days=60)
    run_daily.run_day(dt.date(2026, 5, 8), wide, _scanner(ps.with_breakdown(ps.LIME_S1_A)), session)
    day3 = run_daily.run_day(
        dt.date(2026, 6, 22), wide, _scanner(ps.with_breakdown(ps.LIME_ROADSHOW)), session
    )
    assert day3.status == "success"
    c3 = session.get(Candidate, day3.selected_candidate_id)
    assert c3.decision == CandidateDecision.selected
    assert c3.resurfaced is True
    assert "resurfaced" in c3.decision_reason


# --- §9.4 Primer duplicate -------------------------------------------------------------


def test_primer_same_trigger_next_day_is_suppressed(session, migrated_database):
    s = _settings(migrated_database)
    day1 = run_daily.run_day(
        dt.date(2026, 5, 20), s, _scanner(ps.with_breakdown(ps.PRIMER_A)), session
    )
    assert day1.status == "success"
    day2 = run_daily.run_day(
        dt.date(2026, 5, 21),
        s,
        _scanner(ps.with_breakdown(ps.PRIMER_B), ps.with_breakdown(ps.PRIMER_C)),
        session,
    )
    assert day2.status == "no_signal"
    decisions = session.scalars(
        select(Candidate.decision).where(Candidate.run_id == day2.run_id)
    ).all()
    assert decisions == [CandidateDecision.dedup_suppressed, CandidateDecision.dedup_suppressed]


# --- blocklist is a database rule ---------------------------------------------------------


def test_cooling_blocklist_entry_suppresses_before_scoring(session, migrated_database):
    session.add(
        Blocklist(
            company_raw="Lime",
            company_norm="lime",
            status=BlocklistStatus.cooling,
            reason="test: outreach happened",
            added_at=dt.date(2026, 4, 1),
            cooling_until=dt.date(2026, 10, 1),
        )
    )
    session.flush()
    s = _settings(migrated_database)
    out = run_daily.run_day(
        dt.date(2026, 5, 8), s, _scanner(ps.with_breakdown(ps.LIME_S1_A)), session
    )
    assert out.status == "no_signal"
    cand = session.scalar(select(Candidate))
    assert cand.decision == CandidateDecision.blocklisted


# --- threshold + selection -------------------------------------------------------------


def test_threshold_is_config_and_applied_after_gates(session, migrated_database):
    strict = _settings(migrated_database, md_threshold=85)
    out = run_daily.run_day(
        dt.date(2026, 5, 8), strict, _scanner(ps.with_breakdown(ps.LIME_S1_A)), session
    )
    assert out.status == "no_signal"
    cand = session.scalar(select(Candidate))
    assert cand.decision == CandidateDecision.below_threshold
    assert cand.score_total == 84


def test_fe_rotation_forces_fe_on_tuesdays_and_fridays():
    pool = [(84, "F1", "f1-top"), (75, "FE", "fe-top"), (60, "FE", "fe-low")]
    assert score.select_top(pool, dt.date(2026, 5, 8)) == "fe-top"  # Friday
    assert score.select_top(pool, dt.date(2026, 5, 5)) == "fe-top"  # Tuesday
    assert score.select_top(pool, dt.date(2026, 5, 6)) == "f1-top"  # Wednesday
    assert score.select_top(pool, dt.date(2026, 5, 9)) == "f1-top"  # Saturday: score only
    assert (
        score.select_top([(84, "F1", "f1-top")], dt.date(2026, 5, 8)) == "f1-top"
    )  # no FE eligible


def test_gate_bookkeeping_is_recorded(session, migrated_database):
    s = _settings(migrated_database)
    out = run_daily.run_day(
        dt.date(2026, 5, 8), s, _scanner(ps.with_breakdown(ps.LIME_S1_A)), session
    )
    cand = session.get(Candidate, out.selected_candidate_id)
    assert cand.gate_results["gate0_source"]["tier"] == 1  # techcrunch.com
    assert cand.gate_results["of_gate"]["applied"] is True
    assert cand.gate_results["preflight"]["outcome"] == "CLEAN"
    assert cand.score_breakdown["total"] == 84 and cand.alumni_boost == 0
    assert cand.tier == "HOT"


# --- §9.8 idempotent day ---------------------------------------------------------------


def test_running_twice_for_the_same_date_is_a_no_op(session, migrated_database):
    s = _settings(migrated_database)
    first = run_daily.run_day(
        dt.date(2026, 5, 8), s, _scanner(ps.with_breakdown(ps.LIME_S1_A)), session
    )
    second = run_daily.run_day(
        dt.date(2026, 5, 8), s, _scanner(ps.with_breakdown(ps.LIME_S1_B)), session
    )
    assert second.already_ran is True
    assert second.selected_candidate_id == first.selected_candidate_id
    assert session.scalar(select(func.count()).select_from(Run)) == 1
    assert session.scalar(select(func.count()).select_from(Candidate)) == 1


def test_failed_run_is_retried_as_attempt_two(session, migrated_database):
    from intel.scan import ScanFailed

    def boom(_date):
        raise ScanFailed("scanner output unparseable after retry")

    s = _settings(migrated_database)
    failed = run_daily.run_day(dt.date(2026, 5, 8), s, boom, session)
    assert failed.status == "failed"
    ok = run_daily.run_day(
        dt.date(2026, 5, 8), s, _scanner(ps.with_breakdown(ps.LIME_S1_A)), session
    )
    assert ok.status == "success" and ok.already_ran is False
    attempts = session.scalars(select(Run.attempt).where(Run.run_date == dt.date(2026, 5, 8))).all()
    assert sorted(attempts) == [1, 2]
