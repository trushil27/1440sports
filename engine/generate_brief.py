"""Render a prospect record into HTML, PDF, and Markdown 2-page briefs."""
from __future__ import annotations

import datetime as _dt
import os
from typing import Any, Dict, Tuple

from jinja2 import Environment, FileSystemLoader, select_autoescape

import scoring

_HERE = os.path.dirname(os.path.abspath(__file__))
_TEMPLATES = os.path.join(_HERE, "templates")

PILLAR_LABELS = [
    ("timing", "Timing"),
    ("capacity", "Capacity"),
    ("brand_fit", "Brand Fit"),
    ("urgency", "Urgency"),
]


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(_TEMPLATES),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_html(prospect: Dict[str, Any], brief_no: str = "—",
                date: str | None = None) -> str:
    p = scoring.enrich(prospect)
    date = date or _dt.date.today().isoformat()
    tmpl = _env().get_template("brief.html.j2")
    return tmpl.render(p=p, brief_no=brief_no, date=date, pillars=PILLAR_LABELS)


def render_markdown(prospect: Dict[str, Any], date: str | None = None) -> str:
    p = scoring.enrich(prospect)
    date = date or _dt.date.today().isoformat()
    L = []
    L.append(f"# 1440 INTELLIGENCE BRIEF — {p['name']}")
    L.append(f"*{p['category']} · {p['hq']}"
             + (f" · {p['ticker']}" if p.get("ticker") else "")
             + f" · {date}*\n")
    L.append(f"> **{p['headline']}**\n")
    L.append(f"## OPPORTUNITY {p['opportunity']} / 100 — {p['band']}\n")
    L.append(f"- **Timing window:** {p['timing_window']}")
    L.append(f"- **Series:** {p['series']}")
    L.append(f"- **Recommended team:** {p['recommended_team']}")
    L.append(f"- **Action horizon:** {p['action_horizon']}")
    L.append(f"- **Inbound crowding:** {p['crowding_label']}")
    L.append(f"- **Signals:** {', '.join(s.replace('_', ' ') for s in p.get('signals', []))}\n")
    L.append("## THE CASE\n" + p["the_case"] + "\n")
    L.append("## WHY NOW\n" + p["why_now"] + "\n")
    L.append(f"## WHY {p['recommended_team'].upper()}\n" + p["why_team"] + "\n")
    L.append("## DEAL ARCHITECTURE\n" + p["deal_architecture"] + "\n")
    dm = p["decision_maker"]
    L.append("## PRIMARY DECISION-MAKER\n"
             f"**{dm['name']}** — {dm['title']}\n\n{dm['bio']}\n")
    L.append("## OPENING ANGLE\n> " + p["opening_angle"] + "\n")
    L.append("## SCORE COMPOSITION")
    for key, label in PILLAR_LABELS:
        L.append(f"- **{label} {p['scores'][key]}/25** — {p['score_rationale'][key]}")
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
    """Render HTML to PDF via WeasyPrint. Returns False (and leaves the HTML
    fallback) if WeasyPrint or its system libraries are unavailable."""
    try:
        from weasyprint import HTML  # noqa: WPS433 (local import is intentional)
        HTML(string=html).write_pdf(out_path)
        return True
    except Exception as exc:  # pragma: no cover - environment dependent
        print(f"[generate_brief] PDF skipped ({exc.__class__.__name__}: {exc}).")
        return False


def write_brief(prospect: Dict[str, Any], out_dir: str, brief_no: str = "—",
                date: str | None = None) -> Dict[str, str]:
    """Write HTML, Markdown and (best-effort) PDF. Returns paths actually written."""
    os.makedirs(out_dir, exist_ok=True)
    date = date or _dt.date.today().isoformat()
    slug = prospect["id"]
    html = render_html(prospect, brief_no=brief_no, date=date)
    md = render_markdown(prospect, date=date)

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
