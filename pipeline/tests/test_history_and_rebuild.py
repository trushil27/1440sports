"""The 5 Sep 2026 clean-up: historical review applied at export, FE calendars, Series/Team
columns in the backfill importer, and the single-company rebuild command."""

from __future__ import annotations

import datetime as dt
import json

from sqlalchemy import select

from intel import rebuild, scan, site_export, verify
from intel.backfill import import_daily_signals
from intel.config import Settings
from intel.models import Brief, CalendarEvent, Series
from intel.seed import load_seeds
from tests.fixtures import production_signals as ps
from tests.fixtures.ramp_brief import RAMP_WRITTEN
from tests.test_m3_verify import FakeVerifier
from tests.test_m4_pipeline import FakeWriter, _block


def test_review_file_parses_and_keys_normalise():
    review = site_export.load_review()
    assert review, "data/history_review.json must load"
    tdk = site_export.review_for(review, "2026-07-18", "TDK Corporation")
    assert tdk["status"] == "screened_out"
    tdk_lower = site_export.review_for(review, "2026-07-18", "tdk corporation")
    assert tdk_lower["reason_code"] == "existing_partner"
    dup = site_export.review_for(review, "2026-04-29", "Hightouch")
    assert dup["status"] == "duplicate_of" and dup["of"] == "2026-04-27|hightouch"
    assert site_export.review_for(review, "2026-05-19", "Armada") == {"status": "keep"}


def test_fe_calendars_are_seeded_for_both_seasons(session):
    load_seeds(session)
    s12 = session.scalars(
        select(CalendarEvent).where(CalendarEvent.series == Series.FE, CalendarEvent.season == 2026)
    ).all()
    s13 = session.scalars(
        select(CalendarEvent).where(CalendarEvent.series == Series.FE, CalendarEvent.season == 2027)
    ).all()
    assert len(s12) == 17 and len(s13) == 21
    assert s13[0].name == "Jeddah E-Prix" and str(s13[0].date_start) == "2026-12-18"
    # An FE mention made in 2026 may refer to the season opening in Dec 2026 (stored as 2027).
    draft = verify.ClaimDraft(
        "Jeddah E-Prix",
        "why_now_callout",
        verify.ClaimType.event,
        True,
        None,
        {"event": {"series": "FE", "place": "Jeddah", "kind": "E-Prix", "when": None}},
    )
    v = verify.check_event_claim(session, draft, dt.date(2026, 9, 5))
    assert v.status.value == "verified"
    bogus = verify.ClaimDraft(
        "Rome E-Prix",
        "why_now_callout",
        verify.ClaimType.event,
        True,
        None,
        {"event": {"series": "FE", "place": "Rome", "kind": "E-Prix", "when": None}},
    )
    bad = verify.check_event_claim(session, bogus, dt.date(2026, 9, 5))
    assert bad.status.value == "contradicted"


def test_backfill_importer_carries_series_and_team_columns(session, tmp_path):
    load_seeds(session)
    rows = [
        {
            "Date": "2026-08-25",
            "Company": "Emerald AI",
            "Score": "66",
            "Tier": "WARM",
            "Track": "1",
            "Person": "Varun Sivaram",
            "Role": "Founder & CEO",
            "Action": "$150M Series A at $1.05B",
            "Source": "https://www.businesswire.com/x",
            "Series": "FE",
            "Team": "Envision Racing",
            "Industry": "Energy Software · Grid",
        }
    ]
    path = tmp_path / "fe_signals_test.json"
    path.write_text(json.dumps(rows))
    res = import_daily_signals(session, path)
    assert res["created"] == 1
    brief = session.scalar(select(Brief).where(Brief.historical.is_(True)))
    assert brief.candidate.series == Series.FE
    assert brief.candidate.recommended_team == "Envision Racing"
    assert brief.brief_data["series_label"] == "FE"
    assert brief.brief_data["historical_source"] == "fe_signals_test"
    card = site_export.brief_card(brief)
    assert site_export.infer_series(card, brief.brief_data) == ("FE", False)


class OneShotClient:
    def __init__(self, text: str) -> None:
        self.text, self.calls = text, []

    def create_text(self, *, model, system, messages, tools):
        self.calls.append({"system": system, "messages": messages, "tools": tools})
        return self.text


def test_single_company_prompt_and_rebuild_issue_a_brief_on_the_original_date(
    session, migrated_database, tmp_path
):
    load_seeds(session)
    system, user = scan.single_company_prompts("Ramp", dt.date(2026, 6, 14), hint="$750M round")
    assert "ONE named company only: Ramp" in user and "$750M round" in user
    assert "FIVE dimensions 0-20 each" in system
    row = dict(ps.RAMP_JUNE_ROUND)
    row["score_breakdown"] = ps.synthetic_split(row["score"])
    client = OneShotClient(json.dumps([row]))
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        anthropic_api_key="x",
    )
    stages = rebuild.run_daily.Stages(
        verifier=FakeVerifier(), writer=FakeWriter([_block(RAMP_WRITTEN)]), font_stack="june"
    )
    out = rebuild.rebuild("Ramp", dt.date(2026, 6, 14), settings, client, stages, session)
    assert out.status == "success" and out.verification_status == "verified"
    brief = session.get(Brief, out.brief_id)
    assert brief.run_date == dt.date(2026, 6, 14) and brief.pdf_path and brief.web_html_path
    assert client.calls[0]["tools"][0]["type"] == "web_search_20260209"
    assert stages.distribute is False


def test_rebuild_runs_again_on_a_taken_day_and_keeps_the_live_brief(
    session, migrated_database, tmp_path
):
    """A rebuild never returns 'already ran': on a day that has a live brief it stores the
    new case with ``historical=True`` (label kept), is not dedup-suppressed for the company
    it rebuilds, and the daily job still sees the live brief as that day's outcome."""
    load_seeds(session)
    row = dict(ps.RAMP_JUNE_ROUND)
    row["score_breakdown"] = ps.synthetic_split(row["score"])
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        anthropic_api_key="x",
    )
    day = dt.date(2026, 6, 15)

    def run_once():
        stages = rebuild.run_daily.Stages(
            verifier=FakeVerifier(), writer=FakeWriter([_block(RAMP_WRITTEN)]), font_stack="june"
        )
        return rebuild.rebuild(
            "Ramp", day, settings, OneShotClient(json.dumps([row])), stages, session
        )

    first = run_once()
    assert first.status == "success" and not first.already_ran
    live = session.get(Brief, first.brief_id)
    assert live.historical is False

    second = run_once()
    assert second.status == "success" and not second.already_ran
    again = session.get(Brief, second.brief_id)
    assert again.id != live.id
    assert again.historical is True  # the day already had a live brief
    assert again.brief_data["rebuilt"] is True
    assert again.brief_data["historical_label"] == f"N° {again.brief_number}"
    assert again.candidate.decision.value == "selected"  # not dedup-suppressed
    assert again.candidate.run.summary["rebuild"] is True

    # the daily job for that date is still final on the live brief
    outcome = rebuild.run_daily.run_day(
        day, settings, lambda _d: [], session, stages=rebuild.run_daily.Stages(distribute=False)
    )
    assert outcome.already_ran and outcome.brief_id == live.id
