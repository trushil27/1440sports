"""Preflight: a missing DATABASE_URL becomes a named diagnosis and an operator email, never a
crash loop; a reachable database passes."""

from __future__ import annotations

from pathlib import Path

from intel import preflight
from intel.config import Settings

GOOD_MAIL = {
    "OPERATOR_EMAIL": "ops@example.com",
    "GRAPH_TENANT_ID": "t",
    "GRAPH_CLIENT_ID": "c",
    "GRAPH_SENDER": "s@example.com",
    "GRAPH_REFRESH_TOKEN": "r",
}


def test_missing_database_url_is_named(monkeypatch):
    diag = preflight.diagnose({"ANTHROPIC_API_KEY": "k", "PDF_STORAGE_DIR": "/data", **GOOD_MAIL})
    assert diag["database_ok"] is False
    assert diag["database_host"] is None
    assert diag["problems"][0].startswith("DATABASE_URL is not set on this service")
    assert diag["variables"]["DATABASE_URL"] is False
    assert "Add Reference" in diag["problems"][0]
    text = preflight.render(diag)
    assert "DATABASE_URL: MISSING" in text and "NOT REACHABLE" in text


def test_localhost_url_is_named_as_the_container_default(monkeypatch):
    """The alembic.ini default (what the Railway log showed): probed, refused, explained.
    The probe is stubbed so the test does not depend on what listens on the runner's 5432."""
    monkeypatch.setattr(
        preflight, "check_database", lambda url, timeout=5: "connection refused (stubbed)"
    )
    diag = preflight.diagnose(
        {
            "DATABASE_URL": "postgresql://postgres@localhost:5432/intel",
            "ANTHROPIC_API_KEY": "k",
            "PDF_STORAGE_DIR": "/d",
            **GOOD_MAIL,
        }
    )
    assert diag["database_ok"] is False
    assert diag["database_host"] == "localhost:5432/intel"
    assert "local address inside the container" in diag["problems"][0]
    assert "not reachable" in diag["problems"][0]


def test_reachable_database_passes(migrated_database):
    diag = preflight.diagnose(
        {
            "DATABASE_URL": migrated_database,
            "ANTHROPIC_API_KEY": "k",
            "PDF_STORAGE_DIR": "/d",
            **GOOD_MAIL,
        }
    )
    assert diag["database_ok"] is True and diag["problems"] == []
    assert "/" in diag["database_host"]


def test_unreachable_database_is_reported_not_raised():
    err = preflight.check_database("postgresql://postgres@127.0.0.1:1/none", timeout=1)
    assert err and "connection" in err.lower()


def test_alert_goes_through_the_configured_mailer(tmp_path: Path):
    settings = Settings(
        execution_mode="dry_run",
        outbox_dir=str(tmp_path / "outbox"),
        operator_email="ops@example.com",
        database_url="postgresql://postgres@localhost:5432/intel",
    )
    diag = preflight.diagnose({"ANTHROPIC_API_KEY": "k"}, probe=False)
    mid = preflight.alert(diag, settings, service="daily job")
    assert mid and mid.startswith("dryrun-")
    eml = next((tmp_path / "outbox").glob("*.eml")).read_text(encoding="utf-8")
    assert "[RUN FAILED] 1440 Intelligence" in eml and "daily job did not start" in eml
    assert "DATABASE_URL is not set on this service" in eml
    assert "postgres@" not in eml  # never the value, only the diagnosis


def test_alert_without_operator_address_is_a_noop(capsys):
    settings = Settings(execution_mode="dry_run", operator_email=None)
    assert preflight.alert(preflight.diagnose({}, probe=False), settings) is None
    assert "OPERATOR_EMAIL not set" in capsys.readouterr().out


def test_cli_exit_codes(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("EXECUTION_MODE", "dry_run")
    monkeypatch.setenv("OUTBOX_DIR", str(tmp_path / "o"))
    monkeypatch.setenv("OPERATOR_EMAIL", "ops@example.com")
    from intel.config import reset_settings

    reset_settings()
    assert preflight.main([]) == preflight.EXIT_DB_UNREACHABLE
    assert preflight.main(["--alert", "--service", "desk build service"]) == (
        preflight.EXIT_DB_UNREACHABLE
    )
    assert len(list((tmp_path / "o").glob("*.eml"))) == 1
    assert "desk build service did not start" in next((tmp_path / "o").glob("*.eml")).read_text()
    reset_settings()


def test_cli_waits_for_a_database_that_comes_back(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres@db.internal:5432/railway")
    monkeypatch.setenv("EXECUTION_MODE", "dry_run")
    monkeypatch.setenv("OUTBOX_DIR", str(tmp_path / "o"))
    monkeypatch.setenv("OPERATOR_EMAIL", "ops@example.com")
    from intel.config import reset_settings

    reset_settings()
    answers = iter(["refused", "refused", None])  # third probe succeeds
    monkeypatch.setattr(preflight, "check_database", lambda url, timeout=5: next(answers))
    monkeypatch.setattr(preflight.time, "sleep", lambda s: None)
    assert preflight.main(["--alert", "--wait", "30"]) == preflight.EXIT_OK
    assert not (tmp_path / "o").exists()  # no email when it recovered
    reset_settings()


def test_unparseable_url_is_its_own_problem(monkeypatch):
    monkeypatch.setattr(preflight, "check_database", lambda url, timeout=5: "x")
    diag = preflight.diagnose({"DATABASE_URL": "postgresql://u:p@[::1/db", **GOOD_MAIL})
    assert diag["database_ok"] is False
    assert "not a valid database URL" in diag["problems"][0]
    diag = preflight.diagnose({"DATABASE_URL": "not a url", **GOOD_MAIL})
    assert diag["database_ok"] is False and "not a valid database URL" in diag["problems"][0]
