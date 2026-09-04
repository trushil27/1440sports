"""API test fixtures: reuse the pipeline's Postgres bootstrap + migrations, wrap the app."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "pipeline"
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

_spec = importlib.util.spec_from_file_location(
    "pipeline_conftest", PIPELINE / "tests" / "conftest.py"
)
_pipeline_conftest = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_pipeline_conftest)

database_url = _pipeline_conftest.database_url
migrated_database = _pipeline_conftest.migrated_database
settings_env = _pipeline_conftest.settings_env
session = _pipeline_conftest.session

OP = "operator@example.test"
MD = "md@example.test"


class FakeMailer:
    channel = None

    def __init__(self) -> None:
        self.sent = []
        self.drafts = []

    def send(self, msg) -> str:
        self.sent.append(msg)
        return f"<msg-{len(self.sent)}@example.test>"

    def create_draft(self, msg) -> str:
        self.drafts.append(msg)
        return f"draft-{len(self.drafts)}"


@pytest.fixture()
def api(session, migrated_database):
    from intel import db as intel_db
    from intel.models import SendChannel
    from intel_api.app import create_app
    from intel_api.settings import ApiSettings, User

    FakeMailer.channel = SendChannel.outlook
    mailer = FakeMailer()
    settings = ApiSettings(
        secret_key="test-secret",
        users=[User(OP, "operator", "Trushil"), User(MD, "md", "Ricky")],
        rp_id="localhost",
        origin="http://testserver",
        api_base_url="http://testserver",
    )
    app = create_app(settings, intel_db.get_sessionmaker(migrated_database), mailer=mailer)
    client = TestClient(app, base_url="http://testserver")
    client.mailer = mailer  # type: ignore[attr-defined]
    client.app_state = app.state  # type: ignore[attr-defined]
    return client


def login(client: TestClient, email: str) -> None:
    """Magic-link round trip: request → link in the fake mailer → verify → session cookie."""
    r = client.post("/auth/magic-link", json={"email": email})
    assert r.status_code == 204
    link = client.mailer.sent[-1].body_text.split("\n")[2]  # type: ignore[attr-defined]
    token = link.split("token=")[1]
    r = client.get("/auth/magic-link/verify", params={"token": token})
    assert r.status_code == 200, r.text
