"""Contact data (build brief §8 People panel, §11.7).

Rules regardless of provider: never scrape LinkedIn, never guess email patterns, display
only what the provider returns, store provider + retrieved date on every record, honour
opt-outs, keep a UK GDPR legitimate-interest basis on the record.

The provider itself is a paid service and needs approval (§0.5, §11.7); until then
``NullProvider`` is wired and the People panel shows the verified role only.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.models import Contact
from intel.normalise import company_norm


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
    return session.scalar(
        select(Contact)
        .where(
            Contact.company_norm == company_norm(company), Contact.person_name.ilike(person_name)
        )
        .order_by(Contact.id.desc())
    )


def store_contact(session: Session, rec: ContactRecord, company: str) -> Contact:
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
