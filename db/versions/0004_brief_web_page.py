"""briefs.web_html_path — the rendered app page (long-form sections) next to the 2-page PDF

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("briefs", sa.Column("web_html_path", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("briefs", "web_html_path")
