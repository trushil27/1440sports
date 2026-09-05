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
    label: str = "model",
) -> Completion:
    """Stream one assistant turn to completion, resuming ``pause_turn`` up to 6 times."""
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "thinking": {"type": "adaptive"},
    }
    if tools:
        kwargs["tools"] = tools
    if effort:
        kwargs["output_config"] = {"effort": effort}

    history = list(messages)
    texts: list[str] = []
    usage: list[dict] = []
    segments = 0
    while True:
        segments += 1
        with client.messages.stream(messages=history, **kwargs) as stream:
            response = stream.get_final_message()
        if (u := _usage_of(response)) is not None:
            usage.append(u)
        if text := _text_of(response.content):
            texts.append(text)
        stop = getattr(response, "stop_reason", None) or "end_turn"
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
