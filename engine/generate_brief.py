"""Render a prospect record into a branded 2-page brief (HTML + PDF + Markdown).

Branding follows the Ramp Intelligence Brief (N 025): navy #191a48 / gold
#d1ae7a, serif body, 1440 Sports logo masthead. STRICTLY two pages.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

import scoring
import team_fit

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_TEMPLATES = os.path.join(_HERE, "templates")
_LOGO_NAVY = os.path.join(_ROOT, "brand", "assets", "logo-blue-gold@3x.png")
_LOGO_WHITE = os.path.join(_ROOT, "brand", "assets", "logo-white@3x.png")

PILLAR_LABELS = [
    ("timing", "Timing"),
    ("capacity", "Capacity"),
    ("brand_fit", "Brand Fit"),
    ("urgency", "Urgency"),
    ("ops_fit", "Ops Fit"),
]


def _short_roster(team: Dict[str, Any], limit: int = 3) -> str:
    """Human-readable incumbent list for the grid-fit panel."""
    names = list(team.get("competitor_locks", [])) or list(team.get("notable_b2b", []))
    names = [n.split("(")[0].strip(" .") for n in names][:limit]
    return ", ".join(names) if names else "no B2B-tech partner"


def build_gridfit(prospect: Dict[str, Any], max_rows: int = 4):
    """Category-whitespace check from the team-fit engine: the recommended team
    marked as the open lane, contrasted with the most crowded alternatives in the
    same series. Returns [] if we lack fit keywords (so the panel hides cleanly)."""
    kw = team_fit.lanes_for(prospect)
    if not kw["lane"]:
        return []
    raw = json.load(open(os.path.join(_ROOT, "data", "teams.json"), encoding="utf-8"))
    series_key = "f1" if prospect.get("series") == "F1" else "formula_e"
    teams = raw.get(series_key, [])
    rec_name = prospect.get("recommended_team", "")
    rows = []
    for t in teams:
        a = team_fit.assess_team(prospect, t)
        is_rec = (t.get("team", "").lower().split()[0] in rec_name.lower())
        if a["conflicts"]:
            status, label = "conflict", "TAKEN"
            detail = _short_roster(t)
        elif is_rec and a["greenfield"]:
            status, label = "prime", "PRIME LANE"
            detail = "greenfield entry — partner roster being built from zero"
        elif a["crowded"]:
            status, label = "crowded", "CROWDED"
            detail = _short_roster(t)
        else:
            status, label = "open", "OPEN"
            detail = "no rival in this category lane"
        rows.append({"team": t.get("team"), "recommended": is_rec, "status": status,
                     "label": label, "detail": detail,
                     "_w": (len(a["conflicts"]) * 2 + len(a["crowded"]))})
    rec_rows = [r for r in rows if r["recommended"]]
    others = sorted((r for r in rows if not r["recommended"]),
                    key=lambda r: r["_w"], reverse=True)
    return (rec_rows + others)[:max_rows]


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(_TEMPLATES),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _date_long(date: str) -> str:
    try:
        return _dt.date.fromisoformat(date).strftime("%d %b %Y").upper()
    except ValueError:
        return date


def render_html(prospect: Dict[str, Any], brief_no: str = "—",
                date: str | None = None) -> str:
    p = scoring.enrich(prospect)
    date = date or _dt.date.today().isoformat()
    # file:// URIs so WeasyPrint can embed the logo regardless of CWD
    logo_navy = "file://" + _LOGO_NAVY if os.path.exists(_LOGO_NAVY) else ""
    logo_white = "file://" + _LOGO_WHITE if os.path.exists(_LOGO_WHITE) else ""
    tmpl = _env().get_template("brief.html.j2")
    return tmpl.render(p=p, brief_no=brief_no, date=date, date_long=_date_long(date),
                       pillars=PILLAR_LABELS, logo_navy=logo_navy, logo_white=logo_white,
                       gridfit=build_gridfit(p))


def render_markdown(prospect: Dict[str, Any], date: str | None = None) -> str:
    p = scoring.enrich(prospect)
    date = date or _dt.date.today().isoformat()
    L = []
    L.append(f"# 1440 INTELLIGENCE BRIEF — {p['name']}  (N° {p.get('_brief_no','—')})")
    L.append(f"*{p['category']} · {p['hq']}"
             + (f" · {p['ticker']}" if p.get("ticker") else "")
             + f" · {date}*\n")
    L.append(f"**{p['tier']}**\n")
    L.append(f"> {p['headline_long']}\n")
    L.append(f"## OPPORTUNITY {p['opportunity']} / 100\n")
    L.append(f"- **Timing window:** {p['timing_window']}")
    L.append(f"- **Series:** {p['series']}")
    L.append(f"- **Recommended team:** {p['recommended_team']}")
    L.append(f"- **Action horizon:** {p['action_horizon']}")
    L.append(f"- **Mode:** {p['mode']} ({'tech in the car / championship' if p['mode']=='A' else 'tech serves the team operation'})")
    L.append(f"- **Inbound crowding:** {p['crowding_label']}")
    L.append(f"- **Discovery:** {p['discovery']}")
    L.append(f"- **Signals:** {', '.join(s.replace('_',' ') for s in p.get('signals', []))}\n")
    L.append("## THE CASE\n" + p["the_case"] + "\n")
    L.append("## WHY NOW\n" + p["why_now"] + "\n")
    if p.get("key_facts"):
        L.append("## PROOF POINTS  *(every figure verified to a primary source)*")
        for kf in p["key_facts"][:6]:
            L.append(f"- **{kf.get('value')}** — {kf.get('fact')}")
        L.append("")
    gf = build_gridfit(p)
    if gf:
        L.append(f"## GRID FIT  *(category-whitespace check across the {p['series']} grid)*")
        for r in gf:
            mark = " **(recommended)**" if r["recommended"] else ""
            L.append(f"- **{r['team']}**{mark} — `{r['label']}` · {r['detail']}")
        L.append("")
    if p.get("thesis"):
        L.append("> **BOTTOM LINE —** " + p["thesis"] + "\n")
    L.append(f"## WHY {p['recommended_team'].upper()}\n" + p["why_team"] + "\n")
    L.append(f"## VALUE TO {p['recommended_team'].upper()}\n" + p["value_to_team"] + "\n")
    L.append("## DEAL ARCHITECTURE\n" + p["deal_architecture"] + "\n")
    dm = p["decision_maker"]
    L.append("## PRIMARY DECISION-MAKER\n"
             f"**{dm['name']}** — {dm['title']}\n\n{dm['bio']}\n")
    L.append("## OPENING ANGLE\n> " + p["opening_angle"] + "\n")
    L.append("## SCORE COMPOSITION")
    for key, label in PILLAR_LABELS:
        L.append(f"- **{label} {p['scores'][key]}/20** — {p['score_rationale'][key]}")
    L.append("")
    L.append("## RISKS & COUNTERS")
    for r in p["risks"]:
        L.append(f"- **{r['title']}** — {r['detail']} *Counter:* {r['counter']}")
    L.append("")
    L.append("## SOURCES")
    for s in p["sources"]:
        L.append(f"- {s}")
    L.append("\n---\n*1440 Sports · London · Confidential*")
    return "\n".join(L)


def render_pdf(html: str, out_path: str) -> bool:
    """Render HTML to PDF via WeasyPrint, then ENFORCE the 2-page rule.

    Returns False (HTML fallback kept) if WeasyPrint/system libs are missing.
    Raises if the rendered brief exceeds 2 pages, so overflow is caught in CI /
    the daily run rather than shipping a 3-page brief.
    """
    try:
        from weasyprint import HTML  # local import: optional dependency
    except Exception as exc:  # pragma: no cover - environment dependent
        print(f"[generate_brief] PDF skipped ({exc.__class__.__name__}: {exc}).")
        return False

    doc = HTML(string=html).render()
    n = len(doc.pages)
    if n > 2:
        raise RuntimeError(
            f"Brief renders to {n} pages; the 1440 standard is strictly 2. "
            "Trim copy in data/prospects.json for this prospect.")
    doc.write_pdf(out_path)
    return True


def write_brief(prospect: Dict[str, Any], out_dir: str, brief_no: str = "—",
                date: str | None = None) -> Dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    date = date or _dt.date.today().isoformat()
    slug = prospect["id"]
    p = dict(prospect)
    p["_brief_no"] = brief_no
    html = render_html(p, brief_no=brief_no, date=date)
    md = render_markdown(p, date=date)

    paths: Dict[str, str] = {}
    html_path = os.path.join(out_dir, f"{slug}.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    paths["html"] = html_path

    md_path = os.path.join(out_dir, f"{slug}.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(md)
    paths["md"] = md_path

    pdf_path = os.path.join(out_dir, f"{slug}.pdf")
    if render_pdf(html, pdf_path):
        paths["pdf"] = pdf_path
    return paths
