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

import team_fit  # noqa: E402

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
# Language that asserts the prospect could OWN a category / that the grid is empty.
EXCLUSIVITY = re.compile(
    r"category exclusivity|exclusivity|own (the|this|it)\b|define and own|"
    r"no .{0,50}(brand|partner|player|rival).{0,50}(grid|car|paddock)|"
    r"entire .{0,30}category (open|unoccupied)|whitespace|"
    r"nobody .{0,30}(claimed|owns)|unoccupied|no one (has|owns)", re.I)


def _days_since(date_str, today: _dt.date):
    try:
        return (today - _dt.date.fromisoformat(str(date_str))).days
    except (ValueError, TypeError):
        return None


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


def check_prospect(p: dict, today: _dt.date,
                   warn_days: int = 30, block_days: int = 90,
                   teams: list = None) -> list:
    """Return a list of (severity, code, message) findings."""
    out = []
    pid = p.get("id", "?")
    shippable = _is_shippable(p)

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

    # 8. FRESHNESS / DECAY — facts go stale; force periodic re-verification
    lv = p.get("last_verified")
    age = _days_since(lv, today) if lv else None
    if not lv:
        out.append((WARN, "never_verified",
                    "no `last_verified` date — re-check facts and stamp it"))
    elif age is not None and age > block_days:
        sev = BLOCKER if shippable else WARN
        out.append((sev, "stale_data",
                    f"last verified {age}d ago (> {block_days}d) — re-verify before shipping"))
    elif age is not None and age > warn_days:
        out.append((WARN, "aging_data",
                    f"last verified {age}d ago (> {warn_days}d) — consider re-checking"))

    # 9. CLAIM-LEVEL CITATIONS — load-bearing facts must each be bound to a source
    key_facts = p.get("key_facts") or []
    if shippable and not key_facts:
        out.append((WARN, "no_key_facts",
                    "no `key_facts` — bind each load-bearing figure/person/date to a source"))
    srcs = set(p.get("sources", []))
    prose = json.dumps({k: p.get(k) for k in
                        ("headline_long", "the_case", "why_now", "score_rationale")})
    for kf in key_facts:
        label = kf.get("fact", "?")
        if not kf.get("source"):
            out.append((BLOCKER, "fact_uncited", f"key_fact '{label}' has no source"))
        elif kf.get("source") not in srcs:
            out.append((WARN, "fact_src_orphan",
                        f"key_fact '{label}' cites a URL not in `sources`"))
        # drift check: the figure should actually appear somewhere in the prose
        val = str(kf.get("value", ""))
        figs = [_norm_fig(t) for t in FIGURE.findall(val)]
        prose_figs = {_norm_fig(t) for t in FIGURE.findall(prose)}
        missing = [f for f in figs if f not in prose_figs]
        if missing:
            out.append((WARN, "fact_drift",
                        f"key_fact '{label}' value {missing} not reflected in the brief prose"))

    # 10. TEAM-FIT — catch a prospect pointed at a team that already has a rival
    rec = p.get("recommended_team")
    if rec and "(excluded)" not in rec:
        teams = teams if teams is not None else team_fit.load_teams()
        t = team_fit.find_team(rec, teams)
        if t is None:
            out.append((WARN, "team_unknown",
                        f"recommended_team '{rec}' not found in data/teams.json inventory"))
        else:
            a = team_fit.assess_team(p, t)
            # Does the prose make an exclusivity / whitespace claim?
            claim_blob = " ".join(str(p.get(k, "")) for k in
                                  ("headline_long", "the_case", "why_now", "why_team",
                                   "opening_angle", "deal_architecture")) + " " + \
                json.dumps(p.get("score_rationale", {}))
            overclaims = bool(EXCLUSIVITY.search(claim_blob))
            if a["conflicts"] and overclaims and shippable:
                out.append((BLOCKER, "exclusivity_overclaim",
                            f"'{rec}' already has a partner in this lane {a['conflicts']} "
                            "AND the copy claims category exclusivity/whitespace — "
                            "narrow the claim or change team"))
            elif a["conflicts"]:
                out.append((WARN, "team_conflict",
                            f"'{rec}' has a partner in this lane {a['conflicts']} — "
                            "verify there is no category clash"))
            elif a["crowded"]:
                out.append((INFO, "team_crowded",
                            f"'{rec}' is adjacent-crowded {a['crowded']} — keep the "
                            "category claim narrow"))
            # is there a clearly better, cleaner team?
            best = team_fit.recommend(p, teams)[0]
            if best["team"] != a["team"] and best["score"] >= a["score"] + 4 \
                    and not best["conflicts"]:
                out.append((INFO, "team_suggestion",
                            f"team-fit engine ranks '{best['team']}' higher "
                            f"({best['score']} vs {a['score']}) — confirm '{rec}' is intended"))

    # 11. LEADERSHIP TIES — tracking gate: has any senior leader prior F1/FE
    #     ecosystem or sponsorship-deal-structuring history? A confirmed tie is the
    #     warmest signal class (a proven motorsport buyer pre-answers the B2B doubt).
    ties = p.get("leadership_ties")
    if ties is None:
        out.append((INFO, "leadership_ties_unassessed",
                    "leadership F1/FE/deal-history gate not assessed — check each senior "
                    "leader's background and set `leadership_ties` ([] if none found)"))
    elif ties:
        who = ", ".join(t.get("name", "?") for t in ties if isinstance(t, dict))
        out.append((INFO, "leadership_tie",
                    f"⭐ leadership tie to F1/FE/deal-structuring: {who}"))
    else:
        out.append((INFO, "leadership_ties_clear",
                    "leadership checked — no prior F1/FE/deal-structuring ties found"))

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
    meta = data.get("_meta", {}) if isinstance(data, dict) else {}
    warn_days = int(meta.get("verify_warn_days", 30))
    block_days = int(meta.get("verify_block_days", 90))
    teams = team_fit.load_teams()
    items = data if isinstance(data, list) else data.get("prospects", data)
    findings = {}
    for p in items:
        if not isinstance(p, dict):
            continue
        if prospect_ids and p.get("id") not in prospect_ids:
            continue
        f = check_prospect(p, today, warn_days=warn_days,
                           block_days=block_days, teams=teams)
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
