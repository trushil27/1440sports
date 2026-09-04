"""Build brief §9.10: every one of the 13 audit rules has a passing and a failing fixture.

The audit is a port of the production n8n ``Audit Brief`` node (v2.1.8d) and these tests
pin the JS semantics — codes, severities, the curly-quote endings, the vacancy patterns
A/B/C/D/E per field, the +5-word grace, the 2300/2100 budgets, the 5-gram overlap, the
pass / retry / manual_review route and the audit-log rows.

The baseline is a ``WrittenBrief`` built ONLY from the real Ramp brief in this repo
(briefs/2026-06-14/ramp.md — N° 017, Visa Cash App Racing Bulls, Eric Glyman, FOUR
YEARS, run date 14 Jun 2026), with sentences trimmed to the word ceilings. Every failing
fixture is the baseline with one field re-worded from that same text. No company, figure,
person or race outside that brief appears here (build brief §0 rule 4).
"""

from __future__ import annotations

from datetime import date

import pytest

from intel.audit import (
    CODES,
    PAGE2_BUDGET_WITH_VALUE,
    PAGE2_BUDGET_WITHOUT_VALUE,
    RULES,
    WORD_CEILING_GRACE,
    AuditResult,
    Violation,
    audit_brief,
    expected_footer_date,
    js_word_count,
    page2_chars,
    plain_text,
    quote_without_ask,
    shared_phrases,
    team_pattern,
    team_vacancy_distance,
    team_vacancy_within,
    violations_feedback,
)
from intel.brief_data import WrittenBrief, strip_markup

RUN_DATE = date(2026, 6, 14)
BOLD = "<font name='Poppins-Bold' size='9.5'>{}</font>"
TEAM = "Visa Cash App Racing Bulls"

# The original Ramp headline_long — "the slot is open at Visa Cash App Racing Bulls". The JS
# vacancy list deliberately has no bare "slot is open" (the Datadog reference construction),
# so production lets this deck through: pinned below as documented behaviour.
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
    "team_label": TEAM,
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
THIRD_RISK = ["UK/EU TIMING", "", "Anchor the launch to the British GP window."]
FILLER = strip_markup(BASELINE["the_case_p1"])  # Ramp prose used to push counts over ceilings


def make_brief(**overrides) -> WrittenBrief:
    return WrittenBrief.model_validate({**BASELINE, **overrides})


def no_value(**overrides) -> WrittenBrief:
    """Baseline switched to the no-value-section shape (score < 70, three risks)."""
    base = dict(score=68, value_section=False, value_content="", value_section_label="")
    base["risks"] = BASELINE["risks"] + [THIRD_RISK]
    return make_brief(**{**base, **overrides})


def fired(brief: WrittenBrief) -> set[int]:
    return audit_brief(brief, RUN_DATE).rules_fired()


def codes(brief: WrittenBrief) -> set[str]:
    return audit_brief(brief, RUN_DATE).codes()


def only(brief: WrittenBrief, code: str) -> Violation:
    hits = [v for v in audit_brief(brief, RUN_DATE).violations if v.code == code]
    assert len(hits) == 1, hits
    return hits[0]


# ------------------------------------------------------------------ rule table


def test_rules_table_is_the_thirteen_production_rules_in_order():
    assert [r[0] for r in RULES] == list(range(1, 14))
    assert {n for n, _ in CODES.values()} == set(range(1, 14))
    assert all(sev in ("critical", "medium") for _, sev in CODES.values())
    # rules 4, 5, 7, 9 and 13 (and the rule-6 count claims) never block a send
    assert {c for c, (n, s) in CODES.items() if s == "medium"} == {
        "footer_date_mismatch",
        "industry_meta_date_suffix",
        "count_claim_in_case_p2",
        "count_claim_in_deck",
        "bad_track_label",
        "p2_why_team_phrase_overlap",
        *(
            f"wc_{k}"
            for k in (
                "deck",
                "the_case_p1",
                "the_case_p2",
                "why_now_callout",
                "why_team_para",
                "value_content",
                "operational_fit_content",
                "deal_arch_para",
                "decision_maker_bio",
                "opening_angle_intro",
                "opening_angle_quote",
            )
        ),
    }


# ------------------------------------------------------------------ text helpers


def test_js_word_count_strips_tags_only_and_keeps_entities_attached():
    assert (
        js_word_count("<font name='Poppins-Bold' size='9'>WHY NOW</font>&nbsp;&nbsp;The raise") == 4
    )
    assert js_word_count("&ldquo;Eric, 25 minutes?&rdquo;") == 3
    assert js_word_count("") == 0 and js_word_count(None) == 0


def test_plain_text_removes_tags_and_named_entities():
    assert plain_text("<font size='9'>WHY NOW</font>&nbsp;&nbsp;The  raise") == "WHY NOW The raise"
    assert plain_text("&ldquo;Eric&rdquo;") == "Eric"


# ------------------------------------------------------------------ baseline


def test_baseline_passes_all_thirteen_rules():
    result = audit_brief(make_brief(), RUN_DATE)
    assert result.violations == [], violations_feedback(result)
    assert result.passed is True and result.route == "pass" and result.warnings == []


def test_baseline_honours_every_ceiling_with_the_js_counter():
    b = make_brief()
    assert js_word_count(b.deck) <= 50
    assert js_word_count(b.the_case_p1) <= 95
    assert js_word_count(b.the_case_p2) <= 75
    # The JS counts the "WHY NOW" prefix too (55-word body + 2); production's +5 grace absorbs it.
    assert js_word_count(b.why_now_callout) == 57 <= 55 + WORD_CEILING_GRACE
    assert js_word_count(b.why_team_para) <= 85
    assert js_word_count(b.value_content) <= 75
    assert js_word_count(b.deal_arch_para) <= 70
    assert js_word_count(b.decision_maker_bio) <= 50
    assert js_word_count(b.opening_angle_intro) <= 18
    assert js_word_count(b.opening_angle_quote) <= 45
    assert page2_chars(b) <= PAGE2_BUDGET_WITH_VALUE


# ------------------------------------------------------------------ rule 1


@pytest.mark.parametrize("duration", ["THREE YEARS", "FOUR YEARS", "FIVE YEARS", "three years"])
def test_rule1_accepts_a_bold_three_four_or_five_years_marker(duration):
    b = make_brief(deal_arch_para=f"Entry tier. {BOLD.format(duration)} at $6-9M/yr.")
    assert 1 not in fired(b)


def test_rule1_two_years_fires_both_codes():
    b = make_brief(deal_arch_para=f"Entry tier. {BOLD.format('TWO YEARS')} at $6-9M/yr.")
    assert {"min_3_year_deal", "missing_duration_marker"} <= codes(b)
    assert only(b, "min_3_year_deal").severity == "critical"


@pytest.mark.parametrize(
    "para",
    [
        "Entry tier. THREE YEARS at $6-9M/yr.",  # right words, no <font> marker
        f"Entry tier. {BOLD.format('3-year')} at $6-9M/yr.",  # digits are not a marker
        f"Entry tier. {BOLD.format('SIX YEARS')} at $6-9M/yr.",  # only THREE/FOUR/FIVE count
        "Entry at Official Spend Management Partner tier. Estimated $6-9M/yr.",
    ],
)
def test_rule1_requires_the_bold_marker_itself(para):
    b = make_brief(deal_arch_para=para)
    assert codes(b) & {"min_3_year_deal", "missing_duration_marker"} == {"missing_duration_marker"}


# ------------------------------------------------------------------ rule 2


def test_rule2_passes_at_baseline():
    assert 2 not in fired(make_brief())


@pytest.mark.parametrize("closing", ["&rdquo;", '"', "”", "“", ""])
def test_rule2_accepts_the_production_quote_endings(closing):
    b = make_brief(opening_angle_quote=f"Eric, 25 minutes before a rival notices?{closing}")
    assert 2 not in fired(b), closing


@pytest.mark.parametrize("closing", ["’", "'", "</font>”", "."])
def test_rule2_rejects_other_endings(closing):
    opening = "<font name='Poppins-Bold' size='9.5'>" if closing.startswith("</font>") else ""
    b = make_brief(
        opening_angle_quote=f"{opening}Eric, 25 minutes before a rival notices?{closing}"
    )
    assert "opening_quote_ending" in codes(b), closing


def test_rule2_fails_without_25_minutes():
    b = make_brief(
        opening_angle_quote=(
            "&ldquo;Eric, the $44B round and your UK/EU launch this summer line up exactly "
            "with Racing Bulls - before a rival notices the open lane?&rdquo;"
        )
    )
    assert only(b, "opening_quote_ending").severity == "critical"


def test_rule2_flags_25_minutes_used_as_a_metaphor():
    b = make_brief(
        opening_angle_quote=(
            "&ldquo;Eric, the fastest 25 minutes of your UK/EU launch: the $44B round and "
            "Racing Bulls line up. Can we book 25 minutes?&rdquo;"
        )
    )
    assert codes(b) & {"opening_quote_ending", "opening_quote_metaphor"} == {
        "opening_quote_metaphor"
    }


def test_rule2_metaphor_check_ignores_the_closing_ask_itself():
    quote = (
        "&ldquo;Eric, before a rival notices the open lane, can we find the whole "
        "25 minutes?&rdquo;"
    )
    assert (
        quote_without_ask(quote)
        == "&ldquo;Eric, before a rival notices the open lane, can we find the whole "
    )
    assert 2 not in fired(make_brief(opening_angle_quote=quote))


# ------------------------------------------------------------------ rule 3


def test_rule3_passes_for_declarative_intro():
    assert 3 not in fired(make_brief())


def test_rule3_fails_when_intro_ends_with_a_question_mark():
    b = make_brief(opening_angle_intro="Lead with the $44B round and the UK/EU launch?")
    assert only(b, "opening_intro_question").severity == "critical"


def test_rule3_only_the_ending_counts():
    # JS `/\?\s*$/` — a question mark mid-intro is not caught by production.
    b = make_brief(opening_angle_intro="The $44B round? Lead with it and the UK/EU launch.")
    assert 3 not in fired(b)


# ------------------------------------------------------------------ rule 4


def test_expected_footer_date_has_no_leading_zero_and_is_uppercase():
    assert expected_footer_date(date(2026, 5, 21)) == "21 MAY 2026"
    assert expected_footer_date(date(2026, 6, 4)) == "4 JUN 2026"


@pytest.mark.parametrize("ok", ["14 JUN 2026", "14 jun 2026", " 14 Jun 2026 "])
def test_rule4_passes_when_footer_date_is_the_run_date_case_insensitive(ok):
    assert 4 not in fired(make_brief(footer_date=ok))


@pytest.mark.parametrize(
    "bad", ["2026-06-14", "04 JUN 2026", "4 JUN 2026", "14 June 2026", "14 JUN 2025"]
)
def test_rule4_fails_when_footer_date_differs_from_run_date(bad):
    v = only(make_brief(footer_date=bad), "footer_date_mismatch")
    assert v.rule == 4 and v.severity == "medium"


# ------------------------------------------------------------------ rule 5


def test_rule5_passes_for_date_free_industry_meta():
    assert 5 not in fired(make_brief())


@pytest.mark.parametrize("suffix", [" · 2026-06-14", " - 2026-06-14", " 2026-06-14"])
def test_rule5_fails_for_trailing_iso_date(suffix):
    v = only(
        make_brief(industry_meta=BASELINE["industry_meta"] + suffix), "industry_meta_date_suffix"
    )
    assert v.rule == 5 and v.severity == "medium"


@pytest.mark.parametrize("suffix", [" · 14 Jun 2026", " · June 2026"])
def test_rule5_only_catches_iso_dates(suffix):
    # JS `/[·\-\s]\s*\d{4}-\d{2}-\d{2}\s*$/` — prose dates pass through production.
    assert 5 not in fired(make_brief(industry_meta=BASELINE["industry_meta"] + suffix))


# ------------------------------------------------------------------ rule 6


def test_team_pattern_is_upper_capitalised_and_raw():
    assert team_pattern("Visa Cash App Racing Bulls") == (
        "(VISA\\ CASH\\ APP\\ RACING\\ BULLS"
        "|Visa\\ Cash\\ App\\ Racing\\ Bulls"
        "|Visa\\ Cash\\ App\\ Racing\\ Bulls)"
    )
    assert team_pattern(" AUDI ") == "(AUDI|Audi|AUDI)"


def test_rule6_passes_for_company_side_deck_and_landscape_p2():
    assert 6 not in fired(make_brief())


def test_rule6_the_slot_is_open_construction_is_allowed_by_production():
    # No bare "is open" / "slot is open" in the JS vacancy list (Datadog reference preserved).
    assert not team_vacancy_within(RAMP_ORIGINAL_HEADLINE, TEAM)
    assert 6 not in fired(make_brief(deck=RAMP_ORIGINAL_HEADLINE))


def test_rule6_pattern_e_team_has_no_in_deck_and_p2():
    text = f"{TEAM} has no spend-management partner; Ramp closed a $750M round in June 2026."
    deck = only(make_brief(deck=text), "team_vacancy_in_deck_e")
    assert deck.rule == 6 and deck.severity == "critical" and deck.field == "deck"
    assert "team_has_no_in_case_p2" in codes(make_brief(the_case_p2=text))
    # "has no spend" is also a vacancy clause 0 chars from the team → pattern B fires too
    assert "team_vacancy_in_deck_b" in codes(make_brief(deck=text))


def test_rule6_pattern_a_team_is_the_only_or_where():
    for phrase in ("is the only", "is where", "is one of the only", "is the destination where"):
        text = f"{TEAM} {phrase} Ramp's spend layer sits above the Visa rail."
        assert "team_vacancy_in_deck_a" in codes(make_brief(deck=text)), phrase
        assert "why_team_claim_in_case_p2_a" in codes(make_brief(the_case_p2=text)), phrase


def test_rule6_pattern_b_uses_min_start_distance_across_all_team_mentions():
    near = f"The corporate-spend category is vacant, and {TEAM} carries Visa as its title sponsor."
    assert (
        team_vacancy_distance(near, TEAM) is not None and team_vacancy_distance(near, TEAM) <= 100
    )
    assert "why_team_claim_in_case_p2_b" in codes(make_brief(the_case_p2=near))
    assert "team_vacancy_in_deck_b" in codes(make_brief(deck=near))
    # first mention far away, second mention near the clause: v2.1.8d matchAll catches it
    two = (
        f"{TEAM} carries Visa as its title sponsor. "
        + "Ramp begins onboarding UK and European businesses this summer. " * 3
        + f"The corporate-spend category is vacant at {TEAM}."
    )
    assert "team_vacancy_in_deck_b" in codes(make_brief(deck=two))


def test_rule6_vacancy_clause_far_from_every_team_mention_is_allowed():
    text = (
        "The corporate-spend category is vacant. "
        + "Ramp begins onboarding UK and European businesses this summer. " * 3
        + f"{TEAM} carries Visa as its title sponsor."
    )
    assert team_vacancy_distance(text, TEAM) > 100
    assert 6 not in fired(make_brief(deck=text, the_case_p2=text))


def test_rule6_pattern_c_only_n_team_framing():
    text = f"The only F1 team without a spend-management brand on the car is {TEAM}."
    assert only(make_brief(deck=text), "team_vacancy_in_deck_c").severity == "critical"
    assert "why_team_claim_in_case_p2_c" in codes(make_brief(the_case_p2=text))


def test_rule6_pattern_d_counted_teams_claim_is_medium():
    text = "Two F1 teams carry no spend-management partner; Ramp's category sits unoccupied."
    v = only(make_brief(deck=text), "count_claim_in_deck")
    assert v.rule == 6 and v.severity == "medium"
    assert only(make_brief(the_case_p2=text), "count_claim_in_case_p2").severity == "medium"
    assert audit_brief(make_brief(deck=text), RUN_DATE).route == "pass"


@pytest.mark.parametrize(
    "phrase",
    [
        "still seeking a spend partner",
        "yet to sign a spend partner",
        "currently lacks a spend partner",
        "remains without a spend partner",
        "the spend category is unclaimed",
        "has no current spend-management partner",
    ],
)
def test_rule6_v218d_vacancy_phrasings(phrase):
    assert team_vacancy_within(f"{TEAM} {phrase}.", TEAM), phrase


def test_rule6_is_skipped_without_a_team_label():
    text = f"{TEAM} has no spend-management partner."
    assert 6 not in fired(make_brief(team_label="", deck=text, the_case_p2=text))


# ------------------------------------------------------------------ rule 7


def test_rule7_passes_at_baseline():
    assert 7 not in fired(make_brief())


def test_rule7_fires_only_beyond_the_five_word_grace():
    words = FILLER.split()
    assert 7 not in fired(make_brief(deck=" ".join(words[:55])))
    v = only(make_brief(deck=" ".join(words[:56])), "wc_deck")
    assert v.rule == 7 and v.severity == "medium" and v.field == "deck"
    assert "deck: 56 words > 50" == v.message


def test_rule7_why_now_prefix_counts_as_two_words():
    prefix = "<font name='Poppins-Bold' size='9'>WHY NOW</font>&nbsp;&nbsp;"
    body = (FILLER + " " + strip_markup(BASELINE["deck"])).split()
    assert 7 not in fired(make_brief(why_now_callout=prefix + " ".join(body[:58])))
    assert "wc_why_now_callout" in codes(make_brief(why_now_callout=prefix + " ".join(body[:59])))


def test_rule7_empty_fields_are_skipped():
    assert 7 not in fired(make_brief(opening_angle_intro=""))


def test_rule7_does_not_count_risks_or_score_cell_notes():
    long_note = "MODE B: back-office and treasury - Ramp serves the team's spend operation."
    b = make_brief(
        score_cells=[[c[0], c[1], c[2], long_note] for c in BASELINE["score_cells"]],
        risks=[[r[0], r[1] + " " + r[2], r[2] + " " + r[1]] for r in BASELINE["risks"]],
    )
    assert 7 not in fired(b)


def test_rule7_value_content_is_audited_even_when_the_section_is_off():
    b = no_value(value_content=FILLER + " " + BASELINE["value_content"])
    assert js_word_count(b.value_content) > 80
    assert "wc_value_content" in codes(b)


# ------------------------------------------------------------------ rule 8


def test_rule8_passes_for_high_confidence():
    assert 8 not in fired(make_brief(confidence_level="MEDIUM"))


@pytest.mark.parametrize("level", ["LOW", "low", "Low"])
def test_rule8_fails_for_low_confidence(level):
    assert only(make_brief(confidence_level=level), "low_confidence").severity == "critical"


# ------------------------------------------------------------------ rule 9


@pytest.mark.parametrize("label", ["", " · ALUMNI INTELLIGENCE"])
def test_rule9_passes_for_the_two_exact_labels(label):
    assert 9 not in fired(make_brief(track_label=label))


@pytest.mark.parametrize(
    "label", ["TRACK 1", "TRACK 2", "ALUMNI INTELLIGENCE", "· ALUMNI INTELLIGENCE", " "]
)
def test_rule9_fails_for_anything_else_as_medium(label):
    v = only(make_brief(track_label=label), "bad_track_label")
    assert v.rule == 9 and v.severity == "medium"


# ------------------------------------------------------------------ rule 10


def test_rule10_passes_with_two_risks_and_value_section():
    assert 10 not in fired(make_brief())


def test_rule10_passes_with_three_risks_and_no_value_section():
    assert 10 not in fired(no_value())


def test_rule10_three_risks_with_value_section_is_critical():
    v = only(make_brief(risks=BASELINE["risks"] + [THIRD_RISK]), "risk_count")
    assert v.rule == 10 and v.severity == "critical" and v.message == "risks=3, expected 2"


def test_rule10_two_risks_without_value_section_is_only_medium():
    b = no_value(risks=BASELINE["risks"])
    v = only(b, "risk_count")
    assert v.severity == "medium" and v.message == "risks=2, expected 3"
    assert audit_brief(b, RUN_DATE).route == "pass"


# ------------------------------------------------------------------ rule 11


def test_rule11_passes_at_baseline():
    assert page2_chars(make_brief()) <= 2300
    assert 11 not in fired(make_brief())


def test_rule11_fails_beyond_2300_chars_with_value_section():
    b = make_brief(value_content=" ".join([BASELINE["value_content"], FILLER, FILLER, FILLER]))
    assert page2_chars(b) > 2300
    v = only(b, "page2_overflow_risk")
    assert v.rule == 11 and v.severity == "critical" and "> 2300" in v.message


def test_rule11_budget_is_2100_without_value_section():
    b = no_value()
    assert page2_chars(b) <= PAGE2_BUDGET_WITHOUT_VALUE
    b2 = no_value(decision_maker_bio=BASELINE["decision_maker_bio"] + " " + FILLER)
    assert 2100 < page2_chars(b2) <= 2300  # would pass with the value section's budget
    assert "> 2100" in only(b2, "page2_overflow_risk").message


def test_rule11_counts_value_content_even_when_section_off_and_all_three_risk_parts():
    b = no_value()
    with_text = no_value(value_content=FILLER)
    assert page2_chars(with_text) - page2_chars(b) == len(FILLER)
    risk = [
        "VISA CHANNEL CONFLICT",
        "Ramp's Visa issuing deal could be read as a conflict.",
        "Frame Ramp above the Visa rail.",
    ]
    b3 = make_brief(risks=[risk, BASELINE["risks"][1]])
    b4 = make_brief(risks=[[risk[0], risk[1], ""], BASELINE["risks"][1]])
    assert page2_chars(b3) - page2_chars(b4) == len(" " + risk[2])


# ------------------------------------------------------------------ rule 12


def test_rule12_passes_when_value_section_rendered_at_score_84():
    assert 12 not in fired(make_brief())


def test_rule12_passes_below_70_without_value_section():
    assert 12 not in fired(no_value(score=69))


def test_rule12_fails_when_value_section_false_at_score_70_plus():
    v = only(no_value(score=70), "value_section_missing")
    assert v.rule == 12 and v.severity == "critical"


def test_rule12_fails_when_value_section_on_but_content_empty_at_any_score():
    assert only(make_brief(value_content=""), "value_content_empty").severity == "critical"
    assert "value_content_empty" in codes(
        make_brief(score=60, value_content="<font size='9'></font>")
    )


def test_rule12_does_not_check_the_section_label():
    # production audits value_section + value_content only; the label is the writer's job
    assert 12 not in fired(make_brief(value_section_label=""))


# ------------------------------------------------------------------ rule 13


def test_rule13_passes_at_baseline():
    assert shared_phrases(BASELINE["the_case_p2"], BASELINE["why_team_para"], TEAM) == []
    assert 13 not in fired(make_brief())


def test_rule13_flags_five_gram_overlap_as_one_medium_warning():
    # Primer-style soft duplication: a THE CASE p2 clause re-used in WHY [TEAM].
    b = make_brief(
        why_team_para=BASELINE["why_team_para"]
        + " Ramp's EU/UK expansion arc and its Visa issuing relationship land the profile here."
    )
    result = audit_brief(b, RUN_DATE)
    hits = [v for v in result.violations if v.code == "p2_why_team_phrase_overlap"]
    assert len(hits) == 1 and hits[0].rule == 13 and hits[0].severity == "medium"
    assert hits[0].message.startswith('5+ word phrase shared: "ramp s eu uk expansion" (+')
    assert result.passed is True and result.route == "pass" and result.warnings == hits


def test_rule13_needs_three_content_tokens_per_five_gram():
    assert shared_phrases("and of the in the on a", "so and of the in the on a") == []
    assert shared_phrases(
        "the visa issuing relationship and the", "the visa issuing relationship and the"
    ) == [
        "the visa issuing relationship and",
        "visa issuing relationship and the",
    ]


def test_rule13_skips_phrases_carrying_two_or_more_team_words():
    phrase = "the profile at Visa Cash App Racing Bulls"
    assert shared_phrases(phrase, phrase, TEAM) == []
    assert shared_phrases(phrase, phrase, "") != []


def test_rule13_is_case_and_punctuation_insensitive_and_splits_on_apostrophes():
    assert shared_phrases(
        "Visa issuing relationship, EU/UK expansion!", "visa ISSUING relationship EU UK expansion"
    ) == [
        "visa issuing relationship eu uk",
        "issuing relationship eu uk expansion",
    ]
    assert shared_phrases("Ramp's Visa issuing agreement", "ramp s visa issuing agreement") == [
        "ramp s visa issuing agreement"
    ]


# ------------------------------------------------------------------ routing, log rows, feedback


def test_route_is_retry_on_first_critical_failure_then_manual_review():
    low = make_brief(confidence_level="LOW")
    first = audit_brief(low, RUN_DATE)
    assert first.passed is False and first.route == "retry" and first.retry_count == 0
    second = audit_brief(low, RUN_DATE, retry_count=1, previous_violations=first.violations)
    assert second.route == "manual_review" and second.previous_violations == first.violations
    # previous violations never change the decision on their own
    assert (
        audit_brief(
            make_brief(), RUN_DATE, retry_count=1, previous_violations=first.violations
        ).route
        == "pass"
    )


def test_medium_only_results_pass_and_log_as_no_violations():
    b = make_brief(track_label="TRACK 1")
    result = audit_brief(b, RUN_DATE)
    assert result.route == "pass" and result.warnings and result.passed
    rows = result.log_rows(b, RUN_DATE)
    assert rows[0] == {
        "run_date": "2026-06-14",
        "brief_number": "017",
        "company": "Ramp",
        "row_type": "summary",
        "rule": "audit_passed",
        "severity": "info",
        "detail": "No violations.",
    }
    assert rows[1]["row_type"] == "violation" and rows[1]["rule"] == "bad_track_label"


def test_log_rows_summary_for_retry_and_manual_review():
    b = make_brief(confidence_level="LOW", track_label="TRACK 1")
    retry = audit_brief(b, RUN_DATE).log_rows(b, RUN_DATE)
    assert retry[0]["rule"] == "audit_failed_retrying" and retry[0]["severity"] == "critical"
    assert retry[0]["detail"] == "1 critical, 1 medium (retry=0)"
    assert [r["rule"] for r in retry[1:]] == ["low_confidence", "bad_track_label"]
    manual = audit_brief(b, RUN_DATE, retry_count=1).log_rows(b, RUN_DATE)
    assert manual[0]["rule"] == "audit_failed_manual_review" and manual[0]["detail"].endswith(
        "(retry=1)"
    )
    blank = make_brief(brief_number="", company="")
    assert audit_brief(blank, RUN_DATE).log_rows(blank, RUN_DATE)[0]["brief_number"] == "???"
    assert audit_brief(blank, RUN_DATE).log_rows(blank, RUN_DATE)[0]["company"] == "RAMP"


def test_as_json_mirrors_the_js_audit_object():
    j = audit_brief(make_brief(confidence_level="LOW"), RUN_DATE).as_json()
    assert j["passed"] is False and j["critical_count"] == 1 and j["medium_count"] == 0
    assert j["violations"] == [
        {"rule": "low_confidence", "severity": "critical", "detail": "confidence_level is LOW"}
    ]
    assert j["retry_count"] == 0 and "run_at" in j


def test_violations_feedback_is_the_retry_prep_line_format():
    b = make_brief(
        confidence_level="LOW",
        track_label="TRACK 1",
        footer_date="2026-06-14",
        opening_angle_intro="Why not lead with the $44B round?",
    )
    result = audit_brief(b, RUN_DATE)
    assert {v.rule for v in result.violations} == {3, 4, 8, 9}
    assert violations_feedback(result).splitlines() == [
        f"- [{v.severity.upper()}] {v.code}: {v.message}" for v in result.violations
    ]
    assert violations_feedback(AuditResult()) == ""
    assert AuditResult([Violation(13, "p2_why_team_phrase_overlap", "medium", "x")]).route == "pass"
