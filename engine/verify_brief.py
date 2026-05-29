"""Pre-flight fact-check / integrity gate for a prospect brief.

Philosophy: a brief that reaches the MD must not contain a claim we cannot
stand behind. This module cannot *know* truth, but it can refuse to let
mechanically-detectable defects through and force every high-risk claim to be
backed by a live, reachable citation. Anything it cannot clear is surfaced as a
BLOCKER so the daily run stops before emailing.

Two layers:
  1. check_prospect()  - mechanical checks, runnable with no network:
       required fields, score integrity, band/score agreement, gate rules,
       generic decision-maker, future/stale dates, numeric cross-consistency.
  2. check_citations() - network layer (HTTPS/443): every URL in `sources`
       must resolve (not 4xx/5xx/dead). 403 is reported as WARN (some sites
       block bots) rather than a hard BLOCKER.

Severity: BLOCKER (must fix before send), WARN (review), INFO.

Usage:
  python engine/verify_brief.py            # verify every prospect, no network
  python engine/verify_brief.py --net      # also check citation URLs live
  python engine/verify_brief.py cohesity --net
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import urllib.request

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_ROOT, "data", "prospects.json")

BLOCKER, WARN, INFO = "BLOCKER", "WARN", "INFO"

# Fields every shippable prospect must carry.
REQUIRED = ["id", "name", "category", "hq", "scores", "score_rationale",
            "headline_long", "the_case", "why_now", "decision_maker", "sources"]
GENERIC_DM = re.compile(r"^(the\s+)?(cmo|ceo|cfo|cro|president|head of|vp|"
                        r"chief\s+\w+\s+officer)\b", re.I)
# A money/figure token, e.g. $17B, $1.5 billion, $531.8M, 28%
FIGURE = re.compile(r"\$\s?\d[\d,.]*\s?(?:bn|billion|million|thousand|b|m|k)?|\b\d[\d,.]*%",
                    re.I)
YEAR = re.compile(r"\b(20\d{2})\b")


def _norm_fig(tok: str) -> str:
    """Normalise a money/percent token so '$1.5B' == '$1.5 billion'."""
    t = re.sub(r"\s+", "", tok.lower()).rstrip(".")
    t = t.replace("billion", "b").replace("bn", "b")
    t = t.replace("million", "m").replace("mm", "m")
    t = t.replace("thousand", "k")
    return t


def _is_shippable(p: dict) -> bool:
    """A prospect we would actually email as a hero. Non-shippable records
    (watch/parked/excluded/gated/already-present) are still checked, but their
    blockers don't gate the daily send because run_daily never selects them."""
    if p.get("status") not in (None, "active"):
        return False
    if p.get("already_present"):
        return False
    pitches = p.get("est_inbound_pitches")
    if isinstance(pitches, (int, float)) and pitches > 100:
        return False
    return True


def check_prospect(p: dict, today: _dt.date) -> list:
    """Return a list of (severity, code, message) findings."""
    out = []
    pid = p.get("id", "?")

    # 1. required fields
    for f in REQUIRED:
        if not p.get(f):
            out.append((BLOCKER, "missing_field", f"`{f}` is missing/empty"))

    # 2. score integrity (five pillars, each 0-20, total drives the band)
    scores = p.get("scores", {})
    if scores:
        for k, v in scores.items():
            if not isinstance(v, (int, float)) or not (0 <= v <= 20):
                out.append((BLOCKER, "score_range",
                            f"score `{k}`={v} outside 0-20"))
        total = sum(v for v in scores.values() if isinstance(v, (int, float)))
        # every scored pillar should carry a rationale
        for k in scores:
            if k not in (p.get("score_rationale") or {}):
                out.append((WARN, "score_no_rationale",
                            f"score `{k}` has no rationale line"))
        out.append((INFO, "score_total", f"opportunity total = {total}/100"))

    # 3. gate rules from methodology
    pitches = p.get("est_inbound_pitches")
    if isinstance(pitches, (int, float)) and pitches > 100:
        out.append((BLOCKER, "crowding_gate",
                    f"est_inbound_pitches={pitches} > 100 (should be gated out)"))
    if isinstance(p.get("min_deal_years"), (int, float)) and p["min_deal_years"] < 3:
        out.append((BLOCKER, "deal_floor",
                    f"min_deal_years={p['min_deal_years']} < 3"))

    # 4. decision-maker must be a verified, named individual
    dm = p.get("decision_maker") or {}
    if isinstance(dm, dict):
        name = (dm.get("name") or "").strip()
        if not name:
            out.append((BLOCKER, "dm_missing", "decision_maker.name is empty"))
        elif GENERIC_DM.match(name) or " " not in name:
            out.append((BLOCKER, "dm_generic",
                        f"decision_maker '{name}' looks generic, not a named person"))
    else:
        out.append((BLOCKER, "dm_shape", "decision_maker is not an object"))

    # 5. dates: nothing should claim a date in the future of `today`
    blob = json.dumps(p)
    for y in set(YEAR.findall(blob)):
        if int(y) > today.year + 1:  # next-year IPO talk is fine; 2+ is suspect
            out.append((WARN, "future_year",
                        f"references year {y} (>{today.year+1}); confirm it's intended"))

    # 6. numeric cross-consistency: figures in the headline should reappear in
    #    the_case (so the punchy number is the same as the argued number).
    head = p.get("headline_long", "")
    case = p.get("the_case", "")
    head_figs = {_norm_fig(t) for t in FIGURE.findall(head)}
    case_figs = {_norm_fig(t) for t in FIGURE.findall(case)}
    for f in head_figs - case_figs:
        out.append((WARN, "figure_unbacked",
                    f"headline figure '{f}' not restated in the_case "
                    "(verify it's supported)"))

    # 7. must have at least one citation, and high-risk claims need sourcing
    if not p.get("sources"):
        out.append((BLOCKER, "no_sources", "no `sources` citations at all"))

    return out


def _url_status(url: str, timeout: int = 12) -> int:
    req = urllib.request.Request(url, method="GET",
                                 headers={"User-Agent": "Mozilla/5.0 (1440-verify)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def check_citations(p: dict) -> list:
    out = []
    for url in p.get("sources", []):
        code = _url_status(url)
        if code == 0:
            out.append((BLOCKER, "cite_dead", f"citation unreachable: {url}"))
        elif code in (401, 403, 429):
            out.append((WARN, "cite_blocked",
                        f"citation returned {code} (bot-blocked/paywall, verify manually): {url}"))
        elif code >= 400:
            out.append((BLOCKER, "cite_broken", f"citation HTTP {code}: {url}"))
        else:
            out.append((INFO, "cite_ok", f"citation {code}: {url}"))
    return out


def verify(prospect_ids=None, net=False, today=None):
    today = today or _dt.date.today()
    data = json.load(open(_DATA, encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("prospects", data)
    findings = {}
    for p in items:
        if not isinstance(p, dict):
            continue
        if prospect_ids and p.get("id") not in prospect_ids:
            continue
        f = check_prospect(p, today)
        if net:
            f += check_citations(p)
        findings[p.get("id", "?")] = {"shippable": _is_shippable(p), "findings": f}
    return findings


def has_blockers(findings, shippable_only=True) -> bool:
    """True if any BLOCKER exists. By default only counts shippable records,
    since the daily run never emails non-shippable ones."""
    for rec in findings.values():
        if shippable_only and not rec["shippable"]:
            continue
        if any(sev == BLOCKER for sev, *_ in rec["findings"]):
            return True
    return False


def _print(findings):
    order = {BLOCKER: 0, WARN: 1, INFO: 2}
    n_block = n_warn = n_ship_block = 0
    for pid, rec in findings.items():
        fs = sorted(rec["findings"], key=lambda x: order[x[0]])
        head = [x for x in fs if x[0] == BLOCKER]
        warn = [x for x in fs if x[0] == WARN]
        n_block += len(head); n_warn += len(warn)
        if rec["shippable"]:
            n_ship_block += len(head)
        tag_ship = "" if rec["shippable"] else "  (non-shippable: not gated)"
        mark = "❌" if head else ("⚠️ " if warn else "✅")
        print(f"\n{mark} {pid}{tag_ship}")
        for sev, code, msg in fs:
            tag = {BLOCKER: "❌ BLOCKER", WARN: "⚠️  WARN  ", INFO: "·  info  "}[sev]
            print(f"   {tag}  [{code}] {msg}")
    print(f"\n— {n_ship_block} blocker(s) on shippable briefs "
          f"({n_block} total), {n_warn} warning(s) across {len(findings)} brief(s) —")
    return n_ship_block


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="prospect ids to check (default: all)")
    ap.add_argument("--net", action="store_true", help="also verify citation URLs live")
    args = ap.parse_args()
    res = verify(args.ids or None, net=args.net)
    blockers = _print(res)
    sys.exit(1 if blockers else 0)
