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
from typing import Any

NAVY = "#191a48"
GOLD = "#d1ae7a"
INK = "#1a1c2e"
MUTED = "#6b6e84"
HAIR = "#e3e0d8"
PANEL = "#f4f3ee"


def brief_url(app_base_url: str, number: int | str) -> str:
    """``<base>/brief/<n>/`` — a real address, not an in-page anchor.

    The export writes each brief as its own static page (``site_export._write_brief_pages``),
    so the link needs no "#" and no server rewrite. It read as ``…/#/brief/127`` before, which
    looks like an internal fragment in an email (operator, 6 Sep 2026); and before that it was
    ``…//brief/127``, which opened the front page because the app is hash-routed internally."""
    return f"{(app_base_url or '').rstrip('/')}/brief/{number}/"


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
        f"Read the full case:  {brief_url(settings.app_base_url, brief.brief_number)}",
        "The 2-page brief is attached.",
        "",
        "— 1440 Intelligence Engine",
    ]
    note = _mode_note(settings)
    if note:
        lines.append(note)
    return "\n".join(lines)


def _mode_note(settings) -> str:
    """Shadow copies used to shout "[SHADOW]" from the subject line. The subject is what the
    MD sees, so the marker lives here instead — still unmistakable to the operator."""
    if getattr(settings, "execution_mode", "production") == "production":
        return ""
    return "Shadow mode: operator copy, not sent to the MD."


def _esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def brief_html(brief, settings) -> str:
    """A brand-styled card. Inline styles only — email clients strip <style> blocks."""
    d = brief.brief_data or {}
    company = d.get("company", "?")
    score = d.get("score", "?")
    tier = (d.get("timing_label") or "").strip()
    number = brief.brief_number
    url = brief_url(settings.app_base_url, number)
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
    note = _mode_note(settings)
    mode_note = f' · <span style="color:{MUTED}">{_esc(note)}</span>' if note else ""
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
  <tr><td style="padding:16px 24px 0;color:{MUTED};font-size:11px;letter-spacing:.1em;
   text-transform:uppercase">1440 Intelligence Engine{mode_note}</td></tr>
</table>
</td></tr></table></div>"""
