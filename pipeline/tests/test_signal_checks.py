"""Signal-level fact-checks: the checked-in file decides each historical row's status in the app
and is written into the ledger by the backfill."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select

from intel import backfill, checks, site_export
from intel.models import Brief, Claim, VerificationStatus

SWEEP = backfill.BACKFILL_DIR / "fe_sweep_signals_2026-09-05.json"


def _checks_file(tmp_path: Path) -> Path:
    data = {
        "checked_at": "2026-09-05",
        "checks": [
            {
                "key": "2026-09-05|antora energy",
                "company": "Antora Energy",
                "trigger_status": "CORRECTED",
                "evidence_url": "https://example.com/antora",
                "evidence_excerpt": "Series C of $550M at a $2.47B valuation (30 Jul 2026).",
                "corrections": ["lead: recorded X → source says Y"],
                "person_status": "CONFIRMED",
                "person_note": "Andrew Ponec is CEO per the company site.",
                "motorsport_status": "NONE_FOUND",
                "motorsport_note": "none found in search",
                "updates": [{"date": "2026-08", "event": "opened a plant", "url": "https://e.com"}],
                "confidence": "HIGH",
                "notes": "",
            },
            {
                "key": "2026-09-05|byd",
                "company": "BYD",
                "trigger_status": "CONFIRMED",
                "evidence_url": "https://example.com/byd",
                "evidence_excerpt": "Trial production began.",
                "corrections": [],
                "person_status": "CONFIRMED",
                "person_note": "Stella Li is EVP.",
                "motorsport_status": "EXISTING_PARTNER",
                "motorsport_note": "BYD is an official partner of the Formula E championship.",
                "updates": [],
                "confidence": "MEDIUM",
                "notes": "existing partner",
            },
            {
                "key": "2026-09-05|waymo",
                "company": "Waymo",
                "trigger_status": "CONTRADICTED",
                "evidence_url": None,
                "evidence_excerpt": "",
                "corrections": [],
                "person_status": "NOT_FOUND",
                "person_note": "",
                "motorsport_status": "NONE_FOUND",
                "motorsport_note": "",
                "updates": [],
                "confidence": "LOW",
                "notes": "",
            },
        ],
    }
    p = tmp_path / "signal_checks.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_verdict_rules():
    assert checks.verdict({"trigger_status": "CONFIRMED", "person_status": "NA"})[0] == "verified"
    assert checks.verdict({"trigger_status": "CORRECTED", "person_status": "CONFIRMED"})[0] == (
        "verified"
    )
    assert checks.verdict({"trigger_status": "CONFIRMED", "person_status": "CHANGED"})[0] == (
        "verified"
    )
    assert checks.verdict({"trigger_status": "CONFIRMED", "person_status": "NOT_FOUND"})[0] == (
        "needs_review"
    )
    assert checks.verdict({"trigger_status": "NOT_FOUND"})[0] == "needs_review"
    assert checks.verdict({"trigger_status": "CONTRADICTED"})[0] == "contradicted"


def test_checks_attach_at_export_and_apply_to_the_ledger(session, tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_STORAGE_DIR", str(tmp_path / "store"))
    from intel.config import reset_settings

    reset_settings()
    backfill.import_daily_signals(session, SWEEP)
    path = _checks_file(tmp_path)
    loaded = checks.load_checks(path)
    assert set(loaded) >= {"antora energy", "byd", "waymo"}
    monkeypatch.setattr(checks, "CHECKS_FILE", path)

    # export: the row's status comes from the check; existing partner is flagged
    data = site_export.export_data(session)
    by = {e["company"]: e for e in data["briefs"]}
    assert by["Antora Energy"]["verification"] == "verified"
    assert by["Antora Energy"]["check"]["corrections"]
    assert by["BYD"]["review"]["status"] == "screened_out"  # existing partner leaves the lists
    assert by["BYD"]["review"]["reason"].startswith("existing partner: BYD is an official")
    assert by["Waymo"]["verification"] == "contradicted"
    assert data["checks_meta"]["records"] == 3 and data["checks_meta"]["rows_checked"] == 3

    # ledger: verification rows + brief status; idempotent
    res = backfill.apply_signal_checks(session, path)
    assert res["applied"] == 3
    antora = session.scalar(
        select(Brief).where(Brief.brief_data["company"].astext == "Antora Energy")
    )
    assert antora.verification_status == VerificationStatus.verified
    assert antora.brief_data["signal_check"]["trigger_status"] == "CORRECTED"
    trig = session.scalar(
        select(Claim).where(Claim.brief_id == antora.id, Claim.section == "trigger")
    )
    assert trig.verifications[-1].status.value == "verified"
    assert trig.verifications[-1].evidence_url == "https://example.com/antora"
    waymo = session.scalar(select(Brief).where(Brief.brief_data["company"].astext == "Waymo"))
    assert waymo.verification_status == VerificationStatus.blocked
    byd = session.scalar(select(Brief).where(Brief.brief_data["company"].astext == "BYD"))
    assert byd.verification_status == VerificationStatus.blocked  # existing partner
    again = backfill.apply_signal_checks(session, path)
    assert again["applied"] == 0 and again["skipped"] == 3
