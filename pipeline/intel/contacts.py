"""The decision path for each company (``data/contacts.json``).

A brief names ONE decision-maker — usually the founder or CEO, because that is who fronts a
capital event. But a sponsorship is bought by a marketing or commercial owner, so the MD's
first question about any signal is "who do I actually call?" (operator request, 6 Sep 2026).
This file answers it: for every company in the desk, the people who would own, sponsor or
veto a three-year deal.

Shape — one record per company, every person carrying the page they were read from::

    {"checked_at": "2026-09-06",
     "companies": [
       {"company": "Fluidstack",
        "people": [
          {"name": "…", "role": "Chief Marketing Officer", "seat": "marketing",
           "source_url": "https://…/leadership", "note": "…", "status": "verified"}],
        "no_cmo": true,
        "note": "no marketing officer is listed on the leadership page (checked 6 Sep 2026)"}]}

``seat`` is what the person is FOR, so the app can order them: ``marketing`` (the buyer),
``commercial`` (revenue/partnerships), ``executive`` (the cheque), ``technical`` (the
counterpart who has to want it), ``regional`` (e.g. President EMEA for a European series).

Rules, and they are the point of the file: a person is listed only when a real page names
them in that role. ``no_cmo`` is a finding, not a gap — plenty of engineering-led companies
genuinely have no CMO, and inventing one would be the worst thing the desk could do.
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.models import Contact

CONTACTS_FILE = Path(__file__).resolve().parents[2] / "data" / "contacts.json"

SEAT_ORDER = ["marketing", "commercial", "regional", "executive", "technical"]
SEAT_LABEL = {
    "marketing": "Marketing owner",
    "commercial": "Commercial owner",
    "regional": "Regional lead",
    "executive": "Executive sponsor",
    "technical": "Technical counterpart",
}


def load_contacts(path: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Records keyed by normalised company name; empty when the file is absent."""
    from intel.normalise import company_norm

    p = Path(path) if path else CONTACTS_FILE
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    rows = data.get("companies", data) if isinstance(data, dict) else data
    out: dict[str, dict[str, Any]] = {}
    for rec in rows:
        if not isinstance(rec, dict) or not rec.get("company"):
            continue
        rec = dict(rec)
        rec.setdefault("checked_at", data.get("checked_at") if isinstance(data, dict) else None)
        rec["people"] = sort_people(rec.get("people") or [])
        out[company_norm(rec["company"])] = rec
    return out


def sort_people(people: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Marketing first — that is who buys — then commercial, regional, executive, technical."""

    def key(p: dict[str, Any]) -> tuple[int, str]:
        seat = (p.get("seat") or "").lower()
        rank = SEAT_ORDER.index(seat) if seat in SEAT_ORDER else len(SEAT_ORDER)
        return (rank, str(p.get("name") or ""))

    return sorted([p for p in people if p.get("name") and p.get("role")], key=key)


def primary_contact(rec: dict[str, Any] | None) -> dict[str, Any] | None:
    """The one person to call first: the marketing owner if there is one, else the top seat."""
    if not rec:
        return None
    people = rec.get("people") or []
    return people[0] if people else None


def summary(contacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    recs = list({id(r): r for r in contacts.values()}.values())
    with_marketing = sum(
        1 for r in recs if any((p.get("seat") or "") == "marketing" for p in r.get("people", []))
    )
    return {
        "companies": len(recs),
        "people": sum(len(r.get("people") or []) for r in recs),
        "with_marketing_owner": with_marketing,
        "no_cmo_confirmed": sum(1 for r in recs if r.get("no_cmo")),
        "checked_at": next((r.get("checked_at") for r in recs if r.get("checked_at")), None),
    }


def attach(entries: list[dict[str, Any]], contacts: dict[str, dict[str, Any]]) -> int:
    """Hang each row's decision path off it for the app. Rows with no record are untouched."""
    from intel.normalise import company_norm

    n = 0
    for e in entries:
        rec = contacts.get(company_norm(e.get("company") or ""))
        if not rec:
            continue
        e["contacts"] = rec
        first = primary_contact(rec)
        if first:
            e["contact_primary"] = first
        n += 1
    return n


# ---------------------------------------------------------------------------------------
# The database side (build brief §8 People panel, §11.7): contact records fetched from a
# provider and stored per person + company. Rules regardless of provider: never scrape
# LinkedIn, never guess email patterns, display only what the provider returns, store the
# provider and the retrieved date on every record, honour opt-outs, keep a UK GDPR
# legitimate-interest basis on the record. The provider is a paid service that needs approval
# (§0.5, §11.7); until then ``NullProvider`` is wired and the People panel shows the verified
# role only. This section was dropped when the file was rewritten around ``contacts.json``
# (7 Sep 2026) and the API's People routes went red in CI; restored 10 Sep 2026.
# ---------------------------------------------------------------------------------------


@dataclass
class ContactRecord:
    person_name: str
    title: str | None
    linkedin_url: str | None
    email: str | None
    phone: str | None
    provider: str
    provider_record_id: str | None


class ContactProvider(Protocol):
    name: str

    def lookup(self, person_name: str, company: str) -> ContactRecord | None: ...


class NullProvider:
    name = "none"

    def lookup(self, person_name: str, company: str) -> ContactRecord | None:
        return None


def provider_for(name: str | None) -> ContactProvider:
    # "apollo" → ApolloProvider once approved and an API key is configured (§11.7).
    return NullProvider()


def find_contact(session: Session, person_name: str, company: str) -> Contact | None:
    from intel.normalise import company_norm

    return session.scalar(
        select(Contact)
        .where(
            Contact.company_norm == company_norm(company), Contact.person_name.ilike(person_name)
        )
        .order_by(Contact.id.desc())
    )


def store_contact(session: Session, rec: ContactRecord, company: str) -> Contact:
    from intel.normalise import company_norm

    row = find_contact(session, rec.person_name, company)
    if row is None:
        row = Contact(person_name=rec.person_name, company_norm=company_norm(company))
        session.add(row)
    row.title = rec.title
    row.linkedin_url, row.email, row.phone = rec.linkedin_url, rec.email, rec.phone
    row.source_provider, row.provider_record_id = rec.provider, rec.provider_record_id
    row.retrieved_at = dt.datetime.now(dt.UTC)
    session.flush()
    return row
