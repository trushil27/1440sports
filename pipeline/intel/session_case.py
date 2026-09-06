"""Build a full, verified case from a *case spec* — no API key, no model call.

The daily pipeline's scanner, verifier and writer are model stages behind interfaces. A case
spec is what a person (or a Claude session doing the research by hand) supplies in their
place: the scanned signal, the evidence each claim rests on, and the written brief. The
CODE stages run unchanged — freshness, dedup, scoring, the claims ledger with the calendar
and sponsor-table checks, the 13-rule audit, the 2-page render, the app page — so a
session-built case is held to exactly the standard of a model-built one and is stored as
the same case record (``<company>.run.json``) the app and the backfill understand.

    python -m intel.session_case spec.json check      # audit + word ceilings + claim coverage
    python -m intel.session_case spec.json build      # temp Postgres → case record in cases/
    python -m intel.session_case spec.json build --database-url postgresql://…  # use a DB

Spec (JSON)::

    {
      "run_date": "2026-09-06",              # the day the brief is issued for (rebuild date)
      "signal_date": "2026-09-03",           # the trigger date (must be inside the window)
      "stem": "fluidstack",                  # file stem of the case record
      "number": 128,                         # optional: brief number to issue (else next)
      "session_model": "claude-session-2026-09-06",
      "signal": { …ScannedSignal fields… },
      "evidence": [ {"needles": ["gary wu"], "url": "…", "excerpt": "…", "method": "manual"} ],
      "brief": { …WrittenBrief fields (brief_number may be empty)… },
      "note": "markdown: what was checked, what is only REPORTED, what was screened out"
    }

Rules the runner enforces: a claim with no evidence entry is UNVERIFIED (never guessed), a
load-bearing unverified claim leaves the case ``needs_review`` and ``build`` exits 2; a
contradicted claim blocks it and ``build`` exits 3. ``check`` lists every claim the ledger
will extract and whether the spec's evidence covers it, so gaps are visible before a build.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from sqlalchemy import select

from intel import audit, run_daily, verify
from intel.brief_data import WrittenBrief
from intel.config import Settings
from intel.models import Brief, Claim, VerificationMethod, VerificationResult
from intel.parse import ScannedSignal
from intel.verify import Verification

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NEEDS_REVIEW = 2
EXIT_BLOCKED = 3


def load_spec(path: Path | str) -> dict[str, Any]:
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("run_date", "signal", "evidence", "brief"):
        if key not in spec:
            raise ValueError(f"spec is missing '{key}'")
    spec.setdefault("stem", re.sub(r"[^a-z0-9]+", "", spec["signal"]["company"].lower()))
    spec.setdefault("session_model", f"claude-session-{spec['run_date']}")
    if spec.get("signal_date") and not spec["signal"].get("signal_date"):
        spec["signal"]["signal_date"] = spec["signal_date"]
    return spec


def signal_of(spec: dict[str, Any]) -> ScannedSignal:
    return ScannedSignal.model_validate(spec["signal"])


def written_of(spec: dict[str, Any], number: str = "001") -> WrittenBrief:
    return WrittenBrief.model_validate(dict(spec["brief"], brief_number=number))


class SpecVerifier:
    """Substring evidence map: the first entry whose needle appears in the claim text is the
    evidence for it; no match → unverified. Never invents."""

    def __init__(self, spec: dict[str, Any]) -> None:
        self.model = spec["session_model"]
        self.entries = [
            (
                tuple(n.lower() for n in e["needles"]),
                e["url"],
                e.get("excerpt") or "",
                e.get("method") or "manual",
                e.get("notes")
                or "checked in-session against the cited source (search summary; direct "
                "fetch may be egress-blocked)",
            )
            for e in spec["evidence"]
        ]
        self.asked: list[tuple[str, str]] = []

    def match(self, text: str) -> tuple[tuple[str, ...], str, str, str, str] | None:
        low = text.lower()
        for entry in self.entries:
            if any(n in low for n in entry[0]):
                return entry
        return None

    def verify(self, claim: verify.ClaimDraft, company: str) -> Verification:
        hit = self.match(claim.text)
        if hit:
            _, url, excerpt, method, notes = hit
            self.asked.append((claim.text, "verified"))
            return Verification(
                status=VerificationResult.verified,
                method=VerificationMethod(method),
                model=self.model,
                evidence_url=url,
                evidence_excerpt=excerpt,
                notes=notes,
            )
        self.asked.append((claim.text, "unverified"))
        return Verification(
            status=VerificationResult.unverified,
            method=VerificationMethod.manual,
            model=self.model,
            notes="no evidence entry in the case spec covers this sentence",
        )


class SpecWriter:
    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec
        self.calls: list[tuple[str, str]] = []

    def write(self, *, model: str, system: str, user: str) -> str:
        self.calls.append((system, user))
        m = re.search(r"Brief number:\s*(\d+)", user)
        data = dict(self.spec["brief"], brief_number=m.group(1) if m else "")
        sig = json.dumps({"signal_date": self.spec["signal"].get("signal_date")})
        return (
            "<BRIEF_DATA>\n"
            + json.dumps(data, ensure_ascii=False)
            + "\n</BRIEF_DATA>\n<SIGNAL_DATA>"
            + sig
            + "</SIGNAL_DATA>"
        )


# --- check -------------------------------------------------------------------------------


def coverage(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Every claim the ledger will extract (stage A from the signal, stage B from the brief)
    with whether the spec's evidence covers it. Event / sponsorship claims are checked by the
    calendar and sponsor tables at build time and are listed as 'table'."""
    sig = signal_of(spec)
    wb = written_of(spec)
    ver = SpecVerifier(spec)
    rows: list[dict[str, Any]] = []
    for stage, drafts in (
        ("A", verify.claims_from_signal(sig)),
        ("B", verify.claims_from_brief(wb)),
    ):
        for d in drafts:
            if d.claim_type.value in {"event", "sponsorship"}:
                status = "table"
            else:
                status = "covered" if ver.match(d.text) else "UNCOVERED"
            rows.append(
                {
                    "stage": stage,
                    "section": d.section,
                    "type": d.claim_type.value,
                    "load_bearing": d.load_bearing,
                    "status": status,
                    "text": d.text,
                    "event": (d.meta or {}).get("event"),
                }
            )
    return rows


def check(spec: dict[str, Any]) -> dict[str, Any]:
    wb = written_of(spec)
    run_date = dt.date.fromisoformat(spec["run_date"])
    res = audit.audit_brief(wb, run_date)
    words = {
        k: (audit.js_word_count(getattr(wb, k)), ceiling)
        for k, ceiling in audit.WORD_CEILINGS.items()
        if getattr(wb, k, None)
    }
    rows = coverage(spec)
    uncovered = [r for r in rows if r["status"] == "UNCOVERED"]
    return {
        "audit_route": res.route,
        "violations": [f"{v.severity} {v.code}: {v.message}" for v in res.violations],
        "word_counts": words,
        "page2_chars": [audit.page2_chars(wb), audit.PAGE2_BUDGET_WITH_VALUE],
        "claims": len(rows),
        "uncovered": uncovered,
        "events": [r for r in rows if r["type"] == "event"],
        "ok": res.route == "pass" and not [u for u in uncovered if u["load_bearing"]],
    }


def print_check(result: dict[str, Any]) -> None:
    print("audit route:", result["audit_route"])
    for v in result["violations"]:
        print("   ", v)
    for k, (n, ceiling) in result["word_counts"].items():
        flag = "  <-- OVER" if n > ceiling else ""
        print(f"   wc {k}: {n}/{ceiling}{flag}")
    p2, budget = result["page2_chars"]
    print(f"   page2 chars: {p2}/{budget}{'  <-- OVER' if p2 > budget else ''}")
    print(f"claims extracted: {result['claims']}; uncovered: {len(result['uncovered'])}")
    for u in result["uncovered"]:
        lb = "LOAD-BEARING" if u["load_bearing"] else "supporting"
        print(f"   [{lb}] {u['section']}/{u['type']}: {u['text'][:140]}")
    for e in result["events"]:
        print(f"   event mention ({e['section']}): {e['text']} -> {e['event']}")
    print("READY" if result["ok"] else "NOT READY")


# --- build -------------------------------------------------------------------------------


def build(
    spec: dict[str, Any],
    database_url: str,
    out_root: Path | str,
    pdf_dir: Path | str | None = None,
    session=None,
) -> dict[str, Any]:
    from intel.backfill import restart_sequence
    from intel.case_record import export_case
    from intel.db import get_sessionmaker

    if session is None:
        Session = get_sessionmaker(database_url)
        with Session() as s:
            return build(spec, database_url, out_root, pdf_dir, s)

    run_date = dt.date.fromisoformat(spec["run_date"])
    pdf_dir = Path(pdf_dir or tempfile.mkdtemp(prefix="case-pdf-"))
    settings = Settings(
        database_url=database_url,
        execution_mode="dry_run",
        pdf_storage_dir=str(pdf_dir),
        outbox_dir=str(pdf_dir / "outbox"),
        operator_email="desk@1440sports.com",
        # The MD's 90-day trigger window (6 Sep 2026), as the daily workflow sets it.
        freshness_days_track1=int(spec.get("freshness_days") or 90),
        freshness_fallback_days=int(spec.get("freshness_days") or 90),
    )
    verifier = SpecVerifier(spec)
    writer = SpecWriter(spec)
    stages = run_daily.Stages(
        verifier=verifier, writer=writer, font_stack="brand", distribute=False, rebuild=True
    )
    if spec.get("number"):
        restart_sequence(session, int(spec["number"]))
    sig = signal_of(spec)
    out = run_daily.run_day(run_date, settings, lambda _d: [sig], session, stages=stages)
    session.commit()
    result: dict[str, Any] = {
        "status": out.status,
        "verification": out.verification_status,
        "audit": out.audit_status,
        "summary": out.summary,
        "ledger": [],
        "files": {},
    }
    brief = session.get(Brief, out.brief_id) if out.brief_id else None
    if brief is not None:
        result["number"] = brief.brief_number
        result["pages"] = brief.page_count
        result["historical"] = brief.historical
        for cl in session.scalars(
            select(Claim).where(Claim.brief_id == brief.id).order_by(Claim.position, Claim.id)
        ):
            v = cl.verifications[-1] if cl.verifications else None
            result["ledger"].append(
                {
                    "section": cl.section,
                    "type": cl.claim_type.value,
                    "load_bearing": cl.load_bearing,
                    "status": v.status.value if v else "none",
                    "method": v.method.value if v else None,
                    "text": cl.text,
                    "notes": v.notes if v else None,
                }
            )
        # Only a fully verified case leaves the runner: the evidence is the author's to
        # supply, so "needs review" here means "go and find the source", not "ship it".
        if (
            out.status == "success"
            and out.verification_status == "verified"
            and brief.web_html_path
        ):
            stem = spec["stem"]
            result["files"] = export_case(session, brief, out_root, stem)
            note = spec.get("note")
            if note:
                folder = Path(out_root) / run_date.isoformat()
                path = folder / f"{stem}.verification.md"
                path.write_text(note.rstrip() + "\n\n" + ledger_table(result), encoding="utf-8")
                result["files"]["note"] = str(path)
    return result


def ledger_table(result: dict[str, Any]) -> str:
    counts: dict[str, int] = {}
    for row in result["ledger"]:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    lines = [
        f"## Ledger as built (N° {result.get('number')}, "
        + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
        + ")",
        "",
        "| Section | Type | Load-bearing | Status | Claim |",
        "|---|---|---|---|---|",
    ]
    for row in result["ledger"]:
        text = row["text"].replace("|", "/").replace("\n", " ")
        lines.append(
            f"| {row['section']} | {row['type']} | {'yes' if row['load_bearing'] else 'no'} | "
            f"{row['status']} | {text[:160]} |"
        )
    return "\n".join(lines) + "\n"


def print_build(result: dict[str, Any]) -> None:
    print(
        "=== OUTCOME",
        result["status"],
        result["verification"],
        result["audit"],
        f"N° {result.get('number')}" if result.get("number") else "",
        f"pages {result.get('pages')}" if result.get("pages") else "",
        "historical" if result.get("historical") else "",
    )
    for row in result["ledger"]:
        mark = " " if row["status"] == "verified" else "!"
        print(
            f" {mark}[{row['status']:12}] {row['type']:12} {row['section']:16} "
            f"lb={row['load_bearing']} :: {row['text'][:110]}"
        )
    if result["status"] != "success":
        cl = (result["summary"] or {}).get("candidate_list") or []
        for c in cl:
            print("  candidate:", c.get("company"), c.get("decision"), "-", c.get("reason"))
    for k, v in result["files"].items():
        print(f"  {k}: {v}")


def exit_code(result: dict[str, Any]) -> int:
    if result["status"] == "success" and result.get("verification") == "verified":
        return EXIT_OK
    v = result.get("verification")
    if v == "blocked" or any(r["status"] == "contradicted" for r in result["ledger"]):
        return EXIT_BLOCKED
    if v == "needs_review" or any(r["status"] == "unverified" for r in result["ledger"]):
        return EXIT_NEEDS_REVIEW
    return EXIT_ERROR


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.session_case", description=__doc__)
    parser.add_argument("spec", help="case spec JSON")
    parser.add_argument("command", choices=["check", "build"])
    parser.add_argument("--out", default="pipeline/intel/cases", help="cases folder")
    parser.add_argument("--pdf-dir", default=None, help="where the render writes (temp)")
    parser.add_argument(
        "--database-url",
        default=None,
        help="use this database instead of a throw-away cluster (must be migrated + seeded)",
    )
    parser.add_argument(
        "--no-backfill",
        action="store_true",
        help="temp cluster: skip loading the repo's memory (faster; numbering not production)",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    spec = load_spec(args.spec)
    if args.command == "check":
        result = check(spec)
        print_check(result)
        return EXIT_OK if result["ok"] else EXIT_ERROR
    cluster = None
    url = args.database_url
    if not url:
        from intel.tempdb import TempCluster, prepare

        cluster = TempCluster()
        url = cluster.start()
        print("[session_case] temp database", url)
        prepare(url, backfill=not args.no_backfill)
    try:
        result = build(spec, url, args.out, args.pdf_dir)
    finally:
        if cluster is not None:
            cluster.stop()
    print_build(result)
    return exit_code(result)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
