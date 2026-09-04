"""Brief writer (build brief §6.6).

System prompt = the verbatim Phase 2.1.3 writer prompt from spec/n8n_v21_prompts.md NODE 2
(``intel/prompts/writer_v213_system.txt``) + an addendum for what the June-2026 production
format needs beyond it (value section modes and three-year minimum from
spec/production_roadmap.md §2.1.8; bottom line, risk detail, signals, hq/ticker). The
addendum is clearly delimited so the spec text itself stays untouched.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any, Protocol

from pydantic import ValidationError

from intel.brief_data import WrittenBrief
from intel.config import Settings, get_settings
from intel.parse import ParseError, ScannedSignal, extract_json_object

PROMPTS = Path(__file__).parent / "prompts"

WRITER_ADDENDUM = """

=====================================================================
JUNE-2026 FORMAT ADDENDUM (Phase 2.1.8 + production brief format). Where a line below
conflicts with an instruction above, THIS ADDENDUM WINS.
=====================================================================

1. DEAL ARCHITECTURE MINIMUM IS THREE YEARS. Ignore the "TWO YEARS" instruction above.
   State the term in bold uppercase: <font name='Poppins-Bold' size='9.5'>THREE YEARS</font>,
   FOUR YEARS or FIVE YEARS (three = entry/associate, four = major partner, five = title /
   category-defining). Never propose a two-year deal.

2. VALUE TO [TEAM] SECTION. Add these fields to BRIEF_DATA:
   "value_section": true,
   "value_section_label": "VALUE TO <TEAM NAME UPPERCASE>",
   "value_mode": "<A|B|C — use the mode given in the user message>",
   "value_content": "<70 words MAX>"
   The mode is decided by code, not by you:
   MODE A (operational): what the product physically does on the car, in the factory or on
   the broadcast feed — name the operational need and the deployment surface.
   MODE B (commercial back-office): paddock supplier settlements, treasury, partner
   onboarding, sponsor-activation flows — what the team's commercial operation gains.
   MODE C (audience / brand pipeline): user-base demographics, race-weekend activation,
   customer-acquisition framing — what the team's audience gives the company and vice versa.
   Every mode must be concrete and two-way: what the team gets AND what the company gets.
   Never a feature list, never "perfect fit for motorsport".

3. RISKS: write EXACTLY TWO risks (the value section is present). Each risk is a
   three-element array ["UPPERCASE LABEL", "the risk in one sentence", "the counter in one
   sentence"]; label excluded, risk + counter together are 32 words MAX.

4. BOTTOM LINE: add "bottom_line": one or two sentences, 45 words MAX, that a busy MD could
   act on alone — the company-side moment plus the single team verdict. This is the ONLY
   place besides why_team_para where the team may be argued for.

5. DECK RULE (hardened): the deck never claims a team vacancy ("[TEAM] has no X",
   "the slot at [TEAM] is open"). The team may be named only as a destination, never
   explained. If unsure, do not mention the team in the deck at all.

6. EXTRA FIELDS: "hq": city from the signal data or null; "ticker": listing or valuation
   line ONLY if it is in the signal data, else null; "signals": 2-4 tags from this
   vocabulary only: funding_event, ipo_filing, ipo_roadshow, new_leadership,
   category_whitespace, expansion, product_launch, partnership, alumni_tie, catalyst.

7. NOT YOURS TO WRITE: proof points, GRID FIT rows, the SOURCES list and the decision-maker
   VERIFIED tag are computed by the pipeline from the verified-claims ledger and the sponsor
   table. Do not emit them. Do not cite venues or races that are not on the current F1 /
   Formula E calendar — an unverifiable race blocks the brief.

8. If the user message contains an AUDIT FEEDBACK block, fix every numbered violation and
   re-emit the complete BRIEF_DATA. Keep everything that was not flagged.
"""

_TODAY_TOKEN = "{{ $today.format('d MMM yyyy').toUpperCase() }}"
_JSON_TOKEN = re.compile(r"\{\{\s*\$json\.([\w.]+)\s*\}\}")
_BRIEF_BLOCK = re.compile(r"<BRIEF_DATA>(.*?)</BRIEF_DATA>", re.DOTALL)


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
    system = (PROMPTS / "writer_v213_system.txt").read_text(encoding="utf-8") + WRITER_ADDENDUM
    user = (PROMPTS / "writer_v213_user.txt").read_text(encoding="utf-8")
    user = user.replace(_TODAY_TOKEN, date_upper(run_date))
    extra = {
        "brief_number": brief_number,
        "confidence_level": signal.confidence_level or "MEDIUM",
        "of_gate_passed": signal.of_gate_passed if signal.of_gate_passed is not None else "",
    }
    user = _JSON_TOKEN.sub(lambda m: _lookup(signal, m.group(1), extra), user)
    user += (
        f"\n\nVALUE SECTION MODE (decided by code from ops_fit and industry): {value_mode}\n"
        "Emit the addendum fields (value_section, value_section_label, value_mode, value_content, "
        "bottom_line, hq, ticker, signals) and exactly TWO risks as three-element arrays."
    )
    if feedback:
        user += (
            f"\n\nAUDIT FEEDBACK — fix every item and re-emit the complete BRIEF_DATA:\n{feedback}"
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
        with self._client.messages.stream(
            model=model,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": user}],
            thinking={"type": "adaptive"},
        ) as stream:
            response = stream.get_final_message()
        if response.stop_reason == "refusal":
            raise ParseError("writer refused")
        return "\n".join(b.text for b in response.content if getattr(b, "type", "") == "text")


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
