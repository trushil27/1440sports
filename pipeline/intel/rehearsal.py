"""The morning, rehearsed — on every push, before 05:40 finds out the hard way.

9 Sep 2026: a change to the pool importer broke the memory rebuild that every run does first;
it surfaced when a resend died, and it would have killed the next morning's run before it
scanned anything. This is the check that would have caught it at push time:

1. a throw-away Postgres, migrated and seeded, then the whole repo memory imported —
   history, every recorded case, every pool, the signal checks;
2. the app exported from it;
3. the latest live brief's email composed exactly as the daily job composes it, through the
   format guard — and it must pass.

No model API, no mailbox, no network. Exit 0 means tomorrow's start will get past the parts
this exercise covers; exit 1 names what broke.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


def run(site_dir: str | None = None) -> list[str]:
    from sqlalchemy import select

    from intel import resend, site_export
    from intel.config import Settings
    from intel.db import session_scope
    from intel.models import Brief
    from intel.tempdb import TempCluster, prepare

    problems: list[str] = []
    cluster = TempCluster()
    url = cluster.start()
    try:
        prepare(url)
        out = Path(site_dir or tempfile.mkdtemp(prefix="rehearsal-site-"))
        settings = Settings(
            database_url=url,
            execution_mode="dry_run",
            site_dir=str(out),
            operator_email="rehearsal@1440sports.com",
            app_base_url="https://1440-intelligence.netlify.app",
        )
        published = site_export.publish(settings)
        if not (out / "index.html").exists() or not published.get("briefs"):
            problems.append(f"site export produced nothing usable: {published}")
        with session_scope(url) as session:
            latest = session.scalar(
                select(Brief)
                .where(Brief.historical.is_(False), Brief.brief_number > 0)
                .order_by(Brief.run_date.desc(), Brief.id.desc())
            )
            if latest is None:
                problems.append("no live brief in memory to compose an email from")
            else:
                msg = resend.message_for(latest, settings)
                if msg.subject.startswith("[FORMAT GUARD]"):
                    head = msg.body_text.split("\n\n", 1)[0]
                    problems.append(f"latest brief N° {latest.brief_number}: {head}")
                if not msg.attachments:
                    problems.append(f"latest brief N° {latest.brief_number}: no PDF attached")
                company = (latest.brief_data or {}).get("company")
                print(
                    f"rehearsal: N° {latest.brief_number} {company} → subject {msg.subject!r}, "
                    f"card {len(msg.body_html or '')} chars, {len(msg.attachments)} attachment(s)"
                )
        briefs, screened = published.get("briefs"), published.get("checked_only")
        print(f"rehearsal: site {briefs} briefs, {screened} screen-outs")
    finally:
        cluster.stop()
    return problems


def main(argv: list[str] | None = None) -> int:
    problems = run((argv or sys.argv[1:])[0] if (argv or sys.argv[1:]) else None)
    for p in problems:
        print(f"REHEARSAL FAILED: {p}")
    print("rehearsal: OK" if not problems else f"rehearsal: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
