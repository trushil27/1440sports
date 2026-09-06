"""Export a brief as a self-contained *case record* — ``<company>.run.json`` — that
``backfill.import_engine_cases`` can load into any database with its live status intact.

The record is the pipeline's own output (run summary, every candidate with its decision, the
brief with its statuses and ``brief_data``, the claims ledger with each verification); nothing
is re-interpreted. Written next to the PDF / app page so the four files travel together:

    python -m intel.case_record 121 --out pipeline/intel/cases
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.models import Brief, Candidate, Claim


def _enum(v: Any) -> Any:
    return getattr(v, "value", v)


def _iso(v: dt.date | dt.datetime | None) -> str | None:
    return v.isoformat() if v is not None else None


def case_record(session: Session, brief: Brief) -> dict[str, Any]:
    run = brief.candidate.run
    candidates = session.scalars(
        select(Candidate).where(Candidate.run_id == run.id).order_by(Candidate.rank, Candidate.id)
    ).all()
    claims = session.scalars(
        select(Claim).where(Claim.brief_id == brief.id).order_by(Claim.position, Claim.id)
    ).all()
    return {
        "run": {
            "id": run.id,
            "date": _iso(run.run_date),
            "status": _enum(run.status),
            "mode": _enum(run.execution_mode),
            "summary": run.summary,
        },
        "candidates": [
            {
                "rank": c.rank,
                "company": c.company_raw,
                "series": _enum(c.series),
                "decision": _enum(c.decision),
                "reason": c.decision_reason,
                "score_total": c.score_total,
                "score_breakdown": c.score_breakdown,
                "gate_results": c.gate_results,
                "recommended_team": c.recommended_team,
                "source_url": c.source_url,
                "trigger_date": _iso(c.trigger_date),
                "trigger_reason": c.trigger_reason_raw,
            }
            for c in candidates
        ],
        "brief": {
            "number": brief.brief_number,
            "verification_status": _enum(brief.verification_status),
            "audit_status": _enum(brief.audit_status),
            "audit_attempts": brief.audit_attempts,
            "pages": brief.page_count,
            "mode": _enum(brief.mode),
            "web_html_path": brief.web_html_path,
            "brief_data": brief.brief_data,
        },
        "ledger": [
            {
                "section": cl.section,
                "type": _enum(cl.claim_type),
                "load_bearing": cl.load_bearing,
                "text": cl.text,
                "cited_source_url": cl.cited_source_url,
                "verifications": [
                    {
                        "status": _enum(v.status),
                        "method": _enum(v.method),
                        "evidence_url": v.evidence_url,
                        "excerpt": v.evidence_excerpt,
                        "notes": v.notes,
                        "model": v.model,
                    }
                    for v in cl.verifications
                ],
            }
            for cl in claims
        ],
    }


def export_case(
    session: Session, brief: Brief, out_root: Path | str, stem: str | None = None
) -> dict[str, str]:
    """Write ``<out_root>/<run_date>/<stem>.run.json`` and copy the PDF / HTML / app page
    next to it. Returns the paths written."""
    stem = stem or Path(brief.pdf_path or brief.web_html_path or "case").stem.replace(".web", "")
    folder = Path(out_root) / brief.run_date.isoformat()
    folder.mkdir(parents=True, exist_ok=True)
    out: dict[str, str] = {}
    record = folder / f"{stem}.run.json"
    record.write_text(
        json.dumps(case_record(session, brief), indent=1, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    out["record"] = str(record)
    for src, suffix in (
        (brief.pdf_path, ".pdf"),
        (brief.html_path, ".html"),
        (brief.web_html_path, ".web.html"),
    ):
        if src and Path(src).exists():
            dest = folder / f"{stem}{suffix}"
            if Path(src).resolve() != dest.resolve():
                shutil.copyfile(src, dest)
            out[suffix] = str(dest)
    return out


def sync_cases(session: Session, out_root: Path | str) -> list[dict[str, str]]:
    """Export every full case (a brief with an app page) that has no record file yet — the
    daily run's own brief and any case rebuilt from the backlog — so the repo carries them.
    Briefs that were themselves imported from a record are skipped (they already have one)."""
    out_root = Path(out_root)
    written: list[dict[str, str]] = []
    briefs = session.scalars(
        select(Brief).where(Brief.web_html_path.is_not(None)).order_by(Brief.run_date, Brief.id)
    ).all()
    for brief in briefs:
        d = brief.brief_data or {}
        if d.get("engine_case_key"):
            continue
        stem = Path(brief.pdf_path or brief.web_html_path or "case").stem.replace(".web", "")
        stem = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", stem)  # storage copies carry a date prefix
        record = out_root / brief.run_date.isoformat() / f"{stem}.run.json"
        if record.exists():
            continue
        written.append(export_case(session, brief, out_root, stem))
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.case_record")
    parser.add_argument("number", type=int, nargs="?", help="brief number to export")
    parser.add_argument(
        "--sync", action="store_true", help="export every full case that has no record yet"
    )
    parser.add_argument("--out", default="pipeline/intel/cases", help="cases folder")
    parser.add_argument("--stem", default=None, help="file stem (default: from the PDF name)")
    args = parser.parse_args(argv)
    from intel.db import session_scope

    with session_scope() as session:
        if args.sync:
            print(json.dumps(sync_cases(session, args.out), indent=1))
            return 0
        if args.number is None:
            parser.error("give a brief number or --sync")
        brief = session.scalar(select(Brief).where(Brief.brief_number == args.number))
        if brief is None:
            print(f"no brief N° {args.number}")
            return 1
        print(json.dumps(export_case(session, brief, args.out, args.stem), indent=1))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
