"""Runtime configuration, read from environment variables.

Every operational knob the build brief says to "store as config" lives here with
its default. Nothing secret has a default. Change scoring/gates only with the
MD's approval (brief §0.5) — those are not here on purpose; they live in
``spec/`` and the modules that port them.
"""

from __future__ import annotations

import os
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

TZ_LONDON = ZoneInfo("Europe/London")


class Settings(BaseModel):
    # --- storage -------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+psycopg://postgres@localhost:5432/intel",
        description="SQLAlchemy URL for the shared Postgres database.",
    )
    pdf_storage_dir: str = Field(
        default="storage/briefs", description="Local PDF store (R2/S3 later)."
    )

    # --- models --------------------------------------------------------------
    anthropic_api_key: str | None = None
    scan_model: str = "claude-sonnet-5"
    writer_model: str = "claude-sonnet-5"
    verify_model: str = "claude-opus-5"

    # --- pipeline policy (brief §6) ---------------------------------------------
    md_threshold: int = Field(default=70, description="Minimum score to produce a brief (§6.4).")
    freshness_days_track1: int = Field(default=14, description="Track 1 trigger window (§6.2).")
    freshness_days_alumni: int = Field(default=90, description="Alumni-move window (§6.2).")
    dedup_window_days: int = Field(default=30, description="surfaced_log lookback (§6.3).")
    max_verification_attempts: int = Field(
        default=3, description="Candidates tried after a block (§6.5)."
    )
    scan_candidates_min: int = 8
    scan_candidates_max: int = 12
    timezone: str = "Europe/London"

    # --- distribution (brief §7) ----------------------------------------------
    execution_mode: str = Field(
        default="shadow",
        description="production | shadow (operator only) | dry_run (no sends).",
    )
    operator_email: str | None = None
    md_email: str | None = None
    graph_tenant_id: str | None = None
    graph_client_id: str | None = None
    graph_client_secret: str | None = None
    graph_sender: str | None = None

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        env = dict(os.environ if env is None else env)
        values: dict[str, object] = {}
        for name, field in cls.model_fields.items():
            key = name.upper()
            if key in env and env[key] != "":
                raw = env[key]
                ann = field.annotation
                if ann is int:
                    values[name] = int(raw)
                else:
                    values[name] = raw
        return cls(**values)


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def reset_settings() -> None:
    """Test hook: forget the cached settings so the next call re-reads the environment."""
    global _settings
    _settings = None
