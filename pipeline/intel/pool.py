"""The day's runner-ups: candidates that cleared the gates and were not the one chosen.

"When we pick the best of 3, the other 2 don't have to be scrapped. It needs to feed into the
app still if they are relevant." (operator, 8 Sep 2026)

Every morning's pool is a dozen candidates; one becomes the brief. Until now the others lived
only in the run record. Now, after the run, the ones that were *relevant* — they passed
freshness, dedup and the gates and scored at or above the threshold — are written to the
repo as ``<date>/pool.json`` next to the day's case, and the next start imports them as thin
rows: visible in the app under their series with a Check badge and a "Build the full case"
button, and in the rebuild backlog. A candidate the ledger BLOCKED (a contradicted claim) is
written too, and shows on the Screened-out page with the claim that sank it — that judgment
is worth as much as the signal.

Nothing here is presented as verified. A runner-up row is exactly what it was in the run:
a scored, fresh, un-verified lead.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.models import Brief, Candidate, CandidateDecision, Run, RunStatus

RELEVANT = {CandidateDecision.not_selected, CandidateDecision.pending}


def _source_of(run: Run, company: str) -> str:
    """Which of the three sources offered this company, from the run's own record."""
    from intel.normalise import company_norm

    offered = ((run.summary or {}).get("sources") or {}).get("offered") or []
    for item in offered:
        name, _, src = str(item).rpartition(" (")
        if company_norm(name) == company_norm(company):
            return src.rstrip(")") or "scanner"
    return "scanner"


def pool_records(session: Session, run: Run, threshold: int) -> list[dict[str, Any]]:
    """Runner-ups (scored at or above the threshold, not chosen) and blocked candidates."""
    from intel.stage import round_stage

    out: list[dict[str, Any]] = []
    for c in session.scalars(
        select(Candidate).where(Candidate.run_id == run.id).order_by(Candidate.rank)
    ).all():
        blocked = c.decision == CandidateDecision.verification_blocked
        relevant = c.decision in RELEVANT and (c.score_total or 0) >= threshold
        if not (blocked or relevant):
            continue
        raw = c.raw_json or {}
        out.append(
            {
                "company": c.company_raw,
                "decision": "blocked" if blocked else "runner_up",
                "reason": c.decision_reason,
                "score": c.score_total,
                "tier": c.tier,
                "series": c.series.value if c.series else None,
                "team": c.recommended_team,
                "trigger": c.trigger_reason_raw,
                "trigger_date": c.trigger_date.isoformat() if c.trigger_date else None,
                "stage": round_stage(c.trigger_reason_raw),
                "source_url": c.source_url,
                "source": _source_of(run, c.company_raw),
                "person": raw.get("person"),
                "role": raw.get("role"),
                "industry": raw.get("industry_meta"),
                "score_breakdown": c.score_breakdown,
                "rank": c.rank,
            }
        )
    return out


def sync_pool(session: Session, out_root: Path | str, threshold: int = 70) -> list[str]:
    """Write ``<date>/pool.json`` for every live daily run that has one. Overwrites: the file
    is the run's record, not an accumulation."""
    written: list[str] = []
    runs = session.scalars(
        select(Run).where(Run.status == RunStatus.success).order_by(Run.run_date, Run.id)
    ).all()
    for run in runs:
        summary = run.summary or {}
        if summary.get("backfill") or summary.get("rebuild") or summary.get("source"):
            continue  # imported memory, not a morning the desk ran
        records = pool_records(session, run, threshold)
        if not records:
            continue
        folder = Path(out_root) / run.run_date.isoformat()
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "pool.json"
        path.write_text(
            json.dumps(
                {"date": run.run_date.isoformat(), "run_id": run.id, "candidates": records},
                indent=1,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        written.append(str(path))
    return written


def load_pools(cases_dir: Path | str) -> list[dict[str, Any]]:
    out = []
    for path in sorted(Path(cases_dir).glob("*/pool.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for rec in data.get("candidates") or []:
            out.append({**rec, "date": data.get("date") or path.parent.name})
    return out


def blocked_rows(cases_dir: Path | str) -> list[dict[str, Any]]:
    """Blocked candidates as screen-out decisions for the app: verdict 'contradicted', the
    ledger's own words as the reason, the candidate's source as the evidence."""
    rows = []
    for rec in load_pools(cases_dir):
        if rec.get("decision") != "blocked":
            continue
        reason = rec.get("reason") or "a load-bearing claim was contradicted"
        rows.append(
            {
                "company": rec["company"],
                "date": rec["date"],
                "series": rec.get("series"),
                "team": rec.get("team"),
                "industry": rec.get("industry"),
                "trigger": rec.get("trigger"),
                "trigger_date": rec.get("trigger_date"),
                "source_url": rec.get("source_url"),
                "score": rec.get("score"),
                "person": rec.get("person"),
                "role": rec.get("role"),
                "stage": rec.get("stage"),
                "review": {
                    "status": "screened_out",
                    "reason": f"contradicted: {reason}",
                    "reason_code": "case_screen",
                    "sources": [u for u in [rec.get("source_url")] if u],
                    "screened_at": rec["date"],
                },
            }
        )
    return rows


def import_pool(session: Session, cases_dir: Path | str) -> dict[str, Any]:
    """Runner-ups become thin historical rows — the same shape as a sweep import — unless
    the desk already carries the company. Idempotent."""
    from sqlalchemy import func

    from intel.backfill import _next_negative_number, _surfaced_at, _upsert_surfaced
    from intel.dedup import trigger_key
    from intel.models import AuditStatus, ExecutionMode, Series, VerificationStatus
    from intel.normalise import company_norm
    from intel.score import source_tier

    created = skipped = 0
    runs_by_date: dict[str, Run] = {}
    for rec in load_pools(cases_dir):
        if rec.get("decision") != "runner_up":
            continue
        norm = company_norm(rec["company"])
        exists = session.scalar(
            select(Brief)
            .join(Candidate, Candidate.id == Brief.candidate_id)
            .where(Candidate.company_norm == norm)
        )
        if exists is not None:
            skipped += 1
            continue
        day = dt.date.fromisoformat(rec["date"])
        # One run per pool date, and its attempt number is the next free one for that date —
        # (run_date, attempt) is unique. The first version used a fixed attempt for every
        # runner-up, so a day with two of them failed the whole backfill (9 Sep 2026: the
        # resend workflow died on it, and the morning run would have too).
        run = runs_by_date.get(rec["date"])
        if run is None:
            last = session.scalar(
                select(func.coalesce(func.max(Run.attempt), 0)).where(Run.run_date == day)
            )
            run = Run(
                run_date=day,
                attempt=int(last or 0) + 1,
                started_at=_surfaced_at(day),
                finished_at=_surfaced_at(day),
                status=RunStatus.success,
                execution_mode=ExecutionMode.production,
                summary={"source": "pool", "backfill": True, "pool_date": rec["date"]},
            )
            session.add(run)
            session.flush()
            runs_by_date[rec["date"]] = run
        series = Series(rec["series"]) if rec.get("series") in ("F1", "FE") else None
        trig = rec.get("trigger")
        cand = Candidate(
            run_id=run.id,
            rank=rec.get("rank") or 1,
            company_raw=rec["company"],
            company_norm=norm,
            track=1,
            series=series,
            trigger_reason_raw=trig,
            trigger_reason_norm=trigger_key(trig) if trig else None,
            trigger_date=dt.date.fromisoformat(rec["trigger_date"])
            if rec.get("trigger_date")
            else None,
            source_url=rec.get("source_url"),
            source_tier=source_tier(rec.get("source_url")),
            raw_json=rec,
            score_total=rec.get("score"),
            score_breakdown=rec.get("score_breakdown"),
            tier=rec.get("tier"),
            recommended_team=rec.get("team"),
            decision=CandidateDecision.not_selected,
            decision_reason=f"runner-up on {rec['date']} ({rec.get('source', 'scanner')})",
        )
        session.add(cand)
        session.flush()
        brief = Brief(
            candidate_id=cand.id,
            run_date=day,
            brief_number=_next_negative_number(session),
            historical=True,
            verification_status=VerificationStatus.needs_review,
            audit_status=AuditStatus.pending,
            brief_data={
                "company": rec["company"],
                "industry_meta": rec.get("industry"),
                "score": rec.get("score"),
                "timing_label": rec.get("tier"),
                "series_label": rec.get("series"),
                "team_label": rec.get("team"),
                "decision_maker_name": rec.get("person"),
                "decision_maker_role": rec.get("role"),
                "deck": trig,
                "historical": True,
                "historical_source": f"pool ({rec.get('source', 'scanner')})",
                "historical_label": f"Runner-up, {rec['date']}",
                "signal_date": rec.get("trigger_date") or rec["date"],
            },
        )
        session.add(brief)
        session.flush()
        if trig:
            _upsert_surfaced(
                session, norm, trigger_key(trig), rec["company"], _surfaced_at(day), brief.id
            )
        created += 1
    session.flush()
    return {"source": "pool", "created": created, "skipped": skipped}
