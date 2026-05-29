"""1440 Sports - daily run.

1. Load prospect + team data.
2. Score and select the day's single hero prospect (respecting gates,
   the crowding rule, and a cooldown so the same company isn't picked daily).
3. Render the 2-page brief (HTML + Markdown + best-effort PDF) into
   briefs/<date>/.
4. Email it (Outlook/M365 via SMTP) if configured; otherwise dry-run to disk.
5. Record the pick in briefs/history.json so tomorrow's run rotates.

Usage:
  python engine/run_daily.py                 # today, real selection
  python engine/run_daily.py --date 2026-05-29
  python engine/run_daily.py --force jfrog   # force a specific prospect id
  python engine/run_daily.py --no-email      # never attempt to send
  python engine/run_daily.py --list          # print the ranked leaderboard
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import scoring          # noqa: E402
import generate_brief   # noqa: E402
import send_email       # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_ROOT, "data", "prospects.json")
_BRIEFS = os.path.join(_ROOT, "briefs")
_HISTORY = os.path.join(_BRIEFS, "history.json")


def load_prospects() -> dict:
    with open(_DATA, encoding="utf-8") as fh:
        return json.load(fh)


def load_history() -> dict:
    if os.path.exists(_HISTORY):
        with open(_HISTORY, encoding="utf-8") as fh:
            return json.load(fh)
    return {"last_hero": {}, "log": []}


def save_history(history: dict) -> None:
    os.makedirs(_BRIEFS, exist_ok=True)
    with open(_HISTORY, "w", encoding="utf-8") as fh:
        json.dump(history, fh, indent=2)


def first_sentences(text: str, n: int = 2) -> str:
    parts = text.replace(". ", ".|").split("|")
    return " ".join(parts[:n]).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    ap.add_argument("--force", help="force a prospect id as today's hero")
    ap.add_argument("--no-email", action="store_true")
    ap.add_argument("--list", action="store_true", help="print leaderboard and exit")
    ap.add_argument("--batch", action="store_true",
                    help="render briefs for ALL eligible prospects (no email)")
    args = ap.parse_args()

    today = _dt.date.fromisoformat(args.date)
    blob = load_prospects()
    prospects = blob["prospects"]
    meta = blob.get("_meta", {})
    cooldown = int(meta.get("cooldown_days", 5))
    min_years = int(meta.get("default_min_deal_years", 3))
    history = load_history()

    ranked = scoring.rank(prospects, today=today, cooldown_days=cooldown,
                          min_deal_years=min_years,
                          history=history.get("last_hero", {}))

    if args.list:
        print(f"\n1440 Sports — prospect leaderboard ({args.date})\n" + "-" * 60)
        for i, p in enumerate(ranked, 1):
            e = scoring.enrich(p)
            print(f"{i:2d}. {e['opportunity']:3d}/100  {e['tier']:13s}  "
                  f"{p['series']:3s}  {p['name']}  [{e['crowding_label']}]")
        # also show gated / parked for transparency
        gated = [p for p in prospects if not scoring.is_eligible_for_hero(p, min_years)]
        if gated:
            print("\nGated / parked (not eligible for hero):")
            for p in gated:
                why = ("crowding>100" if (p.get("est_inbound_pitches") or 0) > 100
                       else p.get("status", "ineligible"))
                print(f"     {scoring.opportunity_score(p):3d}/100  {p['name']}  ({why})")
        return 0

    if args.batch:
        out_dir = os.path.join(_BRIEFS, args.date)
        print(f"Batch: rendering {len(ranked)} eligible briefs into {os.path.relpath(out_dir, _ROOT)}/")
        for i, p in enumerate(ranked, 1):
            e = scoring.enrich(p)
            paths = generate_brief.write_brief(p, out_dir, brief_no=f"{i:03d}", date=args.date)
            print(f"  {e['opportunity']:3d}/100 {e['tier']:13s} {p['name']:22s} -> {os.path.basename(paths.get('pdf', paths['html']))}")
        return 0

    if args.force:
        hero = next((p for p in prospects if p["id"] == args.force), None)
        if hero is None:
            print(f"No prospect with id '{args.force}'.")
            return 1
    else:
        hero = ranked[0] if ranked else None

    if hero is None:
        print("No eligible prospect today.")
        return 1

    e = scoring.enrich(hero)
    brief_no = f"{len(history.get('log', [])) + 1:03d}"
    out_dir = os.path.join(_BRIEFS, args.date)
    paths = generate_brief.write_brief(hero, out_dir, brief_no=brief_no, date=args.date)

    print(f"Hero: {hero['name']}  ({e['opportunity']}/100, {e['tier']})")
    for k, v in paths.items():
        print(f"  {k.upper():4s} -> {os.path.relpath(v, _ROOT)}")

    # Email
    if not args.no_email:
        subject = f"1440 Brief {brief_no} — {hero['name']} ({e['opportunity']}/100 {e['tier']}) — {args.date}"
        html_body = send_email.email_html_wrapper(
            hero["name"], e["opportunity"], e["tier"], hero["headline_long"],
            first_sentences(hero["the_case"], 3), args.date)
        text_body = generate_brief.render_markdown(hero, date=args.date)
        attachments = {k: v for k, v in paths.items() if k in ("pdf", "html")}
        channel = send_email.deliver(subject, html_body, text_body, attachments)
        print(f"  Delivery channel: {channel}")

    # Record history
    history.setdefault("last_hero", {})[hero["id"]] = args.date
    history.setdefault("log", []).append({
        "date": args.date, "brief_no": brief_no, "id": hero["id"],
        "name": hero["name"], "opportunity": e["opportunity"], "tier": e["tier"],
    })
    save_history(history)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
