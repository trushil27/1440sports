"""Desk v3: one row per company, deal updates from the sponsor table, the rebuild queue."""

from __future__ import annotations

import datetime as dt
import json

import httpx

from intel import rebuild_queue, site_export
from intel.config import Settings
from intel.models import Series, Sponsor, SponsorLevel, SponsorStatus


def _entry(**kw):
    base = {
        "key": f"{kw.get('date', '2026-07-08')}|{kw.get('company', 'x').lower()}",
        "review": {"status": "keep"},
        "company": "SambaNova Systems",
        "date": "2026-07-08",
        "historical": True,
        "score": 87,
        "team": None,
        "bottom_line": None,
        "page_html": None,
    }
    base.update(kw)
    return base


def test_same_company_folds_into_the_richest_row():
    thin = _entry(date="2026-07-08", score=87)
    rich = _entry(
        date="2026-07-16",
        key="2026-07-16|sambanova systems",
        historical=False,
        score=77,
        team="Haas",
        bottom_line="…",
    )
    other = _entry(company="Antora Energy", key="2026-07-30|antora energy", date="2026-07-30")
    entries = [thin, rich, other]
    site_export.merge_same_company(entries)
    assert rich["review"]["status"] == "keep" and rich["also_surfaced"] == ["2026-07-08"]
    assert thin["review"] == {"status": "merged", "of": rich["key"]}
    assert other["review"]["status"] == "keep" and "also_surfaced" not in other


def test_deal_update_marks_companies_that_have_since_signed():
    sp = Sponsor(
        series=Series.F1,
        level=SponsorLevel.team_major,
        team="Audi F1 Team",
        brand="NinjaOne",
        brand_norm="ninjaone",
        status=SponsorStatus.joined,
        season="2026",
        notes=None,
        source="spec",
    )
    entries = [
        _entry(company="NinjaOne", key="2026-06-10|ninjaone"),
        _entry(company="Antora Energy", key="2026-07-30|antora energy"),
    ]
    site_export.attach_deal_updates(entries, [sp])
    assert entries[0]["deal_update"]["team"] == "Audi F1 Team"
    assert entries[0]["deal_update"]["status"] == "joined"
    assert "deal_update" not in entries[1]


def test_rebuild_queue_reads_netlify_and_github_and_remembers_what_ran(tmp_path):
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        url = str(request.url)
        if url.endswith("/sites/site1/forms"):
            return httpx.Response(200, json=[{"id": "f1", "name": "rebuild"}])
        if url.endswith("/forms/f1/submissions"):
            return httpx.Response(
                200,
                json=[{"id": "s1", "data": {"company": "Antora Energy", "date": "2026-07-30"}}],
            )
        if "api.github.com" in url:
            return httpx.Response(
                200,
                json=[
                    {"number": 7, "title": "Rebuild: Fervo Energy (2026-05-13)"},
                    {"number": 8, "title": "Unrelated issue"},
                ],
            )
        return httpx.Response(404)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    settings = Settings(
        netlify_auth_token="t", netlify_site_id="site1", pdf_storage_dir=str(tmp_path)
    )
    ran = []

    class Out:
        status, brief_id = "success", 42

    def runner(company, date, s):
        ran.append((company, date))
        return Out()

    first = rebuild_queue.process(settings, http=http, runner=runner)
    assert [(r["company"], r["date"]) for r in first] == [
        ("Antora Energy", "2026-07-30"),
        ("Fervo Energy", "2026-05-13"),
    ]
    assert ran[1] == ("Fervo Energy", dt.date(2026, 5, 13))
    done = json.loads((tmp_path / "rebuild_done.json").read_text())
    assert set(done) == {"s1", "gh-7"}
    second = rebuild_queue.process(settings, http=http, runner=runner)
    assert second == [] and len(ran) == 2  # nothing runs twice


def test_queue_without_any_source_is_silent(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    settings = Settings(pdf_storage_dir=str(tmp_path))
    assert rebuild_queue.process(settings, http=http, runner=lambda *a: None) == []
