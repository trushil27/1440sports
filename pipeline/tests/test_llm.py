"""The shared Messages-API turn loop: pause_turn is resumed, truncation/refusal are explicit.

Live run 3 (5 Sep 2026) failed with "no JSON array found": the scanner's ten web searches
hit the server-side loop limit, the API returned ``pause_turn`` with the text so far, and
the adapter treated that partial as the final answer.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from intel import brief, scan, verify
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


def test_scanner_adapter_resumes_a_paused_scan_and_reports_truncation_as_scan_failed():
    paused = _resp([_tool_use()], "pause_turn")
    final = _resp([_text("[]")], "end_turn")
    adapter = scan.AnthropicText(FakeClient([paused, final]))
    assert adapter.create_text(model="m", system="s", messages=[], tools=[]) == "[]"
    assert adapter.last_segments == 2
    truncated = scan.AnthropicText(FakeClient([_resp([_text("[{")], "max_tokens")]))
    with pytest.raises(scan.ScanFailed, match="truncated") as exc:
        truncated.create_text(model="m", system="s", messages=[], tools=[])
    assert exc.value.raw == "[{"


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
