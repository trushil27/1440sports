"""One place for the Messages-API turn loop shared by the scanner, verifier and writer.

Server-side tools (web search / web fetch) run a sampling loop inside the API; when it
reaches its per-request limit the response comes back with ``stop_reason: "pause_turn"``
and only the text produced *so far*. The caller must resend the conversation with the
assistant content appended and let the server resume — the first live scan (5 Sep 2026,
run 3) treated the paused partial as final ("no JSON array found"). ``complete_text``
does the resume loop, concatenates the text of every segment, and turns the two
non-recoverable stops (``max_tokens``, ``refusal``) into a clear ``ModelTurnError``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MAX_CONTINUATIONS = 6

#: Every model call's usage, in order, for the run to total up. Reset per run. This exists
#: because "how much does one run cost?" (operator, 7 Sep 2026) had no measured answer.
LEDGER: list[dict[str, Any]] = []

#: $ per million tokens: (input, output). Cache reads bill at 0.1× input, cache writes at
#: 1.25× input. Anthropic first-party rates, cached 2026-06-24 — an estimate, not an invoice.
PRICES: dict[str, tuple[float, float]] = {
    "claude-sonnet-5": (2.0, 10.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


def reset_ledger() -> None:
    LEDGER.clear()


def ledger_totals() -> dict[str, Any]:
    """Tokens by kind, calls by stage, and an estimated dollar cost at the table above."""
    tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    calls: dict[str, int] = {}
    cost = 0.0
    for row in LEDGER:
        u = row["usage"] or {}
        i, o = int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0)
        cr = int(u.get("cache_read_input_tokens") or 0)
        cw = int(u.get("cache_creation_input_tokens") or 0)
        tokens["input"] += i
        tokens["output"] += o
        tokens["cache_read"] += cr
        tokens["cache_write"] += cw
        calls[row["label"]] = calls.get(row["label"], 0) + 1
        pin, pout = PRICES.get(row["model"], (0.0, 0.0))
        cost += (i * pin + cr * pin * 0.1 + cw * pin * 1.25 + o * pout) / 1_000_000
    return {"tokens": tokens, "calls": calls, "estimated_usd": round(cost, 3)}


class ModelTurnError(RuntimeError):
    """A turn ended in a state that cannot be parsed or resumed (truncation, refusal)."""

    def __init__(self, message: str, *, stop_reason: str, text: str = "") -> None:
        super().__init__(message)
        self.stop_reason = stop_reason
        self.text = text


@dataclass
class Completion:
    text: str
    stop_reason: str
    segments: int = 1
    usage: list[dict] = field(default_factory=list)

    @property
    def continuations(self) -> int:
        return self.segments - 1


def _text_of(content: list[Any]) -> str:
    return "\n".join(
        getattr(b, "text", "") for b in content if getattr(b, "type", "") == "text"
    ).strip()


def _usage_of(response: Any) -> dict | None:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    return usage.to_dict() if hasattr(usage, "to_dict") else None


def complete_text(
    client: Any,
    *,
    model: str,
    system: str,
    messages: list[dict],
    max_tokens: int,
    tools: list[dict] | None = None,
    effort: str | None = None,
    output_format: dict[str, Any] | None = None,
    label: str = "model",
) -> Completion:
    """Stream one assistant turn to completion, resuming ``pause_turn`` up to 6 times."""
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        # The system prompt is the same for every call of a stage (scanner, verifier, writer):
        # cache it, so the 17-odd verifier calls per case pay for it once, not 17 times.
        "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        "thinking": {"type": "adaptive"},
    }
    if tools:
        kwargs["tools"] = tools
    output_config: dict[str, Any] = {}
    if effort:
        output_config["effort"] = effort
    if output_format:
        # Structured output: the API constrains the reply to this JSON schema, so a turn
        # cannot end as prose, or as nothing (run 192, 7 Sep 2026: an empty reply).
        output_config["format"] = {"type": "json_schema", "schema": output_format}
    if output_config:
        kwargs["output_config"] = output_config

    history = list(messages)
    texts: list[str] = []
    usage: list[dict] = []
    segments = 0
    while True:
        segments += 1
        with client.messages.stream(messages=history, **kwargs) as stream:
            response = stream.get_final_message()
        text = _text_of(response.content)
        if text:
            texts.append(text)
        stop = getattr(response, "stop_reason", None) or "end_turn"
        # Shape as well as size: run 192 (7 Sep 2026) ended with an EMPTY text and nothing in
        # the record said whether the model refused, thought and stopped, or never answered.
        blocks: dict[str, int] = {}
        for b in response.content:
            kind = getattr(b, "type", "?")
            blocks[kind] = blocks.get(kind, 0) + 1
        u = _usage_of(response)
        if u is not None:
            usage.append(u)
        LEDGER.append(
            {"label": label, "model": model, "usage": u, "stop": stop, "blocks": blocks,
             "chars": len(text)}
        )
        if stop == "pause_turn":
            if segments > MAX_CONTINUATIONS:
                raise ModelTurnError(
                    f"{label}: still paused after {MAX_CONTINUATIONS} continuations",
                    stop_reason=stop,
                    text="\n".join(texts),
                )
            # Resend as-is: the server sees the trailing server-tool block and resumes.
            history = history + [{"role": "assistant", "content": response.content}]
            continue
        joined = "\n".join(texts)
        if stop == "max_tokens":
            raise ModelTurnError(
                f"{label}: output truncated at max_tokens={max_tokens} "
                f"(segment {segments}); raise the limit or shorten the task",
                stop_reason=stop,
                text=joined,
            )
        if stop == "refusal":
            details = getattr(response, "stop_details", None)
            raise ModelTurnError(
                f"{label}: model refused ({details})", stop_reason=stop, text=joined
            )
        return Completion(joined, stop, segments, usage)
