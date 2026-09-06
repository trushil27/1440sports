"""rebuild_requests — "Build the full case" clicks from the app, queued and worked off

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rebuild_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("brief_number", sa.Integer(), nullable=True),
        sa.Column("company", sa.Text(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "done", "failed", name="rebuild_status"),
            nullable=False,
            server_default="queued",
        ),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_brief_id", sa.Integer(), nullable=True),
        sa.Column("result_number", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("requester", sa.Text(), nullable=True),
    )
    op.create_index("ix_rebuild_requests_status", "rebuild_requests", ["status"])


def downgrade() -> None:
    op.drop_index("ix_rebuild_requests_status", table_name="rebuild_requests")
    op.drop_table("rebuild_requests")
    sa.Enum(name="rebuild_status").drop(op.get_bind(), checkfirst=True)
