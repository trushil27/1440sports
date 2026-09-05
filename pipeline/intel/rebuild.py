"""Rebuild one historical signal as a full, verified case brief (the Crusoe standard).

    python -m intel.rebuild "TDK Corporation" --date 2026-07-18
    python -m intel.rebuild "Sila Nanotechnologies"            # date = today

Runs the whole pipeline for ONE named company: the scanner is pointed at that company only
(``scan.single_company_prompts``), then the same verify → write → audit → render → app-page
stages as the daily job. The brief is issued for ``--date`` (the original signal's date by
default, so it slots into the history where the thin row sat) and gets the next number from
the global sequence. Distribution is off: a rebuild never emails anyone.

The app's "Build the full case" button opens an email to the operator with exactly this
command, because the static site cannot run the models itself.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from typing import Any

from sqlalchemy import select

from intel import run_daily
from intel.config import Settings, get_settings
from intel.db import session_scope
from intel.models import Brief, Candidate
from intel.parse import ParseError, ScannedSignal, parse_scan_output
from intel.scan import (
    WEB_SEARCH_TOOL,
    AnthropicText,
    MessagesClient,
    ScanFailed,
    single_company_prompts,
)


def scan_one(
    company: str,
    today: dt.date,
    client: MessagesClient | None = None,
    settings: Settings | None = None,
    hint: str | None = None,
) -> list[ScannedSignal]:
    settings = settings or get_settings()
    client = client or AnthropicText()
    system, user = single_company_prompts(company, today, hint)
    raw = client.create_text(
        model=settings.scan_model,
        system=system,
        messages=[{"role": "user", "content": user}],
        tools=[WEB_SEARCH_TOOL],
    )
    try:
        signals = parse_scan_output(raw, min_n=1, max_n=1)
    except ParseError as exc:
        raise ScanFailed(
            f"single-company scan for {company!r} unparseable: {exc}", raw=raw
        ) from exc
    return signals


def historical_hint(session, company: str) -> str | None:
    """The thin historical row's own trigger text, so the scanner starts from what we knew."""
    from intel.normalise import company_norm

    row = session.scalar(
        select(Candidate)
        .join(Brief, Brief.candidate_id == Candidate.id)
        .where(Candidate.company_norm == company_norm(company), Brief.historical.is_(True))
        .order_by(Brief.run_date.desc())
    )
    return row.trigger_reason_raw if row else None


def rebuild(
    company: str,
    date: dt.date,
    settings: Settings | None = None,
    client: MessagesClient | None = None,
    stages: run_daily.Stages | None = None,
    session=None,
) -> run_daily.RunOutcome:
    settings = settings or get_settings()
    if session is None:
        with session_scope(settings.database_url) as s:
            return rebuild(company, date, settings, client, stages, s)
    hint = historical_hint(session, company)
    scanner = lambda _d: scan_one(company, date, client, settings, hint)  # noqa: E731
    stages = stages or run_daily.Stages()
    stages.distribute = False
    stages.rebuild = True
    return run_daily.run_day(date, settings, scanner, session, stages=stages)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.rebuild", description=__doc__)
    parser.add_argument("company")
    parser.add_argument("--date", type=dt.date.fromisoformat, default=None)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    settings = get_settings()
    date = args.date or dt.datetime.now(settings.tz).date()
    out = rebuild(args.company, date, settings)
    summary: dict[str, Any] = {
        "status": out.status,
        "brief_id": out.brief_id,
        "verification": out.verification_status,
        "audit": out.audit_status,
        "pdf": out.pdf_path,
        "already_ran": out.already_ran,
    }
    print(json.dumps(summary, indent=1, default=str))
    return 0 if out.status == "success" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
