"""Scan: Claude + web search → ranked candidate list (§6.1).

Prompt text is the verbatim production scanner from the live n8n export
(``Anthropic — Run Signals`` node, spec/n8n_workflow_production_2026-09-04.json; see
intel/prompts/README.md). Malformed output → one retry with the parse error fed back →
then ``ScanFailed`` (the run fails and the operator is alerted).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from intel.config import Settings, get_settings
from intel.llm import ModelTurnError, complete_text
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
    """The scan produced nothing usable. ``raw`` keeps the last model text for diagnosis."""

    def __init__(self, message: str, raw: str = "") -> None:
        super().__init__(message)
        self.raw = raw


class MessagesClient(Protocol):
    """The slice of the Anthropic client we use (so tests can pass a fake)."""

    def create_text(
        self, *, model: str, system: str, messages: list[dict], tools: list[dict]
    ) -> str: ...


# Streaming, so the ceiling can be generous: ten candidates + citations + thinking.
SCAN_MAX_TOKENS = 32000


class AnthropicText:
    """Adapter over ``anthropic.Anthropic``: one complete turn (pause_turn resumed) as text."""

    def __init__(self, client: Any | None = None) -> None:
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self._client = client
        self.last_usage: list[dict] | None = None
        self.last_segments: int = 0

    def create_text(
        self, *, model: str, system: str, messages: list[dict], tools: list[dict]
    ) -> str:
        try:
            done = complete_text(
                self._client,
                model=model,
                system=system,
                messages=messages,
                tools=tools,
                max_tokens=SCAN_MAX_TOKENS,
                label="scanner",
            )
        except ModelTurnError as exc:
            raise ScanFailed(str(exc), raw=exc.text) from exc
        self.last_usage, self.last_segments = done.usage, done.segments
        return done.text


def load_prompt(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8")


# --- scoring-block restoration ---------------------------------------------------------
# The production v2.1.8 scanner prompt regressed to the pre-Phase-2.1 scoring text (four
# dimensions 0-25, `urgency_or_alumni`, no OPS FIT) while the writer, the audit and the
# build brief (§1, §6.4) all use the Phase 2.1 contract: five dimensions 0-20 incl. OPS FIT
# and the OF gate (docs/N8N_RECONCILIATION.md 2.1). The first live run (5 Sep 2026) produced
# the 4×25 shape and failed to parse. The v2.1.8 text is kept verbatim on disk; at run time
# its regressed block and example are swapped for the 2.1.3 ones (scanner_v213_system.txt),
# which is the scoring the brief specifies — not a new scale.
_REGRESSED_SCORING = (
    "SCORING (V2.1): Six gates first, then four dimensions 0-25 each.\n"
    "Gates: (1) Tier 1 source. (2) Trigger within 12 months. (3) Capacity: $1B+ valuation or "
    "$100M+ ARR. (4) Motorsport relevance 5+/10. (5) Saturation penalty. (6) Alumni check.\n"
    "Dimensions: TIMING, CAPACITY, BRAND FIT, URGENCY.\n"
)
_REGRESSED_EXAMPLE_TAIL = (
    '      "competitor_signal": "...", "strategic_hook": "...", "us_presence": "...", '
    '"alumni_match": "..."\n'
    "    },\n"
    '    "score_breakdown": { "timing": 23, "capacity": 22, "brand_fit": 20, '
    '"urgency_or_alumni": 17 }\n'
)
_V213_EXAMPLE_TAIL = (
    '      "competitor_signal": "...", "strategic_hook": "...", "us_presence": "...", '
    '"alumni_match": "...",\n'
    '      "taxonomy_category": "A1 | A2 | B1 | B2 | C1 | D1 | E1 | F1",\n'
    '      "ops_fit_note": "one-line on team-need fit (max 14 words)"\n'
    "    },\n"
    '    "score_breakdown": { "timing": 18, "capacity": 17, "brand_fit": 16, "urgency": 14, '
    '"ops_fit": 15, "ops_fit_subscores": { "product_to_need": 6, "slot_availability": 3, '
    '"on_camera": 3, "lock_in": 3 } },\n'
    '    "of_gate_passed": true,\n'
    '    "confidence_level": "HIGH"\n'
)
_V213_SCORING_START = "SCORING (V2.1 — Phase 2.1"
_V213_SCORING_END = "ALUMNI DATABASE"


def v213_scoring_block() -> str:
    """The Phase 2.1 scoring text (gates, anti-hallucination, five /20 dims, OF gate, tiers)."""
    text = load_prompt("scanner_v213_system.txt")
    start, end = text.index(_V213_SCORING_START), text.index(_V213_SCORING_END)
    return text[start:end].rstrip() + "\n"


def scanner_system_prompt() -> str:
    """v2.1.8 verbatim, with the regressed scoring block/example replaced by the 2.1.3 ones."""
    system = load_prompt("scanner_v218_system.txt")
    for anchor in (_REGRESSED_SCORING, _REGRESSED_EXAMPLE_TAIL):
        if anchor not in system:
            raise RuntimeError(
                "scanner_v218_system.txt changed: scoring-restore anchor not found — "
                "re-check intel/scan.py against the new export"
            )
    system = system.replace(_REGRESSED_SCORING, v213_scoring_block())
    return system.replace(_REGRESSED_EXAMPLE_TAIL, _V213_EXAMPLE_TAIL)


def scanner_prompts(today: dt.date) -> tuple[str, str]:
    system = scanner_system_prompt().replace(_TODAY_TOKEN, today.isoformat())
    user = load_prompt("scanner_v218_user.txt")
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
    raise ScanFailed(f"scanner output unparseable after retry: {last_error}", raw=raw)
