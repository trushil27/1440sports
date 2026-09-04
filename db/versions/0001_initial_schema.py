"""initial schema — build brief §5

Revision ID: 0001
Revises:
Create Date: 2026-09-04
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def _e(name: str, *values: str) -> sa.Enum:
    return sa.Enum(*values, name=name)


ENUMS: dict[str, tuple[str, ...]] = {
    "run_status": ("running", "success", "no_signal", "failed"),
    "execution_mode": ("production", "shadow", "dry_run"),
    "series": ("F1", "FE"),
    "candidate_decision": (
        "pending",
        "selected",
        "not_selected",
        "dedup_suppressed",
        "stale",
        "blocklisted",
        "gate_failed",
        "below_threshold",
        "verification_blocked",
    ),
    "audit_status": ("pending", "pass", "pass_after_retry", "failed"),
    "verification_status": ("pending", "verified", "needs_review", "blocked"),
    "value_mode": ("A", "B", "C"),
    "claim_type": ("funding", "person_role", "sponsorship", "event", "revenue", "date", "other"),
    "verification_result": ("verified", "unverified", "contradicted"),
    "verification_method": ("llm_source_fetch", "sponsor_db", "calendar", "manual"),
    "send_channel": ("outlook", "app_only"),
    "send_kind": (
        "md_brief",
        "operator_copy",
        "needs_review",
        "blocked_notice",
        "no_signal",
        "run_failure",
    ),
    "send_status": ("sent", "failed", "dry_run", "skipped"),
    "alumni_tier": ("strict", "medium"),
    "blocklist_status": ("active", "closed_lost", "cooling"),
    "sponsor_level": (
        "championship_title",
        "championship_global",
        "championship_official",
        "race_title",
        "team_title",
        "team_major",
        "team_other",
        "powertrain",
    ),
    "sponsor_status": ("active", "joined", "departed", "unverified"),
    "event_status": ("confirmed", "provisional", "cancelled"),
    "brief_action": ("pursuing", "snoozed", "killed", "contacted"),
}


def _pg(name: str) -> postgresql.ENUM:
    """Reference an enum type created earlier in this migration (no re-create)."""
    return postgresql.ENUM(*ENUMS[name], name=name, create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    for name, values in ENUMS.items():
        _e(name, *values).create(bind, checkfirst=True)

    op.execute(sa.schema.CreateSequence(sa.Sequence("brief_number_seq", start=1)))

    ts = sa.DateTime(timezone=True)
    now = sa.text("now()")

    op.create_table(
        "runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_date", sa.Date(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("started_at", ts, nullable=False, server_default=now),
        sa.Column("finished_at", ts),
        sa.Column("status", _pg("run_status"), nullable=False, server_default="running"),
        sa.Column("execution_mode", _pg("execution_mode"), nullable=False, server_default="shadow"),
        sa.Column("model_versions", postgresql.JSONB()),
        sa.Column("error", sa.Text()),
        sa.Column("summary", postgresql.JSONB()),
        sa.UniqueConstraint("run_date", "attempt", name="uq_runs_date_attempt"),
    )
    op.create_index("ix_runs_run_date", "runs", ["run_date"])

    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "run_id", sa.Integer(), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("rank", sa.Integer()),
        sa.Column("company_raw", sa.Text(), nullable=False),
        sa.Column("company_norm", sa.Text(), nullable=False),
        sa.Column("track", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("series", _pg("series")),
        sa.Column("trigger_reason_raw", sa.Text()),
        sa.Column("trigger_reason_norm", sa.Text()),
        sa.Column("trigger_date", sa.Date()),
        sa.Column("source_url", sa.Text()),
        sa.Column("source_tier", sa.SmallInteger()),
        sa.Column("raw_json", postgresql.JSONB(), nullable=False),
        sa.Column("gate_results", postgresql.JSONB()),
        sa.Column("score_total", sa.Integer()),
        sa.Column("score_breakdown", postgresql.JSONB()),
        sa.Column("alumni_boost", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tier", sa.String(32)),
        sa.Column("recommended_team", sa.Text()),
        sa.Column("decision", _pg("candidate_decision"), nullable=False, server_default="pending"),
        sa.Column("decision_reason", sa.Text()),
        sa.Column("resurfaced", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", ts, nullable=False, server_default=now),
    )
    op.create_index("ix_candidates_run_id", "candidates", ["run_id"])
    op.create_index("ix_candidates_company_norm", "candidates", ["company_norm"])
    op.create_index("ix_candidates_trigger_reason_norm", "candidates", ["trigger_reason_norm"])

    op.create_table(
        "briefs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_id",
            sa.Integer(),
            sa.ForeignKey("candidates.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column("run_date", sa.Date(), nullable=False),
        sa.Column(
            "brief_number",
            sa.Integer(),
            nullable=False,
            unique=True,
            server_default=sa.text("nextval('brief_number_seq')"),
        ),
        sa.Column("brief_data", postgresql.JSONB()),
        sa.Column("mode", _pg("value_mode")),
        sa.Column("audit_status", _pg("audit_status"), nullable=False, server_default="pending"),
        sa.Column("audit_violations", postgresql.JSONB()),
        sa.Column("audit_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "verification_status",
            _pg("verification_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("pdf_path", sa.Text()),
        sa.Column("html_path", sa.Text()),
        sa.Column("page_count", sa.Integer()),
        sa.Column("historical", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", ts, nullable=False, server_default=now),
    )
    op.create_index("ix_briefs_run_date", "briefs", ["run_date"])
    op.create_index(
        "uq_briefs_issued_per_day",
        "briefs",
        ["run_date"],
        unique=True,
        postgresql_where=sa.text("verification_status <> 'blocked'"),
    )

    op.create_table(
        "claims",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "brief_id", sa.Integer(), sa.ForeignKey("briefs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("section", sa.String(64), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("claim_type", _pg("claim_type"), nullable=False),
        sa.Column("load_bearing", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("cited_source_url", sa.Text()),
        sa.Column("created_at", ts, nullable=False, server_default=now),
    )
    op.create_index("ix_claims_brief_id", "claims", ["brief_id"])

    op.create_table(
        "verifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "claim_id", sa.Integer(), sa.ForeignKey("claims.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("status", _pg("verification_result"), nullable=False),
        sa.Column("method", _pg("verification_method"), nullable=False),
        sa.Column("evidence_url", sa.Text()),
        sa.Column("evidence_excerpt", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("model", sa.String(64)),
        sa.Column("checked_at", ts, nullable=False, server_default=now),
    )
    op.create_index("ix_verifications_claim_id", "verifications", ["claim_id"])

    op.create_table(
        "sends",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("brief_id", sa.Integer(), sa.ForeignKey("briefs.id", ondelete="SET NULL")),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("runs.id", ondelete="SET NULL")),
        sa.Column("recipient", sa.Text(), nullable=False),
        sa.Column("channel", _pg("send_channel"), nullable=False),
        sa.Column("kind", _pg("send_kind"), nullable=False),
        sa.Column("subject", sa.Text()),
        sa.Column("sent_at", ts),
        sa.Column("message_id", sa.Text()),
        sa.Column("status", _pg("send_status"), nullable=False),
        sa.Column("error", sa.Text()),
        sa.UniqueConstraint("brief_id", "recipient", "kind", name="uq_sends_brief_recipient_kind"),
        sa.UniqueConstraint("run_id", "recipient", "kind", name="uq_sends_run_recipient_kind"),
    )
    op.create_index("ix_sends_brief_id", "sends", ["brief_id"])
    op.create_index("ix_sends_run_id", "sends", ["run_id"])

    op.create_table(
        "surfaced_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_norm", sa.Text(), nullable=False),
        sa.Column("trigger_reason_norm", sa.Text(), nullable=False),
        sa.Column("company_display", sa.Text()),
        sa.Column("first_surfaced_at", ts, nullable=False, server_default=now),
        sa.Column("last_surfaced_at", ts, nullable=False, server_default=now),
        sa.Column("times_surfaced", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("brief_id", sa.Integer(), sa.ForeignKey("briefs.id", ondelete="SET NULL")),
        sa.UniqueConstraint(
            "company_norm", "trigger_reason_norm", name="uq_surfaced_company_trigger"
        ),
    )
    op.create_index("ix_surfaced_log_company_norm", "surfaced_log", ["company_norm"])

    op.create_table(
        "alumni",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("previous_role", sa.Text()),
        sa.Column("previous_company", sa.Text()),
        sa.Column("deal_involvement", sa.Text()),
        sa.Column("current_role", sa.Text()),
        sa.Column("current_company", sa.Text()),
        sa.Column("company_norm", sa.Text()),
        sa.Column("move_date", sa.Date()),
        sa.Column("tier", _pg("alumni_tier"), nullable=False),
        sa.Column("boost_applied", sa.Integer()),
        sa.Column("base_score", sa.Integer()),
        sa.Column("final_score", sa.Integer()),
        sa.Column("complications", sa.Text()),
        sa.Column("verification", sa.Text()),
        sa.Column("outreach_status", sa.Text()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.Text()),
        sa.Column("updated_at", ts, nullable=False, server_default=now),
    )
    op.create_index("ix_alumni_company_norm", "alumni", ["company_norm"])

    op.create_table(
        "blocklist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_raw", sa.Text(), nullable=False),
        sa.Column("company_norm", sa.Text(), nullable=False, unique=True),
        sa.Column("status", _pg("blocklist_status"), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("added_at", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("cooling_until", sa.Date()),
        sa.Column("added_by", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("updated_at", ts, nullable=False, server_default=now),
    )

    op.create_table(
        "sponsors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("series", _pg("series"), nullable=False),
        sa.Column("level", _pg("sponsor_level"), nullable=False),
        sa.Column("team", sa.Text()),
        sa.Column("brand", sa.Text(), nullable=False),
        sa.Column("brand_norm", sa.Text(), nullable=False),
        sa.Column("category", sa.Text()),
        sa.Column("status", _pg("sponsor_status"), nullable=False),
        sa.Column("season", sa.String(16)),
        sa.Column("notes", sa.Text()),
        sa.Column("source", sa.Text()),
        sa.Column("verified_at", sa.Date()),
        sa.Column("updated_at", ts, nullable=False, server_default=now),
    )
    op.create_index("ix_sponsors_brand_norm", "sponsors", ["brand_norm"])
    op.create_index("ix_sponsors_series_team_brand", "sponsors", ["series", "team", "brand_norm"])

    op.create_table(
        "calendar_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("series", _pg("series"), nullable=False),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("city", sa.Text()),
        sa.Column("country", sa.Text()),
        sa.Column("date_start", sa.Date()),
        sa.Column("date_end", sa.Date()),
        sa.Column("title_sponsor", sa.Text()),
        sa.Column("status", _pg("event_status"), nullable=False),
        sa.Column("source", sa.Text()),
        sa.Column("verified_at", sa.Date()),
        sa.UniqueConstraint("series", "season", "round", name="uq_calendar_series_season_round"),
    )

    op.create_table(
        "brief_actions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "brief_id", sa.Integer(), sa.ForeignKey("briefs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("action", _pg("brief_action"), nullable=False),
        sa.Column("by", sa.Text(), nullable=False),
        sa.Column("at", ts, nullable=False, server_default=now),
        sa.Column("note", sa.Text()),
    )
    op.create_index("ix_brief_actions_brief_id", "brief_actions", ["brief_id"])

    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("person_name", sa.Text(), nullable=False),
        sa.Column("title", sa.Text()),
        sa.Column("company_norm", sa.Text(), nullable=False),
        sa.Column("linkedin_url", sa.Text()),
        sa.Column("email", sa.Text()),
        sa.Column("phone", sa.Text()),
        sa.Column("source_provider", sa.Text()),
        sa.Column("provider_record_id", sa.Text()),
        sa.Column("retrieved_at", ts),
        sa.Column("role_verified_at", ts),
        sa.Column(
            "role_verification_id",
            sa.Integer(),
            sa.ForeignKey("verifications.id", ondelete="SET NULL"),
        ),
        sa.Column(
            "consent_basis", sa.Text(), nullable=False, server_default="b2b_legitimate_interest"
        ),
        sa.Column("opted_out", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", ts, nullable=False, server_default=now),
    )
    op.create_index("ix_contacts_company_norm", "contacts", ["company_norm"])

    op.create_table(
        "outreach_drafts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "brief_id", sa.Integer(), sa.ForeignKey("briefs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("contact_id", sa.Integer(), sa.ForeignKey("contacts.id", ondelete="SET NULL")),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", ts, nullable=False, server_default=now),
        sa.Column("outlook_draft_id", sa.Text()),
    )
    op.create_index("ix_outreach_drafts_brief_id", "outreach_drafts", ["brief_id"])

    op.create_table(
        "highlights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "brief_id", sa.Integer(), sa.ForeignKey("briefs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("generated_at", ts, nullable=False, server_default=now),
        sa.Column("claim_ids", postgresql.JSONB(), nullable=False, server_default="[]"),
    )
    op.create_index("ix_highlights_brief_id", "highlights", ["brief_id"])


def downgrade() -> None:
    for table in (
        "highlights",
        "outreach_drafts",
        "contacts",
        "brief_actions",
        "calendar_events",
        "sponsors",
        "blocklist",
        "alumni",
        "surfaced_log",
        "sends",
        "verifications",
        "claims",
        "briefs",
        "candidates",
        "runs",
    ):
        op.drop_table(table)
    op.execute(sa.schema.DropSequence(sa.Sequence("brief_number_seq")))
    bind = op.get_bind()
    for name in ENUMS:
        sa.Enum(name=name).drop(bind, checkfirst=True)
