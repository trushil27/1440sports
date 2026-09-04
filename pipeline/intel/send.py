"""Distribution (build brief §7) and the Microsoft Graph mailer (§4, §11.2).

Rules, enforced here and by the ``sends`` table's unique constraints:
- The MD receives an email ONLY for a brief that is ``verified`` AND audit pass /
  pass_after_retry — and only in ``production`` mode. In ``shadow`` mode the same email
  goes to the operator alone (subject prefixed [SHADOW]).
- The operator receives everything: the MD copy (cc), needs-review briefs (footer
  "VERIFY BEFORE CIRCULATION"), blocked notices with the failing claim, run failures,
  and the "no verified signal today" note.
- A brief is never sent twice for the same (brief, recipient, kind); ``message_id`` is
  recorded on every send.

Mailer implementations:
- ``GraphMailer`` — Entra app registration with Mail.Send application permission
  (client-credentials), or delegated auth with a stored refresh token (same interface);
  creates a draft message then sends it so the ``internetMessageId`` can be recorded.
- ``DryRunMailer`` — writes an .eml per message to ``outbox_dir``; used when no Graph
  credentials are configured or ``execution_mode`` is ``dry_run``.
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import uuid
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Protocol

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.brief_data import strip_markup
from intel.config import Settings, get_settings
from intel.models import (
    AuditStatus,
    Brief,
    Candidate,
    CandidateDecision,
    Run,
    Send,
    SendChannel,
    SendKind,
    SendStatus,
    VerificationResult,
    VerificationStatus,
)

GRAPH = "https://graph.microsoft.com/v1.0"
LOGIN = "https://login.microsoftonline.com"


@dataclass
class Attachment:
    name: str
    content: bytes
    content_type: str = "application/pdf"


@dataclass
class Outgoing:
    to: list[str]
    subject: str
    body_text: str
    cc: list[str] = field(default_factory=list)
    body_html: str | None = None
    attachments: list[Attachment] = field(default_factory=list)


class Mailer(Protocol):
    channel: SendChannel

    def send(self, msg: Outgoing) -> str:
        """Send and return a message id."""
        ...

    def create_draft(self, msg: Outgoing) -> str:
        """Create a Draft in the sender's mailbox WITHOUT sending; return its id (§8 outreach)."""
        ...


class DryRunMailer:
    channel = SendChannel.app_only

    def __init__(self, outbox: Path) -> None:
        self.outbox = outbox
        self.sent: list[Outgoing] = []

    def send(self, msg: Outgoing) -> str:
        self.outbox.mkdir(parents=True, exist_ok=True)
        mid = f"dryrun-{uuid.uuid4()}"
        em = EmailMessage()
        em["To"] = ", ".join(msg.to)
        if msg.cc:
            em["Cc"] = ", ".join(msg.cc)
        em["Subject"] = msg.subject
        em["Message-ID"] = f"<{mid}@1440.local>"
        em.set_content(msg.body_text)
        for a in msg.attachments:
            main, _, sub = a.content_type.partition("/")
            em.add_attachment(
                a.content, maintype=main, subtype=sub or "octet-stream", filename=a.name
            )
        (self.outbox / f"{mid}.eml").write_bytes(bytes(em))
        self.sent.append(msg)
        return mid

    def create_draft(self, msg: Outgoing) -> str:
        (self.outbox / "drafts").mkdir(parents=True, exist_ok=True)
        did = f"dryrun-draft-{uuid.uuid4()}"
        em = EmailMessage()
        em["To"] = ", ".join(msg.to)
        em["Subject"] = msg.subject
        em.set_content(msg.body_text)
        (self.outbox / "drafts" / f"{did}.eml").write_bytes(bytes(em))
        return did


class GraphMailer:
    channel = SendChannel.outlook

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str | None,
        sender: str,
        refresh_token: str | None = None,
        http: httpx.Client | None = None,
    ) -> None:
        self.tenant_id, self.client_id, self.client_secret = tenant_id, client_id, client_secret
        self.sender, self.refresh_token = sender, refresh_token
        self.http = http or httpx.Client(timeout=60)
        self._token: str | None = None
        self._token_expiry = 0.0

    # --- auth -------------------------------------------------------------------------
    def token(self) -> str:
        import time

        if self._token and time.time() < self._token_expiry - 60:
            return self._token
        url = f"{LOGIN}/{self.tenant_id}/oauth2/v2.0/token"
        if self.refresh_token:  # delegated fallback (§11.2)
            data = {
                "client_id": self.client_id,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "scope": "https://graph.microsoft.com/Mail.Send offline_access",
            }
            if self.client_secret:
                data["client_secret"] = self.client_secret
        else:  # application permission (Mail.Send, admin consent)
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret or "",
                "grant_type": "client_credentials",
                "scope": "https://graph.microsoft.com/.default",
            }
        r = self.http.post(url, data=data)
        r.raise_for_status()
        payload = r.json()
        self._token = payload["access_token"]
        self._token_expiry = time.time() + float(payload.get("expires_in", 3600))
        return self._token

    # --- send -------------------------------------------------------------------------
    def _message(self, msg: Outgoing) -> dict[str, Any]:
        return {
            "subject": msg.subject,
            "body": {
                "contentType": "HTML" if msg.body_html else "Text",
                "content": msg.body_html or msg.body_text,
            },
            "toRecipients": [{"emailAddress": {"address": a}} for a in msg.to],
            "ccRecipients": [{"emailAddress": {"address": a}} for a in msg.cc],
            "attachments": [
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": a.name,
                    "contentType": a.content_type,
                    "contentBytes": base64.b64encode(a.content).decode("ascii"),
                }
                for a in msg.attachments
            ],
        }

    def _base(self) -> str:
        return f"{GRAPH}/users/{self.sender}" if not self.refresh_token else f"{GRAPH}/me"

    def create_draft(self, msg: Outgoing) -> str:
        """POST /messages only — the draft sits in the mailbox; nothing is sent."""
        headers = {"Authorization": f"Bearer {self.token()}", "Content-Type": "application/json"}
        created = self.http.post(
            f"{self._base()}/messages", headers=headers, content=json.dumps(self._message(msg))
        )
        created.raise_for_status()
        return created.json()["id"]

    def send(self, msg: Outgoing) -> str:
        headers = {"Authorization": f"Bearer {self.token()}", "Content-Type": "application/json"}
        base = self._base()
        created = self.http.post(
            f"{base}/messages", headers=headers, content=json.dumps(self._message(msg))
        )
        created.raise_for_status()
        draft = created.json()
        sent = self.http.post(f"{base}/messages/{draft['id']}/send", headers=headers)
        sent.raise_for_status()
        return draft.get("internetMessageId") or draft["id"]


def mailer_for(settings: Settings | None = None) -> Mailer:
    settings = settings or get_settings()
    creds = settings.graph_tenant_id and settings.graph_client_id and settings.graph_sender
    if settings.execution_mode == "dry_run" or not creds:
        return DryRunMailer(Path(settings.outbox_dir))
    return GraphMailer(
        settings.graph_tenant_id,  # type: ignore[arg-type]
        settings.graph_client_id,  # type: ignore[arg-type]
        settings.graph_client_secret,
        settings.graph_sender,  # type: ignore[arg-type]
        refresh_token=settings.graph_refresh_token,
    )


# --- message composition ------------------------------------------------------------------


def _md_eligible(brief: Brief) -> bool:
    return brief.verification_status == VerificationStatus.verified and brief.audit_status in (
        AuditStatus.passed,
        AuditStatus.pass_after_retry,
    )


def md_subject(brief: Brief) -> str:
    d = brief.brief_data or {}
    company, score = d.get("company", "?"), d.get("score", "?")
    return f"1440 Intelligence Brief N° {brief.brief_number:03d} — {company} — {score}/100"


def executive_take(brief: Brief, settings: Settings) -> str:
    """Three-line executive take + link (§7)."""
    d = brief.brief_data or {}
    lines = [
        strip_markup(d.get("deck", "")),
        strip_markup(d.get("bottom_line", "")),
        f"Decision-maker: {d.get('decision_maker_name', '?')}, {d.get('decision_maker_role', '?')}",
        "",
        f"Open in the app: {settings.app_base_url}/brief/{brief.brief_number}",
        "",
        "PDF attached.",
        "— 1440 Intelligence Engine",
    ]
    return "\n".join(lines)


def _ledger_summary(brief: Brief) -> str:
    rows = []
    for c in brief.claims:
        if not c.load_bearing or not c.verifications:
            continue
        v = sorted(c.verifications, key=lambda x: (x.checked_at, x.id))[-1]
        if v.status != VerificationResult.verified:
            rows.append(f"- [{v.status.value}] {c.text}" + (f" — {v.notes}" if v.notes else ""))
    return "\n".join(rows) or "- (no open claims)"


def _audit_summary(brief: Brief) -> str:
    vs = brief.audit_violations or []
    if not vs:
        return "- none"
    return "\n".join(
        f"- rule {v.get('rule')} {v.get('code', '')}: {v.get('message') or v.get('note', '')}"
        for v in vs
    )


def _attachment(brief: Brief) -> list[Attachment]:
    if brief.pdf_path and Path(brief.pdf_path).exists():
        d = brief.brief_data or {}
        name = f"1440_Intelligence_Brief_{d.get('company', 'brief').replace(' ', '_')}.pdf"
        return [Attachment(name, Path(brief.pdf_path).read_bytes())]
    return []


# --- recording ----------------------------------------------------------------------------


def _already_sent(
    session: Session, *, brief_id: int | None, run_id: int | None, recipient: str, kind: SendKind
) -> bool:
    q = select(Send).where(Send.recipient == recipient, Send.kind == kind)
    q = (
        q.where(Send.brief_id == brief_id)
        if brief_id is not None
        else q.where(Send.run_id == run_id)
    )
    row = session.scalar(q)
    return row is not None and row.status in (SendStatus.sent, SendStatus.dry_run)


def _record(
    session: Session,
    *,
    brief_id: int | None,
    run_id: int | None,
    recipient: str,
    kind: SendKind,
    channel: SendChannel,
    subject: str,
    message_id: str | None,
    status: SendStatus,
    error: str | None = None,
) -> Send:
    row = Send(
        brief_id=brief_id,
        run_id=run_id,
        recipient=recipient,
        channel=channel,
        kind=kind,
        subject=subject,
        sent_at=dt.datetime.now(dt.UTC),
        message_id=message_id,
        status=status,
        error=error,
    )
    session.add(row)
    session.flush()
    return row


def _deliver(
    session: Session,
    mailer: Mailer,
    msg: Outgoing,
    *,
    brief_id: int | None,
    run_id: int | None,
    kinds: list[tuple[str, SendKind]],
) -> list[Send]:
    """One email, one Send row per (recipient, kind). Skips entirely if any is already sent."""
    if any(
        _already_sent(session, brief_id=brief_id, run_id=run_id, recipient=r, kind=k)
        for r, k in kinds
    ):
        return []
    status = SendStatus.dry_run if isinstance(mailer, DryRunMailer) else SendStatus.sent
    try:
        mid = mailer.send(msg)
        error = None
    except Exception as exc:  # network / Graph errors are recorded, never lost
        mid, status, error = None, SendStatus.failed, f"{type(exc).__name__}: {exc}"
    return [
        _record(
            session,
            brief_id=brief_id,
            run_id=run_id,
            recipient=r,
            kind=k,
            channel=mailer.channel,
            subject=msg.subject,
            message_id=mid,
            status=status,
            error=error,
        )
        for r, k in kinds
    ]


# --- distribution --------------------------------------------------------------------------


def distribute(
    session: Session,
    run: Run,
    settings: Settings,
    mailer: Mailer,
    issued_brief: Brief | None,
) -> list[Send]:
    """Apply §7 for one completed run. Returns the Send rows created."""
    op = settings.operator_email
    md = settings.md_email
    out: list[Send] = []
    if not op:
        return out  # nothing can be sent without an operator address; the DB still has everything

    # Blocked briefs this run → operator notices with the failing claim(s).
    blocked = session.scalars(
        select(Brief)
        .join(Candidate, Candidate.id == Brief.candidate_id)
        .where(Candidate.run_id == run.id, Brief.verification_status == VerificationStatus.blocked)
    ).all()
    for b in blocked:
        company = b.candidate.company_raw
        msg = Outgoing(
            to=[op],
            subject=f"[BLOCKED] 1440 Intelligence — {company} — {run.run_date:%-d %b %Y}",
            body_text=(
                f"Brief for {company} was BLOCKED before any send "
                "(contradicted load-bearing claim).\n\n"
                f"Claims:\n{_ledger_summary(b)}\n\nBrief id {b.id}, run {run.id}."
            ),
        )
        out += _deliver(
            session, mailer, msg, brief_id=b.id, run_id=None, kinds=[(op, SendKind.blocked_notice)]
        )

    if run.status.value == "failed":
        msg = Outgoing(
            to=[op],
            subject=f"[RUN FAILED] 1440 Intelligence — {run.run_date:%-d %b %Y}",
            body_text=(
                f"The daily run failed (attempt {run.attempt}).\n\n{run.error}\n\nRun id {run.id}."
            ),
        )
        return out + _deliver(
            session, mailer, msg, brief_id=None, run_id=run.id, kinds=[(op, SendKind.run_failure)]
        )

    if issued_brief is None:
        decisions = (run.summary or {}).get("decisions", {})
        msg = Outgoing(
            to=[op],
            subject=f"[NO SIGNAL] 1440 Intelligence — {run.run_date:%-d %b %Y}",
            body_text=(
                "No verified signal today. The MD has NOT been emailed.\n\n"
                f"Candidates: {(run.summary or {}).get('candidates', 0)}; "
                f"decisions: {json.dumps(decisions)}\n"
                f"Run id {run.id}."
            ),
        )
        return out + _deliver(
            session, mailer, msg, brief_id=None, run_id=run.id, kinds=[(op, SendKind.no_signal)]
        )

    brief = issued_brief
    if _md_eligible(brief):
        msg = Outgoing(
            to=[md] if (md and settings.execution_mode == "production") else [op],
            cc=[op] if (md and settings.execution_mode == "production") else [],
            subject=("" if settings.execution_mode == "production" else "[SHADOW] ")
            + md_subject(brief),
            body_text=executive_take(brief, settings),
            attachments=_attachment(brief),
        )
        if md and settings.execution_mode == "production":
            kinds = [(md, SendKind.md_brief), (op, SendKind.operator_copy)]
        else:
            kinds = [(op, SendKind.operator_copy)]
        return out + _deliver(session, mailer, msg, brief_id=brief.id, run_id=None, kinds=kinds)

    # needs_review, or audit failed / pending: operator only, never the MD.
    reason = (
        "VERIFY BEFORE CIRCULATION"
        if brief.verification_status == VerificationStatus.needs_review
        else f"audit {brief.audit_status.value}"
    )
    msg = Outgoing(
        to=[op],
        subject=f"[REVIEW] {md_subject(brief)} — {reason}",
        body_text=(
            f"{executive_take(brief, settings)}\n\n"
            f"Verification: {brief.verification_status.value}\n"
            f"Open claims:\n{_ledger_summary(brief)}\n\n"
            f"Audit: {brief.audit_status.value} ({brief.audit_attempts} attempt(s))\n"
            f"{_audit_summary(brief)}\n\n"
            "The MD has NOT been emailed."
        ),
        attachments=_attachment(brief),
    )
    return out + _deliver(
        session, mailer, msg, brief_id=brief.id, run_id=None, kinds=[(op, SendKind.needs_review)]
    )


def candidate_reasons(run: Run) -> list[dict]:
    """Why each candidate was or wasn't chosen — for the ops view and operator emails."""
    return [
        {
            "rank": c.rank,
            "company": c.company_raw,
            "score": c.score_total,
            "decision": c.decision.value,
            "reason": c.decision_reason,
        }
        for c in sorted(run.candidates, key=lambda c: c.rank or 0)
        if c.decision != CandidateDecision.pending
    ]
