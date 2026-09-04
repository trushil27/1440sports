"""Team-fit engine: match a prospect to the right racing team, and — more
importantly — catch when a prospect is pointed at a team that already carries a
competitor in its lane. This is the automated guard against the class of error
where a brief overclaims 'category whitespace' on a team that is actually taken.

Two-tier matching, so we can tell a hard clash from mere crowding:
  - fit_lane:   the prospect's NARROW category (e.g. 'backup', 'recovery').
                A team `competitor_locks` / partner hit here = CONFLICT (blocker).
  - fit_domain: the prospect's BROAD space (e.g. 'data', 'security').
                A team partner hit here (but not the lane) = CROWDED (warning).

Prospects may declare `fit_lane` / `fit_domain` explicitly (preferred, precise);
otherwise we derive rough tokens from the `category` string.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TEAMS = os.path.join(_ROOT, "data", "teams.json")

_STOP = {"ai", "the", "and", "of", "/", "-", "&", "tech", "technology", "enterprise",
         "software", "platform", "management", "services", "solutions"}


def _tokens(text: str) -> set:
    return {t for t in re.split(r"[^a-z0-9]+", str(text).lower())
            if t and t not in _STOP and len(t) > 2}


def lanes_for(prospect: Dict[str, Any]) -> Dict[str, set]:
    """Return {'lane': set, 'domain': set} for a prospect."""
    lane = set(map(str.lower, prospect.get("fit_lane", [])))
    domain = set(map(str.lower, prospect.get("fit_domain", [])))
    if not lane:
        lane = _tokens(prospect.get("category", ""))
    if not domain:
        domain = _tokens(prospect.get("category", ""))
    # expand multi-word lane/domain entries into their tokens too
    lane |= {t for phrase in list(lane) for t in _tokens(phrase)}
    domain |= {t for phrase in list(domain) for t in _tokens(phrase)}
    return {"lane": lane, "domain": domain}


def _hits(keywords: set, *blobs: str) -> List[str]:
    blob = " ".join(b.lower() for b in blobs if b)
    return sorted({k for k in keywords if k in blob})


def load_teams() -> List[Dict[str, Any]]:
    data = json.load(open(_TEAMS, encoding="utf-8"))
    teams = list(data.get("f1", [])) + list(data.get("formula_e", []))
    return teams


def assess_team(prospect: Dict[str, Any], team: Dict[str, Any]) -> Dict[str, Any]:
    """Assess one team for one prospect: conflicts, crowding, openings, score."""
    kw = lanes_for(prospect)
    locks = " ; ".join(team.get("competitor_locks", []))
    partners = " ; ".join(team.get("notable_b2b", []))
    opens = " ; ".join(team.get("open_categories", []))

    # A genuine clash = a PRODUCT brand locking the prospect's narrow lane
    # (competitor_locks). Services integrators (Mphasis, TCS, Cognizant...) sit
    # in notable_b2b and count only as crowding, never a hard conflict.
    conflicts = _hits(kw["lane"], locks)                       # lane locked -> CONFLICT
    crowded = sorted(set(_hits(kw["domain"], locks, partners)) - set(conflicts))
    openings = _hits(kw["lane"] | kw["domain"], opens)

    greenfield = not team.get("notable_b2b") or "debut" in str(team.get("note", "")).lower()
    score = (len(openings) * 2) - (len(conflicts) * 4) - len(crowded) + (1 if greenfield else 0)
    return {
        "team": team.get("team"),
        "score": score,
        "conflicts": conflicts,
        "crowded": crowded,
        "openings": openings,
        "greenfield": greenfield,
    }


def recommend(prospect: Dict[str, Any], teams: Optional[List] = None) -> List[Dict[str, Any]]:
    teams = teams if teams is not None else load_teams()
    out = [assess_team(prospect, t) for t in teams]
    out.sort(key=lambda a: a["score"], reverse=True)
    return out


def find_team(name: str, teams: Optional[List] = None) -> Optional[Dict[str, Any]]:
    """Match a recommended_team string (e.g. 'Cadillac F1 Team') to inventory."""
    teams = teams if teams is not None else load_teams()
    n = (name or "").lower()
    for t in teams:
        tn = t.get("team", "").lower()
        if tn and (tn in n or n in tn or tn.split()[0] in n):
            return t
    return None
