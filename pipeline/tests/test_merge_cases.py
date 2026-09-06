"""intel.merge_cases — screen-outs from case builders become review decisions."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from intel import merge_cases

CASES = Path(__file__).resolve().parents[1] / "intel" / "cases"


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_screened_files_become_review_rows(tmp_path):
    cases = tmp_path / "cases"
    (cases / "2026-09-05").mkdir(parents=True)
    shutil.copy(CASES / "2026-09-05" / "crusoe.run.json", cases / "2026-09-05")  # N° 121
    _write(
        cases / "2026-06-20" / "crusoeenergycrusoecloud.screened.json",
        {
            "company": "Crusoe Energy / Crusoe Cloud",
            "date": "2026-06-20",
            "verdict": "duplicate_of",
            "duplicate_of": "N° 121",
            "reason": "same company as the 5 Sep case",
        },
    )
    _write(
        cases / "2026-05-05" / "strava.screened.json",
        {
            "company": "Strava",
            "date": "2026-05-05",
            "verdict": "stale",
            "reason": "January S-1 is 124 days before the row",
            "sources": ["https://www.sec.gov/"],
        },
    )
    _write(
        cases / "2026-06-01" / "broken.screened.json",
        {"company": "Broken", "date": "2026-06-01", "verdict": "meh"},
    )
    review = tmp_path / "history_review.json"
    _write(review, {"_meta": {}, "rows": {"2026-01-01|Strava": {"status": "keep_flagged"}}})

    out = merge_cases.apply_screened(cases, review)
    rows = json.loads(review.read_text(encoding="utf-8"))["rows"]
    dup = rows["2026-06-20|Crusoe Energy / Crusoe Cloud"]
    assert dup["status"] == "duplicate_of" and dup["of"] == "2026-09-05|Crusoe"
    stale = rows["2026-05-05|Strava"]
    assert stale["status"] == "screened_out" and stale["reason"].startswith("stale:")
    assert stale["sources"] == ["https://www.sec.gov/"]
    assert rows["2026-01-01|Strava"]["status"] == "keep_flagged"  # untouched
    assert len(out["applied"]) == 2 and len(out["skipped"]) == 1


def test_inventory_lists_built_cases():
    inv = merge_cases.inventory(CASES)
    numbers = {b["number"] for b in inv["built"]}
    assert {121, 122, 127} <= numbers
    assert all(b["verification"] for b in inv["built"])
