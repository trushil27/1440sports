"""§7 distribution rules, §9.9 no-signal day, never-send-twice, and the Graph mailer."""

from __future__ import annotations

import base64
import datetime as dt
import json

import httpx
import pytest
from sqlalchemy import select

from intel import run_daily, schedule, send
from intel.config import Settings
from intel.models import Send, SendChannel, SendStatus
from intel.seed import load_seeds
from tests.fixtures import production_signals as ps
from tests.fixtures.ramp_brief import RAMP_WRITTEN
from tests.test_m3_verify import FakeVerifier
from tests.test_m4_pipeline import FakeWriter, _block, _ramp_signal

RUN_DATE = dt.date(2026, 6, 14)
MD = "md@example.test"
OP = "operator@example.test"


class FakeMailer:
    channel = SendChannel.outlook

    def __init__(self, fail: bool = False) -> None:
        self.sent: list[send.Outgoing] = []
        self.fail = fail

    def send(self, msg: send.Outgoing) -> str:
        if self.fail:
            raise httpx.HTTPError("graph down")
        self.sent.append(msg)
        return f"<msg-{len(self.sent)}@example.test>"


def _settings(url, tmp, mode="production", **kw) -> Settings:
    return Settings(
        database_url=url,
        execution_mode=mode,
        pdf_storage_dir=str(tmp / "briefs"),
        outbox_dir=str(tmp / "outbox"),
        operator_email=OP,
        md_email=MD,
        **kw,
    )


def _stages(mailer, verifier=None, writer_outputs=None):
    return run_daily.Stages(
        verifier=verifier or FakeVerifier(),
        writer=FakeWriter(writer_outputs or [_block(RAMP_WRITTEN)]),
        font_stack="june",
        mailer=mailer,
    )


def _sends(session):
    return [(s.recipient, s.kind.value, s.status.value) for s in session.scalars(select(Send))]


def test_md_receives_only_a_verified_audited_brief_in_production(
    session, migrated_database, tmp_path
):
    load_seeds(session)
    mailer = FakeMailer()
    out = run_daily.run_day(
        RUN_DATE,
        _settings(migrated_database, tmp_path),
        lambda _d: [_ramp_signal()],
        session,
        stages=_stages(mailer),
    )
    assert out.status == "success" and out.verification_status == "verified"
    assert len(mailer.sent) == 1
    msg = mailer.sent[0]
    assert msg.to == [MD] and msg.cc == [OP]
    assert msg.subject.startswith("1440 Intelligence Brief N° ") and msg.subject.endswith(
        "— Ramp — 84/100"
    )
    # sectioned body (THE CALL / AT A GLANCE / …) and a short link: <base>/<number>, no "#"
    assert "THE CALL" in msg.body_text and "AT A GLANCE" in msg.body_text
    link = msg.body_text.split("Read the full case:")[1].split()[0]
    assert "#" not in link and link.rstrip("/").split("/")[-1].isdigit()
    assert msg.attachments and msg.attachments[0].name.endswith(".pdf")
    assert sorted(_sends(session)) == [(MD, "md_brief", "sent"), (OP, "operator_copy", "sent")]
    rows = session.scalars(select(Send)).all()
    assert all(r.message_id == "<msg-1@example.test>" for r in rows)


def test_shadow_mode_sends_the_md_copy_to_the_operator_only(session, migrated_database, tmp_path):
    load_seeds(session)
    mailer = FakeMailer()
    run_daily.run_day(
        RUN_DATE,
        _settings(migrated_database, tmp_path, mode="shadow"),
        lambda _d: [_ramp_signal()],
        session,
        stages=_stages(mailer),
    )
    assert [m.to for m in mailer.sent] == [[OP]]
    # The subject carries no mode tag (operator decision, 6 Sep 2026) — the MD reads it.
    assert mailer.sent[0].subject.startswith("1440 Intelligence Brief")
    assert "SHADOW" not in mailer.sent[0].subject
    # …but a shadow copy is still unmistakable in the body.
    assert "Shadow mode: operator copy" in mailer.sent[0].body_text
    assert _sends(session) == [(OP, "operator_copy", "sent")]


def test_needs_review_goes_to_the_operator_with_verify_before_circulation(
    session, migrated_database, tmp_path
):
    load_seeds(session)
    mailer = FakeMailer()
    unverified = FakeVerifier(default="unverified")
    out = run_daily.run_day(
        RUN_DATE,
        _settings(migrated_database, tmp_path),
        lambda _d: [_ramp_signal()],
        session,
        stages=_stages(mailer, verifier=unverified),
    )
    assert out.verification_status == "needs_review"
    assert [m.to for m in mailer.sent] == [[OP]]
    assert (
        "[REVIEW]" in mailer.sent[0].subject
        and "VERIFY BEFORE CIRCULATION" in mailer.sent[0].subject
    )
    assert "The MD has NOT been emailed" in mailer.sent[0].body_text
    assert _sends(session) == [(OP, "needs_review", "sent")]


def test_no_signal_day_md_gets_nothing_operator_gets_the_note(session, migrated_database, tmp_path):
    """§9.9 — every candidate suppressed (stale)."""
    mailer = FakeMailer()
    out = run_daily.run_day(
        dt.date(2026, 5, 26),
        _settings(migrated_database, tmp_path),
        lambda _d: [ps.with_breakdown(ps.STRAVA), ps.with_breakdown(ps.ONEKOMMA5)],
        session,
        stages=_stages(mailer),
    )
    assert out.status == "no_signal"
    assert [m.to for m in mailer.sent] == [[OP]]
    assert "[NO SIGNAL]" in mailer.sent[0].subject
    assert "The MD has NOT been emailed" in mailer.sent[0].body_text
    assert _sends(session) == [(OP, "no_signal", "sent")]


def test_blocked_brief_gets_an_operator_notice_with_the_failing_claim(
    session, migrated_database, tmp_path
):
    load_seeds(session)
    mailer = FakeMailer()
    out = run_daily.run_day(
        dt.date(2026, 5, 28),
        _settings(migrated_database, tmp_path),
        lambda _d: [ps.with_breakdown(ps.RAMP_PHANTOM_RACE, series="F1")],
        session,
        stages=_stages(mailer),
    )
    assert out.status == "no_signal"
    subjects = [m.subject for m in mailer.sent]
    assert any(s.startswith("[BLOCKED]") for s in subjects) and any(
        s.startswith("[NO SIGNAL]") for s in subjects
    )
    blocked = next(m for m in mailer.sent if m.subject.startswith("[BLOCKED]"))
    assert "[contradicted] F1 London race August 2026" in blocked.body_text
    assert sorted(k for _, k, _ in _sends(session)) == ["blocked_notice", "no_signal"]


def test_a_brief_is_never_sent_twice(session, migrated_database, tmp_path):
    load_seeds(session)
    mailer = FakeMailer()
    settings = _settings(migrated_database, tmp_path)
    out = run_daily.run_day(
        RUN_DATE, settings, lambda _d: [_ramp_signal()], session, stages=_stages(mailer)
    )
    assert len(mailer.sent) == 1
    # second daily run: idempotent, no send
    again = run_daily.run_day(
        RUN_DATE, settings, lambda _d: [_ramp_signal()], session, stages=_stages(mailer)
    )
    assert again.already_ran and len(mailer.sent) == 1
    # a direct re-distribution (e.g. the 06:00 step retried after a crash) is a no-op too
    from intel.models import Brief, Run

    run = session.get(Run, out.run_id)
    brief = session.get(Brief, out.brief_id)
    assert send.distribute(session, run, settings, mailer, brief) == []
    assert len(mailer.sent) == 1


def test_run_failure_alerts_the_operator(session, migrated_database, tmp_path):
    from intel.scan import ScanFailed

    def boom(_d):
        raise ScanFailed("scanner output unparseable after retry")

    mailer = FakeMailer()
    out = run_daily.run_day(
        RUN_DATE, _settings(migrated_database, tmp_path), boom, session, stages=_stages(mailer)
    )
    assert out.status == "failed"
    assert mailer.sent[0].subject.startswith("[RUN FAILED]") and mailer.sent[0].to == [OP]
    assert _sends(session) == [(OP, "run_failure", "sent")]


def test_graph_failure_is_recorded_not_lost(session, migrated_database, tmp_path):
    load_seeds(session)
    mailer = FakeMailer(fail=True)
    run_daily.run_day(
        RUN_DATE,
        _settings(migrated_database, tmp_path),
        lambda _d: [_ramp_signal()],
        session,
        stages=_stages(mailer),
    )
    rows = session.scalars(select(Send)).all()
    assert rows and all(r.status == SendStatus.failed and "graph down" in r.error for r in rows)


def test_dry_run_mailer_writes_eml_to_the_outbox(tmp_path):
    m = send.DryRunMailer(tmp_path / "outbox")
    mid = m.send(
        send.Outgoing(
            to=[OP], subject="hello", body_text="x", attachments=[send.Attachment("a.pdf", b"%PDF")]
        )
    )
    files = list((tmp_path / "outbox").glob("*.eml"))
    assert mid.startswith("dryrun-") and len(files) == 1 and b"a.pdf" in files[0].read_bytes()


def test_mailer_for_falls_back_to_dry_run_without_credentials():
    assert isinstance(send.mailer_for(Settings(execution_mode="shadow")), send.DryRunMailer)
    s = Settings(
        execution_mode="production",
        graph_tenant_id="t",
        graph_client_id="c",
        graph_client_secret="s",
        graph_sender="me@x",
    )
    assert isinstance(send.mailer_for(s), send.GraphMailer)


def test_graph_mailer_round_trip_with_mocked_transport():
    calls: list[tuple[str, str, dict | None]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = (
            json.loads(request.content)
            if request.content
            and request.headers.get("content-type", "").startswith("application/json")
            else None
        )
        calls.append((request.method, str(request.url), body))
        if "oauth2/v2.0/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
        if str(request.url).endswith("/messages"):
            return httpx.Response(201, json={"id": "AAMk123", "internetMessageId": "<abc@outlook>"})
        if str(request.url).endswith("/send"):
            return httpx.Response(202)
        return httpx.Response(404)

    mailer = send.GraphMailer(
        "tenant",
        "client",
        "secret",
        "sender@1440sports.com",
        http=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    mid = mailer.send(
        send.Outgoing(
            to=[MD],
            cc=[OP],
            subject="s",
            body_text="b",
            attachments=[send.Attachment("x.pdf", b"%PDF-1.4")],
        )
    )
    assert mid == "<abc@outlook>"
    assert (
        calls[0][0] == "POST"
        and "login.microsoftonline.com/tenant/oauth2/v2.0/token" in calls[0][1]
    )
    assert calls[1][1] == "https://graph.microsoft.com/v1.0/users/sender@1440sports.com/messages"
    created = calls[1][2]
    assert created["toRecipients"][0]["emailAddress"]["address"] == MD
    assert created["ccRecipients"][0]["emailAddress"]["address"] == OP
    assert base64.b64decode(created["attachments"][0]["contentBytes"]) == b"%PDF-1.4"
    assert calls[2][1].endswith("/messages/AAMk123/send")
    # delegated fallback uses /me and the refresh-token grant
    d = send.GraphMailer(
        "tenant",
        "client",
        None,
        "sender@1440sports.com",
        refresh_token="rt",
        http=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    d.send(send.Outgoing(to=[MD], subject="s", body_text="b"))
    assert calls[-2][1] == "https://graph.microsoft.com/v1.0/me/messages"


@pytest.mark.parametrize(
    ("utc", "is_slot"),
    [
        (dt.datetime(2026, 7, 1, 4, 30, tzinfo=dt.UTC), True),  # BST: 05:30 London
        (dt.datetime(2026, 7, 1, 5, 30, tzinfo=dt.UTC), False),  # BST: 06:30 London
        (dt.datetime(2026, 12, 1, 5, 30, tzinfo=dt.UTC), True),  # GMT: 05:30 London
        (dt.datetime(2026, 12, 1, 4, 30, tzinfo=dt.UTC), False),  # GMT: 04:30 London
    ],
)
def test_schedule_picks_the_london_slot_across_bst_and_gmt(utc, is_slot):
    assert schedule.is_run_slot(utc) is is_slot


def test_seconds_until_send_is_thirty_minutes_from_the_run_slot():
    assert schedule.seconds_until_send(dt.datetime(2026, 7, 1, 4, 30, tzinfo=dt.UTC)) == 1800.0
    assert schedule.seconds_until_send(dt.datetime(2026, 7, 1, 5, 30, tzinfo=dt.UTC)) == 0.0
