"""app users + passkeys (build brief §8 sign-in)

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-04
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    ts = sa.DateTime(timezone=True)
    op.create_table(
        "app_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("display_name", sa.Text()),
        sa.Column("enrolled_at", ts),
        sa.Column("last_login_at", ts),
        sa.Column("created_at", ts, nullable=False, server_default=sa.text("now()")),
    )
    op.create_table(
        "passkeys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_email", sa.String(320), nullable=False),
        sa.Column("credential_id", sa.LargeBinary(), nullable=False, unique=True),
        sa.Column("public_key", sa.LargeBinary(), nullable=False),
        sa.Column("sign_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transports", postgresql.JSONB()),
        sa.Column("device_name", sa.Text()),
        sa.Column("created_at", ts, nullable=False, server_default=sa.text("now()")),
        sa.Column("last_used_at", ts),
    )
    op.create_index("ix_passkeys_user_email", "passkeys", ["user_email"])


def downgrade() -> None:
    op.drop_table("passkeys")
    op.drop_table("app_users")
