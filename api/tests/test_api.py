"""API: auth (§8), today/history/search, brief detail + verification panel, actions → cooling
list, People + role drift (§9.11), outreach safety (§9.12), operator-only ops."""

from __future__ import annotations

import datetime as dt

from conftest import MD, OP, login  # the api/tests conftest (pipeline's is 'tests.conftest')
from sqlalchemy import select

from intel import run_daily
from intel.config import Settings
from intel.models import (
    Blocklist,
    BlocklistStatus,
    Brief,
    Contact,
    VerificationMethod,
    VerificationResult,
)
from intel.seed import load_seeds
from tests.fixtures import production_signals as ps
from tests.fixtures.ramp_brief import RAMP_WRITTEN
from tests.test_m3_verify import FakeVerifier
from tests.test_m4_pipeline import FakeWriter, _block, _ramp_signal

RUN_DATE = dt.date(2026, 6, 14)


def _issue_ramp(session, migrated_database, tmp_path, verifier=None) -> Brief:
    load_seeds(session)
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "b"),
    )
    stages = run_daily.Stages(
        verifier=verifier or FakeVerifier(),
        writer=FakeWriter([_block(RAMP_WRITTEN)]),
        font_stack="june",
        distribute=False,
    )
    out = run_daily.run_day(RUN_DATE, settings, lambda _d: [_ramp_signal()], session, stages=stages)
    assert out.status == "success", out.summary
    session.commit()  # the API uses its own sessions
    return session.get(Brief, out.brief_id)


# --- auth ------------------------------------------------------------------------------------


def test_unknown_address_is_a_silent_no_op_and_no_session(api):
    r = api.post("/auth/magic-link", json={"email": "stranger@example.test"})
    assert r.status_code == 204 and api.mailer.sent == []
    assert api.get("/api/today").status_code == 401


def test_magic_link_enrols_and_opens_a_session(api):
    login(api, MD)
    me = api.get("/auth/me").json()
    assert me["email"] == MD and me["role"] == "md" and me["passkeys"] == 0
    assert "Your 1440 Intelligence sign-in link" == api.mailer.sent[0].subject


def test_expired_or_forged_magic_link_is_rejected(api):
    assert api.get("/auth/magic-link/verify", params={"token": "nope"}).status_code == 400


def test_passkey_options_are_scoped_to_the_relying_party(api):
    login(api, MD)
    r = api.post("/auth/passkey/register/options")
    assert r.status_code == 200
    opts = r.json()
    assert opts["rp"]["id"] == "localhost" and opts["user"]["name"] == MD
    assert opts["authenticatorSelection"]["userVerification"] == "required"
    assert "intel_wa_challenge" in r.cookies
    # login options work without a session and without an email (discoverable credential)
    anon = api.__class__(api.app, base_url="http://testserver")
    r2 = anon.post("/auth/passkey/login/options", json={})
    assert r2.status_code == 200 and r2.json()["allowCredentials"] == []
    assert r2.json()["rpId"] == "localhost"


def test_logout_clears_the_session(api):
    login(api, MD)
    assert api.post("/auth/logout").status_code == 204
    assert api.get("/auth/me").status_code == 401


# --- briefs ----------------------------------------------------------------------------------


def test_today_and_detail_carry_the_verification_panel(api, session, migrated_database, tmp_path):
    brief = _issue_ramp(session, migrated_database, tmp_path)
    login(api, MD)
    today = api.get("/api/today").json()
    card = today["brief"]
    assert card["company"] == "Ramp" and card["badge"] == "Verified" and card["score"] == 84
    assert card["team"] == "Visa Cash App Racing Bulls" and card["person"] == "Eric Glyman"
    assert today["highlights"] and all(h["claim_ids"] for h in today["highlights"])
    detail = api.get(f"/api/briefs/{brief.brief_number}").json()
    panel = detail["verification_panel"]
    assert panel["summary"].endswith("load-bearing claims verified")
    assert panel["load_bearing_verified"] == panel["load_bearing_total"] > 0
    assert all(c["status"] == "verified" for c in panel["claims"] if c["load_bearing"])
    assert detail["audit_result"]["status"] == "pass"
    assert detail["score_composition"]["cells"][0]["label"] == "TIMING"
    assert detail["pdf_url"].endswith("/pdf")
    pdf = api.get(detail["pdf_url"])
    assert pdf.status_code == 200 and pdf.headers["content-type"] == "application/pdf"


def test_history_search_and_filters(api, session, migrated_database, tmp_path):
    _issue_ramp(session, migrated_database, tmp_path)
    login(api, OP)
    assert [c["company"] for c in api.get("/api/briefs").json()["items"]] == ["Ramp"]
    assert api.get("/api/briefs", params={"q": "glyman"}).json()["items"][0]["company"] == "Ramp"
    assert api.get("/api/briefs", params={"q": "racing bulls"}).json()["items"]
    assert api.get("/api/briefs", params={"q": "nomatch-zzz"}).json()["items"] == []
    assert api.get("/api/briefs", params={"series": "FE"}).json()["items"] == []
    assert api.get("/api/briefs", params={"status": "verified"}).json()["items"]
    assert api.get("/api/briefs", params={"from": "2026-07-01"}).json()["items"] == []


def test_actions_are_logged_and_snooze_kill_write_the_cooling_list(
    api, session, migrated_database, tmp_path
):
    brief = _issue_ramp(session, migrated_database, tmp_path)
    login(api, MD)
    n = brief.brief_number
    r = api.post(
        f"/api/briefs/{n}/actions", json={"action": "snoozed", "note": "revisit after Silverstone"}
    )
    assert r.status_code == 200 and r.json()["actions"][0]["action"] == "snoozed"
    session.expire_all()
    row = session.scalar(select(Blocklist).where(Blocklist.company_norm == "ramp"))
    assert (
        row.status == BlocklistStatus.cooling
        and row.cooling_until == (dt.datetime.now(dt.UTC) + dt.timedelta(days=30)).date()
    )
    api.post(f"/api/briefs/{n}/actions", json={"action": "killed"})
    session.expire_all()
    row = session.scalar(select(Blocklist).where(Blocklist.company_norm == "ramp"))
    assert row.status == BlocklistStatus.closed_lost and row.cooling_until is None
    api.post(f"/api/briefs/{n}/actions", json={"action": "pursuing"})
    session.expire_all()
    assert (
        session.scalar(select(Blocklist).where(Blocklist.company_norm == "ramp")).status
        == BlocklistStatus.active
    )
    assert api.post(f"/api/briefs/{n}/actions", json={"action": "dance"}).status_code == 400
    assert [a["action"] for a in api.get(f"/api/briefs/{n}").json()["actions"]] == [
        "snoozed",
        "killed",
        "pursuing",
    ]


# --- people + outreach ----------------------------------------------------------------------------


def test_people_card_and_role_drift_disable_outreach(api, session, migrated_database, tmp_path):
    """§9.11 — a contact whose title no longer matches the source is contradicted → no outreach."""
    brief = _issue_ramp(session, migrated_database, tmp_path)
    n = brief.brief_number
    login(api, OP)
    card = api.get(f"/api/briefs/{n}/people").json()
    assert card["name"] == "Eric Glyman" and card["role"]["status"] == "verified"
    assert card["role"]["verified_on"] and card["outreach_enabled"] is True
    assert card["contact"] is None  # no provider approved → nothing fetched, nothing guessed
    assert api.post(f"/api/briefs/{n}/people/lookup").status_code == 409

    # the role check now fails (the fetched source disagrees with the stored title)
    session.add(
        Contact(person_name="Eric Glyman", title="CEO & Co-Founder, Ramp", company_norm="ramp")
    )
    session.commit()
    api.app_state.session_factory.kw.get("bind")  # noqa: B018 (touch)
    drift = FakeVerifier({"Eric Glyman": "contradicted"})
    sm = api.app_state.session_factory

    class Patched:
        def __call__(self):
            s = sm()
            s._verifier_override = drift
            return s

    api.app_state.session_factory = Patched()
    card = api.post(f"/api/briefs/{n}/people/reverify").json()
    assert card["role"]["drifted"] is True and card["outreach_enabled"] is False
    assert "re-verify" in card["warning"].lower()
    assert api.post(f"/api/briefs/{n}/outreach").status_code == 409
    session.expire_all()
    contact = session.scalar(select(Contact).where(Contact.person_name == "Eric Glyman"))
    assert contact.role_verification_id is not None


def test_outreach_draft_uses_verified_claims_only_and_never_sends(
    api, session, migrated_database, tmp_path
):
    """§9.12 — no figure in the draft is absent from the verified claims; Outlook draft ≠ send."""
    brief = _issue_ramp(session, migrated_database, tmp_path)
    n = brief.brief_number
    login(api, MD)
    r = api.post(f"/api/briefs/{n}/outreach")
    assert r.status_code == 201, r.text
    draft = r.json()
    assert "25 minutes" in draft["body"] and draft["claim_ids"]
    from intel import outreach as outreach_mod

    session.expire_all()
    b = session.get(Brief, brief.id)
    assert outreach_mod.check_draft(draft["body"], outreach_mod.verified_claims(b)) == []
    r = api.post(f"/api/outreach/{draft['id']}/outlook-draft")
    assert r.status_code == 200 and r.json()["outlook_draft_id"] == "draft-1"
    assert api.mailer.drafts and api.mailer.sent == [
        m for m in api.mailer.sent if "sign-in link" in m.subject
    ]
    assert api.post(f"/api/outreach/{draft['id']}/contacted").status_code == 200
    assert api.get(f"/api/briefs/{n}").json()["actions"][-1]["action"] == "contacted"


def test_a_draft_with_an_unverified_figure_is_rejected_by_the_safety_check():
    from intel import outreach as outreach_mod
    from intel.models import Claim, ClaimType, Verification

    c = Claim(
        text="Closed $750M primary round at $44B valuation",
        section="key_facts",
        claim_type=ClaimType.funding,
        load_bearing=True,
    )
    c.verifications = [
        Verification(
            status=VerificationResult.verified,
            method=VerificationMethod.manual,
            checked_at=dt.datetime.now(dt.UTC),
        )
    ]
    assert outreach_mod.check_draft("Your $750M round at $44B is the moment.", [c]) == []
    assert outreach_mod.check_draft("Your $750M round and 40% growth in 2024.", [c]) == [
        "2024",
        "40%",
    ]


# --- ops --------------------------------------------------------------------------------------


def test_ops_is_operator_only_and_explains_every_candidate(
    api, session, migrated_database, tmp_path
):
    load_seeds(session)
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "b"),
    )
    stages = run_daily.Stages(
        verifier=FakeVerifier(),
        writer=FakeWriter([_block(RAMP_WRITTEN)]),
        font_stack="june",
        distribute=False,
    )
    out = run_daily.run_day(
        RUN_DATE,
        settings,
        lambda _d: [_ramp_signal(), ps.with_breakdown(ps.STRAVA)],
        session,
        stages=stages,
    )
    session.commit()
    login(api, MD)
    assert api.get("/api/ops/runs").status_code == 403
    api.post("/auth/logout")
    login(api, OP)
    runs = api.get("/api/ops/runs").json()
    assert runs[0]["id"] == out.run_id and runs[0]["candidates"] == 2
    reasons = api.get(f"/api/ops/runs/{out.run_id}/candidates").json()
    assert {r["company"]: r["decision"] for r in reasons} == {"Ramp": "selected", "Strava": "stale"}
    assert any("days old" in r["reason"] for r in reasons)
    assert api.get("/api/ops/queue").json() == []
    bl = api.post(
        "/api/ops/blocklist",
        json={
            "company": "Lime",
            "status": "cooling",
            "cooling_until": "2026-12-01",
            "reason": "test",
        },
    )
    assert bl.status_code == 201 and bl.json()["company_norm"] == "lime"
    assert any(b["company_norm"] == "lime" for b in api.get("/api/ops/blocklist").json())
    sponsors = api.get("/api/ops/sponsors", params={"q": "splunk"}).json()
    assert sponsors and sponsors[0]["team"] == "McLaren F1 Team"
    cfg = api.get("/api/ops/config").json()
    assert cfg["md_threshold"] == 70 and cfg["anthropic_key_configured"] is False
    assert api.get("/api/ops/alumni").json()[0]["tier"] in ("strict", "medium")
