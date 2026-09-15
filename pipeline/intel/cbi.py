"""CB Insights API v2 as a structured source of signals — dates, rounds, people, no guessing.

Operator, 15 Sep 2026: "I am trying to get API from CB Insights and PitchBook to get better
signals for us." The desk's web-search scanner gets trigger dates and valuations wrong often
enough to matter (OLIX "2 Sep" was 3 Aug; Walden "3 Aug" was 15 Jul; Positron "tripled" was
about 5x). CB Insights holds the same facts as structured data with the source article URLs,
and holds every executive's title and start date. This module turns that into the desk's own
shapes:

* a daily sweep — companies whose last round closed in the window at a $1B+ valuation (the
  capacity gate as a query filter, not a prompt instruction) — with each round's date, amount,
  post-money valuation, lead and new investors and source URLs;
* the decision path from the management endpoint (CEO / CMO / CCO / CRO, or honestly "none
  listed"), a *new_cmo* / *new_ceo* trigger when such a title started inside the window, and
  leadership ties: any work history at a team or at a brand on the sponsor table;
* ``data/cbi_inbox.json`` for the desk to judge (Outreach page + the Monday report), and
  leads for the 06:00 pool, which the scanner then scores with the structured facts passed as
  its hint — every claim still goes through the ledger like any other candidate.

Credits: every endpoint but ``/v2/organizations`` charges. The client counts charged calls
(weighted by the organisations in the request) and stops at ``CBI_CREDIT_CAP`` per run. The
generative endpoints (scouting reports, ChatCBI, RAG) are not used: the API's own text says
they make mistakes, and nothing generative is evidence here. Mosaic and the other outlook
scores are carried as REPORTED context, never as a fact or a score of ours.

Off until ``CBI_CLIENT_ID`` + ``CBI_CLIENT_SECRET`` are set (GitHub secrets; never the repo).

    python -m intel.cbi --days 7            # sweep, merge into data/cbi_inbox.json
    python -m intel.cbi --days 7 --print    # sweep, print, do not write
    python -m intel.cbi --fixture f.json    # run the parsing on saved responses (no key)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

BASE = "https://api.cbinsights.com"
INBOX_FILE = Path(__file__).resolve().parents[2] / "data" / "cbi_inbox.json"
SEEDS_DIR = Path(__file__).resolve().parent / "seeds"
FREE_PATHS = {"/v2/authorize", "/v2/organizations"}

#: Titles that own or sign a sponsorship, in the order the decision path lists them.
_TITLE_KINDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ceo", ("chief executive", "ceo")),
    ("cmo", ("chief marketing", "cmo", "chief brand")),
    ("cco", ("chief commercial", "cco", "chief revenue", "cro", "chief business")),
    ("cfo", ("chief financial", "cfo")),
    ("coo", ("chief operating", "coo")),
    ("cto", ("chief technology", "cto", "chief product", "cpo")),
    ("cso", ("chief strategy", "cso")),
    ("founder", ("founder", "co-founder")),
)
_TRIGGER_TITLES = {"ceo": "new_ceo", "cmo": "new_cmo", "cco": "new_cmo"}


class CreditCapReached(RuntimeError):
    """The run's charged-call budget is spent; nothing more is fetched this run."""


class CBIError(RuntimeError):
    pass


def http_transport(url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - fixed host
            return json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", "replace")[:400]
        raise CBIError(f"{exc.code} on {url.replace(BASE, '')}: {text}") from exc


class Client:
    """Thin client: bearer auth, one POST per endpoint, a credit counter, a per-run cache."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        transport=http_transport,
        credit_cap: int = 40,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.transport = transport
        self.credit_cap = credit_cap
        self.credits_used = 0
        self.calls: list[str] = []
        self._token: str | None = None
        self._cache: dict[str, dict[str, Any]] = {}

    def token(self) -> str:
        if self._token is None:
            out = self.transport(
                BASE + "/v2/authorize",
                {"clientId": self.client_id, "clientSecret": self.client_secret},
                {"Content-Type": "application/json"},
            )
            self._token = out.get("token") or out.get("accessToken") or out.get("access_token")
            if not self._token:
                raise CBIError("authorize returned no token")
        return self._token

    def post(self, path: str, body: dict[str, Any], weight: int = 1) -> dict[str, Any]:
        key = path + json.dumps(body, sort_keys=True)
        if key in self._cache:
            return self._cache[key]
        charged = path not in FREE_PATHS
        if charged and self.credits_used + weight > self.credit_cap:
            raise CreditCapReached(
                f"{self.credits_used} of {self.credit_cap} credits used; {path} would need {weight}"
            )
        out = self.transport(
            BASE + path,
            body,
            {"Content-Type": "application/json", "Authorization": f"Bearer {self.token()}"},
        )
        if charged:
            self.credits_used += weight
        self.calls.append(path)
        self._cache[key] = out
        return out

    # --- endpoints ---------------------------------------------------------------
    def lookup(self, names: list[str]) -> list[dict[str, Any]]:
        """Name → organisation match. Never charges; use it before spending on a company."""
        out = self.post("/v2/organizations", {"names": names, "limit": 100})
        return out.get("orgs") or out.get("organizations") or []

    def firmographics(self, **filters: Any) -> list[dict[str, Any]]:
        body = {k: v for k, v in filters.items() if v not in (None, [], "")}
        body.setdefault("limit", 50)
        orgs: list[dict[str, Any]] = []
        for _ in range(4):  # at most four pages a run: the sweep is a shortlist, not a census
            out = self.post("/v2/firmographics", body, weight=1)
            orgs.extend(out.get("orgs") or [])
            token = out.get("nextPageToken")
            if not token:
                break
            body = {**body, "nextPageToken": token}
        return orgs

    def fundings(self, org_ids: list[int]) -> list[dict[str, Any]]:
        if not org_ids:
            return []
        out = self.post(
            "/v2/financialtransactions/fundings",
            {"orgIds": org_ids[:100], "limit": 100},
            weight=len(org_ids[:100]),
        )
        return out.get("fundings") or _flatten(out, "fundings")

    def management(self, org_ids: list[int]) -> list[dict[str, Any]]:
        if not org_ids:
            return []
        out = self.post(
            "/v2/managementandboard", {"orgIds": org_ids[:100]}, weight=len(org_ids[:100])
        )
        return out.get("orgs") or out.get("organizations") or _flatten(out, "people", wrap=True)


def _flatten(out: dict[str, Any], key: str, wrap: bool = False) -> list[dict[str, Any]]:
    """Multi-org responses come back either as a flat list or grouped per org; accept both."""
    rows: list[dict[str, Any]] = []
    for org in out.get("results") or out.get("data") or []:
        if wrap:
            rows.append(org)
        else:
            rows.extend(org.get(key) or [])
    return rows


# --- parsing -------------------------------------------------------------------------


def _num(v: Any) -> float | None:
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def _musd(v: float | None) -> str:
    if v is None:
        return ""
    if v >= 1000:
        b = v / 1000
        return f"${b:.1f}B".replace(".0B", "B")
    return f"${v:.0f}M"


def title_kind(title: str | None) -> str | None:
    t = (title or "").lower()
    for kind, needles in _TITLE_KINDS:
        for n in needles:
            if len(n) <= 3:
                if re.search(rf"\b{n}\b", t):
                    return kind
            elif n in t:
                return kind
    return None


def _days_ago(date: str | None, today: dt.date) -> int | None:
    try:
        return (today - dt.date.fromisoformat((date or "")[:10])).days
    except ValueError:
        return None


def sponsor_names(seeds_dir: Path = SEEDS_DIR) -> dict[str, str]:
    """Normalised brand and team names on the grid → display name (for leadership ties)."""
    from intel.normalise import company_norm

    out: dict[str, str] = {}
    try:
        rows = json.loads((seeds_dir / "sponsors.json").read_text(encoding="utf-8"))
        rows = rows if isinstance(rows, list) else rows.get("sponsors") or rows.get("rows") or []
        for r in rows:
            for k in ("brand", "team"):
                if r.get(k):
                    out.setdefault(company_norm(r[k]), r[k])
        profiles = json.loads((seeds_dir / "team_profiles.json").read_text(encoding="utf-8"))
        profiles = profiles if isinstance(profiles, list) else profiles.get("teams") or []
        for p in profiles:
            for k in ("team", "display_name", "teams_json_name"):
                if p.get(k):
                    out.setdefault(company_norm(p[k]), p[k])
    except (OSError, ValueError):
        pass
    for junk in ("", "f1", "fe", "formulae", "formula1"):
        out.pop(junk, None)
    return out


def latest_round(fundings: list[dict[str, Any]], org_id: int) -> dict[str, Any] | None:
    mine = [
        f
        for f in fundings
        if (f.get("recipient") or {}).get("orgId", org_id) == org_id and not f.get("isExit")
    ]
    mine.sort(key=lambda f: f.get("date") or "", reverse=True)
    return mine[0] if mine else None


def round_text(f: dict[str, Any]) -> str:
    """One sentence of structured fact for the scanner's hint and the inbox row."""
    amt = _musd(_num(f.get("amountInMillions")))
    val = _musd(_num(f.get("valuationInMillions")))
    leads = [i.get("name") for i in f.get("investors") or [] if i.get("isLead") and i.get("name")]
    news = [
        i.get("name")
        for i in f.get("investors") or []
        if i.get("isNew") and not i.get("isLead") and i.get("name")
    ]
    bits = [f"{amt} {f.get('round') or f.get('simplifiedRound') or 'round'}".strip()]
    if val:
        bits.append(f"at a {val} valuation")
    if f.get("date"):
        bits.append(f"on {f['date']}")
    s = " ".join(bits)
    if leads:
        s += f", led by {', '.join(leads[:4])}"
    if news:
        s += f"; new investors {', '.join(news[:5])}"
    return s


def people_rows(people: list[dict[str, Any]], today: dt.date) -> list[dict[str, Any]]:
    """Current executives with the titles the desk cares about, newest start first."""
    rows = []
    for p in people or []:
        name = " ".join(x for x in (p.get("givenName"), p.get("surname")) if x).strip()
        for w in p.get("workExperience") or []:
            if not w.get("isCurrent", True) or w.get("endDate"):
                continue
            kind = title_kind(w.get("title"))
            if not kind:
                continue
            start = (w.get("startDate") or "")[:10] or None
            rows.append(
                {
                    "name": name,
                    "title": w.get("title"),
                    "kind": kind,
                    "start": start,
                    "days_in_role": _days_ago(start, today),
                    "linkedin": p.get("linkedInUrl"),
                }
            )
    order = {k: i for i, (k, _) in enumerate(_TITLE_KINDS)}
    rows.sort(key=lambda r: (order.get(r["kind"], 9), -(r.get("days_in_role") or 10**6)))
    return rows


def leadership_ties(people: list[dict[str, Any]], names: dict[str, str]) -> list[dict[str, Any]]:
    """Work history or board seats at a team or a sponsor-table brand — the warmest signal."""
    from intel.normalise import company_norm

    ties = []
    for p in people or []:
        who = " ".join(x for x in (p.get("givenName"), p.get("surname")) if x).strip()
        for w in (p.get("workExperience") or []) + (p.get("boardAssociations") or []):
            org = w.get("orgName") or ""
            hit = names.get(company_norm(org))
            if hit:
                ties.append(
                    {
                        "person": who,
                        "at": hit,
                        "title": w.get("title"),
                        "from": (w.get("startDate") or "")[:10] or None,
                        "to": (w.get("endDate") or "")[:10] or None,
                    }
                )
    return ties


def decision_path(execs: list[dict[str, Any]]) -> dict[str, Any]:
    """Who signs: the marketing or commercial owner when listed, else the CEO; and say so."""
    by = {}
    for r in execs:
        by.setdefault(r["kind"], r)
    owner = by.get("cmo") or by.get("cco")
    buyer = owner or by.get("ceo") or by.get("founder")
    path = [by[k] for k in ("ceo", "cfo", "coo", "cto", "cso") if k in by and by[k] is not buyer]
    return {
        "buyer": buyer,
        "path": path[:3],
        "marketing_owner_listed": owner is not None,
    }


def build_rows(
    orgs: list[dict[str, Any]],
    fundings: list[dict[str, Any]],
    management: list[dict[str, Any]],
    today: dt.date,
    lookback_days: int = 7,
    window_days: int = 90,
    names: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Inbox rows from the three responses: one per organisation, with its triggers."""
    names = sponsor_names() if names is None else names
    people_by_org = {int(m.get("orgId") or 0): m.get("people") or [] for m in management}
    rows = []
    for org in orgs:
        org_id = int(org.get("orgId") or 0)
        summary = org.get("summary") or {}
        fin = org.get("financials") or {}
        head = org.get("headcount") or {}
        rnd = latest_round(fundings, org_id)
        execs = people_rows(people_by_org.get(org_id, []), today)
        triggers = []
        if rnd and (_days_ago(rnd.get("date"), today) or 10**6) <= lookback_days:
            triggers.append(
                {
                    "type": "funding_round",
                    "date": rnd.get("date"),
                    "text": round_text(rnd),
                    "amount_musd": _num(rnd.get("amountInMillions")),
                    "valuation_musd": _num(rnd.get("valuationInMillions")),
                    "round": rnd.get("round") or rnd.get("simplifiedRound"),
                    "investors": [
                        i.get("name") for i in rnd.get("investors") or [] if i.get("name")
                    ],
                    "sources": [u for u in rnd.get("sources") or [] if isinstance(u, str)][:6],
                    "deal_id": rnd.get("dealId"),
                }
            )
        for e in execs:
            t = _TRIGGER_TITLES.get(e["kind"])
            if t and e.get("days_in_role") is not None and 0 <= e["days_in_role"] <= window_days:
                triggers.append(
                    {
                        "type": t,
                        "date": e["start"],
                        "text": f"{e['name']} started as {e['title']} on {e['start']}",
                        "person": e["name"],
                        "title": e["title"],
                        "sources": [e["linkedin"]] if e.get("linkedin") else [],
                    }
                )
        if not triggers:
            continue
        loc = summary.get("address") or summary.get("location") or {}
        hq = ", ".join(
            x
            for x in (
                loc.get("city") or summary.get("city"),
                loc.get("stateProvince") or summary.get("state"),
                loc.get("country") or summary.get("country"),
            )
            if x
        )
        primary = triggers[0]
        rows.append(
            {
                "id": f"cbi:{org_id}:{primary.get('deal_id') or primary.get('date')}",
                "org_id": org_id,
                "company": summary.get("name") or org.get("name") or "",
                "url": summary.get("url") or summary.get("website") or "",
                "description": (summary.get("description") or "")[:400],
                "hq": hq,
                "status": summary.get("status") or summary.get("orgStatus"),
                "headcount": head.get("current") or head.get("currentHeadcount"),
                "valuation_musd": _num(fin.get("valuationInMillions") or fin.get("valuation")),
                "total_funding_musd": _num(
                    fin.get("totalFundingInMillions") or fin.get("totalFunding")
                ),
                "revenue": fin.get("revenue") or fin.get("revenueRange"),
                "industry": " · ".join(
                    x
                    for x in (
                        (org.get("taxonomy") or {}).get("sector"),
                        (org.get("taxonomy") or {}).get("industry"),
                        (org.get("taxonomy") or {}).get("subindustry"),
                    )
                    if x
                ),
                "triggers": triggers,
                "trigger_type": primary["type"],
                "trigger_date": primary.get("date"),
                "executives": execs[:8],
                "decision_path": decision_path(execs),
                "leadership_ties": leadership_ties(people_by_org.get(org_id, []), names),
                "sources": primary.get("sources") or [],
                "swept": today.isoformat(),
                "judged": False,
            }
        )
    rows.sort(key=lambda r: r.get("trigger_date") or "", reverse=True)
    return rows


# --- the sweep -------------------------------------------------------------------------


def sweep(
    client: Client,
    today: dt.date,
    days: int = 7,
    min_valuation_musd: float = 1000.0,
    country_ids: list[int] | None = None,
    window_days: int = 90,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Companies that raised in the window at the capacity gate, with rounds and people."""
    note: dict[str, Any] = {"orgs": 0, "rows": 0}
    start = today - dt.timedelta(days=days)
    filters: dict[str, Any] = {
        "minLastFundingDate": start.isoformat(),
        "maxLastFundingDate": today.isoformat(),
        "minValuationInMillions": min_valuation_musd,
        "vcBacked": True,
        "sort": {"field": "lastFundingDate", "direction": "desc"},
    }
    if country_ids:
        filters["countryIds"] = country_ids
    rows: list[dict[str, Any]] = []
    try:
        orgs = client.firmographics(**filters)
        note["orgs"] = len(orgs)
        ids = [int(o.get("orgId")) for o in orgs if o.get("orgId")]
        fundings = client.fundings(ids)
        management = client.management(ids)
        rows = build_rows(orgs, fundings, management, today, days, window_days)
    except CreditCapReached as exc:
        note["credit_cap"] = str(exc)
    except CBIError as exc:
        note["error"] = str(exc)
    note["rows"] = len(rows)
    note["credits_used"] = client.credits_used
    return rows, note


def client_for(settings: Any, transport=http_transport) -> Client | None:
    cid = getattr(settings, "cbi_client_id", None)
    sec = getattr(settings, "cbi_client_secret", None)
    if not cid or not sec:
        return None
    return Client(cid, sec, transport=transport, credit_cap=int(settings.cbi_credit_cap))


# --- the inbox file --------------------------------------------------------------------


def load_inbox(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path else INBOX_FILE
    if not p.exists():
        return {
            "_meta": {
                "what": "CB Insights candidates to judge (intel.cbi): rounds at $1B+ in the "
                "last week, new CEO/CMO starts, with the decision path and leadership ties"
            },
            "hits": [],
        }
    return json.loads(p.read_text(encoding="utf-8"))


def merge(
    inbox: dict[str, Any], rows: list[dict[str, Any]], keep_days: int = 90, today=None
) -> int:
    today = today or dt.date.today()
    cutoff = (today - dt.timedelta(days=keep_days)).isoformat()
    have = {h["id"]: h for h in inbox.get("hits") or []}
    added = 0
    for r in rows:
        if r["id"] in have:
            have[r["id"]].update({k: v for k, v in r.items() if k != "judged"})
        else:
            have[r["id"]] = r
            added += 1
    kept = [h for h in have.values() if (h.get("trigger_date") or h.get("swept") or "") >= cutoff]
    kept.sort(key=lambda r: r.get("trigger_date") or "", reverse=True)
    inbox["hits"] = kept
    inbox.setdefault("_meta", {})["swept_at"] = today.isoformat()
    return added


def save_inbox(inbox: dict[str, Any], path: Path | str | None = None) -> Path:
    p = Path(path) if path else INBOX_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(inbox, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def unjudged(inbox: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    inbox = inbox if inbox is not None else load_inbox()
    rows = [h for h in inbox.get("hits") or [] if not h.get("judged")]
    rows.sort(key=lambda r: r.get("trigger_date") or "", reverse=True)
    return rows


# --- leads for the 06:00 pool ----------------------------------------------------------


def leads(rows: list[dict[str, Any]], known: set[str]) -> list[Any]:
    """Rows with a funding trigger, not already in the desk's memory, as inbox Leads.

    The trigger text carries the structured facts and the source URLs, so the scanner's
    single-company pass (``inbox.enrich``) starts from the numbers rather than searching for
    them. The lead's ``source_url`` is the first source article CB Insights lists.
    """
    from intel.inbox import Lead
    from intel.normalise import company_norm

    out = []
    for r in rows:
        t = next((x for x in r.get("triggers") or [] if x["type"] == "funding_round"), None)
        if t is None or not r.get("company") or company_norm(r["company"]) in known:
            continue
        srcs = [u for u in t.get("sources") or [] if u]
        if not srcs:
            continue  # no article to cite → nothing the ledger could verify; stays in the inbox
        dp = r.get("decision_path") or {}
        buyer = dp.get("buyer") or {}
        out.append(
            Lead(
                company=r["company"],
                source="cbi",
                series=None,
                team=None,
                trigger=f"funding round: {t['text']} (CB Insights; sources: {', '.join(srcs[:3])})",
                trigger_date=t.get("date"),
                source_url=srcs[0],
                person=buyer.get("name"),
                role=buyer.get("title"),
                score=None,
                raw={"cbi_org_id": r.get("org_id"), "leadership_ties": r.get("leadership_ties")},
            )
        )
    return out


def collect(session: Any, settings: Any, today: dt.date, transport=http_transport):
    """(signals for today's pool, a run-record note). Never raises."""
    note: dict[str, Any] = {"status": "off — CBI_CLIENT_ID / CBI_CLIENT_SECRET not set"}
    client = client_for(settings, transport)
    if client is None:
        return [], note
    try:
        rows, note = sweep(
            client,
            today,
            days=int(settings.cbi_lookback_days),
            min_valuation_musd=float(settings.cbi_min_valuation_musd),
            country_ids=list(settings.cbi_country_ids or []),
        )
        inbox = load_inbox()
        note["new_in_inbox"] = merge(inbox, rows, today=today)
        save_inbox(inbox)
        from intel.inbox import as_signals, known_companies

        found = leads(rows, known_companies(session))
        note["offered"] = [x.company for x in found]
        signals = as_signals(found)
        note["candidates"] = len(signals)
        note["status"] = "read"
        return signals, note
    except Exception as exc:  # noqa: BLE001 — a source that fails is a missing source
        note["status"] = f"unavailable: {type(exc).__name__}: {str(exc)[:160]}"
        return [], note


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.cbi", description=__doc__)
    parser.add_argument("--days", type=int, default=None)
    parser.add_argument("--print", action="store_true")
    parser.add_argument("--inbox", default=None)
    parser.add_argument("--cap", type=int, default=None)
    parser.add_argument(
        "--fixture", default=None, help="JSON with orgs/fundings/management responses (no key)"
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    from intel.config import get_settings

    settings = get_settings()
    today = dt.date.today()
    days = args.days or int(settings.cbi_lookback_days)
    if args.fixture:
        fx = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
        rows = build_rows(
            fx.get("orgs") or [], fx.get("fundings") or [], fx.get("management") or [], today, days
        )
        note = {"fixture": args.fixture, "rows": len(rows)}
    else:
        client = client_for(settings)
        if client is None:
            print("cbi: off — set CBI_CLIENT_ID and CBI_CLIENT_SECRET (GitHub secrets)")
            return 0
        if args.cap is not None:
            client.credit_cap = args.cap
        rows, note = sweep(
            client,
            today,
            days=days,
            min_valuation_musd=float(settings.cbi_min_valuation_musd),
            country_ids=list(settings.cbi_country_ids or []),
        )
    if args.print:
        for r in rows:
            t = r["triggers"][0]
            print(f"{t.get('date')}  {t['type']:<13} {r['company']}  {t['text']}")
            dp = r["decision_path"]
            b = dp.get("buyer") or {}
            print(f"    buyer: {b.get('name') or 'none listed'} ({b.get('title') or '—'})")
            for tie in r.get("leadership_ties") or []:
                print(f"    tie: {tie['person']} at {tie['at']} ({tie.get('title')})")
        print(f"{len(rows)} row(s); {note}")
        return 0
    inbox = load_inbox(args.inbox)
    added = merge(inbox, rows, today=today)
    save_inbox(inbox, args.inbox)
    print(f"cbi: {len(rows)} row(s), {added} new, {len(unjudged(inbox))} to judge; {note}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
