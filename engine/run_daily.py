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
import verify_brief     # noqa: E402
import cadence          # noqa: E402

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


def weekly_decision(prospects, today, cooldown, min_years, history, args) -> int:
    """DECISION day: review the week's contenders across BOTH series and surface
    the single company we should proceed with, with the runners-up for context."""
    monday, sunday = cadence.week_bounds(today)
    # The week's featured heroes (what the FE/F1 days surfaced).
    featured = [r for r in history.get("log", [])
                if monday.isoformat() <= r.get("date", "") <= today.isoformat()
                and r.get("kind") != "weekly_decision"]

    # The GO is chosen from THIS WEEK's contenders (the heroes we actually surfaced),
    # per the mandate — not a re-rank of the whole DB, which would resurface old/
    # already-sent names. Rank the week's eligible featured heroes; fall back to the
    # full eligible board only if the week produced none.
    by_id = {p["id"]: p for p in prospects}
    seen = set()
    week_pool = []
    for r in featured:
        pid = r.get("id")
        if pid and pid not in seen and pid in by_id:
            seen.add(pid)
            week_pool.append(by_id[pid])
    ranked = scoring.rank(week_pool, today=today, cooldown_days=0,
                          min_deal_years=min_years, history={}, series=None)
    if not ranked:
        ranked = scoring.rank(prospects, today=today, cooldown_days=0,
                              min_deal_years=min_years, history={}, series=None)
    if not ranked:
        print("No eligible prospect for the weekly decision.")
        return 1
    go = ranked[0]
    e = scoring.enrich(go)

    # Verification gate — never recommend a GO we can't stand behind.
    vf = verify_brief.check_prospect(go, today)
    blockers = [f for f in vf if f[0] == verify_brief.BLOCKER]

    # Build the decision digest (markdown + HTML).
    lines = [f"# 1440 WEEKLY DECISION — week of {monday:%d %b %Y}", ""]
    lines.append(f"## ✅ PROCEED: {go['name']}  ({e['opportunity']}/100 · {e['tier']})")
    lines.append(f"- **Series / team:** {go.get('series')} · {go.get('recommended_team')}")
    lines.append(f"- **Crowding:** {e['crowding_label']}")
    lines.append(f"- **Why this one:** {first_sentences(go.get('the_case',''), 2)}")
    lines.append(f"- **Opening move:** {go.get('opening_angle','').strip(chr(34))}")
    if blockers:
        lines.append(f"- ⚠️ **{len(blockers)} verification blocker(s) — resolve before outreach.**")
    lines.append("\n## This week's contenders (ranked)")
    for i, p in enumerate(ranked[:6], 1):
        pe = scoring.enrich(p)
        star = " ← GO" if p["id"] == go["id"] else ""
        lines.append(f"{i}. **{pe['opportunity']}/100** {pe['tier']:13s} · {p['series']:2s} · "
                     f"{p['name']} ({p.get('recommended_team')}){star}")
    if featured:
        names = ", ".join(f"{r['name']} ({r['date']})" for r in featured)
        lines.append(f"\n## Featured in briefs this week\n{names}")
    digest_md = "\n".join(lines)

    out_dir = os.path.join(_BRIEFS, args.date)
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, "weekly-decision.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(digest_md)
    # Also render the GO's full 2-page brief to attach.
    brief_no = f"{len(history.get('log', [])) + 1:03d}"
    paths = generate_brief.write_brief(go, out_dir, brief_no=brief_no, date=args.date)

    print(f"\nWEEKLY DECISION ({monday:%d %b}–{sunday:%d %b}) -> PROCEED: "
          f"{go['name']} ({e['opportunity']}/100)")
    print(f"  Digest -> {os.path.relpath(md_path, _ROOT)}")
    for k, v in paths.items():
        print(f"  {k.upper():4s} -> {os.path.relpath(v, _ROOT)}")

    if blockers and not args.allow_unverified:
        print(f"  ❌ {len(blockers)} verification blocker(s) on the GO pick — not emailing.")
        args.no_email = True

    if not args.no_email:
        html = ("<div style=\"font-family:Georgia,serif;max-width:640px;color:#1a1c2e\">"
                + digest_md.replace("\n", "<br>") + "</div>")
        subject = (f"1440 WEEKLY DECISION — PROCEED: {go['name']} "
                   f"({e['opportunity']}/100) — week of {monday:%d %b}")
        atts = {k: v for k, v in paths.items() if k in ("pdf", "html")}
        atts["digest"] = md_path
        channel = send_email.deliver(subject, html, digest_md, atts)
        print(f"  Delivery channel: {channel}")

    history.setdefault("log", []).append({
        "date": args.date, "brief_no": brief_no, "id": go["id"], "name": go["name"],
        "opportunity": e["opportunity"], "tier": e["tier"], "kind": "weekly_decision"})
    save_history(history)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    ap.add_argument("--force", help="force a prospect id as today's hero")
    ap.add_argument("--no-email", action="store_true")
    ap.add_argument("--allow-unverified", action="store_true",
                    help="email even if the fact-check gate finds blockers (NOT recommended)")
    ap.add_argument("--verify-net", action="store_true",
                    help="also check that every citation URL resolves before sending")
    ap.add_argument("--list", action="store_true", help="print leaderboard and exit")
    ap.add_argument("--batch", action="store_true",
                    help="render briefs for ALL eligible prospects (no email)")
    ap.add_argument("--series", choices=["F1", "FE", "all", "auto"], default="auto",
                    help="restrict to a championship; 'auto' uses the weekly rota (cadence.py)")
    ap.add_argument("--decision", action="store_true",
                    help="force a weekly DECISION-day digest (the single GO pick)")
    args = ap.parse_args()

    today = _dt.date.fromisoformat(args.date)
    blob = load_prospects()
    prospects = blob["prospects"]
    meta = blob.get("_meta", {})
    cooldown = int(meta.get("cooldown_days", 5))
    min_years = int(meta.get("default_min_deal_years", 3))
    history = load_history()

    # Resolve the day's plan from the weekly rota unless overridden.
    plan = cadence.plan_for(today)
    decision_day = args.decision or (args.series == "auto" and plan == cadence.DECISION)
    if args.series in ("F1", "FE", "all"):
        series = args.series
    elif decision_day:
        series = "all"
    else:  # auto, normal day
        series = plan  # FE or F1
    if not args.list and not args.batch:
        mode = "DECISION (both series)" if decision_day else cadence.LABEL.get(series, series)
        print(f"Cadence: {today:%A} -> {mode}")

    if decision_day and not args.force and not args.list and not args.batch:
        return weekly_decision(prospects, today, cooldown, min_years, history, args)

    ranked = scoring.rank(prospects, today=today, cooldown_days=cooldown,
                          min_deal_years=min_years,
                          history=history.get("last_hero", {}),
                          series=None if series == "all" else series)

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
                why = ("HOLD — " + str(p.get("hold")) if p.get("hold")
                       else "approached (human-layer pipeline)" if p.get("approached")
                       else "crowding>100" if (p.get("est_inbound_pitches") or 0) > 100
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

    # Fact-check / integrity gate — never email a brief that fails verification.
    vfindings = verify_brief.check_prospect(hero, _dt.date.fromisoformat(args.date))
    if args.verify_net:
        vfindings += verify_brief.check_citations(hero)
    blockers = [f for f in vfindings if f[0] == verify_brief.BLOCKER]
    warns = [f for f in vfindings if f[0] == verify_brief.WARN]
    if blockers or warns:
        print("\n  Verification gate:")
        for sev, code, msg in blockers + warns:
            print(f"    {sev}  [{code}] {msg}")
    if blockers and not args.allow_unverified:
        print(f"\n  ❌ {len(blockers)} blocker(s) — refusing to email this brief. "
              "Fix the data (or re-run with --allow-unverified to override).")
        args.no_email = True

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
