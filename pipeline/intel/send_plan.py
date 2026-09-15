"""The MD send plan — one verified brief to the MD a day, from a queue kept in the repo.

Operator, 15 Sep 2026: "These should also be sent to Ricky one a day after they are passing
all the verification gates. So we need to plan that as well on a daily basis."

``data/send_plan.json`` holds two lists:

- ``queue`` — brief numbers in the order they should go, each with an optional ``hold``
  (kept back until the operator releases it) and a ``note``. A number whose case is not
  yet built, or whose brief is not MD-eligible (verified + audit pass + 2 pages), is skipped
  until it is — the plan never sends a brief that has not passed every gate.
- ``sent`` — every send to the MD, whoever triggered it: this module's daily run, the
  "Send a brief" button, or a scheduled session. ``intel.resend`` records here, so the
  repo is the durable answer to "was this ever sent to Ricky?" (the CI database is thrown
  away after each run; the mailbox is not a system of record).

The rule is one MD send per London day. If anything already went to the MD today — the
morning's live signal, a button press — the daily run holds. The 07:00 London slot is
gated in the workflow, not here.

    python -m intel.send_plan --list                 # queue, eligibility, history
    python -m intel.send_plan --add 261 --note "…"   # append to the queue
    python -m intel.send_plan --hold 245 / --release 245 / --remove 245
    python -m intel.send_plan --dry-run              # what would go now, and why not
    python -m intel.send_plan --send                 # send the next eligible brief to the MD
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.config import Settings, get_settings
from intel.db import session_scope
from intel.models import Brief
from intel.render import brief_status_for_md

PLAN_FILE = Path(__file__).resolve().parents[2] / "data" / "send_plan.json"
LONDON = ZoneInfo("Europe/London")


def _empty() -> dict[str, Any]:
    return {
        "_meta": {
            "what": "MD send plan: one verified brief a day, in queue order (intel.send_plan)",
            "rule": "one send to the MD per London day; only briefs that pass every gate",
            "slot_london": "07:00",
        },
        "queue": [],
        "sent": [],
    }


def load_plan(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path else PLAN_FILE
    if not p.exists():
        return _empty()
    data = json.loads(p.read_text(encoding="utf-8"))
    data.setdefault("queue", [])
    data.setdefault("sent", [])
    return data


def save_plan(plan: dict[str, Any], path: Path | str | None = None) -> Path:
    p = Path(path) if path else PLAN_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def london_today(now: dt.datetime | None = None) -> dt.date:
    now = now or dt.datetime.now(dt.UTC)
    return now.astimezone(LONDON).date()


def md_sends(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [s for s in plan.get("sent") or [] if s.get("to") == "md"]


def sent_numbers(plan: dict[str, Any]) -> set[int]:
    return {int(s["number"]) for s in md_sends(plan) if s.get("number") is not None}


def sent_today(plan: dict[str, Any], day: dt.date | None = None) -> dict[str, Any] | None:
    day = day or london_today()
    for s in md_sends(plan):
        if s.get("date") == day.isoformat():
            return s
    return None


def record_send(
    number: int,
    company: str | None,
    to: str,
    message_id: str | None,
    by: str,
    when: dt.datetime | None = None,
    path: Path | str | None = None,
) -> dict[str, Any]:
    """Append one delivery to the log (idempotent on message id) and save."""
    plan = load_plan(path)
    when = when or dt.datetime.now(dt.UTC)
    entry = {
        "number": int(number),
        "company": company,
        "to": to,
        "date": when.astimezone(LONDON).date().isoformat(),
        "time_london": when.astimezone(LONDON).strftime("%H:%M"),
        "time_utc": when.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "message_id": message_id,
        "by": by,
    }
    if message_id and any(s.get("message_id") == message_id for s in plan["sent"]):
        return entry
    plan["sent"].append(entry)
    save_plan(plan, path)
    return entry


def brief_by_number(session: Session, number: int) -> Brief | None:
    return session.scalar(select(Brief).where(Brief.brief_number == number))


def eligibility(session: Session, item: dict[str, Any], plan: dict[str, Any]) -> tuple[bool, str]:
    """Why a queue item can or cannot go: every gate, stated."""
    number = int(item["number"])
    if item.get("hold"):
        return False, "held by the operator"
    if number in sent_numbers(plan):
        return False, "already sent to the MD"
    brief = brief_by_number(session, number)
    if brief is None:
        return False, "no case built yet"
    if not brief_status_for_md(brief):
        return False, (
            f"not MD-eligible: verification {brief.verification_status.value}, "
            f"audit {brief.audit_status.value}"
        )
    if brief.page_count != 2:
        return False, f"page count {brief.page_count}, not 2"
    if not brief.pdf_path:
        return False, "no PDF rendered"
    return True, "verified, audit pass, 2 pages"


def next_eligible(
    session: Session, plan: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[tuple[int, str]]]:
    """The first queue item that passes every gate, plus the reason each earlier one did not."""
    skipped: list[tuple[int, str]] = []
    for item in plan.get("queue") or []:
        ok, why = eligibility(session, item, plan)
        if ok:
            return item, skipped
        skipped.append((int(item["number"]), why))
    return None, skipped


def send_next(
    session: Session,
    settings: Settings,
    mailer,
    plan: dict[str, Any],
    day: dt.date | None = None,
    dry_run: bool = False,
    path: Path | str | None = None,
) -> str:
    """Send the next eligible brief to the MD unless one already went today."""
    from intel import resend

    day = day or london_today()
    already = sent_today(plan, day)
    if already:
        return (
            f"hold: N° {already['number']} {already.get('company') or ''} already went to the "
            f"MD today at {already.get('time_london')} London ({already.get('by')})"
        )
    item, skipped = next_eligible(session, plan)
    lines = [f"  N° {n}: {why}" for n, why in skipped]
    if item is None:
        return "nothing eligible to send:\n" + ("\n".join(lines) if lines else "  queue is empty")
    number = int(item["number"])
    if dry_run:
        company = (brief_by_number(session, number).brief_data or {}).get("company")
        return f"would send N° {number} {company} to the MD" + (
            "\n" + "\n".join(lines) if lines else ""
        )
    result = resend.resend(session, number, settings, mailer, to="md", cc_operator=True)
    # resend records the delivery in the plan; re-load so the caller sees it
    return result + ("\n" + "\n".join(lines) if lines else "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.send_plan", description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--add", type=int, metavar="N")
    parser.add_argument("--note", default=None)
    parser.add_argument("--hold", type=int, metavar="N")
    parser.add_argument("--release", type=int, metavar="N")
    parser.add_argument("--remove", type=int, metavar="N")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--plan", default=None, help="plan file (default data/send_plan.json)")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    plan = load_plan(args.plan)

    if args.add is not None:
        if any(int(q["number"]) == args.add for q in plan["queue"]):
            print(f"N° {args.add} is already queued")
        else:
            plan["queue"].append(
                {
                    "number": args.add,
                    "hold": False,
                    "note": args.note,
                    "added": london_today().isoformat(),
                }
            )
            save_plan(plan, args.plan)
            print(f"queued N° {args.add}")
        return 0
    for flag, value in (("hold", args.hold), ("release", args.release), ("remove", args.remove)):
        if value is None:
            continue
        hit = next((q for q in plan["queue"] if int(q["number"]) == value), None)
        if hit is None:
            print(f"N° {value} is not in the queue", file=sys.stderr)
            return 1
        if flag == "remove":
            plan["queue"].remove(hit)
        else:
            hit["hold"] = flag == "hold"
        save_plan(plan, args.plan)
        print(f"{flag}: N° {value}")
        return 0

    settings = get_settings()
    with session_scope(settings.database_url) as session:
        if args.list or not (args.send or args.dry_run):
            today = sent_today(plan)
            print(
                f"today ({london_today()}): "
                + (f"sent N° {today['number']}" if today else "nothing sent yet")
            )
            for item in plan["queue"]:
                ok, why = eligibility(session, item, plan)
                mark = "READY" if ok else "wait "
                print(
                    f"  [{mark}] N° {item['number']}: {why}"
                    + (f" — {item['note']}" if item.get("note") else "")
                )
            print(f"sent to the MD so far: {len(md_sends(plan))}")
            for s in md_sends(plan)[-5:]:
                print(
                    f"  {s['date']} {s['time_london']} N° {s['number']} "
                    f"{s.get('company') or ''} ({s.get('by')})"
                )
            return 0
        from intel.resend import mailer_for

        if args.dry_run:
            settings = settings.model_copy(update={"execution_mode": "dry_run"})
        print(
            send_next(
                session, settings, mailer_for(settings), plan, dry_run=args.dry_run, path=args.plan
            )
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
