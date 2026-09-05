"""Brief writer (build brief §6.6).

System prompt = the verbatim production writer prompt from the live n8n export
(``Anthropic - Write Brief`` node, v2.1.8 — ``intel/prompts/writer_v218_system.txt``) + a
short delimited addendum for the June-2026 BRIEF_DATA fields the production prompt does not
emit (``value_mode``, three-element risks, ``bottom_line``, ``hq`` / ``ticker`` /
``signals``) and for what the pipeline computes itself. Everything the production prompt
already covers (three-year minimum, VALUE TO [TEAM] modes, deck rule, risk count, retry
handling) lives only in the verbatim text.

A failed audit is fed back exactly as the production ``Retry Prep`` node does: the
``=== RETRY MODE - CORRECTING PREVIOUS DRAFT ===`` block goes into the user message at the
``{{ JSON.stringify($json._retry_block || '').slice(1, -1) }}`` slot.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Protocol

from pydantic import ValidationError

from intel.brief_data import WrittenBrief
from intel.config import Settings, get_settings
from intel.llm import ModelTurnError, complete_text
from intel.parse import ParseError, ScannedSignal, extract_json_object

PROMPTS = Path(__file__).parent / "prompts"

# Only what the June-2026 BRIEF_DATA contract needs beyond the verbatim production prompt.
WRITER_ADDENDUM = """

=====================================================================
JUNE-2026 FORMAT ADDENDUM — extra BRIEF_DATA fields for the June-2026 renderer. Every rule
above stands unchanged; this only adds fields.
=====================================================================

1. VALUE SECTION MODE: the mode (A, B or C, as defined above) is decided by code and given
   in the user message — use that mode, and add "value_mode": "A" | "B" | "C" to BRIEF_DATA.

2. RISK SHAPE: each risk is a three-element array ["UPPERCASE LABEL", "the risk in one
   sentence", "the counter in one sentence"]; label excluded, risk + counter together are
   32 words MAX. The risk COUNT rule above (2 with the value section, 3 without) stands.

3. BOTTOM LINE: add "bottom_line": one or two sentences, 45 words MAX, that a busy MD could
   act on alone — the company-side moment plus the single team verdict. This is the ONLY
   place besides why_team_para where the team may be argued for.

4. EXTRA FIELDS: "hq": city from the signal data or null; "ticker": listing or valuation
   line ONLY if it is in the signal data, else null; "signals": 2-4 tags from this
   vocabulary only: funding_event, ipo_filing, ipo_roadshow, new_leadership,
   category_whitespace, expansion, product_launch, partnership, alumni_tie, catalyst.

5. NOT YOURS TO WRITE: proof points, GRID FIT rows, the SOURCES list and the decision-maker
   VERIFIED tag are computed by the pipeline from the verified-claims ledger and the sponsor
   table. Do not emit them. Do not cite venues or races that are not on the current F1 /
   Formula E calendar — an unverifiable race blocks the brief.

6. EXTENDED SECTIONS FOR THE APP PAGE (the 2-page PDF keeps every ceiling above; this block
   is read on screen by the MD and has no word ceiling, but every sentence must still be
   sourced, business-side and specific — write like a commercial director, not a marketer):
   "extended": {
     "why_now":   3-4 objects {"label": "...", "text": "..."} — the trigger and its date; the
                  budget / brand-authority moment it creates; the concrete calendar window
                  (only races on the current calendar); the competitive clock (who else could
                  take the lane and when).
     "why_team":  3-4 objects — the open category lane on THIS team and what it is worth; the
                  audience / market overlap in business terms; the activation platform the team
                  actually has (races, hospitality, content, facilities); why this team can
                  consume the product, not just carry the logo.
     "value":     3-4 objects — the operational workstream the team would run with the product;
                  the commercial lift (pipeline, deal flow, procurement, partner introductions);
                  content and ecosystem the partnership creates; what the team gives back.
     "ruled_out": one object {"team": "...", "reason": "..."} per team excluded, naming the
                  incumbent partner that closes the lane.
     "ask":       one sentence: the meeting ask and what the first conversation should settle.
   }
"""

RETRY_MODE_HEADER = "=== RETRY MODE - CORRECTING PREVIOUS DRAFT ==="

_TODAY_TOKEN = "{{ $today.format('d MMM yyyy').toUpperCase() }}"
_RETRY_TOKEN = "{{ JSON.stringify($json._retry_block || '').slice(1, -1) }}"
_JSON_TOKEN = re.compile(r"\{\{\s*\$json\.([\w.]+)\s*\}\}")
_BRIEF_BLOCK = re.compile(r"<BRIEF_DATA>(.*?)</BRIEF_DATA>", re.DOTALL)


def retry_block(violation_lines: str, previous_draft: dict[str, Any] | None = None) -> str:
    """The production ``Retry Prep`` block, verbatim. ``previous_draft`` (the failed
    BRIEF_DATA) is included when the caller has it; the orchestrator currently passes only
    the violation lines, so the PREVIOUS DRAFT section is omitted in that case."""
    parts = [
        "",
        RETRY_MODE_HEADER,
        "The previous draft of this brief failed automated audit. Fix EVERY violation below "
        "while keeping the facts intact.",
        "",
        "VIOLATIONS TO FIX:",
        violation_lines,
        "",
    ]
    if previous_draft is not None:
        parts += [
            "PREVIOUS DRAFT (BRIEF_DATA fields):",
            json.dumps(previous_draft, indent=2, ensure_ascii=False),
            "",
        ]
    parts += [
        "Produce a corrected BRIEF_DATA that resolves every violation. Keep the same facts; "
        "change only the prose that violates the rules. Apply the retry rules in the system "
        "prompt. There is no second retry - get it right this time.",
        "",
    ]
    return "\n".join(parts)


def date_upper(d: dt.date) -> str:
    """'D MMM YYYY' uppercase without a leading zero, e.g. '14 JUN 2026'."""
    return f"{d.day} {d.strftime('%b').upper()} {d.year}"


def _lookup(signal: ScannedSignal, path: str, extra: dict[str, Any]) -> str:
    if path in extra:
        return "" if extra[path] is None else str(extra[path])
    obj: Any = signal
    for part in path.split("."):
        if isinstance(obj, dict):
            obj = obj.get(part)
        else:
            obj = getattr(obj, part, None)
        if obj is None:
            return ""
    return "" if obj is None else str(obj)


def writer_prompts(
    signal: ScannedSignal,
    brief_number: str,
    run_date: dt.date,
    value_mode: str,
    feedback: str | None = None,
) -> tuple[str, str]:
    system = (PROMPTS / "writer_v218_system.txt").read_text(encoding="utf-8") + WRITER_ADDENDUM
    user = (PROMPTS / "writer_v218_user.txt").read_text(encoding="utf-8")
    user = user.replace(_TODAY_TOKEN, date_upper(run_date))
    user = user.replace(_RETRY_TOKEN, retry_block(feedback) if feedback else "")
    extra = {
        "brief_number": brief_number,
        "confidence_level": signal.confidence_level or "MEDIUM",
    }
    user = _JSON_TOKEN.sub(lambda m: _lookup(signal, m.group(1), extra), user)
    user += (
        f"\n\nVALUE SECTION MODE (decided by code from ops_fit and industry): {value_mode}\n"
        "Emit the addendum fields (value_mode, bottom_line, hq, ticker, signals) and the risks "
        "as three-element arrays."
    )
    return system, user


def parse_written(text: str) -> WrittenBrief:
    m = _BRIEF_BLOCK.search(text or "")
    payload = m.group(1) if m else text
    data = extract_json_object(payload)
    try:
        return WrittenBrief.model_validate(data)
    except ValidationError as exc:
        errs = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors())
        raise ParseError(f"BRIEF_DATA failed validation — {errs}") from exc


class Writer(Protocol):
    def write(self, *, model: str, system: str, user: str) -> str: ...


class AnthropicWriter:
    def __init__(self, client: Any | None = None) -> None:
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self._client = client

    def write(self, *, model: str, system: str, user: str) -> str:
        try:
            return complete_text(
                self._client,
                model=model,
                system=system,
                messages=[{"role": "user", "content": user}],
                max_tokens=32000,
                label="writer",
            ).text
        except ModelTurnError as exc:  # truncated / refused → the audit retry path
            raise ParseError(str(exc)) from exc


def write_brief(
    signal: ScannedSignal,
    brief_number: str,
    run_date: dt.date,
    value_mode: str,
    writer: Writer,
    settings: Settings | None = None,
    feedback: str | None = None,
) -> tuple[WrittenBrief, str]:
    settings = settings or get_settings()
    system, user = writer_prompts(signal, brief_number, run_date, value_mode, feedback)
    raw = writer.write(model=settings.writer_model, system=system, user=user)
    written = parse_written(raw)
    written.brief_number = brief_number
    written.footer_date = date_upper(run_date)
    if not written.footer_company:
        written.footer_company = signal.company.upper()
    return written, raw
