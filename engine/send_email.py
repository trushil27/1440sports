"""Email delivery for the daily hero brief.

Delivery is via SMTP, configured entirely through environment variables so no
credentials are committed. If SMTP is not configured, the brief is still written
to disk and the function reports that delivery was skipped (dry-run).

Required env vars to actually send:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO
Optional:
  SMTP_STARTTLS=1 (default 1), EMAIL_CC

For Microsoft 365 / Outlook, typical settings are:
  SMTP_HOST=smtp.office365.com  SMTP_PORT=587  SMTP_STARTTLS=1
  SMTP_USER=<your o365 address>  SMTP_PASS=<app password>
(See README.md -> 'Delivery' for the M365 setup and alternatives.)
"""
from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Dict, List, Optional


def _required(name: str) -> Optional[str]:
    val = os.environ.get(name)
    return val if val else None


def is_configured() -> bool:
    return all(_required(k) for k in
               ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS",
                "EMAIL_FROM", "EMAIL_TO"))


def build_message(subject: str, html_body: str, text_body: str,
                  attachments: Optional[Dict[str, str]] = None) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ.get("EMAIL_FROM", "briefs@1440sports.com")
    msg["To"] = os.environ.get("EMAIL_TO", "trushil.jani@1440sports.com")
    if os.environ.get("EMAIL_CC"):
        msg["Cc"] = os.environ["EMAIL_CC"]
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    for label, path in (attachments or {}).items():
        if not path or not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            data = fh.read()
        if path.endswith(".pdf"):
            maintype, subtype = "application", "pdf"
        elif path.endswith(".html"):
            maintype, subtype = "text", "html"
        else:
            maintype, subtype = "application", "octet-stream"
        msg.add_attachment(data, maintype=maintype, subtype=subtype,
                           filename=os.path.basename(path))
    return msg


def send(subject: str, html_body: str, text_body: str,
         attachments: Optional[Dict[str, str]] = None) -> bool:
    """Send the brief. Returns True if sent, False if dry-run (not configured)."""
    if not is_configured():
        print("[send_email] SMTP not configured (set SMTP_* + EMAIL_* env vars). "
              "Dry-run: email not sent, brief written to disk.")
        return False

    msg = build_message(subject, html_body, text_body, attachments)
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]
    use_starttls = os.environ.get("SMTP_STARTTLS", "1") != "0"

    recipients: List[str] = [r.strip() for r in os.environ.get("EMAIL_TO", "trushil.jani@1440sports.com").split(",") if r.strip()]
    if os.environ.get("EMAIL_CC"):
        recipients += [r.strip() for r in os.environ["EMAIL_CC"].split(",") if r.strip()]

    context = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(user, password)
            server.send_message(msg, to_addrs=recipients)
    else:
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            if use_starttls:
                server.starttls(context=context)
                server.ehlo()
            server.login(user, password)
            server.send_message(msg, to_addrs=recipients)
    print(f"[send_email] Sent '{subject}' to {recipients}.")
    return True


def email_html_wrapper(prospect_name: str, opportunity: int, band: str,
                       headline: str, inner_summary: str, date: str) -> str:
    """A compact HTML email body summarising the brief (full brief attached).

    Uses the 1440 brand palette: navy #191a48 / gold #d1ae7a, serif."""
    return f"""\
<div style="font-family:Georgia,'Times New Roman',serif;color:#1a1c2e;max-width:640px">
  <div style="font-family:Arial,sans-serif;letter-spacing:.16em;font-size:11px;
              text-transform:uppercase;color:#6b6e84;
              border-bottom:2px solid #191a48;padding-bottom:6px">
    <strong style="color:#191a48">1440 Sports</strong> &middot; Daily Intelligence Brief &middot; {date}
  </div>
  <h1 style="font-size:26px;font-weight:400;color:#191a48;margin:16px 0 4px">{prospect_name}</h1>
  <div style="background:#191a48;color:#fff;border-radius:6px;padding:10px 16px;
              display:inline-block;margin:6px 0">
    <span style="font-size:30px;font-weight:700">{opportunity}</span>
    <span style="color:#d1ae7a"> / 100 &middot; {band}</span>
  </div>
  <p style="font-size:15px;font-weight:600;border-left:3px solid #d1ae7a;
            padding-left:12px;line-height:1.45;color:#191a48">{headline}</p>
  <p style="font-size:13px;line-height:1.55;color:#3a3f47">{inner_summary}</p>
  <p style="font-size:12px;color:#6b6e84">Full 2-page brief attached (PDF + HTML).</p>
  <div style="font-family:Arial,sans-serif;border-top:1px solid #e2e0ea;margin-top:16px;
              padding-top:8px;font-size:10px;color:#9a98aa;letter-spacing:.08em;
              text-transform:uppercase">
    1440 Sports &middot; London &middot; Confidential
  </div>
</div>"""


def deliver(subject: str, html_body: str, text_body: str,
            attachments: Optional[Dict[str, str]] = None) -> str:
    """Unified delivery: try Microsoft Graph (HTTPS/443) first, then SMTP, else
    dry-run. Returns 'graph', 'smtp', or 'dry-run' so callers can report it.

    Graph is preferred because HTTPS is reliably open where SMTP (587) may be
    blocked by network policy or tenant SMTP-AUTH settings.
    """
    try:
        import send_graph
        if send_graph.is_configured():
            if send_graph.send(subject, html_body, text_body, attachments):
                return "graph"
    except Exception as exc:  # pragma: no cover - network/credential dependent
        print(f"[deliver] Graph attempt failed ({exc.__class__.__name__}: {exc}); "
              "falling back to SMTP.")

    try:
        if is_configured():
            if send(subject, html_body, text_body, attachments):
                return "smtp"
    except Exception as exc:  # pragma: no cover
        print(f"[deliver] SMTP attempt failed ({exc.__class__.__name__}: {exc}).")

    print("[deliver] No working delivery channel configured. Dry-run: brief written to disk.")
    return "dry-run"
