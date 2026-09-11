"""Outreach drafts (build brief §8): brand voice, built from the opening angle and VERIFIED
claims only, ending with the 25-minute ask. §9.12: a draft contains no claim absent from the
brief's verified claims, and creating an Outlook draft never sends.

Without a model credential the draft is composed deterministically from verified claim
text; with one, the writer model drafts in ``spec/brand_voice.md`` voice and the same safety
check gates the result.
"""

from __future__ import annotations

import datetime as _dt
import json as _json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any as _Any

from intel.brief_data import strip_markup
from intel.models import Brief, Claim, ClaimType, VerificationResult
from intel.triggers import TYPES as TRIGGER_TYPES
from intel.triggers import classify as classify_trigger
from intel.triggers import label as trigger_label

_FIGURE = re.compile(
    r"(?:[$€£]\s?\d[\d.,]*\s?(?:[MBK]|bn|million|billion)?\+?)|(?:\d+(?:\.\d+)?%)|(?:\b(?:19|20)\d{2}\b)",
    re.IGNORECASE,
)
BRAND_VOICE = Path(__file__).resolve().parents[2] / "spec" / "brand_voice.md"


@dataclass
class Draft:
    subject: str
    body: str
    claim_ids: list[int]


def verified_claims(brief: Brief) -> list[Claim]:
    out = []
    for c in brief.claims:
        if not c.verifications:
            continue
        v = sorted(c.verifications, key=lambda x: (x.checked_at, x.id))[-1]
        if v.status == VerificationResult.verified:
            out.append(c)
    return out


def figures_in(text: str) -> set[str]:
    return {m.group(0).replace(" ", "").lower() for m in _FIGURE.finditer(text or "")}


def check_draft(body: str, claims: list[Claim]) -> list[str]:
    """§9.12 safety: every figure/year in the draft must appear in a verified claim.

    Returns the offending figures (empty list = safe)."""
    allowed: set[str] = set()
    for c in claims:
        allowed |= figures_in(strip_markup(c.text))
    return sorted(f for f in figures_in(body) if f not in allowed)


def compose_deterministic(brief: Brief) -> Draft:
    d = brief.brief_data or {}
    company = d.get("company", "")
    name = (d.get("decision_maker_name") or "").split(" ")[0]
    claims = verified_claims(brief)
    numeric = [
        c for c in claims if c.claim_type in (ClaimType.funding, ClaimType.revenue, ClaimType.date)
    ][:2]
    team = d.get("team_label") or ""
    lines = [f"{name}," if name else "Hello,", ""]
    if numeric:
        lines.append(" ".join(strip_markup(c.text).rstrip(".") + "." for c in numeric))
    angle = strip_markup(d.get("opening_angle_intro") or "")
    if angle:
        lines.append(angle)
    if team:
        lines.append(
            "1440 places companies at exactly this moment with one F1 or Formula E team — "
            f"for {company} the fit we have mapped is {team}, with a category lane that is "
            "open today."
        )
    lines += [
        "",
        "Would 25 minutes this week or next work to walk you through it?",
        "",
        "Best,",
        "1440 Sports",
    ]
    body = "\n".join(lines)
    return Draft(
        subject=f"{company} × {team or 'F1 / Formula E'} — 25 minutes?",
        body=body,
        claim_ids=[c.id for c in numeric],
    )


def compose(brief: Brief, model_writer=None) -> Draft:
    """Model-written in brand voice when a writer is available; deterministic otherwise.
    Either way the §9.12 check must pass, else fall back to the deterministic draft."""
    claims = verified_claims(brief)
    if model_writer is not None:
        d = brief.brief_data or {}
        voice = BRAND_VOICE.read_text(encoding="utf-8") if BRAND_VOICE.exists() else ""
        system = (
            "You write first-contact outreach emails for 1440Sports, a London "
            "motorsport-sponsorship agency. Use ONLY the verified facts listed; do not add any "
            "figure, date, investor, or event that is not listed. End with a specific 25-minute "
            'ask. Return JSON {"subject": ..., "body": ...}.\n\n' + voice
        )
        facts = "\n".join(f"- {strip_markup(c.text)}" for c in claims)
        user = (
            f"Company: {d.get('company')}\n"
            f"Recipient: {d.get('decision_maker_name')}, {d.get('decision_maker_role')}\n"
            f"Recommended team: {d.get('team_label')}\n"
            f"Opening angle: {strip_markup(d.get('opening_angle_quote') or '')}\n"
            f"Verified facts:\n{facts}"
        )
        try:
            from intel.config import get_settings
            from intel.parse import extract_json_object

            raw = model_writer.write(model=get_settings().writer_model, system=system, user=user)
            data = extract_json_object(raw)
            body = str(data.get("body", ""))
            if body and not check_draft(body, claims):
                return Draft(str(data.get("subject", "")), body, [c.id for c in claims])
        except Exception:
            pass  # fall through to the deterministic draft
    draft = compose_deterministic(brief)
    offenders = check_draft(draft.body, claims)
    if offenders:  # cannot happen by construction, but never ship an unverified figure
        raise ValueError(f"draft contains unverified figures: {offenders}")
    return draft


# =========================================================================================
# Sequences per trigger, a weekly cadence, and the log that makes reply and meeting rates
# real numbers (operator, 11 Sep 2026: "outreach sequence per trigger … a weekly cadence
# with reply and meeting rates tracked"). Everything below is file-based and stdlib +
# the desk's case records: no database, no model, so it runs in a weekly Actions job.
# =========================================================================================


LOG_FILE = Path(__file__).resolve().parents[2] / "data" / "outreach_log.json"
CASES_DIR = Path(__file__).resolve().parent / "cases"

#: One touch a week for four weeks, a LinkedIn connect in the first week, a call in the
#: third. Day offsets are from the first email. After the last step the sequence is parked
#: for 90 days unless a reply arrived. Each playbook differs in what the touches SAY.
_CADENCE = [
    ("open", 0, "email"),
    ("connect", 3, "linkedin"),
    ("follow_up", 7, "email"),
    ("value_add", 14, "email"),
    ("call", 21, "phone"),
    ("close_loop", 28, "email"),
]

PLAYBOOKS: dict[str, dict[str, _Any]] = {
    "funding_round": {
        "name": "New money, new brand budget",
        "premise": "A round resets the marketing budget in the quarter after it "
        "closes. Open on the "
        "round, land the team and the open lane, and ask for 25 minutes before the "
        "next race window.",
        "steps": {
            "open": "Congratulate on the round; one sentence on why this quarter; the team and the "
            "open category lane; the 25-minute ask.",
            "connect": "LinkedIn connect to the decision-maker with a one-line note "
            "naming the team.",
            "follow_up": "Reply on the same thread: the race-calendar window that makes it timely.",
            "value_add": "Send the grid-fit note: which lanes are open, which teams "
            "are ruled out and why.",
            "call": "Call the office line; leave a 20-second message naming the team and the ask.",
            "close_loop": "Close the loop: park it politely, name the next natural "
            "moment, leave the door open.",
        },
    },
    "spin_off": {
        "name": "A new name needs a stage",
        "premise": "A spin-off has a brand to launch and a first budget being set now. Open as a "
        "launch-partner conversation with the executive who owns the separated business.",
        "steps": {
            "open": "Name the separation and the new identity; a founding-partner position on a "
            "team launching or refreshing in the same season; the 25-minute ask.",
            "connect": "LinkedIn connect; note the launch-season timing in one line.",
            "follow_up": "Follow up with the season timeline: launch, livery, home round.",
            "value_add": "Send the case page: why that team, the value to the team, "
            "the ruled-out list.",
            "call": "Call; ask who will own brand for the standalone and offer to brief them.",
            "close_loop": "Close the loop before the ownership change; ask to be "
            "introduced to the new owner's brand lead.",
        },
    },
    "listing": {
        "name": "Public company, public audience",
        "premise": "A listing brings a new investor audience and a brand that has to "
        "be known. Open "
        "on the listing and the investor-relations calendar, not the share price.",
        "steps": {
            "open": "Congratulate on the listing; the team and the lane; the 25-minute ask.",
            "connect": "LinkedIn connect to the decision-maker and the IR/communications lead.",
            "follow_up": "Follow up with the race that falls in the next quarter's "
            "investor calendar.",
            "value_add": "Send the grid-fit note and a precedent: a listed peer "
            "already on the grid.",
            "call": "Call the communications office; ask for the brand owner.",
            "close_loop": "Close the loop; propose the next results window as the "
            "moment to revisit.",
        },
    },
    "new_ceo": {
        "name": "First hundred days",
        "premise": "A new chief executive sets the brand agenda in their first hundred days. Open "
        "within two weeks of the appointment, on strategy rather than sport.",
        "steps": {
            "open": "Welcome to the role; one line on what the company's moment is; "
            "the team; the 25-minute ask.",
            "connect": "LinkedIn connect with a one-line note.",
            "follow_up": "Follow up referencing their first public statement of priorities.",
            "value_add": "Send the case page and the decision path: who on their team "
            "would own it.",
            "call": "Call the chief of staff or executive office; ask for 25 minutes "
            "in the hundred-day window.",
            "close_loop": "Close the loop; name the next natural moment (first "
            "results, first strategy day).",
        },
    },
    "new_cmo": {
        "name": "The buyer just arrived",
        "premise": "A new marketing or commercial owner writes a 90-day plan. This is "
        "the person who "
        "buys a sponsorship; open to them directly and early.",
        "steps": {
            "open": "Welcome to the role; the team and the open lane; the 25-minute ask.",
            "connect": "LinkedIn connect with a one-line note on the team.",
            "follow_up": "Follow up with the calendar window and the season's first "
            "activation moment.",
            "value_add": "Send the case page: value to the team, deal architecture, precedent.",
            "call": "Call; offer a 25-minute walk-through of the lane before their plan is set.",
            "close_loop": "Close the loop; ask for their planning cycle and the right "
            "month to return.",
        },
    },
    "exec_move": {
        "name": "Shared history",
        "premise": "The person did a deal on the grid before. Open with that history, not the "
        "company's news; the warmest sequence the desk runs.",
        "steps": {
            "open": "Name the earlier deal and the sponsor they were at; why their new "
            "company fits "
            "a team now; the 25-minute ask.",
            "connect": "LinkedIn connect referencing the earlier partnership.",
            "follow_up": "Follow up with the team and the lane, one paragraph.",
            "value_add": "Send the case page and a note on what changed on the grid "
            "since their deal.",
            "call": "Call directly; a person who has done this before takes the call.",
            "close_loop": "Close the loop; ask to stay in touch for the next season's planning.",
        },
    },
    "expansion": {
        "name": "New market, new audience",
        "premise": "A market entry needs local awareness fast. Open on the market and "
        "the race that "
        "sits in it.",
        "steps": {
            "open": "Name the market entry; the race in that market; the team; the 25-minute ask.",
            "connect": "LinkedIn connect with the regional lead copied in.",
            "follow_up": "Follow up with the local activation moment on the calendar.",
            "value_add": "Send the case page and the regional hospitality outline.",
            "call": "Call the regional office.",
            "close_loop": "Close the loop; propose the next market milestone as the "
            "moment to revisit.",
        },
    },
    "other": {
        "name": "Standard sequence",
        "premise": "No single trigger dominates; run the standard four-week cadence on the case.",
        "steps": {
            "open": "The company's moment in one line; the team; the 25-minute ask.",
            "connect": "LinkedIn connect.",
            "follow_up": "Follow up with the calendar window.",
            "value_add": "Send the case page.",
            "call": "Call.",
            "close_loop": "Close the loop.",
        },
    },
}


def playbook(kind: str | None) -> dict[str, _Any]:
    pb = PLAYBOOKS.get(kind or "other", PLAYBOOKS["other"])
    return {
        "type": kind or "other",
        "label": trigger_label(kind),
        "name": pb["name"],
        "premise": pb["premise"],
        "steps": [
            {"step": s, "day": d, "channel": ch, "purpose": pb["steps"][s]} for s, d, ch in _CADENCE
        ],
    }


def playbooks() -> dict[str, dict[str, _Any]]:
    return {k: playbook(k) for k in TRIGGER_TYPES}


def sequence_plan(kind: str | None, start: _dt.date) -> list[dict[str, _Any]]:
    """The dated touches for a sequence starting on ``start``."""
    return [
        {**step, "date": (start + _dt.timedelta(days=step["day"])).isoformat(), "status": "planned"}
        for step in playbook(kind)["steps"]
    ]


# ---- the log ----------------------------------------------------------------------------


def load_log(path: Path | str | None = None) -> dict[str, _Any]:
    p = Path(path) if path else LOG_FILE
    if not p.exists():
        return {
            "_meta": {
                "what": "Outreach sequences started from desk signals, with every touch, reply "
                "and meeting logged — the outcomes loop. Rates are computed from this file.",
                "how": "python -m intel.outreach start <N°> | touch <id> <step> | reply <id> | "
                "meeting <id> | outcome <id> won|declined|parked | report [--email]",
            },
            "sequences": [],
        }
    return _json.loads(p.read_text(encoding="utf-8"))


def save_log(log: dict[str, _Any], path: Path | str | None = None) -> Path:
    p = Path(path) if path else LOG_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_json.dumps(log, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def find_case(number: int, cases_dir: Path | str | None = None) -> dict[str, _Any] | None:
    """The desk's case record for a brief number (no database needed)."""
    for rec in sorted(Path(cases_dir or CASES_DIR).glob("*/*.run.json")):
        try:
            data = _json.loads(rec.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (data.get("brief") or {}).get("number") == number:
            return data
    return None


def _case_row(data: dict[str, _Any]) -> dict[str, _Any]:
    b = data.get("brief") or {}
    bd = b.get("brief_data") or {}
    cands = data.get("candidates") or []
    cand = next((c for c in cands if c.get("decision") == "selected"), cands[0] if cands else {})
    return {
        "company": bd.get("company") or cand.get("company"),
        "person": bd.get("decision_maker_name") or cand.get("person"),
        "role": bd.get("decision_maker_role") or cand.get("role"),
        "team": bd.get("team_label") or cand.get("recommended_team"),
        "series": bd.get("series_label") or cand.get("recommended_series"),
        "trigger": cand.get("trigger_reason") or (cand.get("key_facts") or {}).get("trigger"),
        "key_facts": cand.get("key_facts") or {},
        "date": data.get("run", {}).get("date"),
    }


def start(
    log: dict[str, _Any],
    number: int,
    on: _dt.date | None = None,
    person: str | None = None,
    kind: str | None = None,
    cases_dir: Path | str | None = None,
) -> dict[str, _Any]:
    """Open a sequence for brief N°. One open sequence per brief at a time."""
    for s in log["sequences"]:
        if s["brief_number"] == number and s["outcome"] == "open":
            raise ValueError(f"N° {number} already has an open sequence ({s['id']})")
    data = find_case(number, cases_dir)
    if data is None:
        raise LookupError(f"no case record for N° {number}")
    row = _case_row(data)
    kind = kind or classify_trigger(row["trigger"], row["key_facts"], row["role"])
    day = on or _dt.date.today()
    seq = {
        "id": f"{number}-{day.isoformat()}",
        "brief_number": number,
        "company": row["company"],
        "person": person or row["person"],
        "role": row["role"],
        "team": row["team"],
        "series": row["series"],
        "trigger": row["trigger"],
        "trigger_type": kind,
        "playbook": playbook(kind)["name"],
        "started": day.isoformat(),
        "touches": sequence_plan(kind, day),
        "replied_on": None,
        "meeting_on": None,
        "outcome": "open",
        "notes": [],
    }
    log["sequences"].append(seq)
    return seq


def _seq(log: dict[str, _Any], seq_id: str) -> dict[str, _Any]:
    for s in log["sequences"]:
        if s["id"] == seq_id or (
            seq_id.isdigit() and s["brief_number"] == int(seq_id) and s["outcome"] == "open"
        ):
            return s
    raise LookupError(f"no sequence {seq_id}")


def touch(
    log: dict[str, _Any], seq_id: str, step: str, on: _dt.date | None = None, note: str = ""
) -> dict[str, _Any]:
    s = _seq(log, seq_id)
    day = (on or _dt.date.today()).isoformat()
    for t in s["touches"]:
        if t["step"] == step:
            t["status"] = "sent"
            t["sent_on"] = day
            if note:
                t["note"] = note
            return t
    raise LookupError(f"no step {step!r} in sequence {s['id']}")


def reply(
    log: dict[str, _Any], seq_id: str, on: _dt.date | None = None, note: str = ""
) -> dict[str, _Any]:
    s = _seq(log, seq_id)
    s["replied_on"] = (on or _dt.date.today()).isoformat()
    if s["outcome"] == "open":
        s["outcome"] = "replied"
    if note:
        s["notes"].append({"date": s["replied_on"], "note": note})
    return s


def meeting(
    log: dict[str, _Any], seq_id: str, on: _dt.date | None = None, note: str = ""
) -> dict[str, _Any]:
    s = _seq(log, seq_id)
    s["meeting_on"] = (on or _dt.date.today()).isoformat()
    if s["outcome"] in ("open", "replied"):
        s["outcome"] = "meeting"
    if note:
        s["notes"].append({"date": s["meeting_on"], "note": note})
    return s


OUTCOMES = ("open", "replied", "meeting", "won", "declined", "parked")


def outcome(log: dict[str, _Any], seq_id: str, value: str, note: str = "") -> dict[str, _Any]:
    if value not in OUTCOMES:
        raise ValueError(f"outcome must be one of {OUTCOMES}")
    s = _seq(log, seq_id)
    s["outcome"] = value
    if note:
        s["notes"].append({"date": _dt.date.today().isoformat(), "note": note})
    return s


# ---- the numbers -------------------------------------------------------------------------


def _week(day: str | None) -> str | None:
    if not day:
        return None
    y, w, _ = _dt.date.fromisoformat(day).isocalendar()
    return f"{y}-W{w:02d}"


def _rate(n: int, d: int) -> float | None:
    return round(n / d, 3) if d else None


def metrics(log: dict[str, _Any], weeks: int = 8, today: _dt.date | None = None) -> dict[str, _Any]:
    """Reply and meeting rates by trigger type, plus the last ``weeks`` ISO weeks."""
    seqs = log.get("sequences") or []
    by_type: dict[str, dict[str, _Any]] = {}
    total = {"sequences": 0, "contacted": 0, "replies": 0, "meetings": 0, "won": 0}

    def bucket(kind: str) -> dict[str, _Any]:
        return by_type.setdefault(
            kind,
            {
                "label": trigger_label(kind),
                "sequences": 0,
                "contacted": 0,
                "replies": 0,
                "meetings": 0,
                "won": 0,
            },
        )

    for s in seqs:
        b = bucket(s.get("trigger_type") or "other")
        sent = any(t.get("status") == "sent" for t in s.get("touches") or [])
        for tgt in (b, total):
            tgt["sequences"] += 1
            tgt["contacted"] += 1 if sent else 0
            tgt["replies"] += 1 if s.get("replied_on") else 0
            tgt["meetings"] += 1 if s.get("meeting_on") else 0
            tgt["won"] += 1 if s.get("outcome") == "won" else 0
    for tgt in list(by_type.values()) + [total]:
        tgt["reply_rate"] = _rate(tgt["replies"], tgt["contacted"])
        tgt["meeting_rate"] = _rate(tgt["meetings"], tgt["contacted"])
        tgt["meetings_per_reply"] = _rate(tgt["meetings"], tgt["replies"])
    # weekly series, newest last
    today = today or _dt.date.today()
    monday = today - _dt.timedelta(days=today.weekday())
    weekly = []
    for i in range(weeks - 1, -1, -1):
        wk_start = monday - _dt.timedelta(days=7 * i)
        key = _week(wk_start.isoformat())
        row = {
            "week": key,
            "from": wk_start.isoformat(),
            "started": 0,
            "touches": 0,
            "replies": 0,
            "meetings": 0,
        }
        for s in seqs:
            row["started"] += 1 if _week(s.get("started")) == key else 0
            row["touches"] += sum(
                1
                for t in s.get("touches") or []
                if t.get("status") == "sent" and _week(t.get("sent_on")) == key
            )
            row["replies"] += 1 if _week(s.get("replied_on")) == key else 0
            row["meetings"] += 1 if _week(s.get("meeting_on")) == key else 0
        weekly.append(row)
    return {"by_type": by_type, "total": total, "weekly": weekly}


def due(log: dict[str, _Any], today: _dt.date | None = None) -> list[dict[str, _Any]]:
    """Touches planned for this week (Mon–Sun) or overdue, on sequences still open."""
    today = today or _dt.date.today()
    monday = today - _dt.timedelta(days=today.weekday())
    sunday = monday + _dt.timedelta(days=6)
    out = []
    for s in log.get("sequences") or []:
        if s.get("outcome") not in ("open", "replied"):
            continue
        for t in s.get("touches") or []:
            if t.get("status") != "planned":
                continue
            d = _dt.date.fromisoformat(t["date"])
            if d <= sunday:
                out.append(
                    {
                        "sequence": s["id"],
                        "brief_number": s["brief_number"],
                        "company": s["company"],
                        "person": s.get("person"),
                        "team": s.get("team"),
                        "trigger_type": s.get("trigger_type"),
                        "step": t["step"],
                        "channel": t["channel"],
                        "date": t["date"],
                        "overdue": d < monday,
                        "purpose": t.get("purpose"),
                    }
                )
    out.sort(key=lambda x: (x["date"], x["company"]))
    return out


def report_text(log: dict[str, _Any], today: _dt.date | None = None) -> str:
    today = today or _dt.date.today()
    m = metrics(log, today=today)
    d = due(log, today)
    lines = [f"1440 OUTREACH — week of {today - _dt.timedelta(days=today.weekday()):%d %b %Y}", ""]
    t = m["total"]
    lines.append(
        f"All time: {t['sequences']} sequences, {t['contacted']} contacted, {t['replies']} replies "
        f"({_pct(t['reply_rate'])}), {t['meetings']} meetings "
        f"({_pct(t['meeting_rate'])}), {t['won']} won."
    )
    lines.append("")
    lines.append("BY TRIGGER")
    for kind in TRIGGER_TYPES:
        b = m["by_type"].get(kind)
        if not b:
            continue
        lines.append(
            f"- {b['label']}: {b['sequences']} seq · {b['contacted']} contacted · "
            f"{b['replies']} replies "
            f"({_pct(b['reply_rate'])}) · {b['meetings']} meetings ({_pct(b['meeting_rate'])})"
        )
    if not m["by_type"]:
        lines.append("- no sequences started yet")
    lines.append("")
    lines.append("LAST 8 WEEKS (started / touches / replies / meetings)")
    for w in m["weekly"]:
        lines.append(
            f"- {w['week']} (from {w['from']}): {w['started']} / {w['touches']} / "
            f"{w['replies']} / {w['meetings']}"
        )
    lines.append("")
    lines.append(f"DUE THIS WEEK ({len(d)})")
    for x in d:
        lines.append(
            f"- {x['date']}{' OVERDUE' if x['overdue'] else ''} · N° "
            f"{x['brief_number']} {x['company']} · "
            f"{x['step'].replace('_', ' ')} by {x['channel']} → {x['person'] or 'decision-maker'}"
        )
    if not d:
        lines.append("- nothing due")
    open_seqs = [s for s in log.get("sequences") or [] if s.get("outcome") in ("open", "replied")]
    lines.append("")
    lines.append(f"OPEN SEQUENCES ({len(open_seqs)})")
    for s in open_seqs:
        sent = sum(1 for t in s["touches"] if t.get("status") == "sent")
        lines.append(
            f"- N° {s['brief_number']} {s['company']} → {s.get('person')} · "
            f"{trigger_label(s.get('trigger_type'))} · "
            f"started {s['started']} · {sent}/{len(s['touches'])} touches · {s['outcome']}"
            + (f" · replied {s['replied_on']}" if s.get("replied_on") else "")
        )
    if not open_seqs:
        lines.append("- none")
    rows = watch_rows(today=today)
    todo = [r for r in rows if r.get("action") == "start_sequence"]
    lines.append("")
    lines.append(f"TRIGGER WATCH — {len(rows)} items, {len(todo)} to start")
    for r in rows:
        who = f"{r['person']} → " if r.get("person") else ""
        lines.append(
            f"- [{r.get('action')}] {r['trigger_label']}: {who}{r.get('company')} · "
            f"{r.get('to_role') or ''} · {r.get('date')} ({r.get('days')}d) · ICP: {r.get('icp')}"
        )
    inbox = _filings_inbox()
    lines.append("")
    lines.append(
        f"SEC FILINGS TO JUDGE — {inbox['to_judge']} (8-K officer changes, S-1 / F-1 / 10-12B; "
        f"swept {inbox.get('swept_at') or 'never'})"
    )
    for h in inbox["unjudged"][:25]:
        lines.append(f"- {h.get('filed')} {h.get('form')} · {h.get('company')} · {h.get('url')}")
    if not inbox["unjudged"]:
        lines.append("- nothing waiting")
    lines.append("")
    lines.append(
        "Start one: python -m intel.outreach start <N°>   (or the Outreach page in the app)"
    )
    return "\n".join(lines)


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{round(x * 100)}%"


def export_payload(
    log: dict[str, _Any] | None = None, today: _dt.date | None = None
) -> dict[str, _Any]:
    """What the app shows: playbooks, sequences, the numbers, and this week's touches."""
    log = log if log is not None else load_log()
    today = today or _dt.date.today()
    rows = watch_rows(today=today)
    return {
        "week": _week(today.isoformat()),
        "playbooks": playbooks(),
        "sequences": log.get("sequences") or [],
        "metrics": metrics(log, today=today),
        "due": due(log, today),
        "watch": rows,
        "inbox": _filings_inbox(),
        "watch_meta": {
            **watch_summary(rows),
            "swept_at": (load_watch().get("_meta") or {}).get("swept_at"),
        },
    }


def _send_report(text: str) -> str:
    from intel.config import get_settings
    from intel.send import Outgoing, mailer_for

    settings = get_settings()
    if not settings.operator_email:
        raise RuntimeError("OPERATOR_EMAIL is not set")
    first = text.split("\n", 1)[0]
    msg = Outgoing(
        to=[settings.operator_email],
        cc=[],
        subject=first,
        body_text=text,
        body_html=None,
        attachments=[],
    )
    return mailer_for(settings).send(msg)


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="python -m intel.outreach")
    parser.add_argument("--log", default=None, help="log file (default data/outreach_log.json)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start", help="open a sequence for a brief number")
    p.add_argument("number", type=int)
    p.add_argument("--date", type=_dt.date.fromisoformat, default=None)
    p.add_argument("--person", default=None)
    p.add_argument("--type", dest="kind", choices=list(TRIGGER_TYPES), default=None)
    p = sub.add_parser("touch", help="mark a step sent")
    p.add_argument("sequence")
    p.add_argument("step", choices=[s for s, _, _ in _CADENCE])
    p.add_argument("--date", type=_dt.date.fromisoformat, default=None)
    p.add_argument("--note", default="")
    for name in ("reply", "meeting"):
        p = sub.add_parser(name)
        p.add_argument("sequence")
        p.add_argument("--date", type=_dt.date.fromisoformat, default=None)
        p.add_argument("--note", default="")
    p = sub.add_parser("outcome")
    p.add_argument("sequence")
    p.add_argument("value", choices=OUTCOMES)
    p.add_argument("--note", default="")
    p = sub.add_parser("report", help="the weekly report (text); --email sends it to the operator")
    p.add_argument("--email", action="store_true")
    p.add_argument("--date", type=_dt.date.fromisoformat, default=None)
    sub.add_parser("plan", help="print every playbook").add_argument(
        "--type", dest="kind", default=None
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    log = load_log(args.log)
    if args.cmd == "start":
        s = start(log, args.number, args.date, args.person, args.kind)
        save_log(log, args.log)
        print(
            f"{s['id']}: {s['company']} → {s['person']} · "
            f"{trigger_label(s['trigger_type'])} · {s['playbook']}"
        )
        for t in s["touches"]:
            print(f"  {t['date']}  {t['step']:<11} {t['channel']:<9} {t['purpose']}")
    elif args.cmd == "touch":
        t = touch(log, args.sequence, args.step, args.date, args.note)
        save_log(log, args.log)
        print(f"{args.sequence}: {t['step']} sent {t['sent_on']}")
    elif args.cmd == "reply":
        s = reply(log, args.sequence, args.date, args.note)
        save_log(log, args.log)
        print(f"{s['id']}: replied {s['replied_on']}")
    elif args.cmd == "meeting":
        s = meeting(log, args.sequence, args.date, args.note)
        save_log(log, args.log)
        print(f"{s['id']}: meeting {s['meeting_on']}")
    elif args.cmd == "outcome":
        s = outcome(log, args.sequence, args.value, args.note)
        save_log(log, args.log)
        print(f"{s['id']}: {s['outcome']}")
    elif args.cmd == "report":
        text = report_text(log, args.date)
        print(text)
        if args.email:
            print("sent:", _send_report(text))
    elif args.cmd == "plan":
        for kind, pb in playbooks().items():
            if args.kind and kind != args.kind:
                continue
            print(f"\n{pb['label']} — {pb['name']}\n  {pb['premise']}")
            for st in pb["steps"]:
                print(f"  day {st['day']:>2}  {st['step']:<11} {st['channel']:<9} {st['purpose']}")
    return 0


# ---- the trigger watch: named people and events, with the desk's judgment ---------------

WATCH_FILE = Path(__file__).resolve().parents[2] / "data" / "trigger_watch.json"
WATCH_ACTIONS = ("start_sequence", "sponsor_side", "watch", "in_pursuit", "screen_out")


def load_watch(path: Path | str | None = None) -> dict[str, _Any]:
    p = Path(path) if path else WATCH_FILE
    if not p.exists():
        return {"_meta": {}, "items": []}
    return _json.loads(p.read_text(encoding="utf-8"))


def watch_rows(
    watch: dict[str, _Any] | None = None, today: _dt.date | None = None
) -> list[dict[str, _Any]]:
    """The watch items as the app shows them: typed, labelled, aged, action first."""
    watch = watch if watch is not None else load_watch()
    today = today or _dt.date.today()
    order = {a: i for i, a in enumerate(WATCH_ACTIONS)}
    rows = []
    for it in watch.get("items") or []:
        row = dict(it)
        row["trigger_label"] = trigger_label(it.get("type"))
        try:
            d = _dt.date.fromisoformat(it.get("date") or "")
            row["days"] = (today - d).days
            row["in_window"] = 0 <= row["days"] <= 90
        except ValueError:
            row["days"] = None
            row["in_window"] = None
        row["company"] = it.get("to_company") or it.get("from_company")
        rows.append(row)
    rows.sort(key=lambda r: (order.get(r.get("action"), 9), -(r.get("days") or 0)))
    return rows


def _filings_inbox() -> dict[str, _Any]:
    """EDGAR hits the desk has not judged yet (intel.edgar_watch), for the app and the report."""
    from intel.edgar_watch import load_inbox, unjudged

    inbox = load_inbox()
    rows = unjudged(inbox)
    return {
        "swept_at": (inbox.get("_meta") or {}).get("swept_at"),
        "unjudged": rows[:50],
        "total": len(inbox.get("hits") or []),
        "to_judge": len(rows),
    }


def watch_summary(rows: list[dict[str, _Any]]) -> dict[str, _Any]:
    out = {a: 0 for a in WATCH_ACTIONS}
    for r in rows:
        out[r.get("action") or "watch"] = out.get(r.get("action") or "watch", 0) + 1
    out["total"] = len(rows)
    return out


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
