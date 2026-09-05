"""Scanner orchestration (§6.1): one retry with the parse error fed back, then fail the run."""

from __future__ import annotations

import datetime as dt
import json

import pytest

from intel import scan
from intel.config import Settings
from tests.fixtures import production_signals as ps


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict] = []

    def create_text(self, *, model, system, messages, tools) -> str:
        self.calls.append({"model": model, "system": system, "messages": messages, "tools": tools})
        return self.responses.pop(0)


def _good_output() -> str:
    row = dict(ps.PRIMER_A)
    row["score_breakdown"] = ps.synthetic_split(row["score"])
    return json.dumps([row])


def test_prompts_are_the_production_text_with_the_phase_21_scoring_restored():
    system, user = scan.scanner_prompts(dt.date(2026, 9, 4))
    assert system.startswith("You are the 1440Sports Signal Scanner. Today is 2026-09-04.")
    assert "{{" not in system
    # The v2.1.8 production scanner keeps the FE quota and adds full-grid team matching …
    assert "FE QUOTA" in system and "TEAM MATCHING — FULL GRID EXPLORATION" in system
    # … but its scoring text had regressed to four dims 0-25 (the first live run, 5 Sep 2026,
    # emitted `timing: 23`, no `urgency`, and failed to parse). The 2.1.3 block is spliced in.
    assert "four dimensions 0-25" not in system and "urgency_or_alumni" not in system
    assert "FIVE dimensions 0-20 each" in system and "OPS FIT (0-20)" in system
    assert "GATE ON OPS FIT" in system and "ANTI-HALLUCINATION RULES" in system
    assert '"ops_fit_subscores": { "product_to_need": 6' in system
    assert '"taxonomy_category": "A1 | A2' in system and '"confidence_level": "HIGH"' in system
    # the regressed text is replaced, not duplicated, and the rest of v2.1.8 is intact
    assert system.count("SCORING (V2.1") == 1
    assert "DEFAULT REASONING PATTERNS — FORBIDDEN" in system
    assert user.startswith("Run today's signal scan.")


def test_the_verbatim_v218_file_is_untouched_on_disk():
    raw = scan.load_prompt("scanner_v218_system.txt")
    assert "four dimensions 0-25" in raw and '"urgency_or_alumni": 17' in raw


# The exact shape the production prompt elicited on the first live run (run id 1, 5 Sep 2026).
LIVE_RUN_1_ITEM = {
    "signal_date": "2026-09-03",
    "company": "Toyota Gazoo Racing",
    "score": 82,
    "tier": "HOT",
    "track": 1,
    "source_url": "https://www.reuters.com/business/autos-transportation/example",
    "recommended_team": "Cadillac F1 Team",
    "recommended_series": "F1",
    "trigger_reason": "funding round",
    "key_facts": {"funding": "$1B"},
    "score_breakdown": {"timing": 23, "capacity": 22, "brand_fit": 20, "urgency_or_alumni": 17},
}


def test_legacy_4x25_breakdown_is_accepted_and_rescaled_to_20():
    [sig] = scan.parse_scan_output(json.dumps([LIVE_RUN_1_ITEM]))
    bd = sig.score_breakdown
    assert bd.legacy_scale is True
    assert (bd.timing, bd.capacity, bd.brand_fit, bd.urgency) == (18, 18, 16, 14)
    assert bd.ops_fit is None and bd.urgency_or_alumni == 17


def test_phase_21_breakdown_is_not_rescaled():
    row = dict(ps.PRIMER_A)
    row["score_breakdown"] = {
        "timing": 18,
        "capacity": 17,
        "brand_fit": 16,
        "urgency": 14,
        "ops_fit": 15,
    }
    [sig] = scan.parse_scan_output(json.dumps([row]))
    assert sig.score_breakdown.legacy_scale is False
    assert sig.score_breakdown.model_dump(exclude_none=True) == {
        "timing": 18,
        "capacity": 17,
        "brand_fit": 16,
        "urgency": 14,
        "ops_fit": 15,
        "legacy_scale": False,
    }


def test_a_live_run_1_style_output_parses_first_time_without_a_retry():
    client = FakeClient([json.dumps([LIVE_RUN_1_ITEM])])
    result = scan.run_scan(dt.date(2026, 9, 5), client, Settings(anthropic_api_key="x"))
    assert result.attempts == 1 and result.signals[0].company == "Toyota Gazoo Racing"


def test_malformed_output_is_retried_once_with_the_error_fed_back():
    client = FakeClient(["Sorry, here is prose with no array", _good_output()])
    result = scan.run_scan(dt.date(2026, 5, 20), client, Settings(anthropic_api_key="x"))
    assert result.attempts == 2
    assert [s.company for s in result.signals] == ["Primer"]
    retry_messages = client.calls[1]["messages"]
    assert retry_messages[1]["role"] == "assistant"
    assert "could not be parsed" in retry_messages[2]["content"]
    assert client.calls[0]["tools"][0]["type"] == "web_search_20260209"
    assert client.calls[0]["model"] == "claude-sonnet-5"


def test_second_failure_fails_the_run():
    client = FakeClient(["no json here", "still no json"])
    with pytest.raises(scan.ScanFailed, match="after retry"):
        scan.run_scan(dt.date(2026, 5, 20), client, Settings(anthropic_api_key="x"))
    assert len(client.calls) == 2
