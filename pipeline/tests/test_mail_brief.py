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
