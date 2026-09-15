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
    # Appointment language, not signature blocks: "as Chief X Officer" appears when someone
    # is appointed or promoted; "Name, Chief Executive Officer" under a signature does not.
    ("new_cmo", "8-K", '"Item 5.02" "as Chief Marketing Officer"'),
    ("new_cmo", "8-K", '"Item 5.02" "as Chief Commercial Officer"'),
    ("new_cmo", "8-K", '"Item 5.02" "as Chief Revenue Officer"'),
    ("new_ceo", "8-K", '"Item 5.02" "as Chief Executive Officer"'),
    ("listing", "S-1", ""),
    ("listing", "F-1", ""),
    ("spin_off", "10-12B", ""),
    # Private rounds, for free (15 Sep 2026, while the CB Insights key is pending): a US
    # private placement is reported on Form D within 15 days of the first sale, with the
    # amount sold and the executive officers and directors named. The sweep keeps filers
    # that sold FORM_D_MIN_USD or more and are not pooled investment funds.
    ("funding_round", "D", ""),
]

#: Form D: the smallest amount sold that is a signal for the desk (a mid-tier F1/FE deal
#: needs a raise in this range or above), and the most XMLs fetched per sweep.
FORM_D_MIN_USD = 25_000_000
FORM_D_MAX_FETCHES = 150

#: SIC industry codes that fit the desk's profile (tech, electrical, industrial, energy,
#: automotive, semiconductors, software, telecoms, crypto/fintech services) and those that
#: never will (banks, REITs, insurers, pharma, biotech, mining, shells). Everything else is
#: "unknown" and still shown, after the in-profile hits.
SIC_IN: tuple[tuple[int, int], ...] = (
    (3500, 3599),  # industrial and commercial machinery, computers
    (3600, 3699),  # electronic and electrical equipment (incl. semiconductors, batteries)
    (3700, 3799),  # transportation equipment (auto parts, aerospace)
    (3800, 3899),  # instruments
    (4800, 4899),  # communications
    (4900, 4999),  # electric, gas, utilities
    (7370, 7379),  # computer programming, software, data processing
    (7380, 7389),  # business services (incl. many fintech / crypto filers)
    (8700, 8748),  # engineering, research, management services
)
SIC_OUT: tuple[tuple[int, int], ...] = (
    (100, 999),  # agriculture
    (1000, 1499),  # mining
    (2830, 2839),  # pharma
    (5000, 5999),  # wholesale, retail
    (6000, 6799),  # banks, insurance, REITs, finance shells
    (6798, 6799),
    (7000, 7099),  # hotels
    (8000, 8099),  # health services
    (8731, 8731),  # biotech research
)


def profile(sic: int | None) -> str:
    if sic is None:
        return "unknown"
    if any(a <= sic <= b for a, b in SIC_OUT):
        return "out"
    if any(a <= sic <= b for a, b in SIC_IN):
        return "in"
    return "unknown"


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


def fetch_text(url: str, timeout: float = 30.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed SEC host
        return resp.read().decode("utf-8", "replace")


def form_d_url(row: dict[str, Any]) -> str:
    """The Form D primary document (XML) next to the filing index."""
    return row["url"].rsplit("/", 1)[0] + "/primary_doc.xml" if row.get("url") else ""


def parse_form_d(xml_text: str) -> dict[str, Any]:
    """Issuer, industry group, amounts, first-sale date and the related persons from Form D."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_text)

    def text(path: str) -> str:
        el = root.find(path)
        return (el.text or "").strip() if el is not None and el.text else ""

    def num(path: str) -> float | None:
        try:
            return float(text(path).replace(",", "")) if text(path) else None
        except ValueError:
            return None

    persons = []
    for p in root.iter("relatedPersonInfo"):
        name = " ".join(
            x.strip()
            for x in (
                (p.findtext("relatedPersonName/firstName") or ""),
                (p.findtext("relatedPersonName/lastName") or ""),
            )
            if x.strip()
        )
        rels = [r.text.strip() for r in p.iter("relationship") if r.text]
        title = (p.findtext("relationshipClarification") or "").strip()
        if name:
            persons.append({"name": name, "relationships": rels, "title": title})
    return {
        "issuer": text("primaryIssuer/entityName"),
        "entity_type": text("primaryIssuer/entityType"),
        "state": text("primaryIssuer/issuerAddress/stateOrCountry"),
        "industry_group": text("offeringData/industryGroup/industryGroupType"),
        "securities": [t.text.strip() for t in root.iter("isEquityType") if t.text]
        + [t.text.strip() for t in root.iter("isDebtType") if t.text],
        "offering_total_usd": num("offeringData/offeringSalesAmounts/totalOfferingAmount"),
        "amount_sold_usd": num("offeringData/offeringSalesAmounts/totalAmountSold"),
        "first_sale": text("offeringData/typeOfFiling/dateOfFirstSale/value"),
        "is_amendment": text("offeringData/typeOfFiling/newOrAmendment/isAmendment"),
        "related_persons": persons[:12],
    }


def enrich_form_d(
    rows: list[dict[str, Any]],
    fetch_page=fetch_text,
    min_usd: float = FORM_D_MIN_USD,
    max_fetches: int = FORM_D_MAX_FETCHES,
) -> list[dict[str, Any]]:
    """Keep the Form D filers worth a look: amount sold at or above ``min_usd``, not a fund,
    not an amendment. Each kept row carries the amounts and the named officers/directors."""
    kept = []
    fetched = 0
    for row in rows:
        if row.get("form") != "D":
            kept.append(row)
            continue
        if row.get("profile") == "out" or fetched >= max_fetches:
            continue
        fetched += 1
        try:
            d = parse_form_d(fetch_page(form_d_url(row)))
        except Exception as exc:  # noqa: BLE001 - one bad XML must not kill the sweep
            print(f"edgar_watch: Form D {row.get('company')}: {exc}", file=sys.stderr)
            continue
        if "pooled investment" in (d["industry_group"] or "").lower():
            continue
        if (d["is_amendment"] or "").lower() == "true":
            continue
        sold = d["amount_sold_usd"] or 0
        if sold < min_usd:
            continue
        officers = [
            p for p in d["related_persons"] if any("Officer" in r for r in p["relationships"])
        ]
        row.update(
            {
                "company": d["issuer"] or row.get("company"),
                "state": d["state"] or row.get("state"),
                "industry_group": d["industry_group"],
                "amount_sold_usd": sold,
                "offering_total_usd": d["offering_total_usd"],
                "first_sale": d["first_sale"],
                "officers": officers[:8],
                "directors": [
                    p
                    for p in d["related_persons"]
                    if "Director" in p["relationships"] and p not in officers
                ][:8],
                "description": (
                    f"Form D: ${sold / 1e6:,.0f}M sold"
                    + (
                        f" of ${d['offering_total_usd'] / 1e6:,.0f}M offered"
                        if d["offering_total_usd"]
                        else ""
                    )
                    + (f"; first sale {d['first_sale']}" if d["first_sale"] else "")
                    + (f"; {d['industry_group']}" if d["industry_group"] else "")
                ),
                "matched": f"Form D, ≥ ${min_usd / 1e6:,.0f}M sold",
            }
        )
        kept.append(row)
    return kept


def parse_hits(kind: str, form: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    """The rows the desk needs from an EFTS response: company, CIK, form, date, link, profile.

    Amendments (S-1/A, F-1/A, 8-K/A) are skipped: the original filing is the trigger."""
    rows = []
    for h in (data.get("hits") or {}).get("hits") or []:
        f = h.get("_source") or {}
        filed_form = f.get("form") or form
        if filed_form.endswith("/A"):
            continue
        names = f.get("display_names") or []
        ciks = f.get("ciks") or []
        sics = f.get("sics") or []
        adsh = (h.get("_id") or "").split(":")[0]
        cik = str(ciks[0]).lstrip("0") if ciks else ""
        folder = adsh.replace("-", "")
        link = (
            f"https://www.sec.gov/Archives/edgar/data/{cik}/{folder}/{adsh}-index.htm"
            if cik and adsh
            else ""
        )
        try:
            sic = int(sics[0]) if sics else None
        except (TypeError, ValueError):
            sic = None
        rows.append(
            {
                "id": f"{form}:{adsh}",
                "type": kind,
                "form": filed_form,
                "filed": f.get("file_date"),
                "company": names[0] if names else "",
                "cik": cik,
                "sic": sic,
                "profile": profile(sic),
                "state": (f.get("biz_states") or [None])[0],
                "description": f.get("file_description") or "",
                "url": link,
                "judged": False,
            }
        )
    return rows


def sweep(
    days: int = 2,
    today: dt.date | None = None,
    fetch=fetch_json,
    fetch_page=fetch_text,
    form_d: bool = True,
) -> list[dict[str, Any]]:
    today = today or dt.date.today()
    start = today - dt.timedelta(days=days)
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for kind, form, query in QUERIES:
        if form == "D" and not form_d:
            continue
        try:
            data = fetch(efts_url(query, form, start, today))
        except Exception as exc:  # noqa: BLE001 - one failed query must not kill the sweep
            print(f"edgar_watch: {form} {query!r}: {exc}", file=sys.stderr)
            continue
        rows = []
        for row in parse_hits(kind, form, data):
            if row["id"] in seen:
                continue
            seen.add(row["id"])
            row["matched"] = query or form
            rows.append(row)
        if form == "D":
            rows = enrich_form_d(rows, fetch_page)
        out.extend(rows)
    out.sort(key=lambda r: r.get("filed") or "", reverse=True)
    out.sort(key=lambda r: _PROFILE_RANK.get(r.get("profile"), 1))  # stable: band, then newest
    return out


_PROFILE_RANK = {"in": 0, "unknown": 1, "out": 2}


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
    rows.sort(key=lambda r: r.get("filed") or "", reverse=True)
    rows.sort(key=lambda r: _PROFILE_RANK.get(r.get("profile"), 1))
    inbox["hits"] = rows
    inbox.setdefault("_meta", {})["swept_at"] = today.isoformat()
    return added


def save_inbox(inbox: dict[str, Any], path: Path | str | None = None) -> Path:
    p = Path(path) if path else INBOX_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(inbox, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def unjudged(
    inbox: dict[str, Any] | None = None, profiles: tuple[str, ...] = ("in", "unknown")
) -> list[dict[str, Any]]:
    """Hits the desk has not judged, in-profile first and newest first within each band;
    off-profile filers (banks, biotech, mining …) stay in the file but out of the list."""
    inbox = inbox if inbox is not None else load_inbox()
    rows = [
        h
        for h in inbox.get("hits") or []
        if not h.get("judged") and (h.get("profile") or "unknown") in profiles
    ]
    rows.sort(key=lambda r: r.get("filed") or "", reverse=True)
    rows.sort(key=lambda r: _PROFILE_RANK.get(r.get("profile"), 1))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.edgar_watch", description=__doc__)
    parser.add_argument("--days", type=int, default=2)
    parser.add_argument("--print", action="store_true", help="print the hits, do not write")
    parser.add_argument("--inbox", default=None)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    hits = sweep(args.days)
    if args.print:
        for h in hits:
            print(
                f"{h['filed']}  {h['form']:<7} {h['type']:<9} {h['profile']:<7} "
                f"{h['company']}  {h['url']}"
            )
        print(f"{len(hits)} hit(s)")
        return 0
    inbox = load_inbox(args.inbox)
    added = merge(inbox, hits)
    save_inbox(inbox, args.inbox)
    counts = {k: sum(1 for h in hits if h.get("profile") == k) for k in ("in", "unknown", "out")}
    print(
        f"edgar_watch: {len(hits)} hit(s) in the last {args.days} day(s) "
        f"(in profile {counts['in']}, unknown {counts['unknown']}, off profile {counts['out']}), "
        f"{added} new; {len(unjudged(inbox))} to judge"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
