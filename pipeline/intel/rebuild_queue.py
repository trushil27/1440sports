"""Process "Build the full case" requests submitted from the app.

The app is a static site on Netlify; its *Build the full case* button posts a Netlify Form
(``form-name = rebuild``, fields ``company`` and ``date``). This module reads the form's
submissions through the Netlify API, rebuilds each company not yet processed
(``intel.rebuild``), and remembers what it has done in ``<pdf_storage_dir>/rebuild_done.json``.
The daily job calls ``process()`` before exporting the site, so a request made during the
day turns into a full brief in the next run — and ``python -m intel.rebuild_queue`` runs it
on demand. ``backlog()`` (``--backlog N``) then works through the unverified history a few
companies per run, newest first, so every past signal becomes a verified case over time.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import httpx

from intel.config import Settings, get_settings

API = "https://api.netlify.com/api/v1"
FORM_NAME = "rebuild"


def fetch_requests(token: str, site_id: str, http: httpx.Client | None = None) -> list[dict]:
    """Submissions of the ``rebuild`` form: [{id, company, date, created_at}]."""
    client = http or httpx.Client(timeout=60)
    headers = {"Authorization": f"Bearer {token}"}
    forms = client.get(f"{API}/sites/{site_id}/forms", headers=headers)
    forms.raise_for_status()
    form = next((f for f in forms.json() if f.get("name") == FORM_NAME), None)
    if form is None:
        return []
    subs = client.get(f"{API}/forms/{form['id']}/submissions", headers=headers)
    subs.raise_for_status()
    out = []
    for sub in subs.json():
        data = sub.get("data") or {}
        company = (data.get("company") or "").strip()
        if not company:
            continue
        out.append(
            {
                "id": sub.get("id"),
                "company": company,
                "date": (data.get("date") or "").strip() or None,
                "created_at": sub.get("created_at"),
            }
        )
    return out


GITHUB_REPO = "trushil27/1440sports"
ISSUE_PREFIX = "Rebuild:"


def fetch_issue_requests(
    repo: str = GITHUB_REPO, http: httpx.Client | None = None, token: str | None = None
) -> list[dict]:
    """Open GitHub issues titled ``Rebuild: <Company> (<date>)`` — the queue when the app is
    hosted on GitHub Pages (the repo is public, so reading needs no token)."""
    client = http or httpx.Client(timeout=60)
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = client.get(
        f"https://api.github.com/repos/{repo}/issues?state=open&per_page=50", headers=headers
    )
    r.raise_for_status()
    out = []
    for issue in r.json():
        title = (issue.get("title") or "").strip()
        if not title.startswith(ISSUE_PREFIX) or issue.get("pull_request"):
            continue
        rest = title[len(ISSUE_PREFIX) :].strip()
        date = None
        if rest.endswith(")") and "(" in rest:
            rest, tail = rest.rsplit("(", 1)
            date = tail[:-1].strip()
        out.append(
            {
                "id": f"gh-{issue['number']}",
                "company": rest.strip(),
                "date": date,
                "created_at": issue.get("created_at"),
            }
        )
    return out


def _done_path(settings: Settings) -> Path:
    return Path(settings.pdf_storage_dir) / "rebuild_done.json"


def load_done(settings: Settings) -> dict[str, Any]:
    path = _done_path(settings)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_done(settings: Settings, done: dict[str, Any]) -> None:
    path = _done_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(done, indent=1), encoding="utf-8")


def process(
    settings: Settings | None = None,
    http: httpx.Client | None = None,
    runner=None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Rebuild up to ``limit`` pending requests (each is a full model run). Returns what ran."""
    settings = settings or get_settings()
    from intel import rebuild as rebuild_mod

    run = runner or rebuild_mod.rebuild
    done = load_done(settings)
    results: list[dict[str, Any]] = []
    requests: list[dict] = []
    if settings.netlify_auth_token and settings.netlify_site_id:
        requests += fetch_requests(settings.netlify_auth_token, settings.netlify_site_id, http)
    try:
        requests += fetch_issue_requests(http=http)
    except Exception as exc:  # noqa: BLE001 — GitHub unreachable must not stop Netlify requests
        print(f"rebuild queue: GitHub issues unavailable ({exc})")
    for req in requests:
        if req["id"] in done:
            continue
        if len(results) >= limit:
            break
        try:
            date = dt.date.fromisoformat(req["date"]) if req["date"] else dt.date.today()
        except ValueError:
            date = dt.date.today()
        try:
            out = run(req["company"], date, settings)
            record = {
                "company": req["company"],
                "date": date.isoformat(),
                "status": out.status,
                "brief_id": out.brief_id,
                "at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            }
        except Exception as exc:  # noqa: BLE001 — one bad request must not stop the queue
            record = {
                "company": req["company"],
                "date": date.isoformat(),
                "status": "failed",
                "error": str(exc)[:500],
                "at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            }
        done[req["id"]] = record
        results.append(record)
        save_done(settings, done)
    return results


def backlog(
    settings: Settings | None = None, limit: int = 4, runner=None, session=None
) -> list[dict[str, Any]]:
    """Turn the unverified history into full cases a few at a time, newest first, skipping
    screened / merged rows and anything already rebuilt. The daily job runs this after the
    queue so the whole log becomes Crusoe-standard cases over the following weeks."""
    from sqlalchemy import select

    from intel import rebuild as rebuild_mod
    from intel import site_export
    from intel.db import session_scope
    from intel.models import Brief, VerificationStatus
    from intel.normalise import company_norm

    settings = settings or get_settings()
    if session is None:
        with session_scope(settings.database_url) as s:
            return backlog(settings, limit, runner, s)
    run = runner or rebuild_mod.rebuild
    review = site_export.load_review()
    done = load_done(settings)
    rebuilt_companies = {
        company_norm(r["company"]) for r in done.values() if r.get("status") == "success"
    }
    verified = {
        company_norm(b.brief_data.get("company") or b.candidate.company_raw)
        for b in session.scalars(
            select(Brief).where(Brief.verification_status == VerificationStatus.verified)
        )
        if b.brief_data
    }
    rows = session.scalars(
        select(Brief)
        .where(
            Brief.historical.is_(True),
            Brief.verification_status.not_in(
                [VerificationStatus.blocked, VerificationStatus.verified]
            ),
        )
        .order_by(Brief.run_date.desc(), Brief.id.desc())
    ).all()
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for b in rows:
        if len(results) >= limit:
            break
        company = (b.brief_data or {}).get("company") or b.candidate.company_raw
        norm = company_norm(company)
        if norm in seen or norm in verified or norm in rebuilt_companies:
            continue
        rv = site_export.review_for(review, b.run_date.isoformat(), company)
        if rv["status"] not in ("keep", "keep_flagged"):
            continue
        seen.add(norm)
        key = f"backlog-{b.id}"
        if key in done:
            continue
        try:
            out = run(company, b.run_date, settings)
            record = {
                "company": company,
                "date": b.run_date.isoformat(),
                "status": out.status,
                "brief_id": out.brief_id,
                "at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            }
        except Exception as exc:  # noqa: BLE001
            record = {
                "company": company,
                "date": b.run_date.isoformat(),
                "status": "failed",
                "error": str(exc)[:500],
                "at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            }
        done[key] = record
        results.append(record)
        save_done(settings, done)
    return results


def main(argv: list[str] | None = None) -> int:
    import sys

    argv = sys.argv[1:] if argv is None else argv
    if "--backlog" in argv:
        n = int(argv[argv.index("--backlog") + 1]) if len(argv) > argv.index("--backlog") + 1 else 4
        print(json.dumps(backlog(limit=n), indent=1, default=str))
        return 0
    print(json.dumps(process(), indent=1, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
