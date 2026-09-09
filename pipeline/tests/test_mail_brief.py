"""The signal email: a scannable card, and a link that actually opens the brief."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from intel import mail_brief

RECORD = (
    Path(__file__).resolve().parents[1] / "intel" / "cases" / "2026-09-06" / "fluidstack.run.json"
)


def _brief():
    data = json.loads(RECORD.read_text(encoding="utf-8"))["brief"]
    return SimpleNamespace(brief_number=data["number"], brief_data=data["brief_data"])


def _settings(base="https://trushil27.github.io/1440sports/"):
    return SimpleNamespace(app_base_url=base)


def test_link_is_the_company_page_with_no_number_in_it():
    # Three shapes so far: "…//brief/127" opened the front page, "…/#/brief/127" reads as an
    # in-page anchor, "…/127" ends in a number the operator will not forward (7 Sep 2026).
    assert (
        mail_brief.brief_url("https://1440-intelligence.netlify.app/", 127, "Fluidstack")
        == "https://1440-intelligence.netlify.app/fluidstack"
    )
    assert mail_brief.page_slug("Ore Energy") == "ore-energy"
    assert mail_brief.page_slug("1Komma5° GmbH") == "1komma5-gmbh"
    assert "#" not in mail_brief.brief_url("https://x.test///", 1, "Acme")
    # no usable name: the desk's front page, never a bare number
    assert mail_brief.brief_url("https://x.test/", 9, None) == "https://x.test"


def test_plain_text_body_is_sectioned_not_one_block():
    body = mail_brief.executive_take(_brief(), _settings())
    for heading in ("THE CALL", "AT A GLANCE", "THE SIGNAL", "THE ASK"):
        assert heading in body, heading
    assert "Fluidstack — 76/100 · HOT" in body
    assert "Gary Wu" in body
    assert "https://trushil27.github.io/1440sports/fluidstack" in body
    # the verdict comes before the detail, so a phone reader gets the call first
    assert body.index("THE CALL") < body.index("THE SIGNAL")


def test_html_card_carries_the_facts_and_one_button():
    html = mail_brief.brief_html(_brief(), _settings())
    assert html.count('<a href="https://trushil27.github.io/1440sports/fluidstack"') == 1
    for bit in (
        "Fluidstack",
        "76/100",
        "HOT",
        "At a glance",
        "Atlassian Williams Racing",
        "The ask",
    ):
        assert bit in html, bit
    assert "<style" not in html  # inline styles only; clients strip style blocks
    # brief text is escaped, so a stray tag in the copy can never break the card
    assert "<b class=" not in html and "<font" not in html


def test_missing_fields_are_left_out_rather_than_faked():
    brief = SimpleNamespace(brief_number=1, brief_data={"company": "Acme", "score": 71})
    text = mail_brief.executive_take(brief, _settings())
    html = mail_brief.brief_html(brief, _settings())
    assert "Acme — 71/100" in text
    assert "Decision-maker" not in text and "Decision-maker" not in html
    assert "?" not in text.split("Read the full case")[0].replace("N°", "")


def test_the_default_link_target_is_an_address_that_exists():
    """A caller that forgets APP_BASE_URL must still produce a reachable link. The old default
    was intel.1440sports.com, a domain nobody owns, and it went out in a real email."""
    from intel.config import Settings

    base = Settings().app_base_url
    assert base == "https://1440-intelligence.netlify.app"
    assert "1440sports.com" not in base


def test_the_format_guard_passes_the_real_card_and_catches_a_broken_one():
    """Operator, 9 Sep 2026: "we need an audit guard around that to make sure the format is
    not lost". The guard checks the pieces of the approved card, in order, and refuses
    placeholders, template leaks, mode markers and numeric links."""
    brief = _brief()
    settings = _settings("https://1440-intelligence.netlify.app")
    html = mail_brief.brief_html(brief, settings)
    text = mail_brief.executive_take(brief, settings)
    assert mail_brief.audit_card(html, text, settings) == []
    # the review variant is the same card plus the panel, and still passes
    review = mail_brief.brief_html(brief, settings, review=True)
    assert "Open points before circulation" in review
    assert mail_brief.audit_card(review, text, settings) == []

    broken = html.replace("At a glance", "").replace("Read the full case", "Read more")
    problems = mail_brief.audit_card(broken, text, settings)
    assert any("At a glance" in p for p in problems) and any(
        "Read the full case" in p for p in problems
    )
    assert "card is missing" in problems[0]
    assert mail_brief.audit_card("", text, settings)[0] == "no HTML card at all"
    leaked = html.replace("Fluidstack", "${company}")
    assert any("${" in p for p in mail_brief.audit_card(leaked, text, settings))
    numeric = html.replace("/fluidstack", "/127")
    assert any("ends in a number" in p for p in mail_brief.audit_card(numeric, text, settings))
    assert any(
        "Shadow mode" in p for p in mail_brief.audit_card(html, text + "\nShadow mode: x", settings)
    )


def test_placeholders_never_print_as_people_and_labels_read_as_names():
    """N° 245 (9 Sep 2026) showed "Not named in source — Executive Leadership (title
    undisclosed)" as the decision-maker, "AUDI" as the team and "83/100HOT" as the score."""
    brief = _brief()
    d = dict(brief.brief_data)
    d.update(
        {
            "decision_maker_name": "Not named in source",
            "decision_maker_role": "Executive Leadership (title undisclosed)",
            "team_label": "AUDI",
            "series_label": "F1",
            "score": 83,
            "timing_label": "HOT",
        }
    )
    brief.brief_data = d
    settings = _settings("https://1440-intelligence.netlify.app")
    html = mail_brief.brief_html(brief, settings)
    text = mail_brief.executive_take(brief, settings)
    assert "Not named in source" not in html and "Decision-maker" not in html  # omitted, not faked
    assert "Audi Revolut F1 Team" in html and ">AUDI<" not in html
    assert "83/100HOT" not in html.replace("&nbsp;", " ") and "83/100 · HOT" in text
    assert mail_brief.audit_card(html, text, settings) == []
    # and the guard would have caught the old output
    old = html.replace("Audi Revolut F1 Team", "AUDI") + "<td>Not named in source</td>"
    problems = mail_brief.audit_card(old, text.replace("83/100 · HOT", "83/100HOT"), settings)
    assert any("Not named in source" in p for p in problems)
    assert any("run together" in p for p in problems)
    assert mail_brief.team_display("Jaguar", "FE") == "Jaguar TCS Racing"
    assert mail_brief.team_display("Nobody Racing", "F1") == "Nobody Racing"


def test_an_old_placeholder_claim_in_the_ledger_reads_as_the_true_state():
    from types import SimpleNamespace

    from intel.models import VerificationResult

    v = SimpleNamespace(status=VerificationResult.unverified, notes="no source", checked_at=1, id=1)
    claim = SimpleNamespace(
        load_bearing=True, verifications=[v], text="Not named in source, CEO (unnamed) at Etched"
    )
    brief = SimpleNamespace(claims=[claim], audit_violations=[], audit_status=None)
    points = mail_brief.review_points(brief)
    assert points == [
        (
            "open",
            "Decision-maker not yet named",
            "Confirm the sponsorship owner on the company's own leadership page.",
        )
    ]
    assert "Not named" not in "".join(mail_brief.review_lines(brief))
