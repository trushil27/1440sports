"""Signal-level verification records (``data/signal_checks.json``).

One record per company, produced by a live fact-check of the signal as it is shown in the app:
the trigger event (figures, dates, investors), the named person and role, any existing
motorsport tie, and what has happened since. The file is checked in so the result survives
any database rebuild; ``site_export`` reads it for the app and ``backfill`` writes it into
the claims ledger. The verdict rules live here so both agree.

Statuses written by the checker:
  trigger_status    CONFIRMED | CORRECTED | NOT_FOUND | CONTRADICTED
  person_status     CONFIRMED | CHANGED | NOT_FOUND | NA
  motorsport_status NONE_FOUND | EXISTING_PARTNER | REPORTED_TALKS | OTHER_MOTORSPORT
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from intel.normalise import company_norm

CHECKS_FILE = Path(__file__).resolve().parents[2] / "data" / "signal_checks.json"

VERIFIED = "verified"
NEEDS_REVIEW = "needs_review"
CONTRADICTED = "contradicted"


def load_checks(path: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Records keyed by normalised company name; empty when the file is absent."""
    p = Path(path) if path else CHECKS_FILE
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    rows = data.get("checks", data) if isinstance(data, dict) else data
    out: dict[str, dict[str, Any]] = {}
    for rec in rows:
        if not isinstance(rec, dict) or not rec.get("company"):
            continue
        rec = dict(rec)
        rec.setdefault("checked_at", data.get("checked_at") if isinstance(data, dict) else None)
        out[company_norm(rec["company"])] = rec
        key = rec.get("key") or ""
        if "|" in key:
            out.setdefault(key.split("|", 1)[1], rec)
    return out


def verdict(rec: dict[str, Any]) -> tuple[str, list[str]]:
    """The signal's verification status from a check record, with the reasons.

    verified      trigger CONFIRMED or CORRECTED, person CONFIRMED, CHANGED (the check names
                  the current holder with a source — a correction, shown as such) or NA
    contradicted  trigger CONTRADICTED
    needs_review  anything else (event not found, person not confirmed)
    An existing motorsport partner does not change the verdict — the facts may be right — but
    the app flags it separately, because the lane is not open.
    """
    reasons: list[str] = []
    trig = (rec.get("trigger_status") or "NOT_FOUND").upper()
    person = (rec.get("person_status") or "NA").upper()
    if trig == "CONTRADICTED":
        reasons.append("trigger contradicted by the sources")
        return CONTRADICTED, reasons
    if trig == "NOT_FOUND":
        reasons.append("trigger event not confirmed")
    if trig == "CORRECTED":
        reasons.append("trigger confirmed with corrections")
    if person == "NOT_FOUND":
        reasons.append("named person not confirmed in that role")
    if person == "CHANGED":
        reasons.append("decision-maker updated")
    ok = trig in ("CONFIRMED", "CORRECTED") and person in ("CONFIRMED", "CHANGED", "NA")
    return (VERIFIED if ok else NEEDS_REVIEW), reasons


def screen_reason(rec: dict[str, Any]) -> str | None:
    """Why a checked signal must leave the lists even when its facts hold: the company already
    sits on the grid (an existing F1 / FE partner or supplier) or is on the desk's hard blocklist.
    Same treatment as the September clean-up of existing sponsors (TDK, Nissan …)."""
    if (rec.get("motorsport_status") or "").upper() == "EXISTING_PARTNER":
        return "existing partner: " + (rec.get("motorsport_note") or "").strip()
    notes = rec.get("notes") or ""
    if "DESK BLOCK" in notes.upper() or "hard blocklist" in notes.lower():
        return "on the 1440 hard blocklist"
    return None


def summary(checks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    recs = list({id(r): r for r in checks.values()}.values())
    counts: dict[str, int] = {}
    for r in recs:
        v, _ = verdict(r)
        counts[v] = counts.get(v, 0) + 1
    return {
        "records": len(recs),
        "verified": counts.get(VERIFIED, 0),
        "needs_review": counts.get(NEEDS_REVIEW, 0),
        "contradicted": counts.get(CONTRADICTED, 0),
        "existing_partner": sum(
            1 for r in recs if (r.get("motorsport_status") or "").upper() == "EXISTING_PARTNER"
        ),
        "screened": sum(1 for r in recs if screen_reason(r)),
        "corrected": sum(1 for r in recs if r.get("corrections")),
        "checked_at": next((r.get("checked_at") for r in recs if r.get("checked_at")), None),
    }
