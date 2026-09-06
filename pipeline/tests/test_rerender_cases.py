"""intel.rerender_cases — a recorded case re-rendered from its own brief_data."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from intel import rerender_cases

CASES = Path(__file__).resolve().parents[1] / "intel" / "cases"


def test_gridfit_display_names_and_rerender(tmp_path):
    src = CASES / "2026-09-06" / "fluidstack.run.json"
    folder = tmp_path / "2026-09-06"
    folder.mkdir()
    shutil.copy(src, folder / "fluidstack.run.json")
    rec = folder / "fluidstack.run.json"
    data = json.loads(rec.read_text(encoding="utf-8"))
    # Pretend the case was built before the fix: sponsor-table key in GRID FIT.
    data["brief"]["brief_data"]["gridfit"][1]["team"] = "MoneyGram Haas F1 Team"
    rec.write_text(json.dumps(data), encoding="utf-8")

    names = rerender_cases.display_names()
    assert names["MoneyGram Haas F1 Team"] == "TGR Haas F1 Team"
    out = rerender_cases.rerender(rec, names)
    assert out["changed"] and out["pages"] == 2
    again = json.loads(rec.read_text(encoding="utf-8"))
    teams = [r["team"] for r in again["brief"]["brief_data"]["gridfit"]]
    assert "TGR Haas F1 Team" in teams and "MoneyGram Haas F1 Team" not in teams
    assert (folder / "fluidstack.pdf").exists() and (folder / "fluidstack.web.html").exists()
    assert "TGR Haas F1 Team" in (folder / "fluidstack.html").read_text(encoding="utf-8")
    # Nothing to change the second time.
    assert rerender_cases.rerender(rec, names)["changed"] is False
