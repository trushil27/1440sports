"""The app page: long-form WHY NOW / WHY THIS TEAM / VALUE sections rendered next to the PDF."""

from __future__ import annotations

import json
from pathlib import Path

from intel import render, run_daily, verify
from intel.brief_data import Extended, WrittenBrief
from intel.config import Settings
from intel.models import Brief
from intel.seed import load_seeds
from tests.fixtures.ramp_brief import RAMP_WRITTEN, ramp_brief_data
from tests.test_m3_verify import FakeVerifier
from tests.test_m4_pipeline import RUN_DATE, FakeWriter, _block, _ramp_signal

EXTENDED = {
    "why_now": [
        {"label": "Trigger", "text": "The $750M round closed on 4 June 2026 at a $44B valuation."},
        {"label": "Window", "text": "The Las Vegas GP in November is the US stage for the launch."},
    ],
    "why_team": [
        {"label": "Open lane", "text": "No spend-management brand sits on the car."},
        {"label": "Audience", "text": "Cash App's founder audience mirrors Ramp's buyers."},
    ],
    "value": [
        {"label": "Operational workstream", "text": "Paddock supplier settlements on Ramp."},
        {"label": "What the team gives back", "text": "Garage hospitality at Silverstone."},
    ],
    "ruled_out": [{"team": "Audi", "reason": "Revolut holds the fintech lane."}],
    "ask": "A 25-minute call before the British GP to size the entry tier.",
}


def test_extended_block_is_optional_and_validated():
    plain = WrittenBrief.model_validate(RAMP_WRITTEN)
    assert plain.extended is None
    rich = WrittenBrief.model_validate(dict(RAMP_WRITTEN, extended=EXTENDED))
    assert isinstance(rich.extended, Extended)
    assert [p.label for p in rich.extended.why_team] == ["Open lane", "Audience"]
    assert len(rich.extended.texts) == 8


def test_extended_figures_and_races_join_the_ledger_as_non_load_bearing():
    rich = WrittenBrief.model_validate(dict(RAMP_WRITTEN, extended=EXTENDED))
    drafts = verify.claims_from_brief(rich)
    ext = [d for d in drafts if d.section == "extended"]
    assert ext and all(not d.load_bearing for d in ext)
    assert any("$750M" in d.text and d.claim_type.value == "funding" for d in ext)
    assert any(d.claim_type.value == "event" and "Las Vegas" in d.text for d in ext)


def test_web_page_renders_the_long_form_sections_self_contained(tmp_path):
    data = ramp_brief_data(extended=Extended.model_validate(EXTENDED))
    out = render.render_web(data, tmp_path / "ramp.web.html")
    html = out.read_text(encoding="utf-8")
    assert "<title>Ramp · Brief N° 017</title>" in html
    assert 'src="data:image/' in html  # logo inlined
    for needle in (
        "Why now",
        "the clock this signal is on",
        "Open lane",
        "Ruled out",
        "Revolut holds the fintech lane.",
        "Operational workstream",
        "The ask",
        "25-minute call",
        '<b class="hl">FOUR YEARS</b>',
        # The desk is the brand's light scheme on every device (operator decision,
        # 6 Sep 2026) — no dark palette, so a phone in dark mode still shows navy on white.
        "color-scheme: light",
    ):
        assert needle in html, needle
    assert "prefers-color-scheme: dark" not in html and 'data-theme="dark"' not in html
    # the short PDF paragraphs are the fallback only when the long form is absent
    assert "MODE B - real operational value" not in html
    plain = render.render_web_html(ramp_brief_data())
    assert "MODE B - real operational value" in plain


def test_run_day_stores_the_web_page_next_to_the_pdf(session, migrated_database, tmp_path):
    load_seeds(session)
    written = dict(RAMP_WRITTEN, extended=EXTENDED)
    stages = run_daily.Stages(
        verifier=FakeVerifier(), writer=FakeWriter([_block(written)]), font_stack="june"
    )
    settings = Settings(
        database_url=migrated_database, execution_mode="dry_run", pdf_storage_dir=str(tmp_path)
    )
    out = run_daily.run_day(RUN_DATE, settings, lambda _d: [_ramp_signal()], session, stages=stages)
    assert out.status == "success", json.dumps(out.summary, default=str)
    brief = session.get(Brief, out.brief_id)
    assert brief.web_html_path and Path(brief.web_html_path).name == "ramp.web.html"
    assert Path(brief.web_html_path).exists()
    assert brief.brief_data["extended"]["ask"].startswith("A 25-minute call")
