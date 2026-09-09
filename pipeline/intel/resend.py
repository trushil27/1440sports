"""Email a brief that already exists — the card body and the 2-page PDF, no model calls.

Every one of the desk's signals carries a full verified case, a 2-page PDF and an app page,
but only the day's hero was ever emailed: the backlog cases were published to the app and
nothing else. So the operator could see N° 241 Nexeon on the site and had never received it
(7 Sep 2026, and fairly raised — "I didn't receive the pdf email and body as discussed").

This sends any brief in the desk's memory, in exactly the format the daily job would have
used, to the operator. It runs the mailer and the renderer only: **no scanner, verifier or
writer, so it costs nothing on the model API.** The MD is never a recipient here.

    python -m intel.resend 241                # one brief by its number
    python -m intel.resend 241 240 --dry-run  # write .eml to the outbox instead of sending
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from intel.config import Settings, get_settings
from intel.db import session_scope
from intel.models import Brief, Send, SendChannel, SendKind, SendStatus
from intel.send import (
    Outgoing,
    _attachment,
    _record,
    brief_body_html,
    executive_take,
    mailer_for,
    md_subject,
)


def brief_by_number(session: Session, number: int) -> Brief | None:
    return session.scalar(
        select(Brief)
        .options(selectinload(Brief.candidate))
        .where(Brief.brief_number == number)
        .order_by(Brief.id.desc())
    )


def resolve_recipient(to: str | None, settings: Settings) -> str:
    """'operator' (default) or 'md' by name, or an address. The MD's address is only ever
    the configured one — never typed into a command by hand."""
    key = (to or "operator").strip().lower()
    if key == "operator":
        if not settings.operator_email:
            raise RuntimeError("OPERATOR_EMAIL is not set — there is nowhere to send it")
        return settings.operator_email
    if key == "md":
        if not settings.md_email:
            raise RuntimeError("MD_EMAIL is not configured for this send")
        return settings.md_email
    if "@" not in key:
        raise RuntimeError(f"unknown recipient {to!r}: use operator, md, or an address")
    return to.strip()


def message_for(
    brief: Brief, settings: Settings, to: str | None = None, cc_operator: bool = False
) -> Outgoing:
    """The same email the daily job sends — the card, the open-points panel when the brief is
    not yet fully verified, the PDF — through the same format guard. Addressed to the
    operator unless told otherwise (operator, 9 Sep 2026: "share that email … to Ricky").
    The open points travel with it whoever the reader is: what is unverified is never
    hidden by changing the audience."""
    from intel.models import AuditStatus, VerificationStatus
    from intel.send import guarded

    review = brief.verification_status != VerificationStatus.verified or brief.audit_status not in (
        AuditStatus.passed,
        AuditStatus.pass_after_retry,
    )
    recipient = resolve_recipient(to, settings)
    subject = md_subject(brief)
    if review and recipient == settings.operator_email:
        subject = f"[REVIEW] {subject}"  # the operator's tag; a reader gets the plain subject
    cc = (
        [settings.operator_email]
        if cc_operator and settings.operator_email and recipient != settings.operator_email
        else []
    )
    return guarded(
        Outgoing(
            to=[recipient],
            cc=cc,
            subject=subject,
            body_text=executive_take(brief, settings),
            body_html=brief_body_html(brief, settings, review=review),
            attachments=_attachment(brief),
        ),
        settings,
    )


def resend(
    session: Session,
    number: int,
    settings: Settings,
    mailer,
    to: str | None = None,
    cc_operator: bool = False,
) -> str:
    brief = brief_by_number(session, number)
    if brief is None:
        raise LookupError(f"no brief numbered {number} in the desk's memory")
    msg = message_for(brief, settings, to=to, cc_operator=cc_operator)
    kind = SendKind.md_brief if msg.to[0] == settings.md_email else SendKind.operator_copy
    # Deliberately NOT going through send._deliver: that skips anything already sent once,
    # which is the right rule for the daily job and the wrong one for an explicit resend.
    message_id = mailer.send(msg)
    status = SendStatus.dry_run if settings.execution_mode == "dry_run" else SendStatus.sent
    # One send row per (brief, recipient, kind) is a database constraint, so a brief that HAS
    # been emailed before updates its row with this delivery rather than adding a second.
    existing = session.scalar(
        select(Send).where(
            Send.brief_id == brief.id,
            Send.recipient == msg.to[0],
            Send.kind == kind,
        )
    )
    if existing is not None:
        existing.sent_at = dt.datetime.now(dt.UTC)
        existing.message_id = message_id
        existing.status = status
        existing.error = None
        session.flush()
    else:
        _record(
            session,
            brief_id=brief.id,
            run_id=None,
            recipient=msg.to[0],
            kind=kind,
            channel=SendChannel.outlook,
            subject=msg.subject,
            message_id=message_id,
            status=status,
        )
    company = (brief.brief_data or {}).get("company") or brief.candidate.company_raw
    return f"N° {number} {company} → {msg.to[0]} ({message_id})"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.resend", description=__doc__)
    parser.add_argument("numbers", nargs="+", type=int, help="brief numbers to send")
    parser.add_argument("--dry-run", action="store_true", help="write .eml to the outbox instead")
    parser.add_argument("--to", default="operator", help="operator (default), md, or an address")
    parser.add_argument(
        "--cc-operator", action="store_true", help="copy the operator when sending elsewhere"
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    settings = get_settings()
    if args.dry_run:
        settings = settings.model_copy(update={"execution_mode": "dry_run"})
    mailer = mailer_for(settings)
    failed = 0
    with session_scope(settings.database_url) as session:
        for number in args.numbers:
            try:
                print(resend(session, number, settings, mailer, args.to, args.cc_operator))
            except (LookupError, RuntimeError) as exc:
                print(f"N° {number}: {exc}", file=sys.stderr)
                failed += 1
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
