"""intel.profiles — the eliminated companies as a page: what they are, where they stand on
money, who runs them, and why the desk passed (operator request, 7 Sep 2026)."""

from __future__ import annotations

import json

from intel import profiles


def test_profiles_load_from_every_file_and_later_files_win(tmp_path):
    (tmp_path / "batch-01.json").write_text(
        json.dumps(
            [
                {
                    "company": "Ore Energy",
                    "website": "https://ore.energy",
                    "confidence": "REPORTED",
                },
                {"company": "", "website": "https://nameless.test"},
                "not a record",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "batch-02.json").write_text(
        json.dumps(
            {
                "companies": [
                    {
                        "company": "ore energy",
                        "website": "https://ore.energy/en",
                        "leaders": [{"name": "A"}],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    recs = profiles.load_profiles(tmp_path)
    assert list(recs) == ["oreenergy"]
    assert recs["oreenergy"]["website"] == "https://ore.energy/en"  # the later file replaced it
    assert recs["oreenergy"]["leaders"] == [{"name": "A"}]
    assert profiles.load_profiles(tmp_path / "missing") == {}


def test_profiles_attach_only_to_screened_rows_and_are_counted():
    rows = [
        {
            "company": "Ore Energy",
            "review": {"status": "screened_out", "reason_code": "case_screen"},
        },
        {"company": "Nexeon", "review": {"status": "keep"}},
        {
            "company": "CoVolt Power",
            "review": {"status": "screened_out", "reason_code": "case_screen"},
        },
    ]
    recs = {
        "oreenergy": {"company": "Ore Energy", "website": "https://ore.energy"},
        "nexeon": {"company": "Nexeon", "website": "https://nexeon.co.uk"},
    }
    assert profiles.attach(rows, recs) == 1
    assert rows[0]["profile"]["website"] == "https://ore.energy"
    assert "profile" not in rows[1]  # a shown signal has its case; profiles are for screen-outs
    assert "profile" not in rows[2]
    s = profiles.summary(recs)
    assert s["companies"] == 2 and s["with_website"] == 2 and s["with_leaders"] == 0


def test_the_worklist_is_every_full_check_screen_out_without_a_profile(monkeypatch):
    monkeypatch.setattr(profiles, "load_profiles", lambda: {"oreenergy": {"company": "Ore Energy"}})
    rows = [
        {
            "company": "Ore Energy",
            "date": "2026-08-04",
            "review": {"status": "screened_out", "reason_code": "case_screen"},
        },
        {
            "company": "CoVolt Power",
            "date": "2026-08-21",
            "series": "FE",
            "team": "Envision Racing",
            "industry": "Storage",
            "trigger": "raised",
            "source_url": "https://x.test",
            "review": {
                "status": "screened_out",
                "reason_code": "case_screen",
                "reason": "capacity: too early",
            },
        },
        {"company": "Cerebras", "review": {"status": "screened_out", "reason_code": "blocklisted"}},
        {"company": "Fluidstack", "review": {"status": "keep"}},
    ]
    todo = profiles.wanted(rows)
    assert [t["company"] for t in todo] == ["CoVolt Power"]
    assert todo[0]["team"] == "Envision Racing" and todo[0]["why"].startswith("capacity")
