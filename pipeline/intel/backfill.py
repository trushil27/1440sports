"""M6 backfill — import every prior brief so day one of the app has the full backlog.

Three sources, all marked ``historical = true`` and ``needs_review`` ("historical,
unverified" per the build brief §10 M6) with every claim carrying an ``unverified`` /
``manual`` verification. Nothing here is invented: every field comes from the source
row, ``briefs/history.json``, ``data/prospects.json`` or the file system; unknown → null.

1. ``import_daily_signals`` — the n8n engine's Google-Sheet audit log
   (``intel/backfill/daily_signals_*.json``). The n8n brief numbers were not logged.
2. ``import_repo_briefs`` — this repo's own engine output: ``briefs/history.json`` +
   ``briefs/<date>/<id>.pdf`` + the matching ``data/prospects.json`` record. Numbered
   001–035 in a numbering SEPARATE from n8n's.
3. ``attach_pdfs`` — PDFs the operator exports later (Outlook / Railway), named
   ``<YYYY-MM-DD>_<company>.pdf`` and matched to a historical brief by date + company.
4. ``import_engine_cases`` — full cases the engine produced outside the scheduled job,
   recorded as ``intel/cases/<date>/<company>.run.json`` (+ .pdf / .web.html). These keep
   their live status (verified, audited, positive number) — see the function docstring.

Imported briefs get NEGATIVE ``brief_number`` values (−1, −2, … in import order): a
negative number marks an import and can never collide with the live sequence.

Sequence: the last known n8n brief number is 120, so **121 is the first free
n8n-continuation number**. ``restart_sequence`` is only run when the operator asks:

    python -m intel.backfill                      # signals + repo (default)
    python -m intel.backfill --signals --repo --pdfs /path/to/exports --restart-sequence 121
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from intel.config import TZ_LONDON, get_settings
from intel.dedup import trigger_key
from intel.freshness import parse_trigger_date
from intel.models import (
    AuditStatus,
    Brief,
    Candidate,
    CandidateDecision,
    Claim,
    ClaimType,
    ExecutionMode,
    Run,
    RunStatus,
    Series,
    SurfacedLog,
    Verification,
    VerificationMethod,
    VerificationResult,
    VerificationStatus,
)
from intel.normalise import company_norm
from intel.score import source_tier

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parents[1]
BACKFILL_DIR = PACKAGE_DIR / "backfill"
DEFAULT_SIGNALS_FILE = BACKFILL_DIR / "daily_signals_2026-09-03.json"

SOURCE_SIGNALS = "n8n daily signals log"
SOURCE_REPO = "1440sports repo engine"
HISTORICAL_SUBDIR = "historical"
IMPORT_NOTE = "historical import — not re-verified"
LAST_N8N_BRIEF_NUMBER = 120
FIRST_FREE_N8N_NUMBER = LAST_N8N_BRIEF_NUMBER + 1

_MONEY_OR_PERCENT = re.compile(r"[$€£]|\d\s?%")
_PDF_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})_(.+)\.pdf$", re.IGNORECASE)


# --- small helpers -------------------------------------------------------------------------


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _clean(value: Any) -> str | None:
    """Stringify a source value; empty / whitespace-only → None (never invent)."""
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _int_or_none(value: Any) -> int | None:
    s = _clean(value)
    if s is None:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _date_upper(d: dt.date) -> str:
    """'D MMM YYYY' uppercase without a leading zero — the brief footer style."""
    return f"{d.day} {d.strftime('%b').upper()} {d.year}"


def _surfaced_at(day: dt.date) -> dt.datetime:
    """The pipeline's send time on that day: 06:00 Europe/London."""
    return dt.datetime.combine(day, dt.time(6, 0), tzinfo=TZ_LONDON)


def _historical_dir() -> Path:
    out = Path(get_settings().pdf_storage_dir) / HISTORICAL_SUBDIR
    out.mkdir(parents=True, exist_ok=True)
    return out


def _copy_into_storage(src: Path, name: str) -> str:
    dest = _historical_dir() / name
    if not (dest.exists() and dest.stat().st_size == src.stat().st_size):
        shutil.copyfile(src, dest)
    return str(dest)


def page_count_of(pdf_path: Path | str) -> int | None:
    try:
        import pymupdf  # type: ignore[import-not-found]
    except ImportError:  # pragma: no cover - dev/render extra not installed
        return None
    with pymupdf.open(str(pdf_path)) as doc:
        return doc.page_count


def _run_for(session: Session, day: dt.date, source: str) -> Run:
    """One run per (date, source); re-used when it already exists. Never collides with a
    live run on the same date: a fresh import run takes the next free attempt number."""
    for run in session.scalars(select(Run).where(Run.run_date == day)).all():
        if (run.summary or {}).get("source") == source and (run.summary or {}).get("backfill"):
            return run
    next_attempt = (
        session.scalar(select(func.coalesce(func.max(Run.attempt), 0)).where(Run.run_date == day))
        or 0
    ) + 1
    run = Run(
        run_date=day,
        attempt=next_attempt,
        started_at=_surfaced_at(day),
        finished_at=_surfaced_at(day),
        status=RunStatus.success,
        execution_mode=ExecutionMode.production,
        summary={"source": source, "backfill": True},
    )
    session.add(run)
    session.flush()
    return run


def _next_negative_number(session: Session) -> int:
    lowest = session.scalar(select(func.min(Brief.brief_number)).where(Brief.brief_number < 0))
    return (lowest or 0) - 1


def _find_historical(session: Session, key: str) -> Brief | None:
    return session.scalar(
        select(Brief).where(
            Brief.historical.is_(True), Brief.brief_data["historical_key"].astext == key
        )
    )


def _unverified(claim: Claim) -> Verification:
    return Verification(
        claim=claim,
        status=VerificationResult.unverified,
        method=VerificationMethod.manual,
        notes=IMPORT_NOTE,
    )


def _add_claims(session: Session, brief: Brief, drafts: list[dict[str, Any]]) -> int:
    for pos, d in enumerate(drafts):
        claim = Claim(
            brief_id=brief.id,
            position=pos,
            section=d["section"],
            text=d["text"],
            claim_type=d["claim_type"],
            load_bearing=d.get("load_bearing", True),
            cited_source_url=d.get("cited_source_url"),
        )
        session.add(claim)
        session.add(_unverified(claim))
    session.flush()
    return len(drafts)


def _upsert_surfaced(
    session: Session, norm: str, trig_key: str, display: str | None, at: dt.datetime, brief_id: int
) -> None:
    row = session.scalar(
        select(SurfacedLog).where(
            SurfacedLog.company_norm == norm, SurfacedLog.trigger_reason_norm == trig_key
        )
    )
    if row is None:
        session.add(
            SurfacedLog(
                company_norm=norm,
                trigger_reason_norm=trig_key,
                company_display=display,
                first_surfaced_at=at,
                last_surfaced_at=at,
                times_surfaced=1,
                brief_id=brief_id,
            )
        )
    else:
        if at < row.first_surfaced_at:
            row.first_surfaced_at = at
        if at >= row.last_surfaced_at:
            row.last_surfaced_at = at
            row.brief_id = brief_id
        row.times_surfaced = (row.times_surfaced or 0) + 1
        if not row.company_display:
            row.company_display = display
    session.flush()


def _person_role_claim(
    person: str | None, role: str | None, company: str, src: str | None
) -> dict[str, Any] | None:
    if not person:
        return None
    text_ = f"{person}, {role} at {company}" if role else f"{person} at {company}"
    return {
        "text": text_,
        "section": "decision_maker",
        "claim_type": ClaimType.person_role,
        "load_bearing": True,
        "cited_source_url": src,
    }


# --- 1. n8n daily signals log -----------------------------------------------------------------


def _signal_key(day: str, norm: str, action: str) -> str:
    return f"{SOURCE_SIGNALS}|{day}|{norm}|{action}"


def import_daily_signals(
    session: Session, path: Path | str | None = None, source_label: str | None = None
) -> dict[str, Any]:
    """Import audit-log style rows as historical, unverified briefs (one per row).

    The n8n log is the default file; any other file with the same columns (plus optional
    ``Series`` / ``Team`` / ``Industry`` columns, e.g. the FE sweep) imports the same way with
    its own ``source_label`` so the app can say where a row came from."""
    src_path = Path(path) if path else DEFAULT_SIGNALS_FILE
    label = source_label or (SOURCE_SIGNALS if src_path == DEFAULT_SIGNALS_FILE else src_path.stem)
    data = _read_json(src_path)
    rows: list[dict[str, Any]] = data["rows"] if isinstance(data, dict) else data
    created = skipped = failed = 0
    errors: list[dict[str, str]] = []
    rank_by_date: dict[str, int] = {}

    for row in rows:
        day_raw = _clean(row.get("Date"))
        company = _clean(row.get("Company"))
        action = _clean(row.get("Action")) or ""
        if not day_raw or not company:
            failed += 1
            errors.append({"row": json.dumps(row), "why": "no Date or Company"})
            continue
        parsed = parse_trigger_date(day_raw)
        if parsed.date is None:
            failed += 1
            errors.append({"row": json.dumps(row), "why": f"unparseable Date {day_raw!r}"})
            continue
        day = parsed.date
        rank_by_date[day_raw] = rank_by_date.get(day_raw, 0) + 1
        norm = company_norm(company)
        key = _signal_key(day_raw, norm, action)
        if _find_historical(session, key) is not None:
            skipped += 1
            continue

        run = _run_for(session, day, label)
        series_raw = _clean(row.get("Series"))
        series = Series(series_raw) if series_raw in ("F1", "FE") else None
        team = _clean(row.get("Team"))
        track_raw = _clean(row.get("Track"))
        track = int(track_raw) if track_raw in {"1", "2"} else 1
        source_url = _clean(row.get("Source"))
        person = _clean(row.get("Person"))
        role = _clean(row.get("Role"))
        tier = _clean(row.get("Tier"))
        score = _int_or_none(row.get("Score"))

        candidate = Candidate(
            run_id=run.id,
            rank=rank_by_date[day_raw],
            company_raw=company,
            company_norm=norm,
            track=track,
            series=series,
            recommended_team=team,
            trigger_reason_raw=action or None,
            trigger_reason_norm=trigger_key(action),
            trigger_date=day,
            source_url=source_url,
            source_tier=source_tier(source_url),
            raw_json=dict(row),
            score_total=score,
            tier=tier,
            decision=CandidateDecision.selected,
            decision_reason="historical n8n signal (backfill)",
        )
        session.add(candidate)
        session.flush()

        brief = Brief(
            candidate_id=candidate.id,
            run_date=day,
            brief_number=_next_negative_number(session),
            historical=True,
            verification_status=VerificationStatus.needs_review,
            audit_status=AuditStatus.pending,
            brief_data={
                "company": company,
                "industry_meta": _clean(row.get("Industry")),
                "score": score if score is not None else _clean(row.get("Score")),
                "timing_label": tier,
                "series_label": series.value if series else None,
                "team_label": team,
                "horizon_label": _clean(row.get("Horizon")),
                "decision_maker_name": person,
                "decision_maker_role": role,
                "deck": action or None,
                "historical": True,
                "historical_source": label,
                "historical_label": None,
                "historical_key": key,
                "signal_date": day_raw,
            },
        )
        session.add(brief)
        session.flush()

        drafts: list[dict[str, Any]] = []
        if pr := _person_role_claim(person, role, company, source_url):
            drafts.append(pr)
        if action:
            drafts.append(
                {
                    "text": action,
                    "section": "trigger",
                    "claim_type": ClaimType.date,
                    "load_bearing": True,
                    "cited_source_url": source_url,
                }
            )
        _add_claims(session, brief, drafts)
        _upsert_surfaced(session, norm, trigger_key(action), company, _surfaced_at(day), brief.id)
        created += 1

    session.flush()
    return {
        "source": SOURCE_SIGNALS,
        "rows": len(rows),
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
    }


# --- 2. this repo's engine output ----------------------------------------------------------------


def _repo_key(day: str, prospect_id: str) -> str:
    return f"{SOURCE_REPO}|{day}|{prospect_id}"


def _load_prospects(repo_root: Path) -> dict[str, dict[str, Any]]:
    path = repo_root / "data" / "prospects.json"
    if not path.exists():
        return {}
    data = _read_json(path)
    records = data.get("prospects", []) if isinstance(data, dict) else data
    return {r["id"]: r for r in records if isinstance(r, dict) and r.get("id")}


_SCORE_LABELS = {
    "timing": "TIMING",
    "capacity": "CAPACITY",
    "brand_fit": "BRAND FIT",
    "urgency": "URGENCY",
    "ops_fit": "OPS FIT",
}


def _score_cells(prospect: dict[str, Any]) -> list[dict[str, Any]]:
    scores = prospect.get("scores") or {}
    rationale = prospect.get("score_rationale") or {}
    return [
        {
            "label": _SCORE_LABELS.get(k, k.replace("_", " ").upper()),
            "num": v,
            "denom": "/ 20",
            "note": rationale.get(k),
        }
        for k, v in scores.items()
    ]


def _sum_scores(prospect: dict[str, Any]) -> int | None:
    scores = prospect.get("scores") or {}
    nums = [v for v in scores.values() if isinstance(v, int | float)]
    return int(sum(nums)) if nums else None


def _brief_data_from_prospect(
    entry: dict[str, Any], prospect: dict[str, Any], day: dt.date, label: str
) -> dict[str, Any]:
    dm = prospect.get("decision_maker") or {}
    team = entry.get("recommended_team") or prospect.get("recommended_team")
    series = entry.get("series") or prospect.get("series")
    return {
        "company": prospect.get("name") or entry.get("name"),
        "deck": prospect.get("headline_long"),
        "industry_meta": prospect.get("category"),
        "hq": prospect.get("hq"),
        "ticker": prospect.get("ticker"),
        "score": _sum_scores(prospect),
        "timing_label": prospect.get("timing_window"),
        "series_label": series,
        "team_label": team,
        "horizon_label": prospect.get("action_horizon"),
        "the_case_p1": prospect.get("the_case"),
        "the_case_p2": "",
        "why_now_callout": prospect.get("why_now"),
        "why_team_label": f"WHY {team.upper()}" if team else None,
        "why_team_para": prospect.get("why_team"),
        "value_section": True,
        "value_mode": prospect.get("mode"),
        "value_content": prospect.get("value_to_team"),
        "deal_arch_para": prospect.get("deal_architecture"),
        "decision_maker_name": dm.get("name"),
        "decision_maker_role": dm.get("title"),
        "decision_maker_bio": dm.get("bio"),
        "opening_angle_quote": prospect.get("opening_angle"),
        "score_cells": _score_cells(prospect),
        "risks": [
            {"label": r.get("title"), "detail": r.get("detail"), "counter": r.get("counter")}
            for r in (prospect.get("risks") or [])
            if isinstance(r, dict)
        ],
        "bottom_line": prospect.get("thesis"),
        "signals": list(prospect.get("signals") or []),
        "sources": list(prospect.get("sources") or []),
        "proof_points": [
            {
                "value": kf.get("value"),
                "fact": kf.get("fact"),
                "source_url": kf.get("source"),
                "verified": False,
            }
            for kf in (prospect.get("key_facts") or [])
            if isinstance(kf, dict)
        ],
        "footer_company": (prospect.get("name") or entry.get("name") or "").upper() or None,
        "footer_date": _date_upper(day),
        "historical": True,
        "historical_source": SOURCE_REPO,
        "historical_label": label,
    }


def _brief_data_minimal_repo(entry: dict[str, Any], day: dt.date, label: str) -> dict[str, Any]:
    return {
        "company": entry.get("name"),
        "industry_meta": None,
        "score": entry.get("opportunity"),
        "timing_label": entry.get("tier"),
        "series_label": entry.get("series"),
        "team_label": entry.get("recommended_team"),
        "horizon_label": None,
        "decision_maker_name": None,
        "decision_maker_role": None,
        "deck": entry.get("note"),
        "historical": True,
        "historical_source": SOURCE_REPO,
        "historical_label": label,
        "signal_date": day.isoformat(),
    }


def _repo_claims(prospect: dict[str, Any] | None, company: str) -> list[dict[str, Any]]:
    drafts: list[dict[str, Any]] = []
    if not prospect:
        return drafts
    for kf in prospect.get("key_facts") or []:
        if not isinstance(kf, dict):
            continue
        value = _clean(kf.get("value"))
        fact = _clean(kf.get("fact"))
        if not value and not fact:
            continue
        text_ = f"{value} — {fact}" if value and fact else (value or fact or "")
        ctype = ClaimType.funding if value and _MONEY_OR_PERCENT.search(value) else ClaimType.other
        drafts.append(
            {
                "text": text_,
                "section": "key_facts",
                "claim_type": ctype,
                "load_bearing": True,
                "cited_source_url": _clean(kf.get("source")),
            }
        )
    dm = prospect.get("decision_maker") or {}
    if pr := _person_role_claim(_clean(dm.get("name")), _clean(dm.get("title")), company, None):
        drafts.append(pr)
    return drafts


def import_repo_briefs(session: Session, repo_root: Path | str | None = None) -> dict[str, Any]:
    """Import ``briefs/history.json`` entries that have a rendered PDF on disk."""
    root = Path(repo_root) if repo_root else REPO_ROOT
    history_path = root / "briefs" / "history.json"
    if not history_path.exists():
        # The deployed image ships pipeline/ only; the repo engine's briefs are imported from a
        # checkout. Nothing to do here must not fail (and roll back) the other imports.
        return {
            "source": SOURCE_REPO,
            "entries": 0,
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "errors": [],
            "note": f"no {history_path} in this environment",
        }
    entries: list[dict[str, Any]] = _read_json(history_path).get("log", [])
    prospects = _load_prospects(root)
    created = skipped = failed = 0
    errors: list[dict[str, str]] = []
    rank_by_date: dict[str, int] = {}

    for entry in entries:
        day_raw = _clean(entry.get("date"))
        pid = _clean(entry.get("id"))
        name = _clean(entry.get("name")) or pid
        if not day_raw or not pid or not name:
            failed += 1
            errors.append({"entry": json.dumps(entry), "why": "no date, id or name"})
            continue
        pdf_src = root / "briefs" / day_raw / f"{pid}.pdf"
        if not pdf_src.exists():
            failed += 1
            errors.append({"entry": f"{day_raw}/{pid}", "why": f"no PDF at {pdf_src}"})
            continue
        parsed = parse_trigger_date(day_raw)
        if parsed.date is None:
            failed += 1
            errors.append({"entry": f"{day_raw}/{pid}", "why": f"unparseable date {day_raw!r}"})
            continue
        day = parsed.date
        rank_by_date[day_raw] = rank_by_date.get(day_raw, 0) + 1
        key = _repo_key(day_raw, pid)
        if _find_historical(session, key) is not None:
            skipped += 1
            continue

        prospect = prospects.get(pid)
        brief_no = _clean(entry.get("brief_no"))
        label = f"N° {brief_no}" if brief_no else None
        series_raw = entry.get("series") or (prospect or {}).get("series")
        series = Series(series_raw) if series_raw in {s.value for s in Series} else None
        team = entry.get("recommended_team") or (prospect or {}).get("recommended_team")
        signals = list((prospect or {}).get("signals") or [])
        trigger_raw = ", ".join(signals) if signals else _clean(entry.get("note"))
        sources = list((prospect or {}).get("sources") or [])
        source_url = _clean(sources[0]) if sources else None
        norm = company_norm(name)

        run = _run_for(session, day, SOURCE_REPO)
        candidate = Candidate(
            run_id=run.id,
            rank=rank_by_date[day_raw],
            company_raw=name,
            company_norm=norm,
            track=1,
            series=series,
            trigger_reason_raw=trigger_raw,
            trigger_reason_norm=trigger_key(trigger_raw) if trigger_raw else None,
            trigger_date=day,
            source_url=source_url,
            source_tier=source_tier(source_url),
            raw_json={**entry, "prospect_id": pid},
            score_total=_int_or_none(entry.get("opportunity")),
            score_breakdown=dict((prospect or {}).get("scores") or {}) or None,
            tier=_clean(entry.get("tier")),
            recommended_team=team,
            decision=CandidateDecision.selected,
            decision_reason="historical repo-engine brief (backfill)",
        )
        session.add(candidate)
        session.flush()

        if prospect:
            brief_data = _brief_data_from_prospect(entry, prospect, day, label)
        else:
            brief_data = _brief_data_minimal_repo(entry, day, label)
        brief_data["historical_key"] = key
        brief_data["prospect_id"] = pid
        brief_data["history_note"] = entry.get("note")

        pdf_path = _copy_into_storage(pdf_src, f"{day_raw}_{pid}.pdf")
        html_src = pdf_src.with_suffix(".html")
        html_path = (
            _copy_into_storage(html_src, f"{day_raw}_{pid}.html") if html_src.exists() else None
        )
        mode_raw = (prospect or {}).get("mode")

        brief = Brief(
            candidate_id=candidate.id,
            run_date=day,
            brief_number=_next_negative_number(session),
            historical=True,
            verification_status=VerificationStatus.needs_review,
            audit_status=AuditStatus.pending,
            brief_data=brief_data,
            mode=mode_raw if mode_raw in {"A", "B", "C"} else None,
            pdf_path=pdf_path,
            html_path=html_path,
            page_count=page_count_of(pdf_path),
        )
        session.add(brief)
        session.flush()

        _add_claims(session, brief, _repo_claims(prospect, name))
        if trigger_raw:
            _upsert_surfaced(
                session, norm, trigger_key(trigger_raw), name, _surfaced_at(day), brief.id
            )
        created += 1

    session.flush()
    return {
        "source": SOURCE_REPO,
        "entries": len(entries),
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
    }


# --- 4. engine cases produced outside the daily job -----------------------------------------

CASES_DIR = PACKAGE_DIR / "cases"
SOURCE_CASES = "1440 engine case record"
CASES_SUBDIR = "cases"


def _case_key(day: str, stem: str) -> str:
    return f"{SOURCE_CASES}|{day}|{stem}"


def _find_case(session: Session, key: str) -> Brief | None:
    return session.scalar(select(Brief).where(Brief.brief_data["engine_case_key"].astext == key))


def _sibling(record: Path, suffix: str) -> Path | None:
    """``crusoe.run.json`` → ``crusoe.pdf`` / ``crusoe.web.html`` in the same folder, if present."""
    stem = record.name[: -len(".run.json")]
    path = record.with_name(f"{stem}{suffix}")
    return path if path.exists() else None


def _copy_case_file(src: Path | None, name: str) -> str | None:
    if src is None:
        return None
    dest = Path(get_settings().pdf_storage_dir) / CASES_SUBDIR / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not (dest.exists() and dest.stat().st_size == src.stat().st_size):
        shutil.copyfile(src, dest)
    return str(dest)


def _ledger_claims(session: Session, brief: Brief, ledger: list[dict[str, Any]]) -> int:
    """Recreate the claims ledger of a case record, verification rows included — the record
    is the run's own output, so nothing is re-interpreted here."""
    for pos, row in enumerate(ledger):
        ctype_raw = row.get("type") or "other"
        claim = Claim(
            brief_id=brief.id,
            position=pos,
            section=row.get("section") or "other",
            text=row.get("text") or "",
            claim_type=ClaimType(ctype_raw) if ctype_raw in set(ClaimType) else ClaimType.other,
            load_bearing=bool(row.get("load_bearing", True)),
            cited_source_url=_clean(row.get("cited_source_url")),
        )
        session.add(claim)
        for v in row.get("verifications") or []:
            status_raw = v.get("status") or "unverified"
            method_raw = v.get("method") or "manual"
            session.add(
                Verification(
                    claim=claim,
                    status=(
                        VerificationResult(status_raw)
                        if status_raw in set(VerificationResult)
                        else VerificationResult.unverified
                    ),
                    method=(
                        VerificationMethod(method_raw)
                        if method_raw in set(VerificationMethod)
                        else VerificationMethod.manual
                    ),
                    evidence_url=_clean(v.get("evidence_url")),
                    evidence_excerpt=_clean(v.get("excerpt") or v.get("evidence_excerpt")),
                    notes=_clean(v.get("notes")),
                    model=_clean(v.get("model")),
                )
            )
    session.flush()
    return len(ledger)


def _bump_sequence(session: Session, number: int) -> None:
    """Keep the live sequence ahead of an imported positive brief number."""
    session.execute(
        text(
            "SELECT setval('brief_number_seq', "
            "GREATEST((SELECT last_value FROM brief_number_seq), :n))"
        ),
        {"n": int(number)},
    )


def import_engine_cases(session: Session, cases_dir: Path | str | None = None) -> dict[str, Any]:
    """Import full cases recorded as ``<date>/<company>.run.json`` (the pipeline's own run
    record: run summary, every candidate with its decision, the brief with its statuses, and
    the claims ledger with each verification). These are cases the engine produced outside the
    scheduled job — the first one is N° 121 Crusoe, built in-session on 5 Sep 2026 — so they
    keep their **live** status: not historical, verified / audited as recorded, positive
    brief number, PDF + app page copied into storage. Idempotent by (date, file).

    Two guards keep the live rules intact: a day that already has a live brief keeps it
    (the case is then stored as ``historical`` with its statuses unchanged, so the one-live-
    brief-per-day rule holds), and a brief number already taken falls back to a negative one.
    """
    folder = Path(cases_dir) if cases_dir else CASES_DIR
    created = skipped = failed = 0
    errors: list[dict[str, str]] = []
    if not folder.exists():
        return {"source": SOURCE_CASES, "files": 0, "created": 0, "skipped": 0, "failed": 0}
    files = sorted(folder.glob("*/*.run.json"))
    for record in files:
        day_raw = record.parent.name
        stem = record.name[: -len(".run.json")]
        key = _case_key(day_raw, stem)
        try:
            with session.begin_nested():
                data = _read_json(record)
                parsed = parse_trigger_date(day_raw)
                if parsed.date is None:
                    raise ValueError(f"folder name {day_raw!r} is not a date")
                day = parsed.date
                if _find_case(session, key) is not None:
                    skipped += 1
                    continue
                brief_rec = data["brief"]
                bdata = dict(brief_rec.get("brief_data") or {})
                company = _clean(bdata.get("company")) or stem
                norm = company_norm(company)
                run_rec = data.get("run") or {}

                run = Run(
                    run_date=day,
                    attempt=(
                        session.scalar(
                            select(func.coalesce(func.max(Run.attempt), 0)).where(
                                Run.run_date == day
                            )
                        )
                        or 0
                    )
                    + 1,
                    started_at=_surfaced_at(day),
                    finished_at=_surfaced_at(day),
                    status=RunStatus.success,
                    execution_mode=ExecutionMode.production,
                    summary={
                        **(run_rec.get("summary") or {}),
                        "source": SOURCE_CASES,
                        "backfill": True,
                        "case_file": str(record.relative_to(folder)),
                    },
                )
                session.add(run)
                session.flush()

                selected: Candidate | None = None
                for c in data.get("candidates") or []:
                    decision_raw = c.get("decision") or "not_selected"
                    series_raw = c.get("series")
                    trig = _clean(c.get("trigger_reason")) or (
                        _clean(bdata.get("deck")) if c.get("decision") == "selected" else None
                    )
                    trig_date = parse_trigger_date(c.get("trigger_date") or "").date
                    cand = Candidate(
                        run_id=run.id,
                        rank=c.get("rank"),
                        company_raw=c.get("company") or "",
                        company_norm=company_norm(c.get("company") or ""),
                        track=1,
                        series=Series(series_raw)
                        if series_raw in {s.value for s in Series}
                        else None,
                        trigger_reason_raw=trig,
                        trigger_reason_norm=trigger_key(trig) if trig else None,
                        trigger_date=trig_date,
                        source_url=_clean(c.get("source_url")),
                        source_tier=source_tier(_clean(c.get("source_url"))),
                        raw_json=dict(c),
                        gate_results=c.get("gate_results"),
                        score_total=c.get("score_total"),
                        score_breakdown=c.get("score_breakdown"),
                        recommended_team=_clean(c.get("recommended_team")),
                        decision=(
                            CandidateDecision(decision_raw)
                            if decision_raw in set(CandidateDecision)
                            else CandidateDecision.not_selected
                        ),
                        decision_reason=_clean(c.get("reason")),
                    )
                    session.add(cand)
                    if (
                        cand.decision == CandidateDecision.selected
                        and cand.company_norm == norm
                        and selected is None
                    ):
                        selected = cand
                if selected is None:
                    selected = Candidate(
                        run_id=run.id,
                        rank=1,
                        company_raw=company,
                        company_norm=norm,
                        track=1,
                        series=(
                            Series(bdata["series_label"])
                            if bdata.get("series_label") in {s.value for s in Series}
                            else None
                        ),
                        trigger_reason_raw=_clean(bdata.get("deck")),
                        trigger_reason_norm=trigger_key(bdata["deck"])
                        if bdata.get("deck")
                        else None,
                        trigger_date=day,
                        raw_json={"from": "brief_data"},
                        score_total=bdata.get("score")
                        if isinstance(bdata.get("score"), int)
                        else None,
                        recommended_team=_clean(bdata.get("team_label")),
                        decision=CandidateDecision.selected,
                        decision_reason="selected (case record)",
                    )
                    session.add(selected)
                session.flush()

                live_exists = session.scalar(
                    select(Brief).where(
                        Brief.run_date == day,
                        Brief.historical.is_(False),
                        Brief.verification_status != VerificationStatus.blocked,
                    )
                )
                number = brief_rec.get("number")
                number_taken = (
                    isinstance(number, int)
                    and session.scalar(select(Brief).where(Brief.brief_number == number))
                    is not None
                )
                if not isinstance(number, int) or number_taken:
                    number = _next_negative_number(session)
                vs_raw = brief_rec.get("verification_status") or "needs_review"
                audit_raw = brief_rec.get("audit_status") or "pending"
                mode_raw = brief_rec.get("mode")
                bdata.update(
                    {
                        "engine_case_key": key,
                        "engine_case_file": str(record.relative_to(folder)),
                        "historical": live_exists is not None,
                        "historical_source": SOURCE_CASES if live_exists is not None else None,
                        "historical_label": f"N° {brief_rec.get('number')}"
                        if live_exists is not None and brief_rec.get("number")
                        else bdata.get("historical_label"),
                    }
                )
                pdf_path = _copy_case_file(_sibling(record, ".pdf"), f"{day_raw}_{stem}.pdf")
                brief = Brief(
                    candidate_id=selected.id,
                    run_date=day,
                    brief_number=number,
                    historical=live_exists is not None,
                    verification_status=(
                        VerificationStatus(vs_raw)
                        if vs_raw in set(VerificationStatus)
                        else VerificationStatus.needs_review
                    ),
                    audit_status=(
                        AuditStatus(audit_raw)
                        if audit_raw in set(AuditStatus)
                        else AuditStatus.pending
                    ),
                    audit_attempts=int(brief_rec.get("audit_attempts") or 0),
                    brief_data=bdata,
                    mode=mode_raw if mode_raw in {"A", "B", "C"} else None,
                    pdf_path=pdf_path,
                    html_path=_copy_case_file(_sibling(record, ".html"), f"{day_raw}_{stem}.html"),
                    web_html_path=_copy_case_file(
                        _sibling(record, ".web.html"), f"{day_raw}_{stem}.web.html"
                    ),
                    page_count=brief_rec.get("pages")
                    or (page_count_of(pdf_path) if pdf_path else None),
                )
                session.add(brief)
                session.flush()
                if number > 0:
                    _bump_sequence(session, number)
                _ledger_claims(session, brief, data.get("ledger") or [])
                if selected.trigger_reason_norm:
                    _upsert_surfaced(
                        session,
                        norm,
                        selected.trigger_reason_norm,
                        company,
                        _surfaced_at(day),
                        brief.id,
                    )
                created += 1
        except Exception as exc:  # noqa: BLE001 — one bad record must not stop the import
            failed += 1
            errors.append({"file": str(record), "why": f"{type(exc).__name__}: {exc}"[:300]})
    session.flush()
    return {
        "source": SOURCE_CASES,
        "files": len(files),
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
    }


# --- 3. operator-exported PDFs -------------------------------------------------------------------


def attach_pdfs(session: Session, directory: Path | str) -> dict[str, Any]:
    """Attach ``<YYYY-MM-DD>_<company>.pdf`` files to the matching historical brief."""
    folder = Path(directory)
    attached = skipped = 0
    unmatched: list[dict[str, str]] = []
    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue
        m = _PDF_NAME.match(path.name)
        if not m:
            unmatched.append(
                {"file": path.name, "why": "filename is not <YYYY-MM-DD>_<company>.pdf"}
            )
            continue
        parsed = parse_trigger_date(m.group(1))
        if parsed.date is None:
            unmatched.append({"file": path.name, "why": f"bad date {m.group(1)!r}"})
            continue
        norm = company_norm(m.group(2))
        briefs = session.scalars(
            select(Brief)
            .join(Candidate, Candidate.id == Brief.candidate_id)
            .where(
                Brief.historical.is_(True),
                Brief.run_date == parsed.date,
                Candidate.company_norm == norm,
            )
            .order_by(Brief.brief_number.desc())
        ).all()
        if not briefs:
            unmatched.append(
                {"file": path.name, "why": f"no historical brief on {parsed.date} for '{norm}'"}
            )
            continue
        brief = next((b for b in briefs if not b.pdf_path), briefs[0])
        dest = _historical_dir() / path.name
        if brief.pdf_path == str(dest) and dest.exists():
            skipped += 1
            continue
        brief.pdf_path = _copy_into_storage(path, path.name)
        brief.page_count = page_count_of(brief.pdf_path)
        attached += 1
    session.flush()
    return {"attached": attached, "skipped": skipped, "unmatched": unmatched}


# --- sequence -----------------------------------------------------------------------------------


def restart_sequence(session: Session, next_number: int) -> None:
    """``ALTER SEQUENCE brief_number_seq RESTART WITH <n>`` — the next live brief gets ``n``.

    121 is the first free n8n-continuation number (last known n8n brief: 120).
    The operator decides; this is never run implicitly.
    """
    n = int(next_number)
    if n < 1:
        raise ValueError("brief_number sequence must restart at a positive integer")
    session.execute(text(f"ALTER SEQUENCE brief_number_seq RESTART WITH {n}"))


# --- CLI ---------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m intel.backfill",
        description=(
            "M6 backfill: import prior briefs as historical / unverified. With no source flag, "
            "imports the n8n daily-signals log and the repo engine briefs."
        ),
    )
    parser.add_argument("--signals", action="store_true", help="import the n8n daily signals log")
    parser.add_argument("--repo", action="store_true", help="import briefs/history.json + PDFs")
    parser.add_argument("--pdfs", metavar="DIR", help="attach <YYYY-MM-DD>_<company>.pdf files")
    parser.add_argument(
        "--cases", action="store_true", help="import intel/cases/<date>/<company>.run.json records"
    )
    parser.add_argument(
        "--restart-sequence",
        type=int,
        metavar="N",
        help=(
            f"ALTER SEQUENCE brief_number_seq RESTART WITH N (operator decision; "
            f"{FIRST_FREE_N8N_NUMBER} is the first free n8n-continuation number)"
        ),
    )
    args = parser.parse_args(argv)
    do_signals, do_repo, do_cases = args.signals, args.repo, args.cases
    if not (do_signals or do_repo or do_cases or args.pdfs or args.restart_sequence is not None):
        do_signals = do_repo = do_cases = True

    from intel.db import session_scope

    with session_scope() as session:
        if do_signals:
            print(json.dumps(import_daily_signals(session), indent=1, ensure_ascii=False))
            # Any further audit-log style file next to the n8n log (e.g. the FE sweep of
            # 5 Sep 2026) imports with its file stem as the source label.
            for extra in sorted(BACKFILL_DIR.glob("*_signals_*.json")):
                if extra != DEFAULT_SIGNALS_FILE and not extra.name.startswith("daily_signals"):
                    res = import_daily_signals(session, extra)
                    print(json.dumps({extra.name: res}, indent=1, ensure_ascii=False))
        if do_repo:
            print(json.dumps(import_repo_briefs(session), indent=1, ensure_ascii=False))
        if args.pdfs:
            print(json.dumps(attach_pdfs(session, args.pdfs), indent=1, ensure_ascii=False))
        if do_cases:
            print(json.dumps(import_engine_cases(session), indent=1, ensure_ascii=False))
        if args.restart_sequence is not None:
            restart_sequence(session, args.restart_sequence)
            print(f"brief_number_seq restarted at {args.restart_sequence}")


if __name__ == "__main__":
    main()
