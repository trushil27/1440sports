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


def _nullable(kind: str) -> dict[str, Any]:
    return {"type": [kind, "null"]}


#: The shape the retry MUST return. Not the whole v2.1 contract — the fields the parser and
#: the scoring stage read. The API allows at most 16 union-typed (nullable) properties per
#: schema; the first version had 23 and both morning runs on 8 Sep 2026 were refused with a
#: 400 before the retry could answer. So: the fields where "unknown" must be distinguishable
#: from "empty" are nullable (13), and the free-text key facts are plain strings where an
#: empty string means "not found" — the parser already treats those alike. Every property
#: is required and nothing else is allowed: that is what lets the API enforce the shape.
#: ``parse_scan_output`` reads the array out of the wrapper unchanged.
_KEY_FACTS = (
    "funding",
    "investors",
    "revenue",
    "trigger",
    "competitor_signal",
    "strategic_hook",
    "us_presence",
    "alumni_match",
    "taxonomy_category",
    "ops_fit_note",
)
_DIMENSIONS = ("timing", "capacity", "brand_fit", "urgency", "ops_fit")
_SIGNAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "company": {"type": "string"},
        "score": {"type": "integer"},
        "track": {"type": "integer"},
        "signal_date": _nullable("string"),
        "tier": _nullable("string"),
        "person": _nullable("string"),
        "role": _nullable("string"),
        "horizon_weeks": _nullable("string"),
        "source_url": _nullable("string"),
        "industry_meta": _nullable("string"),
        "recommended_team": _nullable("string"),
        "recommended_series": _nullable("string"),
        "timing_label": _nullable("string"),
        "trigger_reason": _nullable("string"),
        "confidence_level": _nullable("string"),
        "of_gate_passed": _nullable("boolean"),
        "key_facts": {
            "type": "object",
            "properties": {k: {"type": "string"} for k in _KEY_FACTS},
            "required": list(_KEY_FACTS),
            "additionalProperties": False,
        },
        "score_breakdown": {
            "type": "object",
            "properties": {k: {"type": "integer"} for k in _DIMENSIONS},
            "required": list(_DIMENSIONS),
            "additionalProperties": False,
        },
    },
    "required": [
        "company",
        "score",
        "track",
        "signal_date",
        "tier",
        "person",
        "role",
        "horizon_weeks",
        "source_url",
        "industry_meta",
        "recommended_team",
        "recommended_series",
        "timing_label",
        "trigger_reason",
        "confidence_level",
        "of_gate_passed",
        "key_facts",
        "score_breakdown",
    ],
    "additionalProperties": False,
}
SCAN_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"signals": {"type": "array", "items": _SIGNAL_SCHEMA}},
    "required": ["signals"],
    "additionalProperties": False,
}
#: The API's limit, asserted by a test so the schema can never drift back over it.
MAX_UNION_PARAMS = 16


def count_union_params(schema: Any) -> int:
    """How many properties in ``schema`` (at any depth) are union-typed — a type array or
    anyOf — which is what the API caps."""
    n = 0
    if isinstance(schema, dict):
        if isinstance(schema.get("type"), list) or "anyOf" in schema:
            n += 1
        for v in schema.values():
            n += count_union_params(v)
    elif isinstance(schema, list):
        n += sum(count_union_params(v) for v in schema)
    return n


class ScanFailed(RuntimeError):
    """The scan produced nothing usable. ``raw`` keeps the last model text for diagnosis."""

    def __init__(self, message: str, raw: str = "") -> None:
        super().__init__(message)
        self.raw = raw


class MessagesClient(Protocol):
    """The slice of the Anthropic client we use (so tests can pass a fake)."""

    def create_text(
        self,
        *,
        model: str,
        system: str,
        messages: list[dict],
        tools: list[dict],
        output_format: dict[str, Any] | None = None,
    ) -> str: ...


# Streaming, so the ceiling can be generous: ten candidates + citations + thinking. Raised
# from 32000 on 7 Sep 2026, when run 192 spent the whole budget narrating eight web searches
# and was cut off before it reached the JSON — the day produced no signal for that alone.
SCAN_MAX_TOKENS = 64000


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
        self,
        *,
        model: str,
        system: str,
        messages: list[dict],
        tools: list[dict],
        output_format: dict[str, Any] | None = None,
    ) -> str:
        try:
            done = complete_text(
                self._client,
                model=model,
                system=system,
                messages=messages,
                tools=tools,
                max_tokens=SCAN_MAX_TOKENS,
                output_format=output_format,
                label="scanner",
            )
        except ModelTurnError as exc:
            # A turn cut off at the ceiling is not the end of the scan. Hand the partial text
            # back: run_scan either finds a complete array in it, or retries with "return ONLY
            # the JSON array", which is short and does not narrate. Failing here instead threw
            # away a scan that had already done its ten searches (run 192, 7 Sep 2026).
            if exc.stop_reason == "max_tokens" and exc.text:
                self.last_usage, self.last_segments = None, 0
                return exc.text
            raise ScanFailed(str(exc), raw=exc.text) from exc
        except Exception as exc:  # noqa: BLE001 — auth, network, 5xx: the run fails cleanly
            raise ScanFailed(f"scanner call failed: {type(exc).__name__}: {exc}") from exc
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


#: Added 7 Sep 2026 after two runs in one day spent their whole output budget describing the
#: searches and were cut off before the array. The searching is the work; the narration is
#: not, and nothing downstream reads a word of it.
OUTPUT_DISCIPLINE = (
    "OUTPUT DISCIPLINE. Do not narrate the searches, summarise what each result said, or "
    "print working notes between them. Read the sources, then write the JSON array — it must "
    "be the only thing in your reply. Nothing downstream reads anything else, and a reply "
    "that runs out of room before the array is a wasted run."
)


def scanner_prompts(today: dt.date, addendum: str | None = None) -> tuple[str, str]:
    system = scanner_system_prompt().replace(_TODAY_TOKEN, today.isoformat())
    user = load_prompt("scanner_v218_user.txt")
    if addendum:
        user = user.rstrip() + "\n\n" + addendum.strip() + "\n"
    return system, user.rstrip() + "\n\n" + OUTPUT_DISCIPLINE + "\n"


SINGLE_COMPANY_USER = (
    "Run the scan for ONE named company only: {company}.\n"
    "Research it live (its own newsroom, filings and Tier-1 coverage) and return a JSON array "
    "with exactly one signal object for {company} in the format specified — same gates, same "
    "five /20 dimensions, same anti-hallucination rules. If the company fails a gate, still "
    "return the object with the honest score and say why in key_facts.strategic_hook. "
    "Anchor signal_date to the most recent verifiable trigger on or before {today}"
    "{hint}."
)


def single_company_prompts(
    company: str, today: dt.date, hint: str | None = None
) -> tuple[str, str]:
    """The same scanner, pointed at one company (used by ``intel.rebuild``)."""
    system = scanner_system_prompt().replace(_TODAY_TOKEN, today.isoformat())
    extra = f" (context from the earlier signal: {hint})" if hint else ""
    user = SINGLE_COMPANY_USER.format(company=company, today=today.isoformat(), hint=extra)
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
    addendum: str | None = None,
) -> ScanResult:
    """One scanner turn. ``addendum`` is appended to the user prompt (the freshness retry)."""
    settings = settings or get_settings()
    client = client or AnthropicText()
    system, user = scanner_prompts(today, addendum)
    messages: list[dict] = [{"role": "user", "content": user}]
    errors: list[str] = []
    raws: list[str] = []
    raw = ""
    for attempt in (1, 2):
        # The retry gets NO search tools. The searching is already done and paid for by then;
        # leaving the tools on lets the model search and narrate all over again and run out of
        # room a second time, which is exactly how 7 Sep 2026 ended with no signal twice. With
        # no tools the only thing it can do is write the array out of what it already has.
        tools = (
            [{**WEB_SEARCH_TOOL, "max_uses": int(settings.scan_search_uses)}]
            if attempt == 1
            else []
        )
        # The retry is also schema-bound: the API will not let it end as prose or as an empty
        # reply, which is how the 21:44Z run on 7 Sep 2026 ended. The first attempt is not,
        # because the searching turn needs room to work and its text is never the product.
        raw = client.create_text(
            model=settings.scan_model,
            system=system,
            messages=messages,
            tools=tools,
            output_format=SCAN_OUTPUT_SCHEMA if attempt == 2 else None,
        )
        raws.append(raw)
        try:
            signals = parse_scan_output(raw, min_n=1, max_n=settings.scan_candidates_max)
        except ParseError as exc:
            errors.append(f"attempt {attempt} ({len(raw)} chars): {exc}")
            messages = messages + [
                {"role": "assistant", "content": raw or "(empty)"},
                {"role": "user", "content": RETRY_NOTE.format(error=str(exc))},
            ]
            continue
        return ScanResult(signals, raw, attempt, settings.scan_model)
    # Both attempts, and the longest text either produced — the last one was empty on 7 Sep
    # 2026 and the record showed nothing of the first, which is where the evidence was.
    raise ScanFailed(
        "scanner output unparseable after retry — " + "; ".join(errors),
        raw=max(raws, key=len) if raws else "",
    )
