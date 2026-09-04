"""§9.7 layout regression: exactly 2 pages, June-2026 production structure, reference match."""

from __future__ import annotations

import re
from pathlib import Path

import pymupdf
import pytest

from intel import render
from intel.brief_data import BriefData, ProofPoint
from tests.fixtures.ramp_brief import ramp_brief_data

REFERENCE = Path(__file__).parent / "fixtures" / "ramp_N007_2026-06-06_reference.pdf"

# Section headers in the order the June-2026 production brief carries them (letter-spaced
# in the PDF text layer, hence the regex normalisation below).
PAGE1_HEADERS = ["THE CASE", "WHY NOW", "PROOF POINTS", "GRID FIT", "BOTTOM LINE"]
PAGE2_HEADERS = [
    "WHY VISA CASH APP RACING BULLS",
    "VALUE TO VISA CASH APP RACING BULLS",
    "DEAL ARCHITECTURE",
    "PRIMARY DECISION-MAKER",
    "OPENING ANGLE",
    "SCORE COMPOSITION",
    "RISKS & COUNTERS",
    "SOURCES",
]


def _page_texts(pdf: Path) -> list[str]:
    """Page texts with ALL whitespace removed, upper-cased (section headers are letter-spaced
    in the PDF text layer, e.g. 'T H E C A S E')."""
    doc = pymupdf.open(pdf)
    return [re.sub(r"\s+", "", p.get_text().upper()) for p in doc]


def _flat(s: str) -> str:
    return re.sub(r"\s+", "", s.upper())


def _headers_in_order(text: str, headers: list[str]) -> list[int]:
    return [text.find(_flat(h)) for h in headers]


def _similarity(a: Path, b: Path, dpi: int = 30) -> float:
    """Mean grayscale agreement of the two 2-page PDFs at low resolution (1.0 = identical)."""
    import numpy as np

    scores = []
    da, db = pymupdf.open(a), pymupdf.open(b)
    for pa, pb in zip(da, db, strict=True):
        ia = pa.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
        ib = pb.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
        xa = np.frombuffer(ia.samples, dtype=np.uint8).reshape(ia.h, ia.w).astype(float)
        xb = np.frombuffer(ib.samples, dtype=np.uint8).reshape(ib.h, ib.w).astype(float)
        h, w = min(xa.shape[0], xb.shape[0]), min(xa.shape[1], xb.shape[1])
        scores.append(1 - abs(xa[:h, :w] - xb[:h, :w]).mean() / 255)
    return float(sum(scores) / len(scores))


@pytest.fixture(scope="module")
def rendered(tmp_path_factory) -> dict[str, Path]:
    out = tmp_path_factory.mktemp("render")
    data = ramp_brief_data()
    june = render.render_brief(data, out / "june", "ramp", font_stack="june")
    brand = render.render_brief(data, out / "brand", "ramp", font_stack="brand")
    return {"june": Path(june["pdf"]), "brand": Path(brand["pdf"])}


def test_reference_is_two_pages_with_the_expected_structure():
    texts = _page_texts(REFERENCE)
    assert len(texts) == 2
    assert _headers_in_order(texts[0], PAGE1_HEADERS) == sorted(
        _headers_in_order(texts[0], PAGE1_HEADERS)
    )
    assert all(i >= 0 for i in _headers_in_order(texts[1], PAGE2_HEADERS))


@pytest.mark.parametrize("stack", ["june", "brand"])
def test_render_is_exactly_two_pages_in_the_production_order(rendered, stack):
    texts = _page_texts(rendered[stack])
    assert len(texts) == 2
    p1 = _headers_in_order(texts[0], PAGE1_HEADERS)
    p2 = _headers_in_order(texts[1], PAGE2_HEADERS)
    assert all(i >= 0 for i in p1) and p1 == sorted(p1), p1
    assert all(i >= 0 for i in p2) and p2 == sorted(p2), p2
    assert _flat("1440 SPORTS · LONDON") in texts[0] and _flat("RAMP · 14 JUN 2026") in texts[0]
    assert _flat("OPPORTUNITY / 100") in texts[0]
    assert _flat("◆ RECOMMENDED") in texts[0]
    assert _flat("CEO & CO-FOUNDER, RAMP · VERIFIED") in texts[1]


def test_june_font_stack_matches_the_reference_pdf_at_low_resolution(rendered):
    score = _similarity(rendered["june"], REFERENCE)
    assert score >= 0.90, f"layout drifted from the June-2026 reference (similarity {score:.3f})"


def test_unverified_figures_change_the_header_and_footer(tmp_path):
    pts = list(ramp_brief_data().proof_points)
    pts[2] = ProofPoint(**{**pts[2].model_dump(), "verified": False})
    data = ramp_brief_data(
        proof_points=pts,
        all_proof_points_verified=False,
        verification_status="needs_review",
        claims_verified=9,
        claims_total=10,
        decision_maker_verified=False,
    )
    html = render.render_html(data)
    assert "not yet verified to a primary source" in html
    assert "VERIFY BEFORE CIRCULATION" in html
    assert "role not yet verified" in html
    assert "9 of 10 load-bearing claims verified" in html
    out = render.render_brief(data, tmp_path, "ramp-review")
    assert out["pages"] == 2


def test_overflow_raises_instead_of_shipping_three_pages(tmp_path):
    data = ramp_brief_data()
    too_long = BriefData.model_validate(
        {
            **data.model_dump(),
            "the_case_p2": (data.the_case_p2 + " ") * 12,
            "why_team_para": data.why_team_para * 4,
        }
    )
    with pytest.raises(render.PageOverflow):
        render.render_brief(too_long, tmp_path, "ramp-overflow")


def test_value_mode_rules_from_phase_218():
    assert render.value_mode_for(15, "AI / Observability") == "A"
    assert render.value_mode_for(12, "Fintech · Corporate Spend") == "B"
    assert render.value_mode_for(13, "Industrial software") == "B"
    assert render.value_mode_for(8, "Consumer fitness app") == "C"
    assert render.value_mode_for(16, "Fintech · Payments") == "A"  # OF ≥ 14 wins over industry
