"""Container preflight: say exactly what is missing before anything can crash.

The daily job's container starts with migrate → seed → run. If ``DATABASE_URL`` is not set
on the Railway service (or the Postgres service is down), Alembic falls back to the
``localhost:5432`` default in ``db/alembic.ini``, fails, and Railway restarts the container
in a loop: the dashboard just says "Crashed". This module runs first and turns that into a
one-line diagnosis in the log plus an email to the operator, with no database needed:

    python -m intel.preflight            # prints the diagnosis; exit 1 if the DB is unreachable
    python -m intel.preflight --alert    # same, and emails the operator; always exits 0

Values are never printed — only whether each variable is set, and the database host.
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from typing import Any
from urllib.parse import urlsplit

from intel.config import Settings, get_settings, normalise_database_url

REQUIRED = ["DATABASE_URL", "ANTHROPIC_API_KEY", "PDF_STORAGE_DIR"]
MAIL = ["OPERATOR_EMAIL", "GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "GRAPH_SENDER"]
MAIL_ONE_OF = ["GRAPH_REFRESH_TOKEN", "GRAPH_CLIENT_SECRET"]
OPTIONAL = ["EXECUTION_MODE", "MD_EMAIL", "GITHUB_TOKEN", "DESK_API_URL", "APP_BASE_URL"]

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", ""}


def _host(url: str | None) -> str | None:
    if not url:
        return None
    try:
        parts = urlsplit(normalise_database_url(url))
    except ValueError:
        return "unparseable"
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    db = parts.path.lstrip("/")
    return f"{host}{port}/{db}" if db else f"{host}{port}"


def check_database(url: str, timeout: int = 5) -> str | None:
    """None when ``SELECT 1`` succeeds, otherwise a one-line reason."""
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(
            normalise_database_url(url),
            pool_pre_ping=False,
            connect_args={"connect_timeout": timeout},
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return None
    except Exception as exc:  # noqa: BLE001 — every failure is a diagnosis, not a crash
        first = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
        return first[:300]


def diagnose(env: dict[str, str] | None = None, probe: bool = True) -> dict[str, Any]:
    env = dict(os.environ if env is None else env)
    present = {k: bool(env.get(k)) for k in REQUIRED + MAIL + MAIL_ONE_OF + OPTIONAL}
    url = env.get("DATABASE_URL") or ""
    host = _host(url)
    problems: list[str] = []
    db_error: str | None = None
    if url and probe:
        db_error = check_database(url)
    if not url:
        problems.append(
            "DATABASE_URL is not set on this service — the code falls back to localhost:5432 "
            "and there is no database there. On Railway: Variables → Add Reference → "
            "Postgres → DATABASE_URL (the variable must be on THIS service)."
        )
    elif db_error:
        local = (urlsplit(normalise_database_url(url)).hostname or "") in LOCAL_HOSTS
        if local:
            problems.append(
                f"DATABASE_URL points at {host}, a local address inside the container where no "
                f"Postgres runs, and it is not reachable: {db_error}. Use the Railway Postgres "
                "service's DATABASE_URL reference on this service."
            )
        else:
            problems.append(
                f"Database at {host} is not reachable: {db_error}. Check that the Postgres "
                "service is running and that this service's DATABASE_URL still references it."
            )
    for k in REQUIRED:
        if k != "DATABASE_URL" and not present[k]:
            problems.append(f"{k} is not set.")
    if not all(present[k] for k in MAIL) or not any(present[k] for k in MAIL_ONE_OF):
        problems.append(
            "Mail is not fully configured (OPERATOR_EMAIL, GRAPH_TENANT_ID, GRAPH_CLIENT_ID, "
            "GRAPH_SENDER and GRAPH_REFRESH_TOKEN or GRAPH_CLIENT_SECRET): failure emails "
            "cannot be delivered."
        )
    return {
        "database_host": host,
        "database_ok": bool(url) and db_error is None,
        "variables": present,
        "problems": problems,
    }


def render(diag: dict[str, Any]) -> str:
    lines = [
        f"database: {diag['database_host'] or 'NOT SET'} — "
        f"{'reachable' if diag['database_ok'] else 'NOT REACHABLE'}",
        "variables (set / MISSING):",
    ]
    for k, ok in diag["variables"].items():
        lines.append(f"  {k}: {'set' if ok else 'MISSING'}")
    if diag["problems"]:
        lines.append("problems:")
        lines.extend(f"  - {p}" for p in diag["problems"])
    else:
        lines.append("problems: none")
    return "\n".join(lines)


def alert(diag: dict[str, Any], settings: Settings | None = None, service: str = "daily job"):
    """Email the operator the diagnosis through the configured mailer (no database needed).
    Returns the message id, or None when no operator address / mailer is available."""
    from intel import send

    settings = settings or get_settings()
    if not settings.operator_email:
        print("[preflight] OPERATOR_EMAIL not set — cannot email the diagnosis")
        return None
    today = dt.datetime.now(dt.UTC).strftime("%-d %b %Y")
    headline = diag["problems"][0] if diag["problems"] else "container could not start"
    msg = send.Outgoing(
        to=[settings.operator_email],
        subject=f"[RUN FAILED] 1440 Intelligence — {today} — {service} did not start",
        body_text=(
            f"The {service} container stopped before running: {headline}\n\n"
            "What the container saw at start-up:\n\n"
            + render(diag)
            + "\n\nFix the variable on the Railway service and redeploy; the next scheduled "
            "run will then proceed. Nothing was scanned, verified or sent."
        ),
    )
    mailer = send.mailer_for(settings)
    try:
        mid = mailer.send(msg)
    except Exception as exc:  # noqa: BLE001 — the log still carries the diagnosis
        print(f"[preflight] alert email failed: {exc}")
        return None
    where = "outbox (dry-run mailer)" if isinstance(mailer, send.DryRunMailer) else "sent"
    print(f"[preflight] alert email {where}: {mid}")
    return mid


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    service = "daily job"
    if "--service" in argv:
        service = argv[argv.index("--service") + 1]
    diag = diagnose()
    print("[preflight]\n" + render(diag))
    if diag["database_ok"]:
        return 0
    if "--alert" in argv:
        alert(diag, service=service)
        return 0
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
