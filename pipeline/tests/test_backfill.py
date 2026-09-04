"""M6 acceptance: prior briefs import as historical / unverified, idempotently, with
negative brief numbers, and the live per-day rule is untouched."""

from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from intel import backfill
from intel.config import reset_settings
from intel.models import (
    Brief,
    Candidate,
    Claim,
    Run,
    SurfacedLog,
    Verification,
    VerificationMethod,
    VerificationResult,
    VerificationStatus,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SIGNALS_ROWS = json.loads(backfill.DEFAULT_SIGNALS_FILE.read_text(encoding="utf-8"))["rows"]
HISTORY = json.loads((REPO_ROOT / "briefs" / "history.json").read_text(encoding="utf-8"))["log"]
HISTORY_WITH_PDF = [
    e for e in HISTORY if (REPO_ROOT / "briefs" / e["date"] / f"{e['id']}.pdf").exists()
]


@pytest.fixture()
def storage(session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    store = tmp_path / "store"
    monkeypatch.setenv("PDF_STORAGE_DIR", str(store))
    reset_settings()
    return store


def _count(session, model) -> int:
    return session.scalar(select(func.count()).select_from(model))


# --- 1. n8n daily signals log -----------------------------------------------------------------


def test_daily_signals_import_is_historical_unverified_and_idempotent(session, storage):
    out = backfill.import_daily_signals(session)
    assert len(SIGNALS_ROWS) == 128
    assert out["created"] == 128 and out["skipped"] == 0 and out["failed"] == 0

    briefs = session.scalars(select(Brief)).all()
    assert len(briefs) == 128
    assert all(b.historical for b in briefs)
    assert all(b.brief_number < 0 for b in briefs)
    assert sorted(b.brief_number for b in briefs) == list(range(-128, 0))
    assert all(b.verification_status == VerificationStatus.needs_review for b in briefs)
    assert all(b.brief_data["historical_source"] == backfill.SOURCE_SIGNALS for b in briefs)

    # First row in file order gets −1 and its fields verbatim from the log.
    first = session.scalar(select(Brief).where(Brief.brief_number == -1))
    row = SIGNALS_ROWS[0]
    assert first.brief_data["company"] == row["Company"]
    assert first.brief_data["decision_maker_name"] == row["Person"]
    assert first.brief_data["decision_maker_role"] == row["Role"]
    assert first.brief_data["deck"] == row["Action"]
    assert first.brief_data["horizon_label"] == row["Horizon"]
    assert first.brief_data["timing_label"] == row["Tier"]
    assert first.brief_data["score"] == int(row["Score"])
    assert first.brief_data["signal_date"] == row["Date"]
    assert first.brief_data["industry_meta"] is None and first.brief_data["team_label"] is None
    assert first.run_date == dt.date.fromisoformat(row["Date"])
    cand = first.candidate
    assert cand.company_raw == row["Company"] and cand.trigger_reason_raw == row["Action"]
    assert cand.source_url == row["Source"] and cand.score_total == int(row["Score"])
    assert cand.raw_json == row
    assert cand.run.summary == {"source": backfill.SOURCE_SIGNALS, "backfill": True}

    # Track values outside {1,2} default to 1 with the raw value kept.
    odd = [r for r in SIGNALS_ROWS if r["Track"] not in {"1", "2"}]
    assert odd
    for r in odd:
        c = session.scalar(
            select(Candidate).where(
                Candidate.company_raw == r["Company"], Candidate.trigger_reason_raw == r["Action"]
            )
        )
        assert c.track == 1 and c.raw_json["Track"] == r["Track"]

    # Claims: person/role + trigger per row, every one unverified / manual.
    assert _count(session, Claim) == 2 * 128
    verifications = session.scalars(select(Verification)).all()
    assert len(verifications) == 2 * 128
    assert all(v.status == VerificationResult.unverified for v in verifications)
    assert all(v.method == VerificationMethod.manual for v in verifications)
    assert all(v.notes == backfill.IMPORT_NOTE for v in verifications)

    # Several signals on one date are allowed for historical briefs (Primer ×3 on 05-20).
    same_day = [r for r in SIGNALS_ROWS if r["Date"] == "2026-05-20"]
    assert len(same_day) >= 3
    n = session.scalar(
        select(func.count()).select_from(Brief).where(Brief.run_date == dt.date(2026, 5, 20))
    )
    assert n == len(same_day)
    assert _count(session, Run) == len({r["Date"] for r in SIGNALS_ROWS})

    # surfaced_log upsert keyed on (company_norm, trigger key)
    log = session.scalar(
        select(SurfacedLog).where(
            SurfacedLog.company_norm == "shieldai", SurfacedLog.brief_id == first.id
        )
    )
    assert log is not None
    assert log.first_surfaced_at.astimezone(dt.UTC).hour in (5, 6)  # 06:00 Europe/London
    assert _count(session, SurfacedLog) < 128  # repeated company+trigger pairs collapsed

    # Idempotent.
    again = backfill.import_daily_signals(session)
    assert again["created"] == 0 and again["skipped"] == 128
    assert _count(session, Brief) == 128
    assert _count(session, Claim) == 2 * 128
    assert _count(session, Run) == len({r["Date"] for r in SIGNALS_ROWS})


# --- 2. this repo's engine output ----------------------------------------------------------------


def test_repo_import_maps_prospect_records_and_copies_pdfs(session, storage):
    out = backfill.import_repo_briefs(session)
    assert out["created"] == len(HISTORY_WITH_PDF) and out["failed"] == 0
    assert _count(session, Brief) == len(HISTORY_WITH_PDF)

    ramp = session.scalar(
        select(Brief).where(Brief.brief_data["historical_label"].astext == "N° 017")
    )
    assert ramp is not None and ramp.historical
    assert ramp.run_date == dt.date(2026, 6, 14)
    assert ramp.verification_status == VerificationStatus.needs_review
    bd = ramp.brief_data
    assert bd["deck"].startswith("Ramp closed a $750M round")
    assert len(bd["proof_points"]) == 6
    assert all(p["verified"] is False for p in bd["proof_points"])
    assert bd["company"] == "Ramp" and bd["team_label"] == "Visa Cash App Racing Bulls"
    assert bd["series_label"] == "F1" and bd["why_team_label"] == "WHY VISA CASH APP RACING BULLS"
    assert bd["score"] == 84 and bd["timing_label"] == "HOT"
    assert bd["decision_maker_name"] == "Eric Glyman"
    assert len(bd["score_cells"]) == 5 and bd["score_cells"][0]["denom"] == "/ 20"
    assert bd["risks"][0]["label"] == "Visa channel conflict"
    assert bd["footer_company"] == "RAMP" and bd["footer_date"] == "14 JUN 2026"
    assert bd["historical"] is True and bd["historical_source"] == backfill.SOURCE_REPO

    assert ramp.pdf_path == str(storage / "historical" / "2026-06-14_ramp.pdf")
    assert Path(ramp.pdf_path).exists()
    assert ramp.html_path == str(storage / "historical" / "2026-06-14_ramp.html")
    assert Path(ramp.html_path).exists()
    assert ramp.page_count == 2
    assert ramp.candidate.recommended_team == "Visa Cash App Racing Bulls"
    assert ramp.candidate.trigger_reason_raw == "funding_event, new_leadership, category_whitespace"
    assert ramp.candidate.raw_json["prospect_id"] == "ramp"

    # Claims: one per key_fact (funding when the value carries a currency) + decision-maker.
    claims = sorted(ramp.claims, key=lambda c: c.position)
    assert len(claims) == 7
    assert claims[0].claim_type.value == "funding" and claims[0].cited_source_url
    assert claims[-1].claim_type.value == "person_role"
    assert all(
        v.status == VerificationResult.unverified and v.method == VerificationMethod.manual
        for c in claims
        for v in c.verifications
    )

    # Idempotent.
    again = backfill.import_repo_briefs(session)
    assert again["created"] == 0 and again["skipped"] == len(HISTORY_WITH_PDF)
    assert _count(session, Brief) == len(HISTORY_WITH_PDF)


def test_negative_numbers_continue_across_sources(session, storage):
    backfill.import_daily_signals(session)
    backfill.import_repo_briefs(session)
    total = 128 + len(HISTORY_WITH_PDF)
    assert _count(session, Brief) == total
    assert session.scalar(select(func.min(Brief.brief_number))) == -total
    assert session.scalar(select(func.max(Brief.brief_number))) == -1


# --- 3. operator-exported PDFs -------------------------------------------------------------------


def test_attach_pdfs_matches_by_date_and_company(session, storage, tmp_path: Path):
    backfill.import_daily_signals(session)
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    src = REPO_ROOT / "briefs" / "2026-07-03" / "cerebras.pdf"
    shutil.copyfile(src, inbox / "2026-05-07_Cerebras Systems.pdf")
    shutil.copyfile(src, inbox / "2026-01-01_Nobody Ltd.pdf")
    (inbox / "notes.txt").write_text("not a pdf")

    out = backfill.attach_pdfs(session, inbox)
    assert out["attached"] == 1 and out["skipped"] == 0
    assert {u["file"] for u in out["unmatched"]} == {"2026-01-01_Nobody Ltd.pdf", "notes.txt"}

    brief = session.scalar(
        select(Brief)
        .join(Candidate, Candidate.id == Brief.candidate_id)
        .where(Brief.run_date == dt.date(2026, 5, 7), Candidate.company_norm == "cerebrassystems")
    )
    assert brief.pdf_path == str(storage / "historical" / "2026-05-07_Cerebras Systems.pdf")
    assert Path(brief.pdf_path).exists() and brief.page_count == 2

    again = backfill.attach_pdfs(session, inbox)
    assert again["attached"] == 0 and again["skipped"] == 1


# --- sequence + live rule -------------------------------------------------------------------------


def _live_brief(session, day: dt.date, name: str, **kw) -> Brief:
    run = session.scalar(select(Run).where(Run.run_date == day, Run.attempt == 99))
    if run is None:
        run = Run(run_date=day, attempt=99)
        session.add(run)
        session.flush()
    c = Candidate(run_id=run.id, company_raw=name, company_norm=name.lower(), raw_json={})
    session.add(c)
    session.flush()
    b = Brief(candidate_id=c.id, run_date=day, **kw)
    session.add(b)
    session.flush()
    return b


def test_restart_sequence_sets_next_live_number(session, storage):
    backfill.import_daily_signals(session)
    backfill.restart_sequence(session, backfill.FIRST_FREE_N8N_NUMBER)
    assert backfill.FIRST_FREE_N8N_NUMBER == 121
    live = _live_brief(session, dt.date(2026, 9, 4), "Alpha")
    assert live.brief_number == 121
    assert live.historical is False


def test_live_day_uniqueness_still_holds_alongside_historical(session, storage):
    backfill.import_daily_signals(session)
    day = dt.date(2026, 5, 7)  # a date with several historical briefs
    _live_brief(session, day, "Alpha")  # one live brief on a historical day is fine
    with pytest.raises(IntegrityError):
        _live_brief(session, day, "Beta")
