"""historical briefs — the one-brief-per-day rule applies to live briefs only (M6 backfill)

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-04

The n8n audit log has several signals on one date (e.g. Primer ×3 on 2026-05-20) and this
repo's engine issued two briefs on 2026-06-03 / 06-09 / 06-11. Imported briefs are marked
``historical = true`` and are exempt from the per-day idempotency index; live briefs keep it.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

INDEX = "uq_briefs_issued_per_day"


def upgrade() -> None:
    op.drop_index(INDEX, table_name="briefs")
    op.create_index(
        INDEX,
        "briefs",
        ["run_date"],
        unique=True,
        postgresql_where=sa.text("verification_status <> 'blocked' AND historical = false"),
    )


def downgrade() -> None:
    op.drop_index(INDEX, table_name="briefs")
    op.create_index(
        INDEX,
        "briefs",
        ["run_date"],
        unique=True,
        postgresql_where=sa.text("verification_status <> 'blocked'"),
    )
