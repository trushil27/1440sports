"""intel.resend — email a brief that already exists, with no model calls at all.

Every signal in the desk carries a verified case, a 2-page PDF and an app page, but only the
day's hero was ever emailed. The operator could see N° 241 Nexeon on the site and had never
received it (7 Sep 2026). This is the missing door.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from intel import resend, run_daily
from intel.config import Settings
from intel.seed import load_seeds
from intel.send import DryRunMailer
from tests.fixtures.ramp_brief import RAMP_WRITTEN
from tests.test_m3_verify import FakeVerifier
from tests.test_m4_pipeline import RUN_DATE, FakeWriter, _block, _ramp_signal


def _number(session):
    from sqlalchemy import select

    from intel.models import Brief

    return session.scalars(select(Brief.brief_number).order_by(Brief.id.desc())).first()


def _issued(session, migrated_database, tmp_path):
    load_seeds(session)
    stages = run_daily.Stages(
        verifier=FakeVerifier(), writer=FakeWriter([_block(RAMP_WRITTEN)]), font_stack="june"
    )
    settings = Settings(
        database_url=migrated_database,
        execution_mode="dry_run",
        pdf_storage_dir=str(tmp_path / "briefs"),
        outbox_dir=str(tmp_path / "outbox"),
        operator_email="desk@example.com",
        md_email="md@example.com",
    )
    out = run_daily.run_day(RUN_DATE, settings, lambda _d: [_ramp_signal()], session, stages=stages)
    assert out.status == "success"
    session.flush()
    return settings, resend.brief_by_number(session, 1) or out


def test_a_brief_already_in_memory_can_be_sent_again_on_demand(
    session, migrated_database, tmp_path
):
    settings, _ = _issued(session, migrated_database, tmp_path)
    number = _number(session)
    brief = resend.brief_by_number(session, number)
    assert brief is not None

    mailer = DryRunMailer(Path(settings.outbox_dir))
    line = resend.resend(session, number, settings, mailer)
    assert f"N° {number} Ramp" in line and "desk@example.com" in line

    msg = resend.message_for(brief, settings)
    assert msg.to == ["desk@example.com"]  # never the MD, whatever the mode
    assert "Ramp" in msg.subject and msg.body_html and "Ramp" in msg.body_text
    assert msg.attachments and msg.attachments[0].name.endswith(".pdf")


def test_sending_twice_is_allowed_because_that_is_the_whole_point(
    session, migrated_database, tmp_path
):
    """The daily job skips anything already sent once. An explicit resend must not."""
    settings, _ = _issued(session, migrated_database, tmp_path)
    number = _number(session)
    mailer = DryRunMailer(Path(settings.outbox_dir))
    assert resend.resend(session, number, settings, mailer)
    assert resend.resend(session, number, settings, mailer)


def test_an_unknown_number_says_so_rather_than_sending_something_else(
    session, migrated_database, tmp_path
):
    settings, _ = _issued(session, migrated_database, tmp_path)
    with pytest.raises(LookupError, match="no brief numbered 999"):
        resend.resend(session, 999, settings, DryRunMailer(Path(settings.outbox_dir)))
