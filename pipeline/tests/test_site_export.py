"""The static app export: data.json + inlined index.html; sponsor since/until parsing;
series inference for historical rows; Netlify zip deploy (mocked)."""

from __future__ import annotations

import json

import httpx
import pytest

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


def _netlify_account(sites: dict[str, dict]) -> tuple[httpx.Client, list[httpx.Request]]:
    """A stand-in Netlify holding `sites` keyed by name, which POST /sites adds to."""
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        path = request.url.path
        if request.method == "GET" and path.startswith("/api/v1/sites/"):
            name = path.rsplit("/", 1)[-1].removesuffix(".netlify.app")
            site = sites.get(name)
            return httpx.Response(200, json=site) if site else httpx.Response(404, json={})
        if request.method == "POST" and path == "/api/v1/sites":
            name = json.loads(request.content)["name"]
            sites[name] = {"id": f"id-{name}", "name": name}
            return httpx.Response(201, json=sites[name])
        raise AssertionError(f"unexpected {request.method} {path}")

    return httpx.Client(transport=httpx.MockTransport(handler)), calls


def test_the_desk_claims_its_own_netlify_site_from_the_token_alone():
    """Setting the link up is ONE secret. Without this the operator has to create the site by
    hand, copy its id and paste it back as a second secret before any link changes."""
    http, calls = _netlify_account({})
    site = netlify.ensure_site("tok", "1440-intelligence", http=http)
    assert site["id"] == "id-1440-intelligence"
    assert [(c.method, c.url.path) for c in calls] == [
        ("GET", "/api/v1/sites/1440-intelligence.netlify.app"),
        ("POST", "/api/v1/sites"),
    ]


def test_the_site_is_claimed_once_and_reused_after_that():
    known = {"1440-intelligence": {"id": "abc", "name": "1440-intelligence"}}
    http, calls = _netlify_account(known)
    assert netlify.ensure_site("tok", "1440-intelligence", http=http)["id"] == "abc"
    assert [c.method for c in calls] == ["GET"]  # nothing created a second site


def test_a_name_somebody_else_owns_is_reported_not_silently_swapped():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(404, json={})
        return httpx.Response(422, json={"errors": {"subdomain": ["must be unique"]}})

    with pytest.raises(RuntimeError, match="1440-intelligence"):
        netlify.ensure_site(
            "tok", "1440-intelligence", http=httpx.Client(transport=httpx.MockTransport(handler))
        )


def test_an_explicit_site_id_still_wins_and_costs_no_api_call():
    settings = Settings(netlify_auth_token="tok", netlify_site_id="chosen")
    assert netlify.resolve_site_id(settings, http=None) == "chosen"


def test_a_company_checked_and_rejected_without_a_row_still_appears():
    """Ore Energy, 7 Sep 2026: the desk held a sourced screen-out (a €37.3m Series A cannot
    fund a three-year deal) and the app showed nothing at all, because a decision could only
    attach to an existing row. The judgment IS the product — it gets a row of its own."""
    entries = [{"company": "Fluidstack", "review": {"status": "keep"}}]
    review = {
        "2026-08-04|Ore Energy": {
            "status": "screened_out",
            "reason": "capacity: a €37.3m Series A cannot fund a three-year deal",
            "reason_code": "case_screen",
            "sources": ["https://example.com/ore"],
        },
        "2026-09-06|Fluidstack": {
            "status": "screened_out",
            "reason": "already on this row",
            "reason_code": "case_screen",
        },
        "2026-05-01|Someone Else": {"status": "keep"},
        # a blocklist entry is not a full check: no reasoning, no sources, wrong heading
        "2026-05-07|Cerebras": {"status": "screened_out", "reason_code": "blocklisted"},
    }
    rows = site_export.orphan_screen_rows(entries, review, names={"oreenergy": "Ore Energy"})
    assert [r["company"] for r in rows] == ["Ore Energy"]  # not Fluidstack: it has a row
    row = rows[0]
    assert row["date"] == "2026-08-04" and row["checked_only"] is True
    assert row["review"]["sources"] == ["https://example.com/ore"]
    assert row["number"] is None and row["has_page"] is False
