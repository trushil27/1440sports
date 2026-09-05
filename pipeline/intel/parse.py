"""Strict parsing of scanner output (build brief §6.1, §9.6).

Two layers:
1. ``extract_json_array`` — a bracket-DEPTH-balanced scanner that ignores brackets
   inside JSON string literals. The retired n8n parser sliced from the first ``[`` to
   the LAST ``]`` in the text, so a stray bracket in prose after the array (or in a
   string) broke the run. This one walks the text tracking string/escape state.
2. Pydantic models — the field contract of the V2.1 scanner (spec/n8n_v21_prompts.md
   NODE 1). Unknown keys are ignored; wrong types are errors that get fed back to the
   model on the single retry.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

_FENCE = re.compile(r"```(?:json)?", re.IGNORECASE)


class ParseError(ValueError):
    """Raised when scanner output cannot be turned into a candidate list."""


def _balanced_span(s: str, start: int) -> int | None:
    """Index just past the bracket that balances ``s[start]`` ('[' or '{'), or None."""
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth == 0:
                return i + 1
            if depth < 0:
                return None
    return None


def extract_json_array(text: str) -> list[Any]:
    """Return the first parseable JSON array in ``text``.

    Tries every ``[`` in order; the first bracket-balanced span that ``json.loads``
    accepts wins, so prose brackets before/after the array and brackets inside string
    values are all harmless.
    """
    s = _FENCE.sub("", text or "")
    last_error: Exception | None = None
    for m in re.finditer(r"\[", s):
        end = _balanced_span(s, m.start())
        if end is None:
            continue
        try:
            value = json.loads(s[m.start() : end])
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        if isinstance(value, list):
            return value
    if last_error is not None:
        raise ParseError(f"no valid JSON array found (last decode error: {last_error})")
    raise ParseError("no JSON array found in scanner output (truncated or missing)")


def extract_json_object(text: str) -> dict[str, Any]:
    """Return the first parseable JSON object in ``text`` (same balancing rules as arrays)."""
    s = _FENCE.sub("", text or "")
    last_error: Exception | None = None
    for m in re.finditer(r"\{", s):
        end = _balanced_span(s, m.start())
        if end is None:
            continue
        try:
            value = json.loads(s[m.start() : end])
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        if isinstance(value, dict):
            return value
    if last_error is not None:
        raise ParseError(f"no valid JSON object found (last decode error: {last_error})")
    raise ParseError("no JSON object found in output")


def _to_str(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, str):
        return v.strip() or None
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, int | float):
        return str(v)
    return json.dumps(v, ensure_ascii=False)


class OpsFitSubscores(BaseModel):
    model_config = ConfigDict(extra="ignore")
    product_to_need: int | None = Field(default=None, ge=0, le=8)
    slot_availability: int | None = Field(default=None, ge=0, le=4)
    on_camera: int | None = Field(default=None, ge=0, le=4)
    lock_in: int | None = Field(default=None, ge=0, le=4)


class ScoreBreakdown(BaseModel):
    """Five dimensions, each 0-20 (Phase 2.1).

    The scanner is prompted for this shape (``scan.scanner_system_prompt`` restores the
    Phase 2.1 block over the regressed v2.1.8 text). As a safety net the pre-2.1 shape the
    v2.1.8 prompt used to elicit — four dimensions 0-25 with ``urgency_or_alumni`` and no
    ``ops_fit`` — is still accepted: each dimension is rescaled ×0.8 onto /20,
    ``urgency_or_alumni`` becomes ``urgency``, ``ops_fit`` stays unknown, and
    ``legacy_scale`` is set so the gate record says so. The /20 contract itself is unchanged
    (build brief §0.5 — a scoring change needs the MD).
    """

    model_config = ConfigDict(extra="ignore")
    timing: int = Field(ge=0, le=20)
    capacity: int = Field(ge=0, le=20)
    brand_fit: int = Field(ge=0, le=20)
    urgency: int = Field(ge=0, le=20)
    ops_fit: int | None = Field(default=None, ge=0, le=20)
    ops_fit_subscores: OpsFitSubscores | None = None
    urgency_or_alumni: int | None = Field(default=None, ge=0, le=25)
    legacy_scale: bool = False

    @model_validator(mode="before")
    @classmethod
    def _accept_legacy_4x25(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        dims = ("timing", "capacity", "brand_fit")
        has_alt = data.get("urgency") is None and data.get("urgency_or_alumni") is not None
        over_20 = any(isinstance(data.get(d), int | float) and data[d] > 20 for d in dims)
        if not (has_alt or over_20):
            return data

        def rescale(v: Any) -> Any:
            if isinstance(v, int | float) and 0 <= v <= 25:
                return int(v * 0.8 + 0.5)
            return v

        out = {**data, "legacy_scale": True}
        for d in dims:
            out[d] = rescale(data.get(d))
        raw_urgency = data.get("urgency") if data.get("urgency") is not None else None
        if raw_urgency is None:
            raw_urgency = data.get("urgency_or_alumni")
        out["urgency"] = rescale(raw_urgency)
        return out


class KeyFacts(BaseModel):
    model_config = ConfigDict(extra="allow")
    funding: str | None = None
    investors: str | None = None
    revenue: str | None = None
    trigger: str | None = None
    competitor_signal: str | None = None
    strategic_hook: str | None = None
    us_presence: str | None = None
    alumni_match: str | None = None
    taxonomy_category: str | None = None
    ops_fit_note: str | None = None
    quota_filler: bool | None = None

    @field_validator(
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
        mode="before",
    )
    @classmethod
    def _coerce_str(cls, v: Any) -> str | None:
        return _to_str(v)


class ScannedSignal(BaseModel):
    """One candidate as emitted by the V2.1 scanner."""

    model_config = ConfigDict(extra="ignore")
    company: str = Field(min_length=1)
    signal_date: str | None = None
    score: int = Field(ge=0, le=100)
    tier: str | None = None
    track: int = 1
    person: str | None = None
    role: str | None = None
    horizon_weeks: str | None = None
    source_url: str | None = None
    industry_meta: str | None = None
    recommended_team: str | None = None
    recommended_series: str | None = None
    timing_label: str | None = None
    trigger_reason: str | None = None
    key_facts: KeyFacts = Field(default_factory=KeyFacts)
    score_breakdown: ScoreBreakdown | None = None
    of_gate_passed: bool | None = None
    confidence_level: str | None = None

    @field_validator("company", mode="before")
    @classmethod
    def _company(cls, v: Any) -> str:
        return (_to_str(v) or "").strip()

    @field_validator(
        "signal_date",
        "tier",
        "person",
        "role",
        "horizon_weeks",
        "source_url",
        "industry_meta",
        "recommended_team",
        "timing_label",
        "trigger_reason",
        "confidence_level",
        mode="before",
    )
    @classmethod
    def _strs(cls, v: Any) -> str | None:
        return _to_str(v)

    @field_validator("track", mode="before")
    @classmethod
    def _track(cls, v: Any) -> int:
        try:
            t = int(v)
        except (TypeError, ValueError) as exc:
            raise ValueError("track must be 1 or 2") from exc
        if t not in (1, 2):
            raise ValueError("track must be 1 or 2")
        return t

    @field_validator("recommended_series", mode="before")
    @classmethod
    def _series(cls, v: Any) -> str | None:
        s = (_to_str(v) or "").upper().replace(".", "").strip()
        if not s:
            return None
        if s in {"F1", "FORMULA 1", "FORMULA ONE"}:
            return "F1"
        if s in {"FE", "FORMULA E"}:
            return "FE"
        if s in {"DUAL", "BOTH", "F1/FE", "FE/F1"}:
            return "DUAL"
        raise ValueError(f"recommended_series must be F1 or FE, got {v!r}")

    @property
    def trigger_text(self) -> str:
        return self.trigger_reason or self.key_facts.trigger or ""


def parse_scan_output(text: str, min_n: int = 1, max_n: int = 12) -> list[ScannedSignal]:
    """Scanner text → validated candidates. Raises ParseError with a message fit to feed back."""
    items = extract_json_array(text)
    if not items:
        raise ParseError("scanner returned an empty array")
    signals: list[ScannedSignal] = []
    problems: list[str] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            problems.append(f"item {i}: not an object")
            continue
        try:
            signals.append(ScannedSignal.model_validate(item))
        except ValidationError as exc:
            errs = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors())
            problems.append(f"item {i} ({item.get('company', '?')}): {errs}")
    if problems:
        raise ParseError("candidate objects failed validation — " + " | ".join(problems))
    if len(signals) < min_n:
        raise ParseError(f"expected at least {min_n} candidates, got {len(signals)}")
    return signals[:max_n]
