"""The daily signal email: a scannable card, not a wall of prose.

The MD reads this on a phone between meetings. The old body ran the deck, the bottom line and
the decision-maker together in one block, so nothing could be taken in at a glance (operator
feedback, 6 Sep 2026: "every food item on one plate"). This builds two things instead:

* ``brief_html`` — a brand-styled card: the verdict first, then the facts as a table, then
  the signal, the team rationale and the ask, each under its own heading.
* ``executive_take`` — the same structure in plain text, for clients that refuse HTML.

Nothing new is invented here: every value comes from the brief's own ``brief_data``. Fields
that are missing are simply left out rather than filled with a placeholder.
"""

from __future__ import annotations

import html
import re
from typing import Any

NAVY = "#191a48"
GOLD = "#d1ae7a"
INK = "#1a1c2e"
MUTED = "#6b6e84"
HAIR = "#e3e0d8"
PANEL = "#f4f3ee"


def page_slug(company: str | None) -> str:
    """A company's own path segment: 'Ore Energy' → 'ore-energy'. Empty if there is no name."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (company or "").lower())).strip("-")


def brief_url(app_base_url: str, number: int | str, company: str | None = None) -> str:
    """``<base>/<company>`` — the address of one brief, with nothing numeric in it.

    The link has been through three shapes. ``…//brief/127`` opened the front page (the app
    is hash-routed internally); ``…/#/brief/127`` reads as an in-page anchor in an email;
    ``…/127`` was short but ends in a number, which the operator did not want to send on
    (7 Sep 2026). The export writes a page per company as well as per number, so the address
    can be the company itself and still be a plain static page — no "#", no server rewrite.
    Numeric paths stay as aliases, so every link already sent keeps working; a brief with no
    usable name falls back to the desk's front page rather than showing a number."""
    base = (app_base_url or "").rstrip("/")
    slug = page_slug(company)
    return f"{base}/{slug}" if slug else base


def _verdict(d: dict[str, Any]) -> str:
    """The one line to read if you read nothing else: the brief's own bottom line."""
    from intel.brief_data import strip_markup

    return strip_markup(d.get("bottom_line") or d.get("deck") or "").strip()


def _facts(d: dict[str, Any]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for label, value in (
        ("Series", d.get("series_label")),
        ("Recommended team", d.get("team_label")),
        ("Decision-maker", _decision_maker(d)),
        ("Action horizon", d.get("horizon_label")),
        ("Confidence", d.get("confidence_level")),
    ):
        if value:
            rows.append((label, str(value)))
    return rows


def _decision_maker(d: dict[str, Any]) -> str | None:
    name, role = d.get("decision_maker_name"), d.get("decision_maker_role")
    if not name:
        return None
    return f"{name} — {role}" if role else str(name)


def _sections(d: dict[str, Any]) -> list[tuple[str, str]]:
    """The body, in reading order. Only sections the brief actually has."""
    from intel.brief_data import strip_markup

    out: list[tuple[str, str]] = []
    deck = strip_markup(d.get("deck") or "").strip()
    if deck:
        out.append(("The signal", deck))
    why_team = strip_markup(d.get("why_team_para") or "").strip()
    if why_team:
        label = (d.get("why_team_label") or "Why this team").title()
        out.append((label, why_team))
    ask = strip_markup(((d.get("extended") or {}).get("ask")) or "").strip()
    if ask:
        out.append(("The ask", ask))
    return out


def executive_take(brief, settings) -> str:
    """Plain-text fallback with the same shape as the HTML card."""
    d = brief.brief_data or {}
    company = d.get("company", "?")
    score, tier = d.get("score", "?"), (d.get("timing_label") or "").strip()
    head = f"{company} — {score}/100" + (f" · {tier}" if tier else "")
    lines = [head, "=" * len(head), ""]
    verdict = _verdict(d)
    if verdict:
        lines += ["THE CALL", verdict, ""]
    facts = _facts(d)
    if facts:
        width = max(len(k) for k, _ in facts)
        lines.append("AT A GLANCE")
        lines += [f"  {k.ljust(width)}   {v}" for k, v in facts]
        lines.append("")
    for label, text in _sections(d):
        lines += [label.upper(), text, ""]
    lines += [
        f"Read the full case:  {brief_url(settings.app_base_url, brief.brief_number, company)}",
        "The 2-page brief is attached.",
        "",
        "— 1440 Intelligence Engine",
    ]
    return "\n".join(lines)


def _esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def review_lines(brief) -> list[str]:
    """The open claims and audit findings, one line each — what "verify before circulation"
    actually means for this brief. Empty when everything is verified and the audit passed."""
    from intel.models import VerificationResult

    lines: list[str] = []
    for c in getattr(brief, "claims", None) or []:
        if not c.load_bearing or not c.verifications:
            continue
        v = sorted(c.verifications, key=lambda x: (x.checked_at, x.id))[-1]
        if v.status != VerificationResult.verified:
            lines.append(f"[{v.status.value}] {c.text}" + (f" — {v.notes}" if v.notes else ""))
    for v in getattr(brief, "audit_violations", None) or []:
        lines.append(f"audit rule {v.get('rule')}: {v.get('message') or v.get('note') or ''}")
    return lines


def review_panel_html(brief) -> str:
    """The same card, plus what still needs a human eye. Only for a brief that is not yet
    MD-eligible; the fully verified card carries no such panel."""
    lines = review_lines(brief)
    status = (getattr(getattr(brief, "verification_status", None), "value", "") or "").replace(
        "_", " "
    )
    audit = (getattr(getattr(brief, "audit_status", None), "value", "") or "").replace("_", " ")
    li = f'<li style="margin:0 0 6px;color:{INK};font-size:13.5px;line-height:1.5">'
    items = "".join(f"{li}{_esc(x)}</li>" for x in lines) or (
        f'<li style="color:{MUTED};font-size:13.5px">No open claims.</li>'
    )
    head = (
        '<div style="color:#8a5a00;font-size:11px;letter-spacing:.18em;'
        'text-transform:uppercase;font-weight:700;margin-bottom:6px">'
        "Verify before circulation</div>"
    )
    line = (
        f'<div style="color:{INK};font-size:13px;margin-bottom:8px">'
        f"Verification: <b>{_esc(status)}</b> &nbsp;·&nbsp; Audit: <b>{_esc(audit)}</b>. "
        f"The MD has not been emailed.</div>"
    )
    return (
        '\n  <tr><td style="padding:18px 24px 0">'
        '<div style="background:#fff7e8;border:1px solid #f0d9a8;border-radius:8px;'
        'padding:14px 18px">'
        f'{head}{line}<ul style="margin:0;padding-left:18px">{items}</ul></div></td></tr>'
    )


#: Every brief email must carry these, in this order, or it is not the card the operator
#: approved (7 Sep 2026). A missing piece, a leaked template token or a placeholder value is
#: a format failure — caught here, before the send, never discovered in an inbox.
REQUIRED_HTML = (
    "1440 Sports · Intelligence",
    "Brief N°",
    "The call",
    "At a glance",
    "Read the full case",
    "The 2-page brief is attached",
    "1440 Intelligence Engine",
)
REQUIRED_TEXT = ("THE CALL", "AT A GLANCE", "Read the full case:", "The 2-page brief is attached.")
FORBIDDEN = ("Shadow mode", "[SHADOW]", "${", "{{", "}}", ">None<", ">?<", "?/100", "None/100")


def audit_card(html: str, text: str, settings=None) -> list[str]:
    """Violations in a brief email's body — empty means the format is intact."""
    problems: list[str] = []
    html = html or ""
    text = text or ""
    if not html.strip():
        problems.append("no HTML card at all")
    last = -1
    for needle in REQUIRED_HTML:
        pos = html.find(needle)
        if pos < 0:
            problems.append(f"card is missing: {needle!r}")
        elif pos < last:
            problems.append(f"card section out of order: {needle!r}")
        else:
            last = pos
    for needle in REQUIRED_TEXT:
        if needle not in text:
            problems.append(f"plain text is missing: {needle!r}")
    for bad in FORBIDDEN:
        if bad in html or bad in text:
            problems.append(f"body contains {bad!r}")
    base = (getattr(settings, "app_base_url", "") or "").rstrip("/")
    if base and f'href="{base}/' not in html:
        problems.append(f"card link does not point at {base}")
    if re.search(r'href="https?://[^"]*/\d+"', html):
        problems.append("card link ends in a number")
    return problems


def brief_html(brief, settings, review: bool = False) -> str:
    """A brand-styled card. Inline styles only — email clients strip <style> blocks."""
    d = brief.brief_data or {}
    company = d.get("company", "?")
    score = d.get("score", "?")
    tier = (d.get("timing_label") or "").strip()
    number = brief.brief_number
    url = brief_url(settings.app_base_url, number, company)
    verdict = _verdict(d)

    facts = "".join(
        f'<tr><td style="padding:7px 14px 7px 0;color:{MUTED};font-size:11px;'
        f"letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;"
        f'vertical-align:top">{_esc(k)}</td>'
        f'<td style="padding:7px 0;color:{INK};font-size:14px;font-weight:600">{_esc(v)}</td></tr>'
        for k, v in _facts(d)
    )
    sections = "".join(
        f'<div style="margin:22px 0 0"><div style="color:{GOLD};font-size:11px;'
        f"letter-spacing:.18em;text-transform:uppercase;font-weight:700;"
        f'margin-bottom:6px">{_esc(label)}</div>'
        f'<div style="color:{INK};font-size:15px;line-height:1.55">{_esc(text)}</div></div>'
        for label, text in _sections(d)
    )
    tier_chip = (
        f'<span style="display:inline-block;background:rgba(255,255,255,.14);color:#fff;'
        f"font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;"
        f'border-radius:5px;padding:4px 9px;margin-left:10px">{_esc(tier)}</span>'
        if tier
        else ""
    )
    verdict_block = (
        f'<div style="background:{PANEL};border-left:4px solid {GOLD};border-radius:0 8px 8px 0;'
        f'padding:14px 18px;margin:0 0 20px">'
        f'<div style="color:{MUTED};font-size:11px;letter-spacing:.18em;text-transform:uppercase;'
        f'font-weight:700;margin-bottom:5px">The call</div>'
        f'<div style="color:{INK};font-size:16px;line-height:1.5">{_esc(verdict)}</div></div>'
        if verdict
        else ""
    )
    return f"""\
<div style="margin:0;padding:0;background:#ffffff">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
 style="background:#ffffff;font-family:'Helvetica Neue',Arial,sans-serif">
<tr><td align="center" style="padding:0">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600"
 style="width:600px;max-width:100%">
  <tr><td style="background:{NAVY};padding:18px 24px;border-radius:10px 10px 0 0">
    <div style="color:{GOLD};font-size:11px;letter-spacing:.22em;text-transform:uppercase;
     font-weight:700">1440 Sports · Intelligence</div>
    <div style="color:#ffffff;font-size:12px;letter-spacing:.1em;margin-top:4px">
     Brief N° {_esc(number)}</div>
  </td></tr>
  <tr><td style="background:{NAVY};padding:0 24px 20px">
    <div style="color:#ffffff;font-size:30px;font-weight:700;line-height:1.1">
     {_esc(company)}</div>
    <div style="margin-top:10px">
      <span style="display:inline-block;background:{GOLD};color:{NAVY};font-size:15px;
       font-weight:700;border-radius:5px;padding:5px 11px">{_esc(score)}/100</span>{tier_chip}
    </div>
  </td></tr>
  <tr><td style="border:1px solid {HAIR};border-top:0;border-radius:0 0 10px 10px;
   padding:22px 24px 26px">
    {verdict_block}
    <div style="color:{GOLD};font-size:11px;letter-spacing:.18em;text-transform:uppercase;
     font-weight:700;margin-bottom:4px">At a glance</div>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0"
     style="width:100%;border-collapse:collapse">{facts}</table>
    {sections}
    <div style="margin:28px 0 0">
      <a href="{_esc(url)}" style="display:inline-block;background:{GOLD};color:{NAVY};
       font-size:13px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
       text-decoration:none;border-radius:7px;padding:12px 22px">Read the full case</a>
    </div>
    <div style="color:{MUTED};font-size:12.5px;margin-top:14px">
     The 2-page brief is attached as a PDF.</div>
  </td></tr>
{review_panel_html(brief) if review else ""}
  <tr><td style="padding:16px 24px 0;color:{MUTED};font-size:11px;letter-spacing:.1em;
   text-transform:uppercase">1440 Intelligence Engine</td></tr>
</table>
</td></tr></table></div>"""
