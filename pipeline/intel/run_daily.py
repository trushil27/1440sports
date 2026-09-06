"""Daily orchestrator — idempotent per date (§4, §6, §9.8).

Stages: scan → parse → freshness → blocklist/dedup → gates+score → select →
verify key facts (ledger stage A) → write → 13-rule audit (one retry) → verify the
written text (ledger stage B) → render → [send: M5].

A candidate whose ledger is *blocked* (stage A or B) is set aside and the next eligible
candidate is tried, up to ``max_verification_attempts``, before the day is declared
no-signal (§6.5). A brief that fails the audit after its retry is kept for operator review
and never becomes MD-eligible (§6.7, §7).
"""

from __future__ import annotations

import datetime as dt
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel import audit, dedup, freshness, render, score, send, verify
from intel import brief as brief_mod
from intel.config import Settings, get_settings
from intel.db import session_scope
from intel.models import (
    AuditStatus,
    Brief,
    Candidate,
    CandidateDecision,
    ExecutionMode,
    Run,
    RunStatus,
    Series,
    ValueMode,
    VerificationStatus,
)
from intel.normalise import company_norm
from intel.parse import ParseError, ScannedSignal
from intel.scan import ScanFailed, run_scan

Scanner = Callable[[dt.date], list[ScannedSignal]]


@dataclass
class RunOutcome:
    run_id: int
    run_date: dt.date
    status: str
    selected_candidate_id: int | None
    brief_id: int | None = None
    verification_status: str | None = None
    audit_status: str | None = None
    pdf_path: str | None = None
    already_ran: bool = False
    summary: dict | None = None


@dataclass
class Stages:
    """Injectable collaborators (real ones by default; fakes in tests)."""

    verifier: verify.Verifier | None = None
    writer: brief_mod.Writer | None = None
    extractor: verify.ClaimExtractor = field(default_factory=verify.NoExtractor)
    font_stack: str = "brand"
    mailer: send.Mailer | None = None
    distribute: bool = True
    # Rebuild mode (``intel.rebuild``): the date may already have a brief, dedup must not
    # suppress the one company being rebuilt, and a second brief on a day that already has
    # a live one is stored with ``historical=True`` (the per-day rule keeps the live one).
    rebuild: bool = False


def progress(msg: str) -> None:
    """One line per stage on stdout so a deploy log shows where a run is (nothing else logs)."""
    print(f"[run {dt.datetime.now(dt.UTC):%H:%M:%S}Z] {msg}", flush=True)


def _existing_outcome(session: Session, run_date: dt.date) -> RunOutcome | None:
    """A completed run (success or no_signal) for the date is final: no re-scan, no re-send.
    Historical imports (M6 backfill) and rebuilt cases never count — they are not this job."""
    issued = session.scalar(
        select(Brief).where(
            Brief.run_date == run_date,
            Brief.verification_status != VerificationStatus.blocked,
            Brief.historical.is_(False),
        )
    )
    if issued is not None:
        run = session.get(Run, issued.candidate.run_id)
        return RunOutcome(
            run.id,
            run_date,
            run.status.value,
            issued.candidate_id,
            issued.id,
            issued.verification_status.value,
            issued.audit_status.value,
            issued.pdf_path,
            True,
            run.summary,
        )
    runs = session.scalars(
        select(Run)
        .where(Run.run_date == run_date, Run.status.in_([RunStatus.success, RunStatus.no_signal]))
        .order_by(Run.attempt.desc())
    ).all()
    done = next(
        (
            r
            for r in runs
            if not (r.summary or {}).get("backfill") and not (r.summary or {}).get("rebuild")
        ),
        None,
    )
    if done is not None:
        return RunOutcome(
            done.id, run_date, done.status.value, None, already_ran=True, summary=done.summary
        )
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
    session: Session,
    run: Run,
    signals: list[ScannedSignal],
    run_date: dt.date,
    settings: Settings,
    rebuild: bool = False,
    rank_offset: int = 0,
) -> list[Candidate]:
    """Persist every candidate with its decision. Returns the eligible ones (decision pending).
    One log line per candidate (company, signal date, decision, reason) so a run can be read
    from its log alone."""
    now = dt.datetime.combine(run_date, dt.time(hour=6), tzinfo=settings.tz)
    eligible: list[Candidate] = []
    for rank, sig in enumerate(signals, start=rank_offset + 1):
        norm = company_norm(sig.company)
        tkey = dedup.trigger_key(sig.trigger_text)
        series = Series(sig.recommended_series) if sig.recommended_series in ("F1", "FE") else None
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
        if dd.suppressed and not rebuild:
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
    for cand in session.scalars(select(Candidate).where(Candidate.run_id == run.id)).all():
        if cand.rank and cand.rank > rank_offset:
            progress(
                f"  {cand.rank:>2}. {cand.company_raw} · signal {cand.raw_json.get('signal_date')}"
                f" · {cand.decision.value}"
                + (f" — {cand.decision_reason}" if cand.decision_reason else "")
                + (f" · score {cand.score_total}" if cand.score_total is not None else "")
            )
    return eligible


def rank_eligible(eligible: list[Candidate], run_date: dt.date) -> list[Candidate]:
    """Selection order: FE first on Tue/Fri (rotation), then by ranking score desc."""
    by_score = sorted(
        eligible, key=lambda c: (c.score_breakdown or {}).get("ranking", 0), reverse=True
    )
    if score.fe_rotation_day(run_date):
        fe = [c for c in by_score if c.series == Series.FE]
        rest = [c for c in by_score if c.series != Series.FE]
        return fe + rest
    return by_score


def _scan_more(scanner, run_date: dt.date, settings: Settings, addendum: str):
    """The freshness retry: an injected scanner that accepts an addendum gets it; the real
    scanner runs with the addendum appended to its prompt."""
    import inspect

    if scanner is None:
        return run_scan(run_date, settings=settings, addendum=addendum).signals
    try:
        n_params = len(inspect.signature(scanner).parameters)
    except (TypeError, ValueError):
        n_params = 1
    if n_params >= 2:
        return scanner(run_date, addendum)
    return []


def _signal_of(cand: Candidate) -> ScannedSignal:
    return ScannedSignal.model_validate(cand.raw_json)


def verify_candidate(
    session: Session,
    cand: Candidate,
    run_date: dt.date,
    verifier: verify.Verifier,
    historical: bool = False,
) -> tuple[Brief, verify.LedgerResult]:
    """Create the Brief row for ``cand`` and run the pre-write claims ledger on its key facts.
    ``historical`` is set by a rebuild on a day that already has a live brief."""
    brief = Brief(candidate_id=cand.id, run_date=run_date, historical=historical)
    session.add(brief)
    session.flush()
    sig = _signal_of(cand)
    drafts = verify.claims_from_signal(sig)
    result = verify.run_ledger(session, brief, drafts, sig.company, run_date, verifier)
    return brief, result


def produce_brief(
    session: Session,
    cand: Candidate,
    brief: Brief,
    run_date: dt.date,
    settings: Settings,
    stages: Stages,
) -> dict:
    """write → audit (one retry) → stage-B ledger → render. Returns a log dict for the run."""
    log: dict = {"brief_id": brief.id}
    sig = _signal_of(cand)
    ops_fit = (cand.score_breakdown or {}).get("ops_fit")
    mode = render.value_mode_for(ops_fit, sig.industry_meta)
    number = f"{brief.brief_number:03d}"

    if stages.writer is None:
        brief.audit_violations = [
            {"note": "writer unavailable (no ANTHROPIC_API_KEY); brief not written"}
        ]
        log["written"] = False
        return log

    written = None
    audit_res = None
    feedback: str | None = None
    attempts = 0
    for attempt in (1, 2):
        attempts = attempt
        progress(f"{sig.company}: writing brief N° {number} (attempt {attempt}, mode {mode})")
        try:
            written, _raw = brief_mod.write_brief(
                sig, number, run_date, mode, stages.writer, settings, feedback
            )
        except ParseError as exc:
            feedback = f"1. BRIEF_DATA could not be parsed: {exc}"
            written = None
            continue
        audit_res = audit.audit_brief(written, run_date)
        progress(f"{sig.company}: audit {audit_res.route} ({len(audit_res.violations)} violations)")
        if audit_res.route == "pass":
            break
        feedback = audit.violations_feedback(audit_res)

    brief.audit_attempts = attempts
    if written is None or audit_res is None:
        brief.audit_status = AuditStatus.failed
        brief.audit_violations = [{"rule": 0, "code": "unparseable", "message": feedback}]
        log.update(written=False, audit="failed")
        return log

    brief.brief_data = written.model_dump()
    brief.mode = ValueMode(mode)
    brief.audit_violations = [
        {
            "rule": v.rule,
            "code": v.code,
            "severity": v.severity,
            "field": v.field,
            "message": v.message,
        }
        for v in audit_res.violations
    ]
    if audit_res.route == "pass":
        brief.audit_status = AuditStatus.passed if attempts == 1 else AuditStatus.pass_after_retry
    else:
        brief.audit_status = AuditStatus.failed
    log.update(written=True, audit=brief.audit_status.value, audit_attempts=attempts)

    # Stage B: every claim in the written text joins the ledger; the status is re-decided
    # over the whole ledger.
    drafts = verify.merge_claims(
        verify.claims_from_brief(written), stages.extractor.extract(written)
    )
    verifier = stages.verifier or verify.default_verifier(settings)
    progress(f"{sig.company}: stage-B verification of {len(drafts)} claims in the written brief")
    result = verify.run_ledger(session, brief, drafts, sig.company, run_date, verifier)
    log.update(stage_b=result.counts, verification=result.status.value, blocking=result.blocking)
    progress(f"{sig.company}: stage B {result.status.value} {result.counts}")
    if result.status == VerificationStatus.blocked:
        return log

    # Render (even a failed-audit brief: the operator needs to see it).
    extra = set()
    if sig.key_facts.taxonomy_category:
        extra = render._tokens(sig.key_facts.taxonomy_category)
    data = render.assemble(session, brief, written, run_date, extra)
    brief.brief_data = data.model_dump()  # the full BRIEF_DATA incl. computed panels
    out_dir = Path(settings.pdf_storage_dir) / run_date.isoformat()
    try:
        paths = render.render_brief(data, out_dir, cand.company_norm, stages.font_stack)
    except render.PageOverflow as exc:
        progress(f"{sig.company}: render failed — {exc}")
        brief.audit_status = AuditStatus.failed
        brief.audit_violations = (brief.audit_violations or []) + [
            {"rule": 11, "code": "page_overflow", "severity": "high", "message": str(exc)}
        ]
        log.update(rendered=False, overflow=str(exc))
        return log
    brief.pdf_path = str(paths["pdf"])
    brief.html_path = str(paths["html"])
    brief.page_count = int(paths["pages"])
    log.update(rendered=True, pdf=brief.pdf_path)
    progress(f"{sig.company}: rendered {brief.page_count} pages → {brief.pdf_path}")
    web = render.render_web(data, out_dir / f"{cand.company_norm}.web.html")
    brief.web_html_path = str(web)
    log["web"] = brief.web_html_path
    from intel import highlights as highlights_mod

    log["highlights"] = len(highlights_mod.store_highlights(session, brief))
    return log


def run_day(
    run_date: dt.date,
    settings: Settings | None = None,
    scanner: Scanner | None = None,
    session: Session | None = None,
    verifier: verify.Verifier | None = None,
    stages: Stages | None = None,
) -> RunOutcome:
    """Run the pipeline for one date. Safe to call twice: the second call is a no-op."""
    settings = settings or get_settings()
    if session is None:
        with session_scope() as s:
            return run_day(run_date, settings, scanner, s, verifier, stages)
    stages = stages or Stages()
    if verifier is not None:
        stages.verifier = verifier
    if stages.verifier is None:
        stages.verifier = verify.default_verifier(settings)
    if stages.writer is None and settings.anthropic_api_key:
        stages.writer = brief_mod.AnthropicWriter()
    if stages.mailer is None:
        stages.mailer = send.mailer_for(settings)

    existing = None if stages.rebuild else _existing_outcome(session, run_date)
    if existing is not None:
        return existing

    run = _new_run(session, run_date, settings)
    day_taken = False
    if stages.rebuild:
        run.summary = {"rebuild": True}
        day_taken = (
            session.scalar(
                select(Brief).where(
                    Brief.run_date == run_date,
                    Brief.verification_status != VerificationStatus.blocked,
                    Brief.historical.is_(False),
                )
            )
            is not None
        )
    progress(f"run {run.id} for {run_date} ({settings.execution_mode}): scanning")
    try:
        signals = scanner(run_date) if scanner else run_scan(run_date, settings=settings).signals
    except ScanFailed as exc:
        raw_tail = (exc.raw or "")[-6000:]
        progress(f"scan failed: {exc}")
        if raw_tail:
            progress(f"last scanner text ({len(exc.raw)} chars), tail:\n{raw_tail}")
        run.status, run.error = RunStatus.failed, str(exc)
        run.summary = {"error": str(exc), "scan_raw_tail": raw_tail}
        run.finished_at = dt.datetime.now(dt.UTC)
        session.flush()
        if stages.distribute:
            send.distribute(session, run, settings, stages.mailer, None)
        return RunOutcome(run.id, run_date, "failed", None, summary=run.summary)

    progress(f"scan returned {len(signals)} signals; triaging (freshness, dedup, score)")
    eligible = triage(session, run, signals, run_date, settings, rebuild=stages.rebuild)
    retried = False
    if not eligible and signals and not stages.rebuild:
        # Every candidate fell outside the window: ask once more, for the window only. The
        # scanner tends to return the best-known rounds; a dated retry finds the week's news.
        stale = [c for c in run.candidates if c.decision == CandidateDecision.stale]
        if len(stale) >= max(1, int(0.8 * len(signals))):
            window = settings.freshness_days_track1
            since = run_date - dt.timedelta(days=window)
            listing = "; ".join(
                f"{c.company_raw} ({c.trigger_date or 'undated'})" for c in stale[:12]
            )
            addendum = (
                f"RETRY. Every candidate in your previous answer was older than the {window}-day "
                f"window (you returned: {listing}). Search again and return ONLY companies whose "
                f"trigger event is dated between {since.isoformat()} and {run_date.isoformat()} "
                "inclusive — this week's funding rounds, IPO filings and pricings, spin-offs, "
                "mega-contracts and leadership appointments. Do not return any company listed "
                "above. If you find fewer than 8, return what you find."
            )
            progress(
                f"all {len(stale)} candidates stale — retrying the scan for {since}..{run_date}"
            )
            try:
                more = _scan_more(scanner, run_date, settings, addendum)
            except ScanFailed as exc:
                progress(f"retry scan failed: {exc}")
                more = []
            if more:
                retried = True
                progress(f"retry returned {len(more)} signals; triaging")
                eligible = triage(session, run, more, run_date, settings, rank_offset=len(signals))
                signals = list(signals) + list(more)
    ordered = rank_eligible(eligible, run_date)
    shortlist = ordered[: settings.max_verification_attempts]
    progress(
        f"{len(eligible)} eligible of {len(signals)}; verifying in order: "
        + (", ".join(f"{c.company_raw} ({c.score_total})" for c in shortlist) or "none")
    )
    now = dt.datetime.combine(run_date, dt.time(hour=6), tzinfo=settings.tz)
    verification_log: list[dict] = []
    issued: tuple[Candidate, Brief] | None = None

    for cand in ordered[: settings.max_verification_attempts]:
        cand.decision = CandidateDecision.selected
        why = (
            "FE rotation day (Tue/Fri)"
            if score.fe_rotation_day(run_date) and cand.series == Series.FE
            else "top ranking score"
        )
        cand.decision_reason = f"{cand.decision_reason}; {why}" if cand.decision_reason else why
        progress(f"{cand.company_raw}: stage-A verification of key facts")
        brief, result = verify_candidate(
            session, cand, run_date, stages.verifier, historical=day_taken
        )
        progress(f"{cand.company_raw}: stage A {result.status.value} {result.counts}")
        entry = {
            "candidate_id": cand.id,
            "company": cand.company_raw,
            "brief_id": brief.id,
            "stage_a": result.counts,
            "status": result.status.value,
            "blocking": result.blocking,
        }
        if result.status == VerificationStatus.blocked:
            cand.decision = CandidateDecision.verification_blocked
            cand.decision_reason = "contradicted load-bearing claim: " + " | ".join(result.blocking)
            verification_log.append(entry)
            continue
        entry.update(produce_brief(session, cand, brief, run_date, settings, stages))
        verification_log.append(entry)
        if brief.verification_status == VerificationStatus.blocked:
            cand.decision = CandidateDecision.verification_blocked
            cand.decision_reason = (
                "contradicted load-bearing claim in the written brief: "
                + " | ".join(entry.get("blocking") or [])
            )
            continue
        if stages.rebuild and brief.brief_data is not None:
            brief.brief_data = {
                **brief.brief_data,
                "rebuilt": True,
                "historical": brief.historical,
                "historical_label": f"N° {brief.brief_number}" if brief.historical else None,
            }
        issued = (cand, brief)
        progress(f"{cand.company_raw}: issued as brief N° {brief.brief_number:03d}")
        break

    for cand in ordered:
        if cand.decision == CandidateDecision.pending:
            cand.decision = CandidateDecision.not_selected
            cand.decision_reason = "eligible but outranked"

    counts: dict[str, int] = {}
    all_cands = session.scalars(
        select(Candidate).where(Candidate.run_id == run.id).order_by(Candidate.rank, Candidate.id)
    ).all()  # a query, not the relationship: the retry added rows after it was loaded
    for c in all_cands:
        counts[c.decision.value] = counts.get(c.decision.value, 0) + 1
    run.summary = {
        "candidates": len(signals),
        "decisions": counts,
        "verification": verification_log,
        "candidate_list": [
            {
                "rank": c.rank,
                "company": c.company_raw,
                "signal_date": (c.raw_json or {}).get("signal_date"),
                "decision": c.decision.value,
                "reason": c.decision_reason,
                "score": c.score_total,
            }
            for c in all_cands
        ],
        **({"freshness_retry": True} if retried else {}),
        **({"rebuild": True} if stages.rebuild else {}),
    }
    run.finished_at = dt.datetime.now(dt.UTC)

    if issued is None:
        run.status = RunStatus.no_signal
        session.flush()
        if stages.distribute:
            send.distribute(session, run, settings, stages.mailer, None)
        return RunOutcome(run.id, run_date, "no_signal", None, summary=run.summary)

    cand, brief = issued
    dedup.record_surfaced(
        session,
        cand.company_norm,
        cand.trigger_reason_norm or "other",
        cand.company_raw,
        now,
        brief.id,
    )
    run.status = RunStatus.success
    session.flush()
    if stages.distribute:
        send.distribute(session, run, settings, stages.mailer, brief)
    return RunOutcome(
        run.id,
        run_date,
        "success",
        cand.id,
        brief.id,
        brief.verification_status.value,
        brief.audit_status.value,
        brief.pdf_path,
        summary=run.summary,
    )


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    run_date = dt.date.fromisoformat(argv[0]) if argv else dt.datetime.now(get_settings().tz).date()
    outcome = run_day(run_date)
    print(outcome)
    return 0 if outcome.status != "failed" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
