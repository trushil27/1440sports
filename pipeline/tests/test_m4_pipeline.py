"""M4 end to end: write → 13-rule audit (one retry) → stage-B ledger → render → persist."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from sqlalchemy import select

from intel import render, run_daily
from intel.config import Settings
from intel.models import AuditStatus, Brief, Candidate, CandidateDecision, SurfacedLog
from intel.seed import load_seeds
from tests.fixtures import production_signals as ps
from tests.fixtures.ramp_brief import RAMP_WRITTEN
from tests.test_m3_verify import FakeVerifier

RUN_DATE = dt.date(2026, 6, 14)


class FakeWriter:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = list(outputs)
        self.calls: list[tuple[str, str]] = []

    def write(self, *, model: str, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self.outputs.pop(0) if len(self.outputs) > 1 else self.outputs[0]


def _block(data: dict) -> str:
    return (
        "<BRIEF_DATA>\n" + json.dumps(data, ensure_ascii=False) + "\n</BRIEF_DATA>\n"
        '<SIGNAL_DATA>{"signal_date": "2026-06-04", "top_signal": {}, "signals_log": []}'
        "</SIGNAL_DATA>"
    )


def _ramp_signal():
    # The five-dimension split is the REAL one recorded for Ramp N° 017 in this repo
    # (data/prospects.json → briefs/2026-06-14/ramp.md): 19/20/19/14/12 = 84.
    return ps.with_breakdown(
        ps.RAMP_JUNE_ROUND,
        series="F1",
        score=84,
        score_breakdown={
            "timing": 19,
            "capacity": 20,
            "brand_fit": 19,
            "urgency": 14,
            "ops_fit": 12,
        },
        recommended_team="Visa Cash App Racing Bulls",
        industry_meta="Fintech · Corporate Spend Management / AI Finance",
    )


def _settings(url: str, tmp: Path, **kw) -> Settings:
    return Settings(
        database_url=url, execution_mode="dry_run", pdf_storage_dir=str(tmp / "briefs"), **kw
    )


def _stages(writer_outputs: list[str]) -> run_daily.Stages:
    return run_daily.Stages(
        verifier=FakeVerifier(), writer=FakeWriter(writer_outputs), font_stack="june"
    )


def test_end_to_end_verified_brief_is_rendered_and_persisted(session, migrated_database, tmp_path):
    load_seeds(session)
    stages = _stages([_block(RAMP_WRITTEN)])
    out = run_daily.run_day(
        RUN_DATE,
        _settings(migrated_database, tmp_path),
        lambda _d: [_ramp_signal()],
        session,
        stages=stages,
    )
    detail = json.dumps(out.summary, default=str)
    assert out.status == "success", detail
    assert out.verification_status == "verified" and out.audit_status == "pass", detail
    brief = session.get(Brief, out.brief_id)
    assert (
        brief.page_count == 2 and Path(brief.pdf_path).exists() and Path(brief.html_path).exists()
    )
    assert brief.mode.value == "B"  # fintech + OF < 14 → MODE B (production_roadmap §2.1.8)
    data = brief.brief_data
    assert data["deck"].startswith("Ramp closed a $750M round")
    assert any("$750M" in p["value"] or "$44B" in p["value"] for p in data["proof_points"])
    assert all(p["verified"] for p in data["proof_points"]) and data["all_proof_points_verified"]
    assert data["decision_maker_verified"] is True
    # evidence URLs from the verifier come first, then the cited sources
    assert data["sources"] and any("techcrunch.com" in s for s in data["sources"])
    grid = data["gridfit"]
    assert grid and grid[0]["recommended"] and "Racing Bulls" in grid[0]["team"]
    assert data["claims_total"] > 0 and data["claims_verified"] == data["claims_total"]
    # the writer got the spec prompt + addendum and today's date; surfaced_log points at the brief
    system, user = stages.writer.calls[0]
    assert "You are the 1440Sports Brief Writer" in system and "JUNE-2026 FORMAT ADDENDUM" in system
    assert "TODAY'S DATE (use for footer_date — NOT signal article date): 14 JUN 2026" in user
    assert "=== RETRY MODE" not in user  # first draft: the retry slot is empty
    assert "Company: Ramp" in user and "VALUE SECTION MODE" in user
    # brief numbers come from the global sequence (never reset, never reused)
    assert f"Brief number: {brief.brief_number:03d}" in user
    assert session.scalar(select(SurfacedLog)).brief_id == brief.id
    assert render.brief_status_for_md(brief) is True


def test_audit_violations_are_fed_back_once_then_pass_after_retry(
    session, migrated_database, tmp_path
):
    load_seeds(session)
    bad = dict(
        RAMP_WRITTEN,
        deal_arch_para="Entry tier. TWO YEARS at $6-9M/yr with Silverstone hospitality.",
    )
    stages = _stages([_block(bad), _block(RAMP_WRITTEN)])
    out = run_daily.run_day(
        RUN_DATE,
        _settings(migrated_database, tmp_path),
        lambda _d: [_ramp_signal()],
        session,
        stages=stages,
    )
    assert out.status == "success" and out.audit_status == "pass_after_retry"
    brief = session.get(Brief, out.brief_id)
    assert brief.audit_attempts == 2
    _, retry_user = stages.writer.calls[1]
    # the production Retry Prep block with the `- [SEVERITY] code: detail` violation lines
    assert "=== RETRY MODE - CORRECTING PREVIOUS DRAFT ===" in retry_user
    assert "- [CRITICAL] min_3_year_deal: deal_arch_para proposes TWO YEARS" in retry_user
    assert "- [CRITICAL] missing_duration_marker:" in retry_user


def test_failed_audit_is_kept_for_operator_and_never_md_eligible(
    session, migrated_database, tmp_path
):
    load_seeds(session)
    bad = dict(
        RAMP_WRITTEN,
        deal_arch_para="Entry tier. TWO YEARS at $6-9M/yr with Silverstone hospitality.",
    )
    stages = _stages([_block(bad), _block(bad)])
    out = run_daily.run_day(
        RUN_DATE,
        _settings(migrated_database, tmp_path),
        lambda _d: [_ramp_signal()],
        session,
        stages=stages,
    )
    assert out.status == "success" and out.audit_status == "failed"
    brief = session.get(Brief, out.brief_id)
    assert brief.audit_status == AuditStatus.failed
    assert any(v["rule"] == 1 for v in brief.audit_violations)
    assert brief.pdf_path and Path(brief.pdf_path).exists()  # rendered for operator review
    assert render.brief_status_for_md(brief) is False


def test_phantom_race_written_into_the_brief_blocks_at_stage_b(
    session, migrated_database, tmp_path
):
    load_seeds(session)
    haunted = dict(
        RAMP_WRITTEN,
        why_now_callout=(
            "<font name='Poppins-Bold' size='9'>WHY NOW</font>&nbsp;&nbsp;The $750M raise has just "
            "closed and the F1 London race August 2026 is the activation window."
        ),
    )
    stages = _stages([_block(haunted)])
    out = run_daily.run_day(
        RUN_DATE,
        _settings(migrated_database, tmp_path),
        lambda _d: [_ramp_signal()],
        session,
        stages=stages,
    )
    assert out.status == "no_signal"
    cand = session.scalar(select(Candidate))
    assert cand.decision == CandidateDecision.verification_blocked
    assert "London" in cand.decision_reason
    brief = session.scalar(select(Brief))
    assert brief.verification_status.value == "blocked" and brief.pdf_path is None
    assert session.scalar(select(SurfacedLog)) is None


def test_without_a_writer_the_brief_stays_pending_for_the_operator(
    session, migrated_database, tmp_path
):
    load_seeds(session)
    stages = run_daily.Stages(verifier=FakeVerifier(), writer=None)
    out = run_daily.run_day(
        RUN_DATE,
        _settings(migrated_database, tmp_path),
        lambda _d: [_ramp_signal()],
        session,
        stages=stages,
    )
    assert out.status == "success" and out.audit_status == "pending" and out.pdf_path is None
    brief = session.get(Brief, out.brief_id)
    assert brief.brief_data is None
    assert "writer unavailable" in brief.audit_violations[0]["note"]
    assert render.brief_status_for_md(brief) is False
