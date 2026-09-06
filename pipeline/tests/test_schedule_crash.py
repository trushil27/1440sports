"""The morning must never die silently: a model-client error is a clean scan failure, and any
other crash inside the run still emails the operator, refreshes the app and exits 0."""

from __future__ import annotations

import pytest

from intel import schedule
from intel.scan import AnthropicText, ScanFailed


class _Boom:
    class messages:  # noqa: N801 — mimics anthropic.Anthropic().messages
        @staticmethod
        def create(**kw):
            raise TypeError("Could not resolve authentication method")

        @staticmethod
        def stream(**kw):
            raise TypeError("Could not resolve authentication method")


def test_model_client_errors_become_scan_failures():
    client = AnthropicText(client=_Boom())
    with pytest.raises(ScanFailed) as exc:
        client.create_text(model="m", system="s", messages=[], tools=[])
    assert "scanner call failed: TypeError" in str(exc.value)


def test_schedule_survives_a_crash_and_emails(monkeypatch, tmp_path):
    monkeypatch.setenv("EXECUTION_MODE", "dry_run")
    monkeypatch.setenv("OUTBOX_DIR", str(tmp_path / "outbox"))
    monkeypatch.setenv("OPERATOR_EMAIL", "ops@example.com")
    monkeypatch.setenv("SITE_DIR", str(tmp_path / "site"))
    from intel.config import reset_settings

    reset_settings()

    def explode(*a, **k):
        raise RuntimeError("writer exploded")

    from intel import run_daily

    monkeypatch.setattr(run_daily, "run_day", explode)
    published = {}
    from intel import site_export

    monkeypatch.setattr(site_export, "publish", lambda settings: published.setdefault("ok", True))
    assert schedule.main(["--force", "--no-wait"]) == 0
    eml = next((tmp_path / "outbox").glob("*.eml")).read_text(encoding="utf-8")
    assert "the run crashed" in eml and "RuntimeError: writer exploded" in eml
    assert published == {"ok": True}  # the app still refreshed
    reset_settings()
