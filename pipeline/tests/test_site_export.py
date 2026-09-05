"""The static app export: data.json + inlined index.html; sponsor since/until parsing;
series inference for historical rows; Netlify zip deploy (mocked)."""

from __future__ import annotations

import json

import httpx

from intel import netlify, site_export
from intel.brief_data import Extended
from intel.config import Settings
from intel.seed import load_seeds
from tests.fixtures.ramp_brief import RAMP_WRITTEN
from tests.test_m3_verify import FakeVerifier
from tests.test_m4_pipeline import RUN_DATE, FakeWriter, _block, _ramp_signal
from tests.test_web_page import EXTENDED


def test_since_until_parsing_from_notes():
    assert site_export.since_until("Partner since 2018; strategy integration") == {
        "since": "2018",
        "until": None,
        "until_kind": None,
    }
    r = site_export.since_until("Joined 2022, deal through 2030. Agentforce fan companion.")
    assert (r["since"], r["until"], r["until_kind"]) == ("2022", "2030", "reported")
    r = site_export.since_until("Commitment publicly reported to at least 2030.")
    assert r["until"] == "2030" and r["until_kind"] == "reported"
    assert site_export.since_until(None) == {"since": None, "until": None, "until_kind": None}


def test_series_inference_only_when_nothing_is_recorded():
    assert site_export.infer_series({"series": "FE"}, {}) == ("FE", False)
    assert site_export.infer_series(
        {"series": None, "team": None, "industry": "EV charging network", "take": "…"}, {}
    ) == ("FE", True)
    assert site_export.infer_series(
        {"series": None, "team": "McLaren", "industry": "DevSecOps", "take": "…"}, {}
    ) == ("F1", True)
    assert site_export.infer_series({"series": None}, {}) == (None, False)


def test_export_writes_inlined_index_and_data_json(session, migrated_database, tmp_path):
    load_seeds(session)
    from intel import run_daily

    stages = run_daily.Stages(
        verifier=FakeVerifier(),
        writer=FakeWriter([_block(dict(RAMP_WRITTEN, extended=EXTENDED))]),
        font_stack="june",
    )
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        site_dir=str(tmp_path / "site"),
    )
    out = run_daily.run_day(RUN_DATE, settings, lambda _d: [_ramp_signal()], session, stages=stages)
    assert out.status == "success"
    session.flush()
    res = site_export.publish(settings, session=session)
    assert res["briefs"] == 1 and "netlify" not in res
    data = json.loads((tmp_path / "site" / "data.json").read_text(encoding="utf-8"))
    assert data["today"]["company"] == "Ramp" and data["today"]["series"] == "F1"
    assert data["today"]["page_html"].startswith("<!DOCTYPE html>")
    assert any(s["brand"] == "Aramco" and s["until"] == "End of 2028" for s in data["sponsors"])
    assert any(
        s["brand"] == "Salesforce" and s["until_kind"] == "confirmed" for s in data["sponsors"]
    )
    assert [c["name"] for c in data["calendar"] if c["series"] == "F1"][:2] == [
        "Australian GP",
        "Chinese GP",
    ]
    index = (tmp_path / "site" / "index.html").read_text(encoding="utf-8")
    assert "__DATA_JSON__" not in index and '"company": "Ramp"' in index
    assert "1440 Intelligence Desk" in index and "Sponsors · FE" in index
    assert Extended.model_validate(EXTENDED)  # the long-form block survived the round trip


def test_netlify_zip_deploy_posts_the_archive():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200, json={"id": "dep1", "state": "uploaded", "ssl_url": "https://intel.netlify.app"}
        )

    res = netlify.deploy(
        b"PK\x03\x04zip",
        "tok",
        "site123",
        http=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    assert res == {
        "id": "dep1",
        "state": "uploaded",
        "url": "https://intel.netlify.app",
        "deploy_url": None,
    }
    req = calls[0]
    assert str(req.url) == "https://api.netlify.com/api/v1/sites/site123/deploys"
    assert req.headers["authorization"] == "Bearer tok"
    assert req.headers["content-type"] == "application/zip"
    assert req.content.startswith(b"PK")
