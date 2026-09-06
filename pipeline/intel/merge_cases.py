"""Merge the case files built on ``cases/*`` branches into this checkout, and turn every
screen-out into a review decision the desk app honours.

Parallel case builders (``docs/CASE_SPEC.md``) each push to their own branch and only ever
add files under ``pipeline/intel/cases/<date>/``. Merging is therefore a file copy, not a
git merge: every case path a branch added or changed is checked out from that branch.

    python -m intel.merge_cases                     # fetch origin cases/*, collect, apply
    python -m intel.merge_cases --no-fetch          # use what is already fetched
    python -m intel.merge_cases --apply-only        # just the screened → review step

A ``<stem>.screened.json`` (``{"company", "date", "verdict", "reason", "sources",
"duplicate_of"?}``) becomes a row in ``data/history_review.json``: ``duplicate_of`` points
at the case it duplicates (``date|company`` of that record); ``contradicted`` /
``existing_partner`` / ``stale`` screen the row out with the reason. The export hides
screened rows and folds duplicates, so a screen-out is visible as a decision, never as a
silently missing signal.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = Path(__file__).resolve().parent / "cases"
REVIEW_FILE = REPO_ROOT / "data" / "history_review.json"
CASES_REL = "pipeline/intel/cases"
SCREEN_VERDICTS = {"contradicted", "existing_partner", "stale", "duplicate_of"}


def _git(*args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def fetch(pattern: str = "cases/*") -> None:
    _git("fetch", "-q", "origin", f"+refs/heads/{pattern}:refs/remotes/origin/{pattern}")


def case_branches(pattern: str = "cases/") -> list[str]:
    out = _git("branch", "-r", "--list", f"origin/{pattern}*")
    return sorted(line.strip() for line in out.splitlines() if line.strip())


def collect(branches: list[str], base: str = "origin/main") -> dict[str, list[str]]:
    """Check out every case file each branch added or changed (relative to ``base``)."""
    taken: dict[str, list[str]] = {}
    for ref in branches:
        files = [
            f
            for f in _git("diff", "--name-only", f"{base}...{ref}", "--", CASES_REL).split()
            if f.startswith(CASES_REL + "/")
        ]
        if not files:
            taken[ref] = []
            continue
        _git("checkout", ref, "--", *files)
        taken[ref] = files
    return taken


# --- screened → review ----------------------------------------------------------------


def _record_identity(path: Path) -> tuple[str, str] | None:
    """(run date, company) of a case record next to / named by a duplicate_of pointer."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    cands = data.get("candidates") or []
    company = next((c.get("company") for c in cands if c.get("decision") == "selected"), None)
    company = company or (cands[0].get("company") if cands else None)
    date = (data.get("run") or {}).get("date")
    return (date, company) if date and company else None


def resolve_duplicate(pointer: str | None, cases_dir: Path) -> tuple[str, str] | None:
    """A duplicate_of pointer may be a stem, a path, or 'N° 121': find the case record."""
    if not pointer:
        return None
    p = pointer.strip()
    if p.lower().startswith(("n°", "no", "n ")):
        digits = "".join(ch for ch in p if ch.isdigit())
        for rec in sorted(cases_dir.glob("*/*.run.json")):
            try:
                if str(json.loads(rec.read_text(encoding="utf-8"))["brief"]["number"]) == digits:
                    return _record_identity(rec)
            except (OSError, ValueError, KeyError):
                continue
        return None
    stem = Path(p).name.replace(".run.json", "").replace(".case.json", "")
    stem = stem.split(".")[0]
    for rec in sorted(cases_dir.glob(f"*/{stem}.run.json")):
        return _record_identity(rec)
    return None


def apply_screened(
    cases_dir: Path | str = CASES_DIR, review_path: Path | str = REVIEW_FILE
) -> dict[str, Any]:
    cases_dir, review_path = Path(cases_dir), Path(review_path)
    review = (
        json.loads(review_path.read_text(encoding="utf-8"))
        if review_path.exists()
        else {"_meta": {}, "rows": {}}
    )
    rows = review.setdefault("rows", {})
    applied: list[dict[str, Any]] = []
    skipped: list[str] = []
    for f in sorted(cases_dir.glob("*/*.screened.json")):
        try:
            s = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as exc:
            skipped.append(f"{f}: {exc}")
            continue
        company, date = s.get("company"), s.get("date") or f.parent.name
        verdict = (s.get("verdict") or "").strip().lower()
        if not company or verdict not in SCREEN_VERDICTS:
            skipped.append(f"{f}: needs company + verdict in {sorted(SCREEN_VERDICTS)}")
            continue
        key = f"{date}|{company}"
        reason = (s.get("reason") or "").strip()
        sources = [u for u in (s.get("sources") or []) if isinstance(u, str)]
        decision: dict[str, Any]
        if verdict == "duplicate_of":
            target = resolve_duplicate(s.get("duplicate_of") or s.get("of"), cases_dir)
            if target:
                decision = {
                    "status": "duplicate_of",
                    "of": f"{target[0]}|{target[1]}",
                    "reason": reason or f"same company as the case built on {target[0]}",
                    "reason_code": "case_screen",
                }
            else:
                decision = {
                    "status": "screened_out",
                    "reason": "duplicate: " + (reason or "already covered by a full case"),
                    "reason_code": "case_screen",
                }
        else:
            decision = {
                "status": "screened_out",
                "reason": f"{verdict.replace('_', ' ')}: {reason}".strip(": "),
                "reason_code": "case_screen",
            }
        if sources:
            decision["sources"] = sources[:5]
        decision["screened_at"] = s.get("screened_at") or dt.date.today().isoformat()
        rows[key] = decision
        applied.append({"key": key, **decision})
    review.setdefault("_meta", {})["case_screens_applied_at"] = dt.date.today().isoformat()
    review_path.write_text(
        json.dumps(review, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {"applied": applied, "skipped": skipped, "review_file": str(review_path)}


def inventory(cases_dir: Path | str = CASES_DIR) -> dict[str, Any]:
    cases_dir = Path(cases_dir)
    built: list[dict[str, Any]] = []
    for rec in sorted(cases_dir.glob("*/*.run.json")):
        try:
            data = json.loads(rec.read_text(encoding="utf-8"))
        except ValueError:
            continue
        ident = _record_identity(rec)
        built.append(
            {
                "number": (data.get("brief") or {}).get("number"),
                "company": ident[1] if ident else rec.stem,
                "date": rec.parent.name,
                "verification": (data.get("brief") or {}).get("verification_status"),
                "audit": (data.get("brief") or {}).get("audit_status"),
                "pages": (data.get("brief") or {}).get("pages"),
            }
        )
    screened = [str(p.relative_to(cases_dir)) for p in sorted(cases_dir.glob("*/*.screened.json"))]
    return {"built": built, "screened": screened}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.merge_cases", description=__doc__)
    parser.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--apply-only", action="store_true")
    parser.add_argument("--pattern", default="cases/", help="remote branch prefix")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    result: dict[str, Any] = {}
    if not args.apply_only:
        if not args.no_fetch:
            fetch(args.pattern + "*")
        branches = case_branches(args.pattern)
        result["branches"] = collect(branches)
    result["screened"] = apply_screened()
    result["inventory"] = inventory()
    print(json.dumps(result, indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
