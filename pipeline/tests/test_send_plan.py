"""intel.send_plan — one verified brief to the MD a day, from a queue in the repo."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import select

from intel import run_daily, send_plan
from intel.config import Settings
from intel.models import Brief
from intel.seed import load_seeds
from tests.fixtures.ramp_brief import RAMP_WRITTEN
from tests.test_m3_verify import FakeVerifier
from tests.test_m4_pipeline import RUN_DATE, FakeWriter, _block, _ramp_signal


class SpyMailer:
    def __init__(self) -> None:
        self.sent: list = []

    def send(self, msg) -> str:
        self.sent.append(msg)
        return f"<msg-{len(self.sent)}@test>"


def _verified_ramp(session, migrated_database, tmp_path) -> Brief:
    load_seeds(session)
    stages = run_daily.Stages(
        verifier=FakeVerifier(), writer=FakeWriter([_block(RAMP_WRITTEN)]), font_stack="june"
    )
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        operator_email="op@1440sports.com",
        md_email="md@1440sports.com",
    )
    out = run_daily.run_day(RUN_DATE, settings, lambda _d: [_ramp_signal()], session, stages=stages)
    assert out.status == "success"
    session.flush()
    return session.get(Brief, out.brief_id), settings


def test_the_next_eligible_brief_goes_once_a_day_and_is_recorded(
    session, migrated_database, tmp_path
):
    brief, settings = _verified_ramp(session, migrated_database, tmp_path)
    plan_path = tmp_path / "send_plan.json"
    plan = send_plan.load_plan(plan_path)
    plan["queue"] = [
        {"number": 999, "hold": False},  # no case built yet → skipped, with the reason
        {"number": brief.brief_number, "hold": True},  # held → skipped
    ]
    send_plan.save_plan(plan, plan_path)

    item, skipped = send_plan.next_eligible(session, plan)
    assert item is None and skipped[0] == (999, "no case built yet")
    assert skipped[1][1] == "held by the operator"

    plan["queue"][1]["hold"] = False
    mailer = SpyMailer()
    day = dt.date(2026, 9, 16)
    msg = send_plan.send_next(session, settings, mailer, plan, day=day, dry_run=True)
    assert msg.startswith(f"would send N° {brief.brief_number} Ramp") and not mailer.sent

    # a real send goes to the MD with the operator copied and is written to the log
    import intel.resend as resend_mod

    live = settings.model_copy(update={"execution_mode": "shadow"})  # dry_run is never logged
    original = send_plan.PLAN_FILE
    send_plan.PLAN_FILE = plan_path
    try:
        msg = send_plan.send_next(session, live, mailer, plan, day=day)
    finally:
        send_plan.PLAN_FILE = original
    assert msg.startswith(f"N° {brief.brief_number} Ramp → md@1440sports.com")
    assert mailer.sent and mailer.sent[0].to == ["md@1440sports.com"]
    assert "op@1440sports.com" in (mailer.sent[0].cc or [])
    logged = send_plan.load_plan(plan_path)
    assert [s["number"] for s in send_plan.md_sends(logged)] == [brief.brief_number]
    assert logged["sent"][0]["message_id"] == "<msg-1@test>"
    assert send_plan.sent_today(logged, send_plan.london_today()) is not None

    # the one-a-day rule: a second call the same London day holds, sends nothing
    today = send_plan.london_today()
    msg = send_plan.send_next(session, settings, mailer, logged, day=today)
    assert msg.startswith("hold:") and len(mailer.sent) == 1
    # and the brief is not eligible again once sent
    ok, why = send_plan.eligibility(session, {"number": brief.brief_number}, logged)
    assert not ok and why == "already sent to the MD"
    assert resend_mod  # imported for the side-effect path above


def test_an_unverified_brief_never_goes(session, migrated_database, tmp_path):
    load_seeds(session)
    haunted = dict(
        RAMP_WRITTEN,
        why_now_callout=(
            "<font name='Poppins-Bold' size='9'>WHY NOW</font>&nbsp;&nbsp;The $750M raise has just "
            "closed and the F1 London race August 2026 is the activation window."
        ),
    )
    stages = run_daily.Stages(
        verifier=FakeVerifier(), writer=FakeWriter([_block(haunted)]), font_stack="june"
    )
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        operator_email="op@1440sports.com",
        md_email="md@1440sports.com",
    )
    run_daily.run_day(RUN_DATE, settings, lambda _d: [_ramp_signal()], session, stages=stages)
    session.flush()
    brief = session.scalar(select(Brief))
    plan = send_plan.load_plan(tmp_path / "p.json")
    plan["queue"] = [{"number": brief.brief_number, "hold": False}]
    ok, why = send_plan.eligibility(session, plan["queue"][0], plan)
    assert not ok and why.startswith("not MD-eligible: verification blocked")
    mailer = SpyMailer()
    msg = send_plan.send_next(session, settings, mailer, plan, day=dt.date(2026, 9, 16))
    assert msg.startswith("nothing eligible to send") and not mailer.sent
    assert not (tmp_path / "p.json").exists()  # nothing was recorded
