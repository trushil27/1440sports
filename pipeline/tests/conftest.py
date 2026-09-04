"""Test fixtures.

Database strategy: if ``$DATABASE_URL`` is set (CI, Railway) use it; otherwise
bootstrap a throw-away Postgres cluster from the locally installed server
binaries. Either way the schema comes from the Alembic migrations, never from
``metadata.create_all`` — the migrations are what ship.
"""

from __future__ import annotations

import glob
import os
import shutil
import socket
import subprocess
import tempfile
import time
from collections.abc import Iterator
from pathlib import Path

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from intel import db as intel_db
from intel.config import reset_settings

REPO_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = REPO_ROOT / "db" / "alembic.ini"


def _pg_bindir() -> str:
    candidates = sorted(glob.glob("/usr/lib/postgresql/*/bin"), reverse=True)
    if candidates:
        return candidates[0]
    pg_config = shutil.which("pg_config")
    if pg_config:
        return subprocess.check_output([pg_config, "--bindir"], text=True).strip()
    pytest.skip("No Postgres server binaries and no DATABASE_URL — cannot run DB tests")


def _as_pg_user(cmd: list[str]) -> list[str]:
    """Postgres refuses to run as root; hop to the postgres system user when needed."""
    if os.geteuid() == 0 and shutil.which("runuser"):
        return ["runuser", "-u", "postgres", "--", *cmd]
    return cmd


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _TempCluster:
    def __init__(self) -> None:
        self.bindir = _pg_bindir()
        self.dir = Path(tempfile.mkdtemp(prefix="intel-pg-", dir="/tmp"))
        self.port = _free_port()
        self.data = self.dir / "data"

    def start(self) -> str:
        os.chmod(self.dir, 0o755)
        if os.geteuid() == 0:
            shutil.chown(self.dir, user="postgres")
        subprocess.run(
            _as_pg_user(
                [
                    f"{self.bindir}/initdb",
                    "-D",
                    str(self.data),
                    "-A",
                    "trust",
                    "-U",
                    "postgres",
                    "-E",
                    "UTF8",
                    "--locale=C.UTF-8",
                ]
            ),
            check=True,
            capture_output=True,
        )
        subprocess.run(
            _as_pg_user(
                [
                    f"{self.bindir}/pg_ctl",
                    "-D",
                    str(self.data),
                    "-o",
                    f"-p {self.port} -k {self.dir} -c listen_addresses=127.0.0.1",
                    "-l",
                    str(self.dir / "log"),
                    "-w",
                    "start",
                ]
            ),
            check=True,
            capture_output=True,
        )
        admin = f"postgresql://postgres@127.0.0.1:{self.port}/postgres"
        for _ in range(50):
            try:
                with psycopg.connect(admin, autocommit=True) as conn:
                    conn.execute("CREATE DATABASE intel_test")
                break
            except psycopg.OperationalError:
                time.sleep(0.2)
        return f"postgresql+psycopg://postgres@127.0.0.1:{self.port}/intel_test"

    def stop(self) -> None:
        subprocess.run(
            _as_pg_user([f"{self.bindir}/pg_ctl", "-D", str(self.data), "-m", "immediate", "stop"]),
            capture_output=True,
        )
        shutil.rmtree(self.dir, ignore_errors=True)


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    url = os.environ.get("DATABASE_URL")
    if url:
        yield url
        return
    cluster = _TempCluster()
    try:
        yield cluster.start()
    finally:
        cluster.stop()


def alembic_config(url: str) -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.attributes["url"] = url
    return cfg


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
                "candidates, runs RESTART IDENTITY CASCADE"
            )
        )
