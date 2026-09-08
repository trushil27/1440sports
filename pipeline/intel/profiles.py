"""Company profiles for the signals the desk screened out.

"Can you update the signals we eliminated into the app? Company name, their current status on
funds and valuation, what business they are in, why eliminated, a link to their company page,
which team or championship it was ideally fit for, and a small brief about the company and
senior leadership." (operator, 7 Sep 2026)

The desk already holds half of that for every screen-out — the trigger and its figures, the
series and team it was aimed at, the industry line, the verdict, the reasoning and the
sources. It does not hold a website, a funding-and-valuation status as of today, a business
one-liner in plain words, or the leadership. Those live here, one record per company, in
``data/screened_profiles/*.json`` — several files, so parallel research runs never conflict.

Every field is optional and every record carries its sources. A field that could not be
verified is left out, and the app says "not on file" rather than showing a guess: the same
rule as the contacts and the signal checks.

Record shape::

    {
      "company": "Ore Energy",
      "website": "https://ore.energy",
      "business": "Iron-air long-duration batteries that store renewable power for days.",
      "funding": {"status": "€37.3m Series A, Aug 2026 (Plural, HV Capital); total $61m",
                  "valuation": null, "as_of": "2026-09-08"},
      "leaders": [{"name": "Aytac Yilmaz", "role": "Co-founder & CEO",
                   "source": "https://ore.energy/team"}],
      "brief": "Two or three sentences on what the company is and where it stands.",
      "checked_at": "2026-09-08",
      "sources": ["https://…", "https://…"],
      "confidence": "VERIFIED | REPORTED | GAP"
    }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROFILES_DIR = Path(__file__).resolve().parents[2] / "data" / "screened_profiles"

FIELDS = (
    "website",
    "business",
    "funding",
    "leaders",
    "brief",
    "checked_at",
    "sources",
    "confidence",
)


def load_profiles(folder: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Records keyed by normalised company name, from every JSON file in the folder.

    A file is a list of records, or an object with a ``companies`` list. A record without a
    company name is skipped; a later file's record for the same company replaces an earlier
    one, so a re-check simply lands in a newer file."""
    from intel.normalise import company_norm

    d = Path(folder) if folder else PROFILES_DIR
    out: dict[str, dict[str, Any]] = {}
    if not d.is_dir():
        return out
    for path in sorted(d.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rows = data.get("companies", data) if isinstance(data, dict) else data
        for rec in rows if isinstance(rows, list) else []:
            if not isinstance(rec, dict) or not rec.get("company"):
                continue
            out[company_norm(rec["company"])] = {k: rec.get(k) for k in ("company", *FIELDS)}
    return out


def attach(entries: list[dict[str, Any]], profiles: dict[str, dict[str, Any]]) -> int:
    """Hang a profile off each screened row that has one. Rows without stay as they are."""
    from intel.normalise import company_norm

    n = 0
    for e in entries:
        if (e.get("review") or {}).get("status") != "screened_out":
            continue
        rec = profiles.get(company_norm(e.get("company") or ""))
        if rec:
            e["profile"] = rec
            n += 1
    return n


def summary(profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    recs = list(profiles.values())
    return {
        "companies": len(recs),
        "with_website": sum(1 for r in recs if r.get("website")),
        "with_leaders": sum(1 for r in recs if r.get("leaders")),
        "checked_at": max((r.get("checked_at") or "" for r in recs), default=None) or None,
    }


def wanted(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The screened companies that still have no profile — the research worklist, with what
    the desk already knows about each so a researcher starts from the record, not from zero."""
    from intel.normalise import company_norm

    profiles = load_profiles()
    out = []
    for e in entries:
        rv = e.get("review") or {}
        if rv.get("status") != "screened_out" or rv.get("reason_code") != "case_screen":
            continue
        if company_norm(e.get("company") or "") in profiles:
            continue
        out.append(
            {
                "company": e.get("company"),
                "date": e.get("date"),
                "series": e.get("series"),
                "team": e.get("team"),
                "industry": e.get("industry"),
                "trigger": e.get("trigger"),
                "source_url": e.get("source_url"),
                "why": (rv.get("reason") or "")[:400],
            }
        )
    return out
