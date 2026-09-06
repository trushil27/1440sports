"""Defects seen on the first in-session live render (Crusoe N° 121, 5 Sep 2026)."""

from __future__ import annotations

from intel import render
from intel.models import Claim, ClaimType, Verification, VerificationMethod, VerificationResult
from intel.seed import load_seeds
from tests.fixtures.ramp_brief import ramp_brief_data


def test_spec_emphasis_markup_renders_as_bold_not_as_a_literal_tag():
    html = render.render_html(ramp_brief_data())
    assert '<b class="hl">FOUR YEARS</b>' in html
    assert "&lt;b class=" not in html and "&lt;font" not in html


def _claim(cid: int, text: str, section: str, verified: bool = True) -> Claim:
    c = Claim(id=cid, section=section, text=text, claim_type=ClaimType.funding, load_bearing=True)
    c.verifications = [
        Verification(
            status=VerificationResult.verified if verified else VerificationResult.unverified,
            method=VerificationMethod.manual,
        )
    ]
    return c


def test_proof_points_are_one_card_per_figure_with_key_facts_first():
    claims = [
        _claim(1, "Crusoe has reportedly closed a $3B+ Series F at a ~$30B valuation", "deck"),
        _claim(
            2, "$3B+ Series F at ~$30B post-money, reported by Bloomberg 3 Sep 2026", "key_facts"
        ),
        _claim(3, "Crusoe's reported $3B+ Series F at roughly $30B post-money", "the_case_p1"),
        _claim(4, "Bloomberg also reports a ~$13B, five-year AI-cloud contract", "the_case_p1"),
        _claim(5, "$1.375B Series E at a valuation above $10B (Oct 2025)", "key_facts", False),
        _claim(6, "Fluidstack raised a reported $1.5B at an $18B valuation", "extended"),
    ]
    claims[5].load_bearing = False
    pts = render.proof_points_from_ledger(claims)
    assert all(p.claim_id != 6 for p in pts)  # rival / estimate figures never become proof
    assert [p.value for p in pts] == ["$3B+", "$13B", "$1.375B"]
    assert pts[0].claim_id == 2  # the scanner's key fact wins over the prose copy
    assert [p.verified for p in pts] == [True, True, False]


def test_gridfit_sees_cloud_rivals_for_a_gpu_cloud_company(session):
    load_seeds(session)
    lane = render._lane_tokens("AI Infrastructure · GPU Cloud / Datacentre Builder")
    assert "cloud" in lane
    rows, _ = render.build_gridfit(session, "F1", "MoneyGram Haas F1 Team", lane, lane, max_rows=11)
    by_team = {r.team: r for r in rows}
    # GRID FIT rows carry the 2026 entry name (team_profiles display_name), not the
    # sponsor-table key, so the block agrees with the recommended-team label.
    assert by_team["TGR Haas F1 Team"].recommended
    assert by_team["TGR Haas F1 Team"].status == "open"
    assert by_team["Oracle Red Bull Racing"].label == "TAKEN"
    assert "Oracle" in by_team["Oracle Red Bull Racing"].detail
    assert by_team["Aston Martin Aramco F1 Team"].label == "TAKEN"
    assert "CoreWeave" in by_team["Aston Martin Aramco F1 Team"].detail
    assert "Aramco" not in by_team["Aston Martin Aramco F1 Team"].detail  # fuel is not a rival
    assert "Core Scientific" in by_team["Cadillac F1 Team"].detail
    assert "Google Cloud" in by_team["McLaren Mastercard F1 Team"].detail  # 2026 entry name
    assert by_team["Mercedes-AMG Petronas F1 Team"].label == "TAKEN"  # Microsoft
