"""Ramp N° 017 (14 Jun 2026) — a real production brief from this repo, as a WrittenBrief.

Text is copied from ``briefs/2026-06-14/ramp.md`` (the June-2026 production format; the
same brief as the N° 007 PDF emailed to the MD on 6 Jun 2026, which is the layout
reference in ``tests/fixtures/ramp_N007_2026-06-06_reference.pdf``), trimmed only where the
Phase 2.1.8 word ceilings require it. Nothing here is invented.
"""

from __future__ import annotations

from intel.brief_data import BriefData, GridRow, ProofPoint, WrittenBrief

RAMP_WRITTEN = {
    "brief_number": "017",
    "track_label": "",
    "company": "Ramp",
    "industry_meta": "Fintech · Corporate Spend Management / AI Finance",
    "hq": "New York",
    "ticker": "Private (~$44B; $750M round closed Jun 2026)",
    "deck": (
        "Ramp closed a $750M round at a $44B valuation in June 2026 (up ~38% from $32B six "
        "months earlier), crossed $1B+ ARR while staying free-cash-flow positive, and is "
        "launching in the UK/EU this summer - with no spend-management brand anywhere on the "
        "F1 grid."
    ),
    "score": 84,
    "timing_label": "HOT",
    "series_label": "F1",
    "team_label": "Visa Cash App Racing Bulls",
    "horizon_label": "6-10 WKS",
    "hot_top_tier": False,
    "confidence_level": "HIGH",
    "the_case_p1": (
        "Ramp's just-closed $750M round at a ~$44B valuation (June 2026, led by ICONIQ, GIC "
        "and Ontario Teachers') - up roughly 38% from $32B only six months earlier - is the "
        "brand-reckoning moment when a category-defining fintech turns from growth story into "
        "institutional brand. It crossed $1B+ in annualized revenue while remaining "
        "free-cash-flow positive, acquired UK/EU payments platform Billhop (March 2026), and "
        "begins onboarding UK and European businesses this summer."
    ),
    "the_case_p2": (
        "The grid gap is total: no spend-management or AI-finance brand holds a position "
        "anywhere in F1, and direct rival Brex has no motorsport deal, so the entire "
        "corporate-spend category sits unoccupied."
    ),
    "why_now_callout": (
        "<font name='Poppins-Bold' size='9'>WHY NOW</font>&nbsp;&nbsp;The $750M raise has just "
        "closed at a $44B valuation - brand-investment authority is at its peak right now - "
        "and Ramp begins UK/EU onboarding this summer. The British Grand Prix at Silverstone "
        "(3-5 July 2026) is the natural UK activation window for that launch, and the "
        "corporate-spend category on the grid is uncontested."
    ),
    "why_team_label": "WHY VISA CASH APP RACING BULLS",
    "why_team_para": (
        "Racing Bulls already carries Visa as its title sponsor, and Ramp's deepened multi-year "
        "Visa issuing agreement makes co-presence structural rather than conflicting: Ramp "
        "becomes the spend-management intelligence layer above the Visa payment rail, "
        "reinforcing both brands. Cash App's younger demographic mirrors Ramp's founder, "
        "developer and CFO-suite audience, and no spend-management brand is anywhere near the "
        "car - so Ramp would own, not share, the category. The British GP at Silverstone gives "
        "the UK launch a home-market stage."
    ),
    "value_section": True,
    "value_section_label": "VALUE TO VISA CASH APP RACING BULLS",
    "value_mode": "B",
    "value_content": (
        "MODE B - real operational value, off-car. Ramp's payments rail and back-office stack "
        "map onto Racing Bulls' commercial machine: paddock supplier settlements, "
        "sponsor-activation treasury flows, and a partner-onboarding funnel of venture-backed, "
        "CFO-led companies - exactly the audience the team wants. In return the team offers "
        "B2B-fit surfaces: garage hospitality, pit-wall broadcast cuts, and founder-audience "
        "content timed to the British GP."
    ),
    "deal_arch_para": (
        "Entry at Official Spend Management Partner tier. <font name='Poppins-Bold' "
        "size='9.5'>FOUR YEARS</font>, to span the EU/UK build-out cycle and capture full FIA "
        "calendar rotations through Silverstone, Las Vegas and Austin. Estimated $6-9M/yr. "
        "Scope: garage and cockpit logo rights, Visa co-activation rights, hospitality at the "
        "British GP and Las Vegas, and digital content rights for Ramp's CFO-audience channels."
    ),
    "decision_maker_name": "Eric Glyman",
    "decision_maker_role": "CEO & Co-Founder, Ramp",
    "decision_maker_bio": (
        "Glyman co-founded Ramp after co-founding Paribus (acquired by Capital One). He drives "
        "strategic capital allocation and partnership decisions; the just-closed $750M raise "
        "and the deepened Visa partnership are direct outputs of his office, so a sponsorship "
        "of this scale is his call."
    ),
    "opening_angle_intro": "",
    "opening_angle_quote": (
        "&ldquo;Eric, the $44B round and your UK/EU launch this summer line up exactly with "
        "Racing Bulls - Ramp as the spend layer above the Visa rail - and the British GP is a "
        "ready-made home-market activation. 25 minutes before a rival notices the open "
        "lane?&rdquo;"
    ),
    "score_cells": [
        ["TIMING", "19", "/ 20", "Round just closed; UK/EU launch this summer."],
        ["CAPACITY", "20", "/ 20", "$44B valuation, $1B+ ARR, FCF positive."],
        ["BRAND FIT", "19", "/ 20", "Visa co-presence structural; CFO audience matches."],
        ["URGENCY", "14", "/ 20", "British GP window; no hard lock."],
        ["OPS FIT", "12", "/ 20", "MODE B: back-office and treasury."],
    ],
    "risks": [
        [
            "VISA CHANNEL CONFLICT",
            "Ramp's Visa issuing deal could read as conflicting with the Visa title.",
            "Frame Ramp as the spend-intelligence layer above the Visa relationship; the roles "
            "are distinct and mutually reinforcing.",
        ],
        [
            "OFF-CAR RELEVANCE (MODE B)",
            "Spend management serves the back office, not the car.",
            "Lead with the Visa co-presence and a CFO/founder hospitality and pipeline play.",
        ],
    ],
    "bottom_line": (
        "A just-closed $750M round at a $44B valuation (+38%), $1B+ ARR and FCF-positive, "
        "launching in the UK/EU this summer - and no spend-management brand sits anywhere on "
        "the F1 grid. Visa Cash App Racing Bulls is the structural fit: Ramp as the spend "
        "layer above the Visa rail."
    ),
    "signals": ["funding_event", "new_leadership", "category_whitespace"],
    "footer_company": "RAMP",
    "footer_date": "14 JUN 2026",
}

# The proof points / sources exactly as the production brief carried them (key_facts in
# data/prospects.json → rendered N° 007/017). Used to reproduce the reference layout.
RAMP_PROOF_POINTS = [
    ProofPoint(
        value="~$44B",
        fact="Valuation ($750M round closed 4 Jun 2026; ICONIQ/GIC/Ontario Teachers')",
        source_url="https://techcrunch.com/2026/06/04/ramp-raises-750m-at-44b-valuation-as-investors-hunger-for-fintechs-with-an-ai-story/",
        verified=True,
    ),
    ProofPoint(
        value="$750M",
        fact="Latest round (+38% step-up from $32B in Nov 2025)",
        source_url="https://www.cnbc.com/2026/06/04/ramp-valuation-funding-ai-spend.html",
        verified=True,
    ),
    ProofPoint(
        value="$1B+", fact="Annualized revenue, free-cash-flow positive (per CEO)", verified=True
    ),
    ProofPoint(value="Eric Glyman", fact="Co-founder & CEO", verified=True),
    ProofPoint(
        value="Billhop acquisition",
        fact="UK/EU expansion - acquired Billhop (Mar 2026), onboarding UK/EU this summer",
        verified=True,
    ),
    ProofPoint(
        value="Visa partnership",
        fact=(
            "Deepened multi-year Visa issuing partnership (structural co-presence with "
            "Racing Bulls' title)"
        ),
        verified=True,
    ),
]
RAMP_GRIDFIT = [
    GridRow(
        team="Visa Cash App Racing Bulls",
        recommended=True,
        status="open",
        label="OPEN",
        detail="no rival in this category lane",
    ),
    GridRow(team="Audi", recommended=False, status="crowded", label="CROWDED", detail="Revolut"),
    GridRow(
        team="Haas",
        recommended=False,
        status="crowded",
        label="CROWDED",
        detail="Mphasis, RUCKUS Networks, MoneyGram",
    ),
    GridRow(
        team="McLaren",
        recommended=False,
        status="open",
        label="OPEN",
        detail="no rival in this category lane",
    ),
]
RAMP_SOURCES = [
    "https://techcrunch.com/2026/06/04/ramp-raises-750m-at-44b-valuation-as-investors-hunger-for-fintechs-with-an-ai-story/",
    "https://www.cnbc.com/2026/06/04/ramp-valuation-funding-ai-spend.html",
    "https://www.prnewswire.com/news-releases/ramp-acquires-billhop-to-expand-access-for-uk-and-european-customers-302712928.html",
    "https://www.prnewswire.com/news-releases/ramp-and-visa-deepen-partnership-to-power-the-next-era-of-autonomous-finance-302728894.html",
    "https://ramp.com/blog/ramp-is-launching-in-europe",
]


def ramp_written() -> WrittenBrief:
    return WrittenBrief.model_validate(RAMP_WRITTEN)


def ramp_brief_data(**overrides) -> BriefData:
    base = dict(
        RAMP_WRITTEN,
        proof_points=RAMP_PROOF_POINTS,
        all_proof_points_verified=True,
        gridfit=RAMP_GRIDFIT,
        gridfit_note="",
        sources=RAMP_SOURCES,
        decision_maker_verified=True,
        verification_status="verified",
        claims_verified=10,
        claims_total=10,
        discovery="seeded",
        date_long="14 JUN 2026",
    )
    base.update(overrides)
    return BriefData.model_validate(base)
