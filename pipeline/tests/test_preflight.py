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


def test_localhost_url_is_named_as_the_container_default():
    """The alembic.ini default (what the Railway log showed): probed, refused, explained."""
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
    assert preflight.main([]) == 1
    assert preflight.main(["--alert", "--service", "desk build service"]) == 0
    reset_settings()
