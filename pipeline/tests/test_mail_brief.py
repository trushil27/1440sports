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


def test_link_is_a_real_page_address():
    # ".../#/brief/127" reads as an in-page anchor in an email; each brief is now its own
    # static page, so the link is a plain address.
    assert (
        mail_brief.brief_url("https://trushil27.github.io/1440sports/", 127)
        == "https://trushil27.github.io/1440sports/127"
    )
    assert mail_brief.brief_url("https://1440sports-intel.github.io", 9) == (
        "https://1440sports-intel.github.io/9"
    )
    # no "#", and no double slash from a base that already ends in one
    assert "#" not in mail_brief.brief_url("https://x.test///", 1)
    assert mail_brief.brief_url("https://x.test///", 1) == "https://x.test/1"


def test_plain_text_body_is_sectioned_not_one_block():
    body = mail_brief.executive_take(_brief(), _settings())
    for heading in ("THE CALL", "AT A GLANCE", "THE SIGNAL", "THE ASK"):
        assert heading in body, heading
    assert "Fluidstack — 76/100 · HOT" in body
    assert "Gary Wu" in body
    assert "https://trushil27.github.io/1440sports/127" in body
    # the verdict comes before the detail, so a phone reader gets the call first
    assert body.index("THE CALL") < body.index("THE SIGNAL")


def test_html_card_carries_the_facts_and_one_button():
    html = mail_brief.brief_html(_brief(), _settings())
    assert html.count('<a href="https://trushil27.github.io/1440sports/127"') == 1
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
