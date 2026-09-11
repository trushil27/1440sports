"""Trigger taxonomy + outreach sequences + the outcomes log (operator, 11 Sep 2026)."""

from __future__ import annotations

import datetime as dt
import json

import pytest

from intel import outreach, triggers


def test_trigger_types_are_spotted_from_verified_text():
    assert triggers.classify("Series C, $550M at $5B, led by Insight Partners") == "funding_round"
    assert (
        triggers.classify("$1.5B round led by Jane Street at an $18B valuation") == "funding_round"
    )
    assert (
        triggers.classify(
            "Carve-out of the Transformation of Industry unit into a standalone company"
        )
        == "spin_off"
    )
    assert (
        triggers.classify("Completed business combination; ADSs begin trading on Nasdaq")
        == "listing"
    )
    assert triggers.classify("Appointed Rahul Mehta as Chief Marketing Officer") == "new_cmo"
    assert (
        triggers.classify("Names Jane Doe as chief executive officer, effective 1 Oct") == "new_ceo"
    )
    assert triggers.classify("Opens European headquarters in London") == "expansion"
    assert triggers.classify("Partnership with a university") == "other"


def test_an_executive_from_a_sponsor_outranks_everything_else():
    kf = {"alumni_match": "Genefa Murphy, ex-Udemy CMO (Udemy–McLaren deal)"}
    assert triggers.classify("Series D, $200M", kf) == "exec_move"
    text = "Hired Sam Lee, formerly at Oracle, as CMO"
    assert triggers.classify(text, sponsor_brands=["Oracle", "Petronas"]) == "exec_move"
    assert (
        triggers.classify(text, sponsor_brands=["Petronas"]) == "new_cmo"
    )  # no sponsor tie → the seat


def test_attach_sets_a_type_on_every_row():
    rows = [
        {"trigger": "Series B, $40M", "stage": "Spin-out"},
        {"trigger": None, "stage": None},
    ]
    counts = triggers.attach(rows)
    assert (
        rows[0]["trigger_type"] == "spin_off" and rows[0]["trigger_label"] == "Spin-off / carve-out"
    )
    assert rows[1]["trigger_type"] == "other"
    assert counts == {"spin_off": 1, "other": 1}


def test_every_trigger_has_a_weekly_cadence_of_six_touches():
    for kind, pb in outreach.playbooks().items():
        days = [s["day"] for s in pb["steps"]]
        assert days == [0, 3, 7, 14, 21, 28], kind
        assert pb["steps"][0]["channel"] == "email" and pb["steps"][4]["channel"] == "phone"
        assert all(s["purpose"] for s in pb["steps"])
    plan = outreach.sequence_plan("spin_off", dt.date(2026, 9, 14))
    assert plan[0]["date"] == "2026-09-14" and plan[-1]["date"] == "2026-10-12"


def _case(tmp_path, number, company, trigger, person="Ann Lee", role="CEO"):
    folder = tmp_path / "cases" / "2026-09-01"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{company.lower()}.run.json").write_text(
        json.dumps(
            {
                "run": {"date": "2026-09-01"},
                "brief": {
                    "number": number,
                    "brief_data": {
                        "company": company,
                        "decision_maker_name": person,
                        "decision_maker_role": role,
                        "team_label": "Envision Racing",
                        "series_label": "FE",
                    },
                },
                "candidates": [
                    {
                        "decision": "selected",
                        "company": company,
                        "trigger_reason": trigger,
                        "key_facts": {"trigger": trigger},
                    }
                ],
                "ledger": [],
            }
        ),
        encoding="utf-8",
    )
    return tmp_path / "cases"


def test_log_start_touch_reply_meeting_and_the_rates(tmp_path):
    cases = _case(tmp_path, 300, "Acme", "Series D, $300M at $2B")
    _case(tmp_path, 301, "Bolt", "Spin-off of the drives unit into a standalone company")
    log = outreach.load_log(tmp_path / "log.json")
    a = outreach.start(log, 300, dt.date(2026, 9, 7), cases_dir=cases)
    b = outreach.start(log, 301, dt.date(2026, 9, 8), cases_dir=cases)
    assert a["trigger_type"] == "funding_round" and b["trigger_type"] == "spin_off"
    assert a["person"] == "Ann Lee" and a["team"] == "Envision Racing"
    with pytest.raises(ValueError):
        outreach.start(
            log, 300, dt.date(2026, 9, 9), cases_dir=cases
        )  # one open sequence per brief

    outreach.touch(log, a["id"], "open", dt.date(2026, 9, 7))
    outreach.touch(log, a["id"], "follow_up", dt.date(2026, 9, 14))
    outreach.reply(log, a["id"], dt.date(2026, 9, 15))
    outreach.meeting(log, a["id"], dt.date(2026, 9, 18))
    outreach.touch(log, "301", "open", dt.date(2026, 9, 8))  # by brief number, open sequence

    m = outreach.metrics(log, today=dt.date(2026, 9, 21))
    assert m["total"] == {
        "sequences": 2,
        "contacted": 2,
        "replies": 1,
        "meetings": 1,
        "won": 0,
        "reply_rate": 0.5,
        "meeting_rate": 0.5,
        "meetings_per_reply": 1.0,
    }
    assert m["by_type"]["funding_round"]["reply_rate"] == 1.0
    assert m["by_type"]["spin_off"]["reply_rate"] == 0.0
    week = next(w for w in m["weekly"] if w["week"] == "2026-W38")
    assert week["replies"] == 1 and week["meetings"] == 1 and week["touches"] == 1

    # the week of 21 Sep: Bolt's follow-up (15 Sep) is overdue and its value-add (22 Sep) due;
    # Acme is in "meeting", so its remaining cadence is not chased
    d = outreach.due(log, dt.date(2026, 9, 21))
    steps = {(x["company"], x["step"]): x["overdue"] for x in d}
    assert steps[("Bolt", "follow_up")] is True and steps[("Bolt", "value_add")] is False
    assert not [x for x in d if x["company"] == "Acme"]
    text = outreach.report_text(log, dt.date(2026, 9, 21))
    assert "Funding round: 1 seq" in text and "DUE THIS WEEK" in text and "Bolt" in text

    outreach.outcome(log, b["id"], "parked")
    assert not [x for x in outreach.due(log, dt.date(2026, 9, 21)) if x["company"] == "Bolt"]
    path = outreach.save_log(log, tmp_path / "log.json")
    assert json.loads(path.read_text())["sequences"][0]["meeting_on"] == "2026-09-18"


def test_the_export_payload_has_playbooks_numbers_and_due_touches(tmp_path):
    log = outreach.load_log(tmp_path / "none.json")
    p = outreach.export_payload(log, dt.date(2026, 9, 11))
    assert p["week"] == "2026-W37" and set(p["playbooks"]) == set(triggers.TYPES)
    assert p["metrics"]["total"]["sequences"] == 0 and p["due"] == []
