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


def test_prompts_are_the_verbatim_production_text_with_today_substituted():
    system, user = scan.scanner_prompts(dt.date(2026, 9, 4))
    assert system.startswith("You are the 1440Sports Signal Scanner. Today is 2026-09-04.")
    assert "{{" not in system
    # The v2.1.8 production scanner keeps the FE quota and adds full-grid team matching; the
    # 2.1.3 "ANTI-HALLUCINATION RULES" block is no longer in the scanner (it lives in the writer).
    assert "FE QUOTA" in system and "TEAM MATCHING — FULL GRID EXPLORATION" in system
    assert "ANTI-HALLUCINATION RULES" not in system
    assert user.startswith("Run today's signal scan.")


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
