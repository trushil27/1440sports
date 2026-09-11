"""Catch executive changes and listings the day they are filed — from SEC EDGAR, for free.

The operator asked (11 Sep 2026): "someone switching CMO today and starting tomorrow — does
our app trigger it automatically when announced? Does SEC or Nasdaq have those data?"

For US-listed companies, yes: a change of a principal officer is reported on Form 8-K,
Item 5.02 ("Departure of Directors or Certain Officers; Election of Directors; Appointment
of Certain Officers"), within four business days. A listing starts with an S-1 or F-1
(or a 10-12B for a spin-off). EDGAR's full-text search indexes every filing within hours
and has a free JSON endpoint, so the desk can ask each morning: which 8-Ks in the last two
days mention a chief marketing, commercial, revenue or executive officer, and which new
registration statements were filed? The hits land in ``data/trigger_inbox.json`` for the
desk to judge (the ICP call is still a person's), show on the Outreach page, and go into
the Monday report. No model, no key, no cost.

What it does NOT cover, stated plainly: private companies (no filings — the routine, the
scanner and the press wires cover those), and officers below "principal officer" level,
which is why a CMO change at a listed company is not always an 8-K. Nasdaq and the
exchanges publish no executive-change feed of their own; the SEC filing is the source.

    python -m intel.edgar_watch --days 2          # sweep, merge into data/trigger_inbox.json
    python -m intel.edgar_watch --days 2 --print  # sweep, print the hits, do not write
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

EFTS = "https://efts.sec.gov/LATEST/search-index"
USER_AGENT = "1440 Sports intelligence desk (desk@1440sports.com)"
INBOX_FILE = Path(__file__).resolve().parents[2] / "data" / "trigger_inbox.json"

#: Each query is one EFTS full-text search; the label becomes the inbox row's trigger type.
QUERIES: list[tuple[str, str, str]] = [
    ("new_cmo", "8-K", '"Item 5.02" "Chief Marketing Officer"'),
    ("new_cmo", "8-K", '"Item 5.02" "Chief Commercial Officer"'),
    ("new_cmo", "8-K", '"Item 5.02" "Chief Revenue Officer"'),
    ("new_ceo", "8-K", '"Item 5.02" "Chief Executive Officer"'),
    ("listing", "S-1", ""),
    ("listing", "F-1", ""),
    ("spin_off", "10-12B", ""),
]


def efts_url(query: str, form: str, start: dt.date, end: dt.date) -> str:
    params = {
        "q": query,
        "forms": form,
        "dateRange": "custom",
        "startdt": start.isoformat(),
        "enddt": end.isoformat(),
    }
    if not query:
        params.pop("q")
    return EFTS + "?" + urllib.parse.urlencode(params)


def fetch_json(url: str, timeout: float = 30.0) -> dict[str, Any]:
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed SEC host
        return json.loads(resp.read().decode("utf-8"))


def parse_hits(kind: str, form: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    """The rows the desk needs from an EFTS response: company, CIK, form, date, link."""
    rows = []
    for h in (data.get("hits") or {}).get("hits") or []:
        f = h.get("_source") or {}
        names = f.get("display_names") or []
        ciks = f.get("ciks") or []
        adsh = (h.get("_id") or "").split(":")[0]
        cik = str(ciks[0]).lstrip("0") if ciks else ""
        folder = adsh.replace("-", "")
        link = (
            f"https://www.sec.gov/Archives/edgar/data/{cik}/{folder}/{adsh}-index.htm"
            if cik and adsh
            else ""
        )
        rows.append(
            {
                "id": f"{form}:{adsh}",
                "type": kind,
                "form": f.get("form") or form,
                "filed": f.get("file_date"),
                "company": names[0] if names else "",
                "cik": cik,
                "description": f.get("file_description") or "",
                "url": link,
                "judged": False,
            }
        )
    return rows


def sweep(days: int = 2, today: dt.date | None = None, fetch=fetch_json) -> list[dict[str, Any]]:
    today = today or dt.date.today()
    start = today - dt.timedelta(days=days)
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for kind, form, query in QUERIES:
        try:
            data = fetch(efts_url(query, form, start, today))
        except Exception as exc:  # noqa: BLE001 - one failed query must not kill the sweep
            print(f"edgar_watch: {form} {query!r}: {exc}", file=sys.stderr)
            continue
        for row in parse_hits(kind, form, data):
            if row["id"] in seen:
                continue
            seen.add(row["id"])
            row["matched"] = query or form
            out.append(row)
    out.sort(key=lambda r: (r.get("filed") or "", r.get("company") or ""), reverse=True)
    return out


def load_inbox(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path else INBOX_FILE
    if not p.exists():
        return {"_meta": {"what": "EDGAR filings to judge (intel.edgar_watch)"}, "hits": []}
    return json.loads(p.read_text(encoding="utf-8"))


def merge(
    inbox: dict[str, Any],
    hits: list[dict[str, Any]],
    keep_days: int = 60,
    today: dt.date | None = None,
) -> int:
    """Add new hits, keep the desk's judgments on old ones, drop hits older than keep_days."""
    today = today or dt.date.today()
    cutoff = (today - dt.timedelta(days=keep_days)).isoformat()
    have = {h["id"]: h for h in inbox.get("hits") or []}
    added = 0
    for h in hits:
        if h["id"] not in have:
            have[h["id"]] = h
            added += 1
    rows = [h for h in have.values() if (h.get("filed") or "") >= cutoff]
    rows.sort(key=lambda r: (r.get("filed") or "", r.get("company") or ""), reverse=True)
    inbox["hits"] = rows
    inbox.setdefault("_meta", {})["swept_at"] = today.isoformat()
    return added


def save_inbox(inbox: dict[str, Any], path: Path | str | None = None) -> Path:
    p = Path(path) if path else INBOX_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(inbox, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def unjudged(inbox: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    inbox = inbox if inbox is not None else load_inbox()
    return [h for h in inbox.get("hits") or [] if not h.get("judged")]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.edgar_watch", description=__doc__)
    parser.add_argument("--days", type=int, default=2)
    parser.add_argument("--print", action="store_true", help="print the hits, do not write")
    parser.add_argument("--inbox", default=None)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    hits = sweep(args.days)
    if args.print:
        for h in hits:
            print(f"{h['filed']}  {h['form']:<7} {h['type']:<9} {h['company']}  {h['url']}")
        print(f"{len(hits)} hit(s)")
        return 0
    inbox = load_inbox(args.inbox)
    added = merge(inbox, hits)
    save_inbox(inbox, args.inbox)
    print(
        f"edgar_watch: {len(hits)} hit(s) in the last {args.days} day(s), {added} new; "
        f"{len(unjudged(inbox))} to judge"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
