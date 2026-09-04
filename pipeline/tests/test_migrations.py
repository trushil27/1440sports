"""M1 acceptance: migrations apply, match the ORM, and enforce the structural rules."""

from __future__ import annotations

import datetime as dt

import pytest
from alembic import command
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from intel.models import (
    Base,
    Brief,
    Candidate,
    Run,
    Send,
    SendChannel,
    SendKind,
    SendStatus,
    SurfacedLog,
)
from tests.conftest import alembic_config


def test_migrations_reach_head_and_match_orm(migrated_database: str):
    from intel import db as intel_db

    engine = intel_db.get_engine(migrated_database)
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    for name, table in Base.metadata.tables.items():
        assert name in tables, f"table {name} missing after upgrade"
        db_cols = {c["name"] for c in insp.get_columns(name)}
        orm_cols = {c.name for c in table.columns}
        assert db_cols == orm_cols, f"{name}: columns differ {db_cols ^ orm_cols}"
    assert "alembic_version" in tables
    with engine.connect() as conn:
        seq = conn.execute(
            text("SELECT 1 FROM pg_class WHERE relkind = 'S' AND relname = 'brief_number_seq'")
        ).scalar()
    assert seq == 1


def test_downgrade_and_upgrade_round_trip(migrated_database: str):
    cfg = alembic_config(migrated_database)
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")


def _run(session, day: dt.date) -> Run:
    run = Run(run_date=day)
    session.add(run)
    session.flush()
    return run


def _candidate(session, run: Run, name: str) -> Candidate:
    c = Candidate(
        run_id=run.id, company_raw=name, company_norm=name.lower(), raw_json={"company": name}
    )
    session.add(c)
    session.flush()
    return c


def test_brief_numbers_come_from_sequence_and_are_never_reused(session):
    run = _run(session, dt.date(2026, 9, 4))
    c1 = _candidate(session, run, "Alpha")
    b1 = Brief(candidate_id=c1.id, run_date=run.run_date)
    session.add(b1)
    session.flush()
    first = b1.brief_number
    assert first >= 1

    # A rolled-back insert still consumes a number: gaps are fine, reuse is not.
    nested = session.begin_nested()
    c2 = _candidate(session, run, "Beta")
    b2 = Brief(candidate_id=c2.id, run_date=dt.date(2026, 9, 5))
    session.add(b2)
    session.flush()
    burned = b2.brief_number
    nested.rollback()

    c3 = _candidate(session, run, "Gamma")
    b3 = Brief(candidate_id=c3.id, run_date=dt.date(2026, 9, 6))
    session.add(b3)
    session.flush()
    assert b3.brief_number > burned > first


def test_one_non_blocked_brief_per_day(session):
    run = _run(session, dt.date(2026, 9, 4))
    c1 = _candidate(session, run, "Alpha")
    c2 = _candidate(session, run, "Beta")
    session.add(Brief(candidate_id=c1.id, run_date=run.run_date))
    session.flush()
    session.add(Brief(candidate_id=c2.id, run_date=run.run_date))
    with pytest.raises(IntegrityError):
        session.flush()


def test_blocked_brief_does_not_consume_the_day(session):
    from intel.models import VerificationStatus

    run = _run(session, dt.date(2026, 9, 4))
    c1 = _candidate(session, run, "Alpha")
    c2 = _candidate(session, run, "Beta")
    session.add(
        Brief(
            candidate_id=c1.id,
            run_date=run.run_date,
            verification_status=VerificationStatus.blocked,
        )
    )
    session.flush()
    session.add(Brief(candidate_id=c2.id, run_date=run.run_date))
    session.flush()  # allowed: the first attempt was blocked, the pipeline moved on


def test_surfaced_log_is_unique_on_company_and_trigger(session):
    session.add(SurfacedLog(company_norm="lime", trigger_reason_norm="s 1 filed"))
    session.flush()
    session.add(SurfacedLog(company_norm="lime", trigger_reason_norm="s 1 filed"))
    with pytest.raises(IntegrityError):
        session.flush()


def test_send_cannot_be_recorded_twice_for_same_brief_recipient_kind(session):
    run = _run(session, dt.date(2026, 9, 4))
    c = _candidate(session, run, "Alpha")
    b = Brief(candidate_id=c.id, run_date=run.run_date)
    session.add(b)
    session.flush()
    kwargs = dict(
        brief_id=b.id,
        recipient="md@example.test",
        channel=SendChannel.outlook,
        kind=SendKind.md_brief,
        status=SendStatus.sent,
    )
    session.add(Send(**kwargs))
    session.flush()
    session.add(Send(**kwargs))
    with pytest.raises(IntegrityError):
        session.flush()
