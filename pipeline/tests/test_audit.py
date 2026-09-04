"""Build brief §9.10: every one of the 13 audit rules has a passing and a failing fixture.

The baseline is a ``WrittenBrief`` built ONLY from the real Ramp brief in this repo
(briefs/2026-06-14/ramp.md — N° 017, Visa Cash App Racing Bulls, Eric Glyman, FOUR
YEARS, run date 14 Jun 2026), with sentences trimmed to the NODE 2 word ceilings.
Every failing fixture is the baseline with exactly one field changed. No company,
figure, person or race outside that brief appears here (build brief §0 rule 4).
"""

from __future__ import annotations

from datetime import date

import pytest

from intel.audit import (
    RULES,
    AuditResult,
    Violation,
    audit_brief,
    expected_footer_date,
    find_vacancy_proximity,
    page2_chars,
    shared_phrases,
    team_name_variants,
    violations_feedback,
)
from intel.brief_data import WrittenBrief, strip_markup, word_count

RUN_DATE = date(2026, 6, 14)
BOLD = "<font name='Poppins-Bold' size='9.5'>{}</font>"

# The original Ramp headline_long — it carries the "no spend-management brand anywhere on
# the F1 grid" vacancy claim next to a team mention, the exact deck failure rule 6 exists
# for. Used ONLY as the rule-6 failing fixture.
RAMP_ORIGINAL_HEADLINE = (
    "Ramp closed a $750M round at a $44B valuation in June 2026 (up ~38% from $32B six "
    "months earlier), crossed $1B+ ARR while staying free-cash-flow positive, and is "
    "launching in the UK/EU this summer - with no spend-management brand anywhere on the "
    "F1 grid, and the slot is open at Visa Cash App Racing Bulls."
)

BASELINE: dict = {
    "brief_number": "017",
    "track_label": "",
    "company": "Ramp",
    "industry_meta": "Fintech · Corporate Spend Management / AI Finance · New York",
    "hq": "New York",
    "ticker": None,
    # Company-side only: what changed for Ramp; the team appears nowhere in the deck.
    "deck": (
        "Ramp closed a $750M round at a $44B valuation in June 2026 (up ~38% from $32B six "
        "months earlier), crossed $1B+ ARR while staying free-cash-flow positive, and is "
        "launching in the UK/EU this summer."
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
        "brand-reckoning moment when a category-defining fintech turns from growth story "
        "into institutional brand. It crossed $1B+ in annualized revenue while remaining "
        "free-cash-flow positive, acquired UK/EU payments platform Billhop (March 2026), and "
        "begins onboarding UK and European businesses this summer. "
        + BOLD.format("THE BRAND-RECKONING MOMENT HAS ARRIVED.")
    ),
    # Landscape only; the team lands as the outcome, well clear of the vacancy clauses.
    "the_case_p2": (
        "The grid gap is total: no spend-management or AI-finance brand holds a position "
        "anywhere in F1, and direct rival Brex has no motorsport deal, so the entire "
        "corporate-spend category sits unoccupied. Audi carries Revolut and Haas carries "
        "Mphasis, RUCKUS Networks and MoneyGram, which rules both out on category-conflict "
        "grounds; Ramp's EU/UK expansion arc and its Visa issuing relationship land the "
        "profile at Visa Cash App Racing Bulls."
    ),
    "why_now_callout": (
        "<font name='Poppins-Bold' size='9'>WHY NOW</font>&nbsp;&nbsp;The $750M raise has "
        "just closed at a $44B valuation - brand-investment authority is at its peak - and "
        "Ramp begins UK/EU onboarding this summer. The British Grand Prix at Silverstone "
        "(3-5 July 2026) is the natural UK activation window; moving in the next 6-10 weeks "
        "aligns the market-entry moment with a home-market race weekend."
    ),
    "why_team_label": "WHY VISA CASH APP RACING BULLS",
    "why_team_para": (
        "Racing Bulls already carries Visa as its title sponsor, and Ramp's deepened "
        "multi-year Visa issuing agreement makes co-presence structural rather than "
        "conflicting: Ramp becomes the spend-management intelligence layer above the Visa "
        "payment rail, reinforcing both brands. Cash App's younger demographic mirrors "
        "Ramp's founder, developer and CFO-suite audience. The British GP at Silverstone "
        "gives the UK launch a home-market stage."
    ),
    "value_section": True,
    "value_section_label": "VALUE TO VISA CASH APP RACING BULLS",
    "value_mode": "B",
    "value_content": (
        "MODE B - real operational value, off-car. Ramp's payments rail and back-office "
        "stack map onto Racing Bulls' commercial machine: paddock supplier settlements, "
        "sponsor-activation treasury flows, and a partner-onboarding funnel of "
        "venture-backed, CFO-led companies. In return the team offers garage hospitality, "
        "pit-wall broadcast cuts, and founder-audience content timed to the British GP."
    ),
    "deal_arch_para": (
        "Entry at Official Spend Management Partner tier. "
        + BOLD.format("FOUR YEARS")
        + ", to span the EU/UK build-out cycle and capture full FIA calendar rotations "
        "through Silverstone, Las Vegas and Austin. Estimated $6-9M/yr. Scope: garage and "
        "cockpit logo rights, Visa co-activation rights, hospitality at the British GP and "
        "Las Vegas, and digital content rights for Ramp's CFO-audience channels."
    ),
    "decision_maker_name": "Eric Glyman",
    "decision_maker_role": "CEO & Co-Founder, Ramp",
    "decision_maker_bio": (
        "Glyman co-founded Ramp after co-founding Paribus (acquired by Capital One). The "
        "just-closed $750M raise and the deepened Visa partnership are direct outputs of "
        "his office, so a sponsorship of this scale is his call."
    ),
    "opening_angle_intro": "Lead with the $44B round and the UK/EU launch:",
    "opening_angle_quote": (
        "&ldquo;Eric, the $44B round and your UK/EU launch this summer line up exactly with "
        "Racing Bulls - Ramp as the spend layer above the Visa rail - and the British GP is "
        "a ready-made home-market activation. 25 minutes before a rival notices the open "
        "lane?&rdquo;"
    ),
    "score_cells": [
        ["TIMING", "19", "/ 20", "$750M closed Jun 2026; UK/EU launch this summer."],
        ["CAPACITY", "20", "/ 20", "$44B valuation, $1B+ ARR, FCF positive."],
        ["BRAND FIT", "19", "/ 20", "Visa co-presence structural; CFO audience matches."],
        ["URGENCY", "14", "/ 20", "Silverstone Jul 2026 home-market window."],
        ["OPS FIT", "12", "/ 20", "MODE B: back-office and treasury."],
    ],
    "risks": [
        [
            "VISA CHANNEL CONFLICT",
            "Ramp's Visa issuing deal could be read as a conflict with the Visa title.",
            "Frame Ramp as the spend-intelligence layer above the existing Visa relationship.",
        ],
        [
            "OFF-CAR RELEVANCE (MODE B)",
            "Spend management serves the back office, not the car.",
            "Lead with the Visa co-presence and a CFO/founder-audience hospitality play.",
        ],
    ],
    "bottom_line": "",
    "signals": ["funding event", "new leadership", "category whitespace"],
    "footer_company": "RAMP",
    "footer_date": "14 JUN 2026",
}


def make_brief(**overrides) -> WrittenBrief:
    return WrittenBrief.model_validate({**BASELINE, **overrides})


def fired(brief: WrittenBrief) -> set[int]:
    return audit_brief(brief, RUN_DATE).rules_fired()


def codes(brief: WrittenBrief) -> set[str]:
    return {v.code for v in audit_brief(brief, RUN_DATE).violations}


# ------------------------------------------------------------------ rule table


def test_rules_table_is_the_thirteen_roadmap_rules_in_order():
    assert [r[0] for r in RULES] == list(range(1, 14))
    assert [r[2] for r in RULES] == ["high"] * 12 + ["medium"]
    assert RULES[12][1] == "phrase_overlap"


# ------------------------------------------------------------------ baseline


def test_baseline_passes_all_thirteen_rules():
    result = audit_brief(make_brief(), RUN_DATE)
    assert result.violations == [], violations_feedback(result)
    assert result.passed is True
    assert result.route == "pass"
    assert result.warnings == []


def test_baseline_honours_every_word_ceiling_with_headroom():
    b = make_brief()
    assert word_count(b.deck) <= 50
    assert word_count(b.the_case_p1) <= 95
    assert word_count(b.the_case_p2) <= 75
    assert word_count(b.why_now_text) <= 55
    assert word_count(b.why_team_para) <= 85
    assert word_count(b.value_content) <= 70
    assert word_count(b.deal_arch_para) <= 70
    assert word_count(b.decision_maker_bio) <= 50
    assert word_count(b.opening_angle_intro) <= 18
    assert word_count(b.opening_angle_quote) <= 45
    assert all(word_count(f"{r.detail} {r.counter}") <= 32 for r in b.risks)
    assert all(word_count(c.note) <= 8 for c in b.score_cells)
    assert page2_chars(b) <= 2500


# ------------------------------------------------------------------ rule 1


@pytest.mark.parametrize(
    "duration",
    ["THREE YEARS", "FOUR YEARS", "FIVE YEARS", "three-year", "3-year", "4 years", "36 months"],
)
def test_rule1_accepts_three_years_or_more(duration):
    b = make_brief(deal_arch_para=f"Entry tier. {BOLD.format(duration)} at $6-9M/yr.")
    assert 1 not in fired(b)


@pytest.mark.parametrize("duration", ["TWO YEARS", "two-year", "2-year", "24 months", "one year"])
def test_rule1_fails_below_three_years(duration):
    b = make_brief(deal_arch_para=f"Entry tier. {BOLD.format(duration)} at $6-9M/yr.")
    assert "deal_duration" in codes(b)


def test_rule1_fails_when_no_duration_named():
    b = make_brief(
        deal_arch_para="Entry at Official Spend Management Partner tier. Estimated $6-9M/yr."
    )
    assert "deal_duration" in codes(b)
    assert 1 in fired(b)


# ------------------------------------------------------------------ rule 2


def test_rule2_passes_when_quote_has_25_minutes_and_ends_with_question():
    assert 2 not in fired(make_brief())


def test_rule2_fails_without_25_minutes():
    b = make_brief(
        opening_angle_quote=(
            "&ldquo;Eric, the $44B round and your UK/EU launch this summer line up exactly "
            "with Racing Bulls - before a rival notices the open lane?&rdquo;"
        )
    )
    assert "opening_quote" in codes(b)


def test_rule2_fails_when_quote_does_not_end_with_question_mark():
    b = make_brief(
        opening_angle_quote=(
            "&ldquo;Eric, the $44B round and your UK/EU launch this summer line up exactly "
            "with Racing Bulls. 25 minutes before a rival notices the open lane.&rdquo;"
        )
    )
    assert 2 in fired(b)


def test_rule2_strips_markup_and_trailing_quote_marks_before_checking_ending():
    for closing in ['"', "”", "’", "'", "&rdquo;", "</font>”"]:
        opening = "<font name='Poppins-Bold' size='9.5'>" if closing.startswith("</font>") else ""
        b = make_brief(
            opening_angle_quote=f"{opening}Eric, 25 minutes before a rival notices?{closing}"
        )
        assert 2 not in fired(b), closing


# ------------------------------------------------------------------ rule 3


def test_rule3_passes_for_declarative_intro():
    assert 3 not in fired(make_brief())


def test_rule3_fails_when_intro_contains_a_question_mark():
    b = make_brief(opening_angle_intro="Lead with the $44B round and the UK/EU launch?")
    assert "opening_intro_declarative" in codes(b)


# ------------------------------------------------------------------ rule 4


def test_expected_footer_date_has_no_leading_zero_and_is_uppercase():
    assert expected_footer_date(date(2026, 5, 21)) == "21 MAY 2026"
    assert expected_footer_date(date(2026, 6, 4)) == "4 JUN 2026"


def test_rule4_passes_when_footer_date_is_the_run_date():
    assert 4 not in fired(make_brief())


@pytest.mark.parametrize(
    "bad", ["2026-06-14", "04 JUN 2026", "4 JUN 2026", "14 June 2026", "14 JUN 2025"]
)
def test_rule4_fails_when_footer_date_differs_from_run_date(bad):
    assert "footer_date" in codes(make_brief(footer_date=bad))


# ------------------------------------------------------------------ rule 5


def test_rule5_passes_for_date_free_industry_meta():
    assert 5 not in fired(make_brief())


@pytest.mark.parametrize(
    "suffix",
    [
        " · 2026-06-14",
        " 2026-06-14",
        " · 14 Jun 2026",
        " · 14 JUN 2026",
        " · June 2026",
        " · Jun 2026",
    ],
)
def test_rule5_fails_for_trailing_date(suffix):
    b = make_brief(industry_meta=BASELINE["industry_meta"] + suffix)
    assert "industry_meta_no_date" in codes(b)


# ------------------------------------------------------------------ rule 6


def test_team_name_variants():
    assert team_name_variants("Visa Cash App Racing Bulls") == [
        "Visa Cash App Racing Bulls",
        "Visa",
        "Bulls",
    ]
    assert team_name_variants("Aston Martin") == ["Aston Martin", "Aston", "Martin"]
    assert "Bulls" in team_name_variants("Racing Bulls")
    assert team_name_variants("Haas") == ["Haas"]  # no 4-letter word other than the label itself


def test_rule6_passes_for_company_side_deck_and_landscape_p2():
    assert 6 not in fired(make_brief())


def test_rule6_fails_on_original_ramp_headline_as_deck():
    result = audit_brief(make_brief(deck=RAMP_ORIGINAL_HEADLINE), RUN_DATE)
    hits = [v for v in result.violations if v.code == "team_vacancy_proximity"]
    assert hits and hits[0].rule == 6 and hits[0].field == "deck"


def test_rule6_fails_when_p2_puts_team_next_to_vacancy_clause():
    # The original Ramp THE CASE sentence: "is open at Visa Cash App Racing Bulls".
    b = make_brief(
        the_case_p2=(
            "The slot that fits Ramp's profile - its deepened, multi-year Visa issuing "
            "relationship and its EU/UK expansion arc - is open at Visa Cash App Racing Bulls."
        )
    )
    hits = [v for v in audit_brief(b, RUN_DATE).violations if v.code == "team_vacancy_proximity"]
    assert hits and hits[0].field == "the_case_p2"


def test_rule6_short_team_alias_near_vacancy_clause_is_caught():
    deck = "Racing Bulls has no spend-management brand anywhere near the car."
    assert find_vacancy_proximity(deck, "Visa Cash App Racing Bulls") is not None


def test_rule6_vacancy_clause_far_from_team_name_is_allowed():
    text = (
        "The category is uncontested. "
        + ("Ramp begins onboarding UK and European businesses. " * 3)
        + "Racing Bulls is the destination."
    )
    assert text.index("Racing Bulls") - text.index("uncontested") > 100
    assert find_vacancy_proximity(text, "Visa Cash App Racing Bulls") is None


# ------------------------------------------------------------------ rule 7


def test_rule7_passes_at_baseline():
    assert 7 not in fired(make_brief())


def test_rule7_fails_when_deck_exceeds_50_words():
    b = make_brief(deck=BASELINE["deck"] + " " + strip_markup(BASELINE["the_case_p1"]))
    assert word_count(b.deck) > 50
    hits = [v for v in audit_brief(b, RUN_DATE).violations if v.code == "word_counts"]
    assert hits and hits[0].field == "deck" and hits[0].rule == 7


def test_rule7_why_now_prefix_is_not_counted():
    # 55 real words after the prefix is still within the ceiling.
    words = (strip_markup(BASELINE["the_case_p1"]) + " " + strip_markup(BASELINE["deck"])).split()[
        :55
    ]
    b = make_brief(
        why_now_callout="<font name='Poppins-Bold' size='9'>WHY NOW</font>&nbsp;&nbsp;"
        + " ".join(words)
    )
    assert word_count(b.why_now_text) == 55
    assert 7 not in fired(b)
    b2 = make_brief(
        why_now_callout="<font name='Poppins-Bold' size='9'>WHY NOW</font>&nbsp;&nbsp;"
        + " ".join(words + ["today."])
    )
    assert 7 in fired(b2)


def test_rule7_reports_every_field_that_exceeds():
    long_note = "MODE B: back-office and treasury - Ramp serves the team's spend operation."
    b = make_brief(
        score_cells=[[c[0], c[1], c[2], long_note] for c in BASELINE["score_cells"]],
        risks=[[r[0], r[1] + " " + r[2], r[2] + " " + r[1]] for r in BASELINE["risks"]],
    )
    hits = [v for v in audit_brief(b, RUN_DATE).violations if v.code == "word_counts"]
    assert len(hits) == 7  # 5 score-cell notes + 2 risks
    assert {v.field for v in hits} >= {"risks[1]", "risks[2]"}


def test_rule7_value_content_not_counted_when_section_off():
    b = make_brief(
        score=68,
        value_section=False,
        value_content=strip_markup(BASELINE["the_case_p1"]) + " " + BASELINE["value_content"],
        risks=BASELINE["risks"] + [["THIRD RISK", "", "Counter."]],
    )
    assert word_count(b.value_content) > 70
    assert 7 not in fired(b)


# ------------------------------------------------------------------ rule 8


def test_rule8_passes_for_high_confidence():
    assert 8 not in fired(make_brief(confidence_level="MEDIUM"))


@pytest.mark.parametrize("level", ["LOW", "low", "Low"])
def test_rule8_fails_for_low_confidence(level):
    assert "confidence_not_low" in codes(make_brief(confidence_level=level))


# ------------------------------------------------------------------ rule 9


@pytest.mark.parametrize("label", ["", " · ALUMNI INTELLIGENCE"])
def test_rule9_passes_for_the_two_exact_labels(label):
    assert 9 not in fired(make_brief(track_label=label))


@pytest.mark.parametrize(
    "label", ["TRACK 1", "TRACK 2", "ALUMNI INTELLIGENCE", "· ALUMNI INTELLIGENCE", " "]
)
def test_rule9_fails_for_anything_else(label):
    assert "track_label" in codes(make_brief(track_label=label))


# ------------------------------------------------------------------ rule 10


def test_rule10_passes_with_two_risks_and_value_section():
    assert 10 not in fired(make_brief())


def test_rule10_passes_with_three_risks_and_no_value_section():
    b = make_brief(
        score=68, value_section=False, risks=BASELINE["risks"] + [["THIRD RISK", "", "Counter."]]
    )
    assert 10 not in fired(b)


def test_rule10_fails_with_three_risks_when_value_section_true():
    b = make_brief(risks=BASELINE["risks"] + [["THIRD RISK", "", "Counter."]])
    assert "risk_count" in codes(b)


def test_rule10_fails_with_two_risks_when_value_section_false():
    b = make_brief(score=68, value_section=False)
    assert "risk_count" in codes(b)


# ------------------------------------------------------------------ rule 11


def test_rule11_passes_at_baseline():
    assert page2_chars(make_brief()) <= 2500
    assert 11 not in fired(make_brief())


def test_rule11_fails_when_page2_exceeds_2500_chars_with_value_section():
    filler = strip_markup(BASELINE["the_case_p1"])
    b = make_brief(
        value_content=BASELINE["value_content"] + " " + filler + " " + filler + " " + filler
    )
    assert page2_chars(b) > 2500
    assert "page2_char_budget" in codes(b)


def test_rule11_budget_is_2300_without_value_section():
    filler = strip_markup(BASELINE["the_case_p1"])
    three = BASELINE["risks"] + [["THIRD RISK", "", "Counter."]]
    b = make_brief(score=68, value_section=False, risks=three)
    base = page2_chars(b)
    assert base <= 2300
    b2 = make_brief(
        score=68,
        value_section=False,
        risks=three,
        decision_maker_bio=BASELINE["decision_maker_bio"] + " " + filler,
    )
    assert 2300 < page2_chars(b2) <= 2500  # would pass with the value section's budget
    assert "page2_char_budget" in codes(b2)


# ------------------------------------------------------------------ rule 12


def test_rule12_passes_when_value_section_rendered_at_score_84():
    assert 12 not in fired(make_brief())


def test_rule12_passes_below_70_without_value_section():
    b = make_brief(
        score=69,
        value_section=False,
        value_content="",
        value_section_label="",
        risks=BASELINE["risks"] + [["THIRD RISK", "", "Counter."]],
    )
    assert 12 not in fired(b)


def test_rule12_fails_when_value_section_false_at_score_70_plus():
    b = make_brief(
        score=70, value_section=False, risks=BASELINE["risks"] + [["THIRD RISK", "", "Counter."]]
    )
    assert "value_section_required" in codes(b)


def test_rule12_fails_when_value_content_empty():
    assert "value_section_required" in codes(make_brief(value_content=""))


def test_rule12_fails_when_value_section_label_empty():
    assert "value_section_required" in codes(make_brief(value_section_label=""))


# ------------------------------------------------------------------ rule 13


def test_rule13_passes_at_baseline():
    assert shared_phrases(BASELINE["the_case_p2"], BASELINE["why_team_para"]) == []
    assert 13 not in fired(make_brief())


def test_rule13_flags_five_word_overlap_as_medium_warning_not_a_retry():
    # Primer-style soft duplication: a THE CASE p2 sentence re-used in WHY [TEAM].
    b = make_brief(
        why_team_para=BASELINE["why_team_para"]
        + " Ramp's EU/UK expansion arc and its Visa issuing relationship land the profile here."
    )
    result = audit_brief(b, RUN_DATE)
    hits = [v for v in result.violations if v.code == "phrase_overlap"]
    assert hits and hits[0].rule == 13 and hits[0].severity == "medium"
    assert "expansion arc and its visa issuing relationship" in hits[0].message
    assert result.passed is True
    assert result.route == "pass"
    assert result.warnings == hits


def test_rule13_ignores_stopword_only_runs():
    assert shared_phrases("and of the in the on a", "so and of the in the on a") == []
    assert shared_phrases(
        "the visa issuing relationship and the", "the visa issuing relationship and the"
    ) == ["the visa issuing relationship and the"]


def test_rule13_is_case_and_punctuation_insensitive():
    assert shared_phrases(
        "Visa issuing relationship, EU/UK expansion!", "visa ISSUING relationship EU UK expansion"
    ) == ["visa issuing relationship eu uk expansion"]


# ------------------------------------------------------------------ routing + feedback


def test_route_is_retry_on_any_high_violation():
    result = audit_brief(make_brief(confidence_level="LOW"), RUN_DATE)
    assert result.passed is False
    assert result.route == "retry"


def test_violations_feedback_lists_every_violation_with_rule_number():
    b = make_brief(
        confidence_level="LOW",
        track_label="TRACK 1",
        footer_date="2026-06-14",
        opening_angle_intro="Why not lead with the $44B round?",
    )
    result = audit_brief(b, RUN_DATE)
    text = violations_feedback(result)
    lines = text.splitlines()
    assert len(lines) == len(result.violations) >= 4
    for i, v in enumerate(result.violations, 1):
        assert lines[i - 1].startswith(f"{i}. Rule {v.rule} ({v.code}")
        assert v.message in lines[i - 1]
    assert {v.rule for v in result.violations} == {3, 4, 8, 9}


def test_violations_feedback_for_clean_result():
    assert violations_feedback(AuditResult()) == "No audit violations."
    assert AuditResult([Violation(13, "phrase_overlap", "medium", "x")]).route == "pass"
