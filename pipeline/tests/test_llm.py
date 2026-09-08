"""The shared Messages-API turn loop: pause_turn is resumed, truncation/refusal are explicit.

Live run 3 (5 Sep 2026) failed with "no JSON array found": the scanner's ten web searches
hit the server-side loop limit, the API returned ``pause_turn`` with the text so far, and
the adapter treated that partial as the final answer.
"""

from __future__ import annotations

import datetime as dt
from types import SimpleNamespace

import pytest

from intel import brief, scan, verify
from intel.config import Settings
from intel.llm import ModelTurnError, complete_text


class _Block(SimpleNamespace):
    pass


def _text(t: str) -> _Block:
    return _Block(type="text", text=t)


def _tool_use() -> _Block:
    return _Block(type="server_tool_use", id="srvtoolu_1", name="web_search", input={"query": "x"})


class _Stream:
    def __init__(self, response):
        self._response = response

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self._response


class FakeMessages:
    """Replays scripted responses; records every request's messages."""

    def __init__(self, responses: list) -> None:
        self.responses = list(responses)
        self.requests: list[dict] = []

    def stream(self, **kwargs):
        self.requests.append(kwargs)
        return _Stream(self.responses.pop(0))


class FakeClient:
    def __init__(self, responses: list) -> None:
        self.messages = FakeMessages(responses)


def _resp(content, stop_reason: str, usage: dict | None = None):
    u = SimpleNamespace(to_dict=lambda: usage) if usage is not None else None
    return SimpleNamespace(content=content, stop_reason=stop_reason, usage=u, stop_details=None)


def test_pause_turn_is_resumed_by_resending_the_assistant_content_and_text_is_joined():
    paused = _resp([_text("Searching…"), _tool_use()], "pause_turn", {"output_tokens": 10})
    final = _resp([_text('[{"company": "Acme"}]')], "end_turn", {"output_tokens": 20})
    client = FakeClient([paused, final])
    done = complete_text(
        client,
        model="m",
        system="s",
        messages=[{"role": "user", "content": "go"}],
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        max_tokens=100,
    )
    assert done.text == 'Searching…\n[{"company": "Acme"}]'
    assert done.stop_reason == "end_turn" and done.segments == 2 and done.continuations == 1
    assert done.usage == [{"output_tokens": 10}, {"output_tokens": 20}]
    first, second = client.messages.requests
    # The paused assistant turn is appended verbatim and NO extra user message is added.
    assert second["messages"][0] == {"role": "user", "content": "go"}
    assert second["messages"][1]["role"] == "assistant"
    assert second["messages"][1]["content"] is paused.content
    assert len(second["messages"]) == 2
    assert first["thinking"] == {"type": "adaptive"} and first["max_tokens"] == 100
    assert "output_config" not in first


def test_effort_is_passed_through_output_config():
    client = FakeClient([_resp([_text("ok")], "end_turn")])
    complete_text(client, model="m", system="s", messages=[], max_tokens=10, effort="high")
    assert client.messages.requests[0]["output_config"] == {"effort": "high"}


def test_endless_pause_turn_stops_after_the_continuation_cap():
    client = FakeClient([_resp([_tool_use()], "pause_turn")] * 10)
    with pytest.raises(ModelTurnError, match="still paused"):
        complete_text(client, model="m", system="s", messages=[], max_tokens=10)
    assert len(client.messages.requests) == 7  # 1 + MAX_CONTINUATIONS


def test_truncation_and_refusal_are_explicit_errors_carrying_the_partial_text():
    with pytest.raises(ModelTurnError, match="truncated at max_tokens=10") as exc:
        complete_text(
            FakeClient([_resp([_text("[{partial")], "max_tokens")]),
            model="m",
            system="s",
            messages=[],
            max_tokens=10,
            label="scanner",
        )
    assert exc.value.stop_reason == "max_tokens" and exc.value.text == "[{partial"
    with pytest.raises(ModelTurnError, match="refused"):
        complete_text(
            FakeClient([_resp([], "refusal")]), model="m", system="s", messages=[], max_tokens=10
        )


def test_scanner_adapter_resumes_a_paused_scan():
    paused = _resp([_tool_use()], "pause_turn")
    final = _resp([_text("[]")], "end_turn")
    adapter = scan.AnthropicText(FakeClient([paused, final]))
    assert adapter.create_text(model="m", system="s", messages=[], tools=[]) == "[]"
    assert adapter.last_segments == 2


def test_a_scan_cut_off_at_the_ceiling_is_handed_back_to_the_retry_not_thrown_away():
    """Run 192 (7 Sep 2026) narrated eight web searches, hit max_tokens before the JSON, and
    the day produced no signal. The searches were already done; the retry only has to ask for
    the array. Failing here discarded all of it."""
    cut_off = _resp([_text("…let me extract the rest")], "max_tokens")
    truncated = scan.AnthropicText(FakeClient([cut_off]))
    assert truncated.create_text(model="m", system="s", messages=[], tools=[]) == (
        "…let me extract the rest"
    )

    client = FakeClient(
        [
            _resp([_text("I searched ten sources and then ran out of room. [{")], "max_tokens"),
            _resp([_text('[{"company": "Acme", "score": 78}]')], "end_turn"),
        ]
    )
    result = scan.run_scan(
        dt.date(2026, 9, 7),
        client=scan.AnthropicText(client),
        settings=Settings(scan_candidates_max=10),
    )
    assert [s.company for s in result.signals] == ["Acme"] and result.attempts == 2
    # the second request carries the "return ONLY the JSON array" note, not another full scan
    assert "ONLY the JSON array" in client.messages.requests[-1]["messages"][-1]["content"]


def test_a_scan_truncated_twice_still_fails_with_the_reason():
    client = FakeClient([_resp([_text("narrating…")], "max_tokens")] * 2)
    with pytest.raises(scan.ScanFailed, match="unparseable after retry"):
        scan.run_scan(dt.date(2026, 9, 7), client=scan.AnthropicText(client), settings=Settings())


def test_a_failed_scan_reports_both_attempts_and_keeps_the_text_that_had_something():
    """Run 192 (7 Sep 2026): the record showed only the LAST attempt's error and its text —
    which was empty — so the first attempt, where the evidence was, was lost."""
    from intel import llm

    llm.reset_ledger()
    client = FakeClient(
        [
            _resp([_text("I searched and here is what I found, at length…")], "end_turn"),
            _resp([], "end_turn"),  # the retry answered with nothing at all
        ]
    )
    with pytest.raises(scan.ScanFailed) as exc:
        scan.run_scan(dt.date(2026, 9, 7), client=scan.AnthropicText(client), settings=Settings())
    msg = str(exc.value)
    assert "attempt 1 (" in msg and "attempt 2 (0 chars)" in msg
    assert exc.value.raw.startswith("I searched")  # the longer text, not the empty last one
    turns = [r for r in llm.LEDGER if r["label"] == "scanner"]
    assert [t["stop"] for t in turns] == ["end_turn", "end_turn"]
    assert turns[0]["blocks"] == {"text": 1} and turns[1]["blocks"] == {} and turns[1]["chars"] == 0


def test_verifier_adapter_resumes_pause_turn_and_never_raises_on_truncation():
    paused = _resp([_tool_use()], "pause_turn")
    final = _resp(
        [_text('{"status": "verified", "evidence_url": "https://x", "excerpt": "e"}')], "end_turn"
    )
    v = verify.AnthropicVerifier(FakeClient([paused, final]))
    claim = verify.ClaimDraft(
        claim_type=verify.ClaimType.funding, text="raised $1", section="deck", load_bearing=True
    )
    out = v.verify(claim, "Acme")
    assert out.status.value == "verified" and out.evidence_url == "https://x"
    truncated = verify.AnthropicVerifier(FakeClient([_resp([_text("{")], "max_tokens")]))
    out2 = truncated.verify(claim, "Acme")
    assert out2.status.value == "unverified" and "truncated" in (out2.notes or "")


def test_writer_adapter_turns_truncation_into_a_parse_error_for_the_retry_path():
    w = brief.AnthropicWriter(FakeClient([_resp([_text("<BRIEF_DATA>{")], "max_tokens")]))
    with pytest.raises(brief.ParseError, match="truncated"):
        w.write(model="m", system="s", user="u")


def test_the_retry_scan_carries_no_search_tools():
    """7 Sep 2026: the first turn spent its budget narrating and was cut off; the retry, still
    holding the search tools, searched and narrated all over again and was cut off too. The
    searching is already paid for by then — the retry only has to write the array."""
    client = FakeClient(
        [
            _resp([_text("I searched ten sources and then ran out of room.")], "max_tokens"),
            _resp([_text('[{"company": "Acme", "score": 71}]')], "end_turn"),
        ]
    )
    scan.run_scan(dt.date(2026, 9, 7), client=scan.AnthropicText(client), settings=Settings())
    first, second = client.messages.requests[0], client.messages.requests[1]
    assert first["tools"][0]["name"] == "web_search"
    assert "tools" not in second  # empty list means the request carries no tools at all


def test_the_scanner_is_told_not_to_narrate():
    _, user = scan.scanner_prompts(dt.date(2026, 9, 7))
    assert "OUTPUT DISCIPLINE" in user and user.rstrip().endswith("a wasted run.")
    _, with_addendum = scan.scanner_prompts(dt.date(2026, 9, 7), addendum="Widen the window.")
    assert "Widen the window." in with_addendum and "OUTPUT DISCIPLINE" in with_addendum


def test_the_retry_is_schema_bound_and_the_wrapper_it_returns_parses():
    """The 21:44Z run on 7 Sep 2026 ended with the retry answering nothing. With a JSON schema
    on that turn the API cannot return prose or an empty reply; the wrapper object it does
    return parses through the same extractor as the bare array."""
    wrapped = (
        '{"signals": [{"company": "Acme", "score": 74, "signal_date": "2026-09-01", "tier": null,'
        ' "track": 1, "person": null, "role": null, "horizon_weeks": null,'
        ' "source_url": "https://x.test/a", "industry_meta": null, "recommended_team": null,'
        ' "recommended_series": "FE", "timing_label": null, "trigger_reason": "raised",'
        ' "confidence_level": null, "of_gate_passed": null,'
        ' "key_facts": {"funding": null, "investors": null, "revenue": null, "trigger": null,'
        ' "competitor_signal": null, "strategic_hook": null, "us_presence": null,'
        ' "alumni_match": null, "taxonomy_category": null, "ops_fit_note": null},'
        ' "score_breakdown": {"timing": 15, "capacity": 15, "brand_fit": 15, "urgency": 14,'
        ' "ops_fit": 15}}]}'
    )
    client = FakeClient(
        [_resp([_text("narration, no array")], "end_turn"), _resp([_text(wrapped)], "end_turn")]
    )
    adapter = scan.AnthropicText(client)
    result = scan.run_scan(dt.date(2026, 9, 7), client=adapter, settings=Settings())
    assert [s.company for s in result.signals] == ["Acme"] and result.signals[0].score == 74
    first, second = client.messages.requests
    assert "output_config" not in first  # the searching turn is unconstrained
    fmt = second["output_config"]["format"]
    assert fmt["type"] == "json_schema" and fmt["schema"] is scan.SCAN_OUTPUT_SCHEMA
    assert "tools" not in second


def test_effort_and_format_share_output_config():
    client = FakeClient([_resp([_text("{}")], "end_turn")])
    complete_text(
        client,
        model="m",
        system="s",
        messages=[],
        max_tokens=10,
        effort="low",
        output_format={"type": "object"},
    )
    cfg = client.messages.requests[0]["output_config"]
    assert cfg["effort"] == "low" and cfg["format"]["schema"] == {"type": "object"}


def test_the_retry_schema_stays_under_the_api_union_limit():
    """Both morning runs on 8 Sep 2026 were refused with a 400: 'Schemas contains too many
    parameters with union types (23 …, limit: 16)'. The schema is the desk's, so the desk
    keeps it under the limit — and this test keeps it there."""
    assert scan.count_union_params(scan.SCAN_OUTPUT_SCHEMA) <= scan.MAX_UNION_PARAMS
    assert scan.count_union_params({"type": ["string", "null"]}) == 1
    assert scan.count_union_params({"anyOf": [{"type": "string"}, {"type": "null"}]}) == 1
    assert scan.count_union_params({"type": "object", "properties": {"a": {"type": "string"}}}) == 0
