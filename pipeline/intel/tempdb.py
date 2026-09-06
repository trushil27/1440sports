"""A throw-away Postgres for one process: the tests, an in-session case build, a local
export. Bootstrapped from the locally installed server binaries (``initdb`` + ``pg_ctl``),
migrated with the shipped Alembic migrations, seeded, and given the repo's memory
(``intel.backfill``) on request. Nothing here touches a real database.

    from intel.tempdb import TempCluster, prepare
    cluster = TempCluster(); url = cluster.start(); prepare(url)   # migrate + seed + backfill
    ...
    cluster.stop()
"""

from __future__ import annotations

import glob
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = REPO_ROOT / "db" / "alembic.ini"


def pg_bindir() -> str:
    candidates = sorted(glob.glob("/usr/lib/postgresql/*/bin"), reverse=True)
    if candidates:
        return candidates[0]
    pg_config = shutil.which("pg_config")
    if pg_config:
        return subprocess.check_output([pg_config, "--bindir"], text=True).strip()
    raise RuntimeError("No Postgres server binaries found (and no DATABASE_URL given)")


def as_pg_user(cmd: list[str]) -> list[str]:
    """Postgres refuses to run as root; hop to the postgres system user when needed."""
    if os.geteuid() == 0 and shutil.which("runuser"):
        return ["runuser", "-u", "postgres", "--", *cmd]
    return cmd


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TempCluster:
    def __init__(self, dbname: str = "intel_test") -> None:
        self.bindir = pg_bindir()
        self.dir = Path(tempfile.mkdtemp(prefix="intel-pg-", dir="/tmp"))
        self.port = free_port()
        self.data = self.dir / "data"
        self.dbname = dbname

    def start(self) -> str:
        import psycopg

        os.chmod(self.dir, 0o755)
        if os.geteuid() == 0:
            shutil.chown(self.dir, user="postgres")
        subprocess.run(
            as_pg_user(
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
            as_pg_user(
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
                    conn.execute(f"CREATE DATABASE {self.dbname}")
                break
            except psycopg.OperationalError:
                time.sleep(0.2)
        return f"postgresql+psycopg://postgres@127.0.0.1:{self.port}/{self.dbname}"

    def stop(self) -> None:
        subprocess.run(
            as_pg_user([f"{self.bindir}/pg_ctl", "-D", str(self.data), "-m", "immediate", "stop"]),
            capture_output=True,
        )
        shutil.rmtree(self.dir, ignore_errors=True)


def alembic_config(url: str):
    from alembic.config import Config

    cfg = Config(str(ALEMBIC_INI))
    cfg.attributes["url"] = url
    return cfg


def migrate(url: str) -> None:
    from alembic import command

    command.upgrade(alembic_config(url), "head")


def prepare(url: str, backfill: bool = True) -> None:
    """Migrate, seed, and (by default) load the repo's memory — history, recorded cases,
    signal checks — so numbering and the day-taken rule behave as in production."""
    migrate(url)
    env = dict(os.environ, DATABASE_URL=url, PYTHONPATH=str(REPO_ROOT / "pipeline"))
    subprocess.run([sys.executable, "-m", "intel.seed"], check=True, env=env, cwd=REPO_ROOT)
    if backfill:
        subprocess.run(
            [sys.executable, "-m", "intel.backfill"],
            check=True,
            env=env,
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
        )
