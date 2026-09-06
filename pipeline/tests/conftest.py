"""Test fixtures.

Database strategy: if ``$DATABASE_URL`` is set (CI, Railway) use it; otherwise
bootstrap a throw-away Postgres cluster from the locally installed server
binaries. Either way the schema comes from the Alembic migrations, never from
``metadata.create_all`` — the migrations are what ship.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import text

from intel import db as intel_db
from intel.config import reset_settings

REPO_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = REPO_ROOT / "db" / "alembic.ini"


from intel.tempdb import TempCluster as _TempCluster  # noqa: E402
from intel.tempdb import alembic_config, pg_bindir  # noqa: E402,F401


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    url = os.environ.get("DATABASE_URL")
    if url:
        yield url
        return
    try:
        cluster = _TempCluster()
    except RuntimeError as exc:
        pytest.skip(str(exc))
    try:
        yield cluster.start()
    finally:
        cluster.stop()


@pytest.fixture(scope="session")
def migrated_database(database_url: str) -> Iterator[str]:
    """A database at Alembic head. Downgrades to base first so re-runs start clean."""
    cfg = alembic_config(database_url)
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    yield database_url
    intel_db.reset_engine()


@pytest.fixture()
def settings_env(monkeypatch: pytest.MonkeyPatch, migrated_database: str) -> Iterator[None]:
    monkeypatch.setenv("DATABASE_URL", migrated_database)
    reset_settings()
    intel_db.reset_engine()
    yield
    reset_settings()
    intel_db.reset_engine()


@pytest.fixture()
def session(settings_env: None, migrated_database: str):
    """A session on a clean database: every table is truncated after each test."""
    intel_db.reset_engine()
    engine = intel_db.get_engine(migrated_database)
    s = intel_db.get_sessionmaker()()
    try:
        yield s
    finally:
        # Tests may leave the transaction failed on purpose (IntegrityError checks):
        # always roll back, never commit, then wipe the tables.
        s.rollback()
        s.close()
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE highlights, outreach_drafts, contacts, brief_actions, calendar_events, "
                "sponsors, blocklist, alumni, surfaced_log, sends, verifications, claims, briefs, "
                "candidates, runs, passkeys, app_users RESTART IDENTITY CASCADE"
            )
        )
