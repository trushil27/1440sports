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


def message_for(brief: Brief, settings: Settings) -> Outgoing:
    """The same email the daily job sends, addressed to the operator only — with the
    verify-before-circulation panel when the brief is not yet MD-eligible, and through the
    same format guard."""
    from intel.models import AuditStatus, VerificationStatus
    from intel.send import guarded

    review = brief.verification_status != VerificationStatus.verified or brief.audit_status not in (
        AuditStatus.passed,
        AuditStatus.pass_after_retry,
    )
    subject = md_subject(brief)
    if review:
        subject = f"[REVIEW] {subject}"
    return guarded(
        Outgoing(
            to=[settings.operator_email or ""],
            subject=subject,
            body_text=executive_take(brief, settings),
            body_html=brief_body_html(brief, settings, review=review),
            attachments=_attachment(brief),
        ),
        settings,
    )


def resend(session: Session, number: int, settings: Settings, mailer) -> str:
    brief = brief_by_number(session, number)
    if brief is None:
        raise LookupError(f"no brief numbered {number} in the desk's memory")
    if not settings.operator_email:
        raise RuntimeError("OPERATOR_EMAIL is not set — there is nowhere to send it")
    msg = message_for(brief, settings)
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
            Send.kind == SendKind.operator_copy,
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
            kind=SendKind.operator_copy,
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
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    settings = get_settings()
    if args.dry_run:
        settings = settings.model_copy(update={"execution_mode": "dry_run"})
    mailer = mailer_for(settings)
    failed = 0
    with session_scope(settings.database_url) as session:
        for number in args.numbers:
            try:
                print(resend(session, number, settings, mailer))
            except (LookupError, RuntimeError) as exc:
                print(f"N° {number}: {exc}", file=sys.stderr)
                failed += 1
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
