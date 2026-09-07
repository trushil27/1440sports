"""The desk's other two sources: the Claude routine, and n8n.

The desk was described as three sources feeding one 06:00 pick, and it was one. The pipeline's
own scanner fed the daily brief; the 10:00 Claude routine emailed its list to a human and
nothing read it; n8n's daily brief did the same. Two-thirds of the sourcing was a person
reading email (operator, 7 Sep 2026: "I thought we have 3 sources to see in one app").

This module reads those two mailboxes' worth of signal and turns it into candidates for the
same pool the scanner's go into, so the hero is picked across all three and the run record
says where each came from.

What each source can give:

* **routine** — the Claude routine's mail carries a ``<SIGNALS>[…]</SIGNALS>`` block with the
  company, series, team, trigger, its date, the source URL and a score. That is everything a
  candidate needs, so these enter the day's pool directly and are triaged, verified and
  audited exactly like the scanner's: nothing skips the ledger because of where it came from.
* **n8n** — its mail is a finished brief, not a candidate record: the subject names the
  company and the date, and the trigger is prose inside a rendered page. So an n8n name the
  desk does not already hold is REPORTED — in the run record and the operator's mail — as a
  company to research, rather than being turned into a candidate out of a subject line. It
  can then be built on demand (``intel.rebuild``), which runs a proper single-company scan.

Nothing here invents a field. A lead with no trigger date stays undated and the freshness
stage decides, the same as any other candidate.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass, field
from typing import Any

ROUTINE_SUBJECT = "1440 Routine Signals"
N8N_SUBJECT = "1440 Intelligence Brief"
SIGNALS_BLOCK = re.compile(r"<SIGNALS>\s*(\[.*?\])\s*</SIGNALS>", re.DOTALL)
#: "1440 Intelligence Brief — Keyfactor — 15 Jul 2026" (an em dash, or a hyphen in older mail)
N8N_SUBJECT_RE = re.compile(rf"{N8N_SUBJECT}\s*[—-]\s*(?P<company>.+?)\s*[—-]\s*(?P<date>.+)$")


@dataclass
class Lead:
    """One company offered by a source other than the desk's own scanner."""

    company: str
    source: str  # "routine" | "n8n"
    received: dt.datetime | None = None
    series: str | None = None
    team: str | None = None
    trigger: str | None = None
    trigger_date: str | None = None
    source_url: str | None = None
    person: str | None = None
    role: str | None = None
    score: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def is_candidate(self) -> bool:
        """Enough of a record to enter the day's pool rather than the research backlog."""
        return bool(self.company and self.trigger and self.source_url)


def parse_routine_email(body: str, received: dt.datetime | None = None) -> list[Lead]:
    """The ``<SIGNALS>`` block. A mail without one, or with unreadable JSON, yields nothing —
    the routine's prose summary is for the reader, and guessing at it would invent data."""
    match = SIGNALS_BLOCK.search(body or "")
    if not match:
        return []
    try:
        rows = json.loads(match.group(1))
    except ValueError:
        return []
    leads = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict) or not (row.get("company") or "").strip():
            continue
        score = row.get("score")
        leads.append(
            Lead(
                company=str(row["company"]).strip(),
                source="routine",
                received=received,
                series=(row.get("series") or None),
                team=(row.get("team") or None),
                trigger=(row.get("trigger") or None),
                trigger_date=(row.get("trigger_date") or None),
                source_url=(row.get("source_url") or None),
                person=(row.get("person") or None),
                role=(row.get("role") or None),
                score=int(score) if isinstance(score, int | float) else None,
                raw=row,
            )
        )
    return leads


def parse_n8n_email(subject: str, received: dt.datetime | None = None) -> Lead | None:
    """The company out of the subject line. The body is a rendered brief, not a record."""
    m = N8N_SUBJECT_RE.match((subject or "").strip())
    if not m:
        return None
    company = m.group("company").strip()
    return Lead(company=company, source="n8n", received=received) if company else None


def _iso(value: Any) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


class GraphInbox:
    """Reads the mailbox the desk already sends from, with the token it already has.

    The delegated refresh token is issued with ``.default`` — every permission consented at
    sign-in, which includes Mail.ReadWrite — so no new grant is needed. If the tenant has not
    consented to reading, ``read`` raises and the caller carries on without this source rather
    than failing the day.
    """

    def __init__(self, mailer: Any) -> None:
        self._mailer = mailer

    def read(self, since: dt.datetime, limit: int = 40) -> list[dict[str, Any]]:
        from intel.send import GRAPH

        m = self._mailer
        base = f"{GRAPH}/me" if m.refresh_token else f"{GRAPH}/users/{m.sender}"
        params = {
            "$filter": f"receivedDateTime ge {since.astimezone(dt.UTC):%Y-%m-%dT%H:%M:%SZ}",
            "$select": "subject,receivedDateTime,body",
            "$orderby": "receivedDateTime desc",
            "$top": str(limit),
        }
        r = self._mailer.http.get(
            f"{base}/messages",
            headers={"Authorization": f"Bearer {self._mailer.token()}"},
            params=params,
        )
        r.raise_for_status()
        return r.json().get("value") or []


def leads_from_messages(messages: list[dict[str, Any]]) -> list[Lead]:
    """Every lead the two sources offer, newest mail first, de-duplicated by company."""
    leads: list[Lead] = []
    for msg in messages:
        subject = (msg.get("subject") or "").strip()
        received = _iso(msg.get("receivedDateTime"))
        if subject.startswith(ROUTINE_SUBJECT):
            leads += parse_routine_email((msg.get("body") or {}).get("content") or "", received)
        elif subject.startswith(N8N_SUBJECT):
            lead = parse_n8n_email(subject, received)
            if lead:
                leads.append(lead)
    seen: set[str] = set()
    unique = []
    for lead in leads:
        from intel.normalise import company_norm

        key = company_norm(lead.company)
        if key and key not in seen:
            seen.add(key)
            unique.append(lead)
    return unique


def known_companies(session: Any) -> set[str]:
    """Every company the desk already carries — held, screened or blocklisted — normalised."""
    from sqlalchemy import select

    from intel.models import Blocklist, Candidate
    from intel.normalise import company_norm

    known = {company_norm(c) for c in session.scalars(select(Candidate.company_raw)).all() if c}
    known |= {b for b in session.scalars(select(Blocklist.company_norm)).all() if b}
    from intel.site_export import load_review

    for key, decision in (load_review() or {}).items():
        if decision.get("status") == "screened_out":
            known.add(company_norm(key.partition("|")[2]))
    known.discard("")
    return known


def new_leads(session: Any, messages: list[dict[str, Any]]) -> list[Lead]:
    """Leads for companies the desk does not already hold, has not screened, is not blocked on."""
    from intel.normalise import company_norm

    known = known_companies(session)
    leads = leads_from_messages(messages)
    return [lead for lead in leads if company_norm(lead.company) not in known]


def as_signals(leads: list[Lead]) -> list[Any]:
    """The candidate-shaped leads as ``ScannedSignal``s for the day's pool.

    Track 1, and no score of our own: the source's number is a hint, and the desk's scoring
    stage recomputes it from the same five dimensions it uses for everything else.
    """
    from intel.parse import ScannedSignal

    out = []
    for lead in leads:
        if not lead.is_candidate:
            continue
        try:
            out.append(
                ScannedSignal.model_validate(
                    {
                        "company": lead.company,
                        "score": int(lead.score or 0),
                        "signal_date": lead.trigger_date,
                        "trigger_reason": lead.trigger,
                        "source_url": lead.source_url,
                        "person": lead.person,
                        "role": lead.role,
                        "recommended_team": lead.team,
                        "recommended_series": lead.series,
                        "track": 1,
                    }
                )
            )
        except ValueError:
            continue  # a lead that will not validate is dropped, never patched into shape
    return out


def collect(session: Any, settings: Any, mailer: Any, days: int = 2) -> tuple[list[Any], dict]:
    """Read the other two sources and return (signals for today's pool, a run-record note).

    Never raises: a mailbox the desk cannot read is a missing source, not a failed run.
    """
    note: dict[str, Any] = {"routine": 0, "n8n": 0, "candidates": 0, "to_research": []}
    if not getattr(mailer, "token", None) or not getattr(mailer, "sender", None):
        note["status"] = "no mailbox configured — scanner only"
        return [], note
    try:
        since = dt.datetime.now(dt.UTC) - dt.timedelta(days=days)
        messages = GraphInbox(mailer).read(since)
        leads = new_leads(session, messages)
    except Exception as exc:  # noqa: BLE001
        note["status"] = f"unavailable: {type(exc).__name__}: {str(exc)[:160]}"
        return [], note
    note["routine"] = sum(1 for lead in leads if lead.source == "routine")
    note["n8n"] = sum(1 for lead in leads if lead.source == "n8n")
    note["to_research"] = [lead.company for lead in leads if not lead.is_candidate]
    signals = as_signals(leads)
    note["candidates"] = len(signals)
    note["status"] = "read"
    return signals, note
