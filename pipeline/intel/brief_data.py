"""BRIEF_DATA — the field contract between writer, audit and renderer (build brief §6.6).

The writer model authors the ``Written*`` fields (its output is validated into
``WrittenBrief``). The pipeline then computes everything that must never come from a
model — proof points and sources from the claims ledger, GRID FIT from the sponsors
table, the decision-maker VERIFIED tag, footer text — into ``BriefData`` for rendering.

Field names follow spec/n8n_v21_prompts.md NODE 2 where the field existed there
(deck, the_case_p1/p2, why_now_callout, why_team_para, deal_arch_para, decision_maker_*,
opening_angle_*, score_cells, risks, footer_*), plus the June-2026 format additions
(bottom_line, value section, risk detail, signals). ``spec/production_roadmap.md``
§2.1.8 is the source for the value-section modes and the three-year minimum.
"""

from __future__ import annotations

import html
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# reportlab-style inline markup the spec writer prompt asks for, e.g.
# <font name='Poppins-Bold' size='9.5'>UPPERCASE PHRASE</font>
_FONT_TAG = re.compile(r"<font[^>]*>(.*?)</font>", re.IGNORECASE | re.DOTALL)
_ANY_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")
WHY_NOW_PREFIX = re.compile(r"^\s*(?:<[^>]+>)?\s*WHY NOW\s*(?:</[^>]+>)?\s*(?:&nbsp;)*\s*", re.I)


def strip_markup(text: str | None) -> str:
    """Plain text: font tags → their content, other tags removed, entities decoded."""
    s = _FONT_TAG.sub(r"\1", text or "")
    s = _ANY_TAG.sub("", s)
    s = html.unescape(s).replace(" ", " ")
    return _WS.sub(" ", s).strip()


def emphasis_to_html(text: str | None) -> str:
    """Render the spec's inline-bold markup as HTML the template styles (``<b class="hl">``)."""
    s = html.escape(html.unescape(text or ""), quote=False)
    # re-open the font tags we just escaped
    s = re.sub(
        r"&lt;font[^&]*?&gt;(.*?)&lt;/font&gt;",
        r'<b class="hl">\1</b>',
        s,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return s.replace("&amp;nbsp;", " ")


def word_count(text: str | None) -> int:
    return len(strip_markup(text).split())


class ScoreCell(BaseModel):
    model_config = ConfigDict(extra="ignore")
    label: str
    num: int = Field(ge=0, le=20)
    denom: str = "/ 20"
    note: str

    @classmethod
    def from_list(cls, item: Any) -> ScoreCell:
        if isinstance(item, dict):
            return cls.model_validate(item)
        label, num, denom, note = list(item) + [""] * (4 - len(item))
        return cls(
            label=str(label), num=int(str(num).strip()), denom=str(denom) or "/ 20", note=str(note)
        )


class Risk(BaseModel):
    model_config = ConfigDict(extra="ignore")
    label: str
    detail: str = ""
    counter: str

    @classmethod
    def from_list(cls, item: Any) -> Risk:
        if isinstance(item, dict):
            return cls.model_validate(item)
        parts = list(item)
        if len(parts) == 2:
            return cls(label=str(parts[0]), detail="", counter=str(parts[1]))
        return cls(label=str(parts[0]), detail=str(parts[1]), counter=str(parts[2]))


ValueMode = Literal["A", "B", "C"]


class WrittenBrief(BaseModel):
    """What the writer model must emit (NODE 2 fields + June-2026 additions)."""

    model_config = ConfigDict(extra="ignore")
    brief_number: str = ""
    track_label: str = ""
    company: str
    industry_meta: str
    hq: str | None = None
    ticker: str | None = None
    deck: str
    score: int = Field(ge=0, le=100)
    timing_label: str
    series_label: str
    team_label: str
    horizon_label: str
    hot_top_tier: bool = False
    confidence_level: str = "HIGH"
    the_case_p1: str
    the_case_p2: str
    why_now_callout: str
    why_team_label: str
    why_team_para: str
    value_section: bool = True
    value_section_label: str = ""
    value_mode: ValueMode | None = None
    value_content: str = ""
    deal_arch_para: str
    decision_maker_name: str
    decision_maker_role: str
    decision_maker_bio: str
    opening_angle_intro: str
    opening_angle_quote: str
    score_cells: list[ScoreCell]
    risks: list[Risk]
    bottom_line: str = ""
    signals: list[str] = Field(default_factory=list)
    footer_company: str
    footer_date: str

    @field_validator("score_cells", mode="before")
    @classmethod
    def _cells(cls, v: Any) -> list[ScoreCell]:
        return [ScoreCell.from_list(x) for x in (v or [])]

    @field_validator("risks", mode="before")
    @classmethod
    def _risks(cls, v: Any) -> list[Risk]:
        return [Risk.from_list(x) for x in (v or [])]

    @field_validator("signals", mode="before")
    @classmethod
    def _signals(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return [str(s).strip() for s in (v or []) if str(s).strip()]

    @property
    def why_now_text(self) -> str:
        """WHY NOW body without the spec's mandatory inline 'WHY NOW' prefix."""
        return WHY_NOW_PREFIX.sub("", self.why_now_callout or "", count=1)


class ProofPoint(BaseModel):
    value: str
    fact: str
    source_url: str | None = None
    verified: bool = False
    claim_id: int | None = None


class GridRow(BaseModel):
    team: str
    recommended: bool = False
    status: Literal["prime", "open", "crowded", "conflict"]
    label: str
    detail: str


class BriefData(WrittenBrief):
    """Everything the renderer needs. Computed fields come from the pipeline, never the model."""

    proof_points: list[ProofPoint] = Field(default_factory=list)
    all_proof_points_verified: bool = False
    gridfit: list[GridRow] = Field(default_factory=list)
    gridfit_note: str = ""
    sources: list[str] = Field(default_factory=list)
    decision_maker_verified: bool = False
    verification_status: str = "pending"
    claims_verified: int = 0
    claims_total: int = 0
    discovery: str = "scan"
    date_long: str = ""

    def render_context(self) -> dict[str, Any]:
        """Plain dict for Jinja with markup converted for HTML."""
        d = self.model_dump()
        for key in (
            "deck",
            "the_case_p1",
            "the_case_p2",
            "why_team_para",
            "value_content",
            "deal_arch_para",
            "decision_maker_bio",
            "opening_angle_intro",
            "opening_angle_quote",
            "bottom_line",
        ):
            d[key + "_html"] = emphasis_to_html(getattr(self, key))
        d["why_now_html"] = emphasis_to_html(self.why_now_text)
        d["risks_html"] = [
            {
                "label": r.label,
                "detail": emphasis_to_html(r.detail),
                "counter": emphasis_to_html(r.counter),
            }
            for r in self.risks
        ]
        return d
