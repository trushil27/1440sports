"""intel.stage — the capital-event stage behind a signal, and the earliness tie-break.

Operator, 8 Sep 2026: be very early to a Series C/D/E or spin-out, not the fiftieth agency."""

from __future__ import annotations

import datetime as dt
from types import SimpleNamespace

from intel import run_daily, scan
from intel.stage import is_growth_stage, round_stage


def test_stage_is_read_from_the_text_never_from_the_amount():
    assert round_stage("closed a $250m Series D led by Lightspeed") == "Series D"
    assert round_stage("Series c extension") == "Series C"
    assert round_stage("Siemens Energy carve-out of its industrial unit") == "Spin-out"
    assert round_stage("filed its S-1 for a Nasdaq listing") == "IPO"
    assert round_stage("undisclosed pre-IPO round") == "Pre-IPO"
    assert round_stage("raised $400m") is None  # no stage named: not inferred
    assert round_stage(None) is None


def test_growth_stage_is_c_and_later_or_born_big():
    assert (
        is_growth_stage("Series C") and is_growth_stage("Series E") and is_growth_stage("Spin-out")
    )
    assert not is_growth_stage("Series A") and not is_growth_stage("Series B")
    assert not is_growth_stage(None)


def _cand(company, score, trigger, days_ago, run_date):
    return SimpleNamespace(
        company_raw=company,
        score_breakdown={"ranking": score},
        trigger_reason_raw=trigger,
        trigger_date=run_date - dt.timedelta(days=days_ago),
        series=None,
    )


def test_at_equal_score_the_newest_growth_stage_trigger_ranks_first():
    day = dt.date(2026, 9, 8)
    old_d = _cand("Old Series D", 80, "Series D round", 60, day)
    new_a = _cand("New Series A", 80, "Series A round", 3, day)
    new_d = _cand("New Series D", 80, "$250m Series D", 5, day)
    spin = _cand("Spin-out", 80, "carve-out from parent", 12, day)
    higher = _cand("Higher score, old", 84, "Series B", 200, day)
    order = run_daily.rank_eligible([old_d, new_a, new_d, spin, higher], day, priority_days=30)
    # the score still decides first; among the 80s, growth-stage inside 30 days lead, newest first
    assert [c.company_raw for c in order] == [
        "Higher score, old",
        "New Series D",
        "Spin-out",
        "New Series A",
        "Old Series D",
    ]


def test_the_scanner_is_asked_for_growth_stage_events_first():
    _, user = scan.scanner_prompts(dt.date(2026, 9, 8), priority_days=30)
    assert "SOURCING PRIORITY" in user and "Series C, Series D, Series E" in user
    assert "2026-08-09" in user and "2026-09-08" in user  # the window is dated, not vague
    assert user.index("SOURCING PRIORITY") < user.index("OUTPUT DISCIPLINE")
