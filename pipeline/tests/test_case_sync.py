"""The daily run saves its own case(s) into the repo: --sync exports every full case without a
record; imported records are not re-exported; the export ships PDFs next to the app."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

from intel import backfill, case_record, site_export
from intel.models import Brief


def test_sync_exports_only_full_cases_without_a_record(session, tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_STORAGE_DIR", str(tmp_path / "store"))
    from intel.config import reset_settings

    reset_settings()
    backfill.import_daily_signals(
        session, backfill.BACKFILL_DIR / "fe_sweep_signals_2026-09-05.json"
    )
    backfill.import_engine_cases(session)  # Crusoe + Fervo arrive with engine_case_key
    out = tmp_path / "cases"
    assert case_record.sync_cases(session, out) == []  # imported records are not re-exported

    # a brief that has a page but no record (what the daily run produces) is exported once
    crusoe = session.scalar(
        select(Brief).where(Brief.brief_data["engine_case_key"].astext.like("%crusoe"))
    )
    crusoe.brief_data = {k: v for k, v in crusoe.brief_data.items() if k != "engine_case_key"}
    session.flush()
    written = case_record.sync_cases(session, out)
    assert len(written) == 1
    rec = Path(written[0]["record"])
    assert rec.name == "crusoe.run.json" and rec.parent.name == "2026-09-05"
    assert (rec.parent / "crusoe.pdf").exists() and (rec.parent / "crusoe.web.html").exists()
    assert case_record.sync_cases(session, out) == []  # idempotent


def test_site_export_ships_pdfs_for_full_cases(session, tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_STORAGE_DIR", str(tmp_path / "store"))
    from intel.config import reset_settings

    reset_settings()
    backfill.import_engine_cases(session)
    data = site_export.export_data(session)
    out = tmp_path / "site"
    site_export.write_site(data, out)
    pdfs = sorted(p.name for p in (out / "pdf").glob("*.pdf"))
    assert any(n.endswith("-crusoe.pdf") for n in pdfs)
    row = next(e for e in data["briefs"] if e["company"] == "Crusoe")
    assert row["pdf_url"].startswith("pdf/") and "pdf_path" not in row
    # The home card carries the PDF of the brief it is actually showing.
    today_row = next(e for e in data["briefs"] if e["number"] == data["today"]["number"])
    assert data["today"]["pdf_url"] == today_row["pdf_url"]
    assert "pdf_path" not in (out / "data.json").read_text(encoding="utf-8")


def test_unbuilt_signals_get_a_queue_position(session, tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_STORAGE_DIR", str(tmp_path / "store"))
    from intel.config import reset_settings

    reset_settings()
    backfill.import_daily_signals(
        session, backfill.BACKFILL_DIR / "fe_sweep_signals_2026-09-05.json"
    )
    backfill.import_engine_cases(session)
    data = site_export.export_data(session)
    unbuilt = [e for e in data["briefs"] if e.get("backlog_position")]
    assert unbuilt and data["backlog_size"] == len(unbuilt)
    assert [e["backlog_position"] for e in unbuilt] == list(range(1, len(unbuilt) + 1))
    assert all("page_html" not in e for e in unbuilt)
    assert "backlog_position" not in next(e for e in data["briefs"] if e["company"] == "Crusoe")
    assert data["backlog_per_run"] == 1
