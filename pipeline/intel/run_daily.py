"""Daily orchestrator — idempotent per date (§4, §6, §9.8).

M2 scope: scan → parse → freshness → blocklist/dedup → gates+score → select, all written
to the database. Later milestones add verify → write → audit → render → send after
``select`` (see ``RunOutcome``).
"""

from __future__ import annotations

import datetime as dt
import sys
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel import dedup, freshness, score
from intel.config import Settings, get_settings
from intel.db import session_scope
from intel.models import (
    Brief,
    Candidate,
    CandidateDecision,
    ExecutionMode,
    Run,
    RunStatus,
    Series,
    VerificationStatus,
)
from intel.normalise import company_norm
from intel.parse import ScannedSignal
from intel.scan import ScanFailed, run_scan

Scanner = Callable[[dt.date], list[ScannedSignal]]


@dataclass
class RunOutcome:
    run_id: int
    run_date: dt.date
    status: str
    selected_candidate_id: int | None
    already_ran: bool = False
    summary: dict | None = None


def _existing_outcome(session: Session, run_date: dt.date) -> RunOutcome | None:
    """A completed run (success or no_signal) for the date is final: no re-scan, no re-send."""
    issued = session.scalar(
        select(Brief).where(
            Brief.run_date == run_date, Brief.verification_status != VerificationStatus.blocked
        )
    )
    if issued is not None:
        run = session.get(Run, issued.candidate.run_id)
        return RunOutcome(
            run.id, run_date, run.status.value, issued.candidate_id, True, run.summary
        )
    done = session.scalar(
        select(Run)
        .where(Run.run_date == run_date, Run.status.in_([RunStatus.success, RunStatus.no_signal]))
        .order_by(Run.attempt.desc())
    )
    if done is not None:
        sel = session.scalar(
            select(Candidate.id).where(
                Candidate.run_id == done.id, Candidate.decision == CandidateDecision.selected
            )
        )
        return RunOutcome(done.id, run_date, done.status.value, sel, True, done.summary)
    return None


def _new_run(session: Session, run_date: dt.date, settings: Settings) -> Run:
    prior = session.scalar(select(Run).where(Run.run_date == run_date).order_by(Run.attempt.desc()))
    run = Run(
        run_date=run_date,
        attempt=(prior.attempt + 1) if prior else 1,
        execution_mode=ExecutionMode(settings.execution_mode),
        model_versions={
            "scan": settings.scan_model,
            "writer": settings.writer_model,
            "verify": settings.verify_model,
        },
    )
    session.add(run)
    session.flush()
    return run


def triage(
    session: Session, run: Run, signals: list[ScannedSignal], run_date: dt.date, settings: Settings
) -> list[Candidate]:
    """Persist every candidate with its decision. Returns the eligible ones (decision pending)."""
    now = dt.datetime.combine(run_date, dt.time(hour=6), tzinfo=settings.tz)
    eligible: list[Candidate] = []
    for rank, sig in enumerate(signals, start=1):
        norm = company_norm(sig.company)
        tkey = dedup.trigger_key(sig.trigger_text)
        series = None
        if sig.recommended_series in ("F1", "FE"):
            series = Series(sig.recommended_series)
        cand = Candidate(
            run_id=run.id,
            rank=rank,
            company_raw=sig.company,
            company_norm=norm,
            track=sig.track,
            series=series,
            trigger_reason_raw=sig.trigger_text or None,
            trigger_reason_norm=tkey,
            source_url=sig.source_url,
            source_tier=score.source_tier(sig.source_url),
            raw_json=sig.model_dump(mode="json"),
            recommended_team=sig.recommended_team,
        )
        session.add(cand)
        session.flush()

        window = (
            settings.freshness_days_alumni if sig.track == 2 else settings.freshness_days_track1
        )
        fr = freshness.check_freshness(sig.signal_date, run_date, window)
        cand.trigger_date = fr.trigger_date
        if not fr.fresh:
            cand.decision, cand.decision_reason = CandidateDecision.stale, fr.reason
            continue

        bl = dedup.check_blocklist(session, norm, run_date)
        if bl.blocked:
            cand.decision, cand.decision_reason = CandidateDecision.blocklisted, bl.reason
            continue

        dd = dedup.check_dedup(session, norm, tkey, now, settings.dedup_window_days)
        if dd.suppressed:
            cand.decision, cand.decision_reason = CandidateDecision.dedup_suppressed, dd.reason
            continue
        cand.resurfaced = dd.resurfaced
        if dd.resurfaced:
            cand.decision_reason = dd.reason

        sc = score.score_signal(session, sig, run_date)
        cand.gate_results = sc.gate_results
        cand.score_breakdown = sc.score_breakdown
        cand.alumni_boost = sc.alumni_boost
        cand.score_total = sc.score_total
        cand.tier = sc.tier
        if not sc.ok:
            cand.decision, cand.decision_reason = CandidateDecision.gate_failed, sc.reason
            continue
        if (sc.ranking_score or 0) < settings.md_threshold:
            cand.decision = CandidateDecision.below_threshold
            cand.decision_reason = (
                f"ranking score {sc.ranking_score} < threshold {settings.md_threshold}"
            )
            continue
        eligible.append(cand)
    session.flush()
    return eligible


def select_candidate(
    session: Session, eligible: list[Candidate], run_date: dt.date, settings: Settings
) -> Candidate | None:
    pool = [
        ((c.score_breakdown or {}).get("ranking", 0), c.series.value if c.series else None, c)
        for c in eligible
    ]
    chosen = score.select_top(pool, run_date)
    for c in eligible:
        if c is chosen:
            c.decision = CandidateDecision.selected
            c.decision_reason = (c.decision_reason + "; " if c.decision_reason else "") + (
                "FE rotation day (Tue/Fri)"
                if score.fe_rotation_day(run_date) and c.series == Series.FE
                else "top ranking score"
            )
        else:
            c.decision = CandidateDecision.not_selected
            c.decision_reason = "eligible but outranked"
    session.flush()
    return chosen  # type: ignore[return-value]


def run_day(
    run_date: dt.date,
    settings: Settings | None = None,
    scanner: Scanner | None = None,
    session: Session | None = None,
) -> RunOutcome:
    """Run the M2 stages for one date. Safe to call twice: the second call is a no-op."""
    settings = settings or get_settings()
    if session is None:
        with session_scope() as s:
            return run_day(run_date, settings, scanner, s)

    existing = _existing_outcome(session, run_date)
    if existing is not None:
        return existing

    run = _new_run(session, run_date, settings)
    try:
        signals = scanner(run_date) if scanner else run_scan(run_date, settings=settings).signals
    except ScanFailed as exc:
        run.status, run.error = RunStatus.failed, str(exc)
        run.finished_at = dt.datetime.now(dt.UTC)
        session.flush()
        return RunOutcome(run.id, run_date, "failed", None, summary={"error": str(exc)})

    eligible = triage(session, run, signals, run_date, settings)
    chosen = select_candidate(session, eligible, run_date, settings)
    counts: dict[str, int] = {}
    for c in run.candidates:
        counts[c.decision.value] = counts.get(c.decision.value, 0) + 1
    run.summary = {"candidates": len(signals), "decisions": counts}
    if chosen is None:
        run.status = RunStatus.no_signal
        run.finished_at = dt.datetime.now(dt.UTC)
        session.flush()
        return RunOutcome(run.id, run_date, "no_signal", None, summary=run.summary)

    # M2 boundary: selection is recorded as "surfaced" here. From M3 on, the surfaced_log
    # row is attached to the issued brief (and unwound when verification blocks it).
    now = dt.datetime.combine(run_date, dt.time(hour=6), tzinfo=settings.tz)
    dedup.record_surfaced(
        session, chosen.company_norm, chosen.trigger_reason_norm or "other", chosen.company_raw, now
    )
    run.status = RunStatus.success
    run.finished_at = dt.datetime.now(dt.UTC)
    session.flush()
    return RunOutcome(run.id, run_date, "success", chosen.id, summary=run.summary)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    run_date = dt.date.fromisoformat(argv[0]) if argv else dt.datetime.now(get_settings().tz).date()
    outcome = run_day(run_date)
    print(outcome)
    return 0 if outcome.status != "failed" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
