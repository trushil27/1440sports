"""ORM models — the data model from the build brief §5.

Structural guarantees live HERE, not in prompts:
- ``surfaced_log`` is UNIQUE on (company_norm, trigger_reason_norm): the dedup rule.
- ``briefs.brief_number`` comes from a Postgres SEQUENCE: never reused, even on rollback.
- one non-blocked brief per run_date (partial unique index): idempotency per day.
- ``sends`` is UNIQUE on (brief_id, recipient, kind): never send a brief twice.
"""

from __future__ import annotations

import datetime as dt
import enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

BRIEF_NUMBER_SEQ = "brief_number_seq"


class Base(DeclarativeBase):
    pass


# --- enums (names are the Postgres type names; keep in sync with db/versions) ---------


class RunStatus(enum.StrEnum):
    running = "running"
    success = "success"
    no_signal = "no_signal"
    failed = "failed"


class ExecutionMode(enum.StrEnum):
    production = "production"
    shadow = "shadow"
    dry_run = "dry_run"


class Series(enum.StrEnum):
    F1 = "F1"
    FE = "FE"


class CandidateDecision(enum.StrEnum):
    pending = "pending"
    selected = "selected"
    not_selected = "not_selected"
    dedup_suppressed = "dedup_suppressed"
    stale = "stale"
    blocklisted = "blocklisted"
    gate_failed = "gate_failed"
    below_threshold = "below_threshold"
    verification_blocked = "verification_blocked"


class AuditStatus(enum.StrEnum):
    pending = "pending"
    passed = "pass"
    pass_after_retry = "pass_after_retry"
    failed = "failed"


class VerificationStatus(enum.StrEnum):
    pending = "pending"
    verified = "verified"
    needs_review = "needs_review"
    blocked = "blocked"


class ValueMode(enum.StrEnum):
    A = "A"
    B = "B"
    C = "C"


class ClaimType(enum.StrEnum):
    funding = "funding"
    person_role = "person_role"
    sponsorship = "sponsorship"
    event = "event"
    revenue = "revenue"
    date = "date"
    other = "other"


class VerificationResult(enum.StrEnum):
    verified = "verified"
    unverified = "unverified"
    contradicted = "contradicted"


class VerificationMethod(enum.StrEnum):
    llm_source_fetch = "llm_source_fetch"
    sponsor_db = "sponsor_db"
    calendar = "calendar"
    manual = "manual"


class SendChannel(enum.StrEnum):
    outlook = "outlook"
    app_only = "app_only"


class SendKind(enum.StrEnum):
    md_brief = "md_brief"
    operator_copy = "operator_copy"
    needs_review = "needs_review"
    blocked_notice = "blocked_notice"
    no_signal = "no_signal"
    run_failure = "run_failure"


class SendStatus(enum.StrEnum):
    sent = "sent"
    failed = "failed"
    dry_run = "dry_run"
    skipped = "skipped"


class AlumniTier(enum.StrEnum):
    strict = "strict"
    medium = "medium"


class BlocklistStatus(enum.StrEnum):
    active = "active"
    closed_lost = "closed_lost"
    cooling = "cooling"


class SponsorLevel(enum.StrEnum):
    championship_title = "championship_title"
    championship_global = "championship_global"
    championship_official = "championship_official"
    race_title = "race_title"
    team_title = "team_title"
    team_major = "team_major"
    team_other = "team_other"
    powertrain = "powertrain"


class SponsorStatus(enum.StrEnum):
    active = "active"
    joined = "joined"
    departed = "departed"
    unverified = "unverified"


class EventStatus(enum.StrEnum):
    confirmed = "confirmed"
    provisional = "provisional"
    cancelled = "cancelled"


class BriefAction(enum.StrEnum):
    pursuing = "pursuing"
    snoozed = "snoozed"
    killed = "killed"
    contacted = "contacted"


def _enum(e: type[enum.Enum], name: str) -> Enum:
    return Enum(e, name=name, values_callable=lambda x: [m.value for m in x])


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


# --- pipeline tables -----------------------------------------------------------------


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (UniqueConstraint("run_date", "attempt", name="uq_runs_date_attempt"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_date: Mapped[dt.date] = mapped_column(Date, nullable=False, index=True)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    started_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[RunStatus] = mapped_column(
        _enum(RunStatus, "run_status"), default=RunStatus.running
    )
    execution_mode: Mapped[ExecutionMode] = mapped_column(
        _enum(ExecutionMode, "execution_mode"), default=ExecutionMode.shadow
    )
    model_versions: Mapped[dict | None] = mapped_column(JSONB)
    error: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[dict | None] = mapped_column(JSONB)

    candidates: Mapped[list[Candidate]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rank: Mapped[int | None] = mapped_column(Integer)
    company_raw: Mapped[str] = mapped_column(Text, nullable=False)
    company_norm: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    track: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    series: Mapped[Series | None] = mapped_column(_enum(Series, "series"))
    trigger_reason_raw: Mapped[str | None] = mapped_column(Text)
    trigger_reason_norm: Mapped[str | None] = mapped_column(Text, index=True)
    trigger_date: Mapped[dt.date | None] = mapped_column(Date)
    source_url: Mapped[str | None] = mapped_column(Text)
    source_tier: Mapped[int | None] = mapped_column(SmallInteger)
    raw_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    gate_results: Mapped[dict | None] = mapped_column(JSONB)
    score_total: Mapped[int | None] = mapped_column(Integer)
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB)
    alumni_boost: Mapped[int] = mapped_column(Integer, default=0)
    tier: Mapped[str | None] = mapped_column(String(32))
    recommended_team: Mapped[str | None] = mapped_column(Text)
    decision: Mapped[CandidateDecision] = mapped_column(
        _enum(CandidateDecision, "candidate_decision"), default=CandidateDecision.pending
    )
    decision_reason: Mapped[str | None] = mapped_column(Text)
    resurfaced: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    run: Mapped[Run] = relationship(back_populates="candidates")
    brief: Mapped[Brief | None] = relationship(back_populates="candidate", uselist=False)


class Brief(Base):
    __tablename__ = "briefs"
    __table_args__ = (
        # Idempotency per day: at most one non-blocked LIVE brief per run_date.
        # Historical imports (M6 backfill) are exempt: the n8n log has several per day.
        Index(
            "uq_briefs_issued_per_day",
            "run_date",
            unique=True,
            postgresql_where=text("verification_status <> 'blocked' AND historical = false"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    run_date: Mapped[dt.date] = mapped_column(Date, nullable=False, index=True)
    brief_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        server_default=text(f"nextval('{BRIEF_NUMBER_SEQ}')"),
    )
    brief_data: Mapped[dict | None] = mapped_column(JSONB)
    mode: Mapped[ValueMode | None] = mapped_column(_enum(ValueMode, "value_mode"))
    audit_status: Mapped[AuditStatus] = mapped_column(
        _enum(AuditStatus, "audit_status"), default=AuditStatus.pending
    )
    audit_violations: Mapped[list | None] = mapped_column(JSONB)
    audit_attempts: Mapped[int] = mapped_column(Integer, default=0)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        _enum(VerificationStatus, "verification_status"), default=VerificationStatus.pending
    )
    pdf_path: Mapped[str | None] = mapped_column(Text)
    html_path: Mapped[str | None] = mapped_column(Text)
    page_count: Mapped[int | None] = mapped_column(Integer)
    historical: Mapped[bool] = mapped_column(Boolean, default=False)  # M6 backfill marker
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    candidate: Mapped[Candidate] = relationship(back_populates="brief")
    claims: Mapped[list[Claim]] = relationship(back_populates="brief", cascade="all, delete-orphan")
    sends: Mapped[list[Send]] = relationship(back_populates="brief")
    actions: Mapped[list[BriefActionLog]] = relationship(back_populates="brief")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brief_id: Mapped[int] = mapped_column(
        ForeignKey("briefs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    section: Mapped[str] = mapped_column(String(64), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[ClaimType] = mapped_column(_enum(ClaimType, "claim_type"), nullable=False)
    load_bearing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cited_source_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    brief: Mapped[Brief] = relationship(back_populates="claims")
    verifications: Mapped[list[Verification]] = relationship(
        back_populates="claim", cascade="all, delete-orphan", foreign_keys="Verification.claim_id"
    )


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[VerificationResult] = mapped_column(
        _enum(VerificationResult, "verification_result"), nullable=False
    )
    method: Mapped[VerificationMethod] = mapped_column(
        _enum(VerificationMethod, "verification_method"), nullable=False
    )
    evidence_url: Mapped[str | None] = mapped_column(Text)
    evidence_excerpt: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(String(64))
    checked_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    claim: Mapped[Claim] = relationship(back_populates="verifications", foreign_keys=[claim_id])


class Send(Base):
    __tablename__ = "sends"
    __table_args__ = (
        UniqueConstraint("brief_id", "recipient", "kind", name="uq_sends_brief_recipient_kind"),
        UniqueConstraint("run_id", "recipient", "kind", name="uq_sends_run_recipient_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brief_id: Mapped[int | None] = mapped_column(
        ForeignKey("briefs.id", ondelete="SET NULL"), index=True
    )
    run_id: Mapped[int | None] = mapped_column(
        ForeignKey("runs.id", ondelete="SET NULL"), index=True
    )
    recipient: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[SendChannel] = mapped_column(_enum(SendChannel, "send_channel"), nullable=False)
    kind: Mapped[SendKind] = mapped_column(_enum(SendKind, "send_kind"), nullable=False)
    subject: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    message_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[SendStatus] = mapped_column(_enum(SendStatus, "send_status"), nullable=False)
    error: Mapped[str | None] = mapped_column(Text)

    brief: Mapped[Brief | None] = relationship(back_populates="sends")


class SurfacedLog(Base):
    __tablename__ = "surfaced_log"
    __table_args__ = (
        UniqueConstraint("company_norm", "trigger_reason_norm", name="uq_surfaced_company_trigger"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_norm: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    trigger_reason_norm: Mapped[str] = mapped_column(Text, nullable=False)
    company_display: Mapped[str | None] = mapped_column(Text)
    first_surfaced_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    last_surfaced_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    times_surfaced: Mapped[int] = mapped_column(Integer, default=1)
    brief_id: Mapped[int | None] = mapped_column(ForeignKey("briefs.id", ondelete="SET NULL"))


# --- reference tables (mirrors of spec/ files; editable in the app) -----------------------


class Alumni(Base):
    __tablename__ = "alumni"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    previous_role: Mapped[str | None] = mapped_column(Text)
    previous_company: Mapped[str | None] = mapped_column(Text)
    deal_involvement: Mapped[str | None] = mapped_column(Text)
    current_role: Mapped[str | None] = mapped_column(Text)
    current_company: Mapped[str | None] = mapped_column(Text)
    company_norm: Mapped[str | None] = mapped_column(Text, index=True)
    move_date: Mapped[dt.date | None] = mapped_column(Date)
    tier: Mapped[AlumniTier] = mapped_column(_enum(AlumniTier, "alumni_tier"), nullable=False)
    boost_applied: Mapped[int | None] = mapped_column(Integer)
    base_score: Mapped[int | None] = mapped_column(Integer)
    final_score: Mapped[int | None] = mapped_column(Integer)
    complications: Mapped[str | None] = mapped_column(Text)
    verification: Mapped[str | None] = mapped_column(Text)
    outreach_status: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class Blocklist(Base):
    __tablename__ = "blocklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_raw: Mapped[str] = mapped_column(Text, nullable=False)
    company_norm: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[BlocklistStatus] = mapped_column(
        _enum(BlocklistStatus, "blocklist_status"), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text)
    added_at: Mapped[dt.date] = mapped_column(Date, nullable=False, default=dt.date.today)
    cooling_until: Mapped[dt.date | None] = mapped_column(Date)
    added_by: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class Sponsor(Base):
    __tablename__ = "sponsors"
    __table_args__ = (Index("ix_sponsors_series_team_brand", "series", "team", "brand_norm"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    series: Mapped[Series] = mapped_column(_enum(Series, "series"), nullable=False)
    level: Mapped[SponsorLevel] = mapped_column(
        _enum(SponsorLevel, "sponsor_level"), nullable=False
    )
    team: Mapped[str | None] = mapped_column(Text)
    brand: Mapped[str] = mapped_column(Text, nullable=False)
    brand_norm: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(Text)
    status: Mapped[SponsorStatus] = mapped_column(
        _enum(SponsorStatus, "sponsor_status"), nullable=False
    )
    season: Mapped[str | None] = mapped_column(String(16))
    notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(Text)
    verified_at: Mapped[dt.date | None] = mapped_column(Date)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class CalendarEvent(Base):
    """Fixed F1/FE race calendar: an event claim not in this table is contradicted (§6.5)."""

    __tablename__ = "calendar_events"
    __table_args__ = (
        UniqueConstraint("series", "season", "round", name="uq_calendar_series_season_round"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    series: Mapped[Series] = mapped_column(_enum(Series, "series"), nullable=False)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(Text)
    date_start: Mapped[dt.date | None] = mapped_column(Date)
    date_end: Mapped[dt.date | None] = mapped_column(Date)
    title_sponsor: Mapped[str | None] = mapped_column(Text)
    status: Mapped[EventStatus] = mapped_column(_enum(EventStatus, "event_status"), nullable=False)
    source: Mapped[str | None] = mapped_column(Text)
    verified_at: Mapped[dt.date | None] = mapped_column(Date)


# --- app-facing tables ------------------------------------------------------------------


class BriefActionLog(Base):
    __tablename__ = "brief_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brief_id: Mapped[int] = mapped_column(
        ForeignKey("briefs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[BriefAction] = mapped_column(_enum(BriefAction, "brief_action"), nullable=False)
    by: Mapped[str] = mapped_column(Text, nullable=False)
    at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    note: Mapped[str | None] = mapped_column(Text)

    brief: Mapped[Brief] = relationship(back_populates="actions")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_name: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(Text)
    company_norm: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(Text)
    source_provider: Mapped[str | None] = mapped_column(Text)
    provider_record_id: Mapped[str | None] = mapped_column(Text)
    retrieved_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    role_verified_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    role_verification_id: Mapped[int | None] = mapped_column(
        ForeignKey("verifications.id", ondelete="SET NULL")
    )
    consent_basis: Mapped[str] = mapped_column(
        Text, nullable=False, default="b2b_legitimate_interest"
    )
    opted_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class OutreachDraft(Base):
    __tablename__ = "outreach_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brief_id: Mapped[int] = mapped_column(
        ForeignKey("briefs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"))
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    outlook_draft_id: Mapped[str | None] = mapped_column(Text)


class Highlight(Base):
    __tablename__ = "highlights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brief_id: Mapped[int] = mapped_column(
        ForeignKey("briefs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    claim_ids: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list
    )  # verified claims only


ALL_ENUM_TYPE_NAMES: tuple[str, ...] = (
    "run_status",
    "execution_mode",
    "series",
    "candidate_decision",
    "audit_status",
    "verification_status",
    "value_mode",
    "claim_type",
    "verification_result",
    "verification_method",
    "send_channel",
    "send_kind",
    "send_status",
    "alumni_tier",
    "blocklist_status",
    "sponsor_level",
    "sponsor_status",
    "event_status",
    "brief_action",
)

__all__ = [name for name in dir() if not name.startswith("_")]
