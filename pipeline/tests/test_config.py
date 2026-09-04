"""Settings: hosted-Postgres URLs are pinned to the psycopg 3 driver (Railway injects postgresql://)."""

from __future__ import annotations

import pytest

from intel.config import Settings, normalise_database_url


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        (
            "postgresql://postgres:pw@postgres.railway.internal:5432/railway",
            "postgresql+psycopg://postgres:pw@postgres.railway.internal:5432/railway",
        ),
        ("postgres://u:p@h/db?sslmode=require", "postgresql+psycopg://u:p@h/db?sslmode=require"),
        ("postgresql+psycopg://u@h/db", "postgresql+psycopg://u@h/db"),  # already pinned
        ("sqlite:///x.db", "sqlite:///x.db"),  # untouched
    ],
)
def test_normalise_database_url(given: str, expected: str):
    assert normalise_database_url(given) == expected


def test_settings_pin_the_driver_from_env():
    s = Settings.from_env({"DATABASE_URL": "postgresql://postgres:pw@host:5432/railway"})
    assert s.database_url == "postgresql+psycopg://postgres:pw@host:5432/railway"
    assert Settings().database_url.startswith("postgresql+psycopg://")
