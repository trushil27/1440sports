"""Scan: Claude + web search → ranked candidate list (§6.1).

Prompt text is the verbatim Phase 2.1.3 scanner from spec/n8n_v21_prompts.md NODE 1
(see intel/prompts/README.md). Malformed output → one retry with the parse error fed
back → then ``ScanFailed`` (the run fails and the operator is alerted).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from intel.config import Settings, get_settings
from intel.parse import ParseError, ScannedSignal, parse_scan_output

PROMPTS = Path(__file__).parent / "prompts"
_TODAY_TOKEN = "{{ $today.format('yyyy-MM-dd') }}"

# Current server-tool type for Sonnet 5 / Opus 5 (web_search_20250305 was the n8n-era variant).
WEB_SEARCH_TOOL: dict[str, Any] = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 10,
}
RETRY_NOTE = (
    "Your previous output could not be parsed: {error}\n\n"
    "Return ONLY the JSON array of signal objects exactly as specified — no preamble, no "
    "markdown fences, no commentary, complete and valid JSON."
)


class ScanFailed(RuntimeError):
    pass


class MessagesClient(Protocol):
    """The slice of the Anthropic client we use (so tests can pass a fake)."""

    def create_text(
        self, *, model: str, system: str, messages: list[dict], tools: list[dict]
    ) -> str: ...


class AnthropicText:
    """Adapter over ``anthropic.Anthropic`` returning the joined text blocks of one response."""

    def __init__(self, client: Any | None = None) -> None:
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self._client = client
        self.last_usage: dict | None = None

    def create_text(
        self, *, model: str, system: str, messages: list[dict], tools: list[dict]
    ) -> str:
        with self._client.messages.stream(
            model=model,
            max_tokens=16000,
            system=system,
            messages=messages,
            tools=tools,
            thinking={"type": "adaptive"},
        ) as stream:
            response = stream.get_final_message()
        if response.stop_reason == "refusal":
            raise ScanFailed(f"model refused the scan: {getattr(response, 'stop_details', None)}")
        usage = getattr(response, "usage", None)
        self.last_usage = usage.to_dict() if hasattr(usage, "to_dict") else None
        return "\n".join(b.text for b in response.content if getattr(b, "type", "") == "text")


def load_prompt(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8")


def scanner_prompts(today: dt.date) -> tuple[str, str]:
    system = load_prompt("scanner_v213_system.txt").replace(_TODAY_TOKEN, today.isoformat())
    user = load_prompt("scanner_v213_user.txt")
    return system, user


@dataclass
class ScanResult:
    signals: list[ScannedSignal]
    raw_text: str
    attempts: int
    model: str


def run_scan(
    today: dt.date,
    client: MessagesClient | None = None,
    settings: Settings | None = None,
) -> ScanResult:
    settings = settings or get_settings()
    client = client or AnthropicText()
    system, user = scanner_prompts(today)
    messages: list[dict] = [{"role": "user", "content": user}]
    last_error: str | None = None
    raw = ""
    for attempt in (1, 2):
        raw = client.create_text(
            model=settings.scan_model, system=system, messages=messages, tools=[WEB_SEARCH_TOOL]
        )
        try:
            signals = parse_scan_output(raw, min_n=1, max_n=settings.scan_candidates_max)
        except ParseError as exc:
            last_error = str(exc)
            messages = messages + [
                {"role": "assistant", "content": raw or "(empty)"},
                {"role": "user", "content": RETRY_NOTE.format(error=last_error)},
            ]
            continue
        return ScanResult(signals, raw, attempt, settings.scan_model)
    raise ScanFailed(f"scanner output unparseable after retry: {last_error}")
