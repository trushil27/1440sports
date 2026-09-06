"""intel.session_case — a case spec builds a verified case with no model call."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from intel import session_case
from intel.backfill import import_engine_cases
from intel.seed import load_seeds

SPEC = Path(__file__).resolve().parents[1] / "intel" / "cases" / "2026-09-06"
SPEC = SPEC / "fluidstack.case.json"


@pytest.fixture()
def spec():
    return session_case.load_spec(SPEC)


def test_check_reports_audit_and_claim_coverage(spec):
    result = session_case.check(spec)
    assert result["audit_route"] == "pass"
    assert result["uncovered"] == []
    assert result["claims"] >= 20
    assert result["ok"]


def test_check_flags_a_claim_with_no_evidence(spec):
    spec = copy.deepcopy(spec)
    spec["brief"]["deck"] = "Fluidstack booked $999M of revenue last year, the deck now says."
    result = session_case.check(spec)
    uncovered = [u for u in result["uncovered"] if "$999M" in u["text"]]
    assert uncovered and uncovered[0]["load_bearing"]
    assert not result["ok"]


def test_build_issues_the_case_and_writes_the_record(session, tmp_path, spec):
    load_seeds(session)
    import_engine_cases(session)  # the repo's cases, so the day-taken rule + numbering apply
    spec = copy.deepcopy(spec)
    spec["number"] = 10900  # a reserved-block number: the live sequence ignores it
    result = session_case.build(spec, "", tmp_path / "cases", tmp_path / "pdf", session=session)
    assert result["status"] == "success"
    assert result["verification"] == "verified" and result["audit"] == "pass"
    assert result["number"] == 10900 and result["pages"] == 2
    assert result["historical"] is True  # 6 Sep 2026 already carries N° 127
    assert all(r["status"] == "verified" for r in result["ledger"])
    folder = tmp_path / "cases" / "2026-09-06"
    record = json.loads((folder / "fluidstack.run.json").read_text(encoding="utf-8"))
    assert record["brief"]["number"] == 10900
    assert (folder / "fluidstack.pdf").exists() and (folder / "fluidstack.web.html").exists()
    note = (folder / "fluidstack.verification.md").read_text(encoding="utf-8")
    assert "Ledger as built" in note and "REPORTED" in note
    assert session_case.exit_code(result) == session_case.EXIT_OK


def test_build_without_evidence_needs_review(session, tmp_path, spec):
    spec = copy.deepcopy(spec)
    spec["evidence"] = []
    spec["run_date"] = "2026-09-04"
    spec["signal"]["signal_date"] = "2026-09-03"
    result = session_case.build(spec, "", tmp_path / "cases", tmp_path / "pdf", session=session)
    assert result["verification"] == "needs_review"
    assert session_case.exit_code(result) == session_case.EXIT_NEEDS_REVIEW
    assert not (tmp_path / "cases").exists()
