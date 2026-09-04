"""SEC EDGAR catalyst scanner — free, primary-source detection for born-big events.

EDGAR full-text search (EFTS) indexes exactly the filings that signal an
overnight $1B+ event, before the trade press catches up:

  - Form 10-12B / 10-12B/A  -> SPIN-OFF registration (a new public company)
  - Form S-4  /  425        -> MERGER / business combination
  - Form S-1  /  424B4      -> IPO

This builds the EFTS query for those forms over a recent window and fetches it.
EDGAR is free and needs no key — only a descriptive User-Agent. Where the running
environment's network policy allows SEC egress, this prints fresh filings to
triage into data/catalysts.json. Where SEC is blocked (e.g. a locked-down
sandbox), it prints the exact query URLs so the daily research session can fetch
them with its own web tools instead. Either way it is the detection mechanism.

    python3 engine/edgar_scan.py                 # last 14 days, spin-offs + mergers
    python3 engine/edgar_scan.py --days 30
    python3 engine/edgar_scan.py --forms 10-12B  # spin-offs only
    python3 engine/edgar_scan.py --urls          # just emit the query URLs (no fetch)

Size matters: EFTS cannot filter by valuation, so this surfaces *candidates*;
the human/agent triage step reads the filing and keeps only the $1B+ ones, then
logs them to the catalyst radar.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import urllib.parse
import urllib.request

EFTS = "https://efts.sec.gov/LATEST/search-index"
# Descriptive UA per SEC fair-access policy (https://www.sec.gov/os/webmaster-faq#developers)
UA = "1440 Sports Origination Desk research@1440sports.com"

# The catalyst-bearing form types, grouped by the born-big event they signal.
CATALYST_FORMS = {
    "spinoff": "10-12B",     # registration of a spun-off company's securities
    "merger": "S-4,425",     # business-combination registration + communications
    "ipo": "S-1",            # initial public offering registration
}
DEFAULT_FORMS = ["10-12B", "S-4,425"]   # highest signal-to-noise by default


def build_url(forms: str, startdt: str, enddt: str, q: str | None = None) -> str:
    params = {"forms": forms, "startdt": startdt, "enddt": enddt}
    if q:
        params["q"] = q
    return EFTS + "?" + urllib.parse.urlencode(params)


def fetch(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def hits(payload: dict) -> list[dict]:
    out = []
    for h in payload.get("hits", {}).get("hits", []):
        s = h.get("_source", {})
        names = s.get("display_names") or ["(unknown filer)"]
        out.append({
            "date": s.get("file_date"),
            "form": s.get("root_form") or s.get("form"),
            "filer": names[0],
        })
    return out


def scan(days: int = 14, forms_list: list[str] | None = None,
         urls_only: bool = False, today: _dt.date | None = None) -> int:
    today = today or _dt.date.today()
    start = (today - _dt.timedelta(days=days)).isoformat()
    end = today.isoformat()
    forms_list = forms_list or DEFAULT_FORMS

    print(f"\n1440 · SEC EDGAR catalyst scan  ({start} → {end})")
    print("-" * 72)
    found = 0
    for forms in forms_list:
        label = next((k for k, v in CATALYST_FORMS.items() if v == forms), forms)
        url = build_url(forms, start, end)
        print(f"\n[{label.upper()}]  forms={forms}")
        print(f"  query: {url}")
        if urls_only:
            continue
        try:
            data = fetch(url)
        except Exception as e:  # SEC blocked / network policy / rate limit
            print(f"  ⚠️  could not fetch directly ({type(e).__name__}). "
                  "Fetch the query URL above with the research session's web tools.")
            continue
        rows = hits(data)
        total = data.get("hits", {}).get("total", {}).get("value", len(rows))
        print(f"  {total} filing(s); newest:")
        for row in rows[:10]:
            print(f"    {row['date']}  {row['form']:9} {row['filer']}")
        found += len(rows)
    print("\n" + "-" * 72)
    print("Triage: open each filing, keep only the $1B+ entities, then add them to "
          "data/catalysts.json (type/counterparty/event_date/status/valuation/"
          "source) and run `python3 engine/catalysts.py`.\n")
    return found


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SEC EDGAR born-big catalyst scanner")
    ap.add_argument("--days", type=int, default=14, help="look-back window (default 14)")
    ap.add_argument("--forms", help="comma form group, e.g. '10-12B' or 'S-4,425' "
                    "(default: spin-offs + mergers)")
    ap.add_argument("--urls", action="store_true", help="only emit query URLs, no fetch")
    args = ap.parse_args()
    forms_list = [args.forms] if args.forms else None
    scan(days=args.days, forms_list=forms_list, urls_only=args.urls)
