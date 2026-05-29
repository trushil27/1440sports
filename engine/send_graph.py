"""Microsoft Graph email delivery (HTTPS / port 443).

This is the PRIMARY, most robust delivery path for 1440 Sports because:
  - It uses HTTPS (443), which is open even where SMTP (587) is blocked.
  - It sends as the real M365 mailbox via OAuth app credentials, so it does not
    depend on tenant SMTP-AUTH being enabled.

Setup (one-time, done by an M365/Azure admin):
  1. Azure Portal -> App registrations -> New registration.
  2. API permissions -> Microsoft Graph -> Application permission `Mail.Send`
     -> Grant admin consent.
  3. Certificates & secrets -> New client secret.
  4. Collect: Directory (tenant) ID, Application (client) ID, the secret VALUE.

Env vars to enable Graph delivery:
  GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET
  GRAPH_SENDER   (the mailbox to send AS, e.g. trushil.jani@1440sports.com)
  EMAIL_TO       (recipient; defaults to trushil.jani@1440sports.com)
  EMAIL_CC       (optional)

No third-party dependencies: uses only urllib (standard library).
"""
from __future__ import annotations

import base64
import json
import os
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

_LOGIN = "https://login.microsoftonline.com"
_GRAPH = "https://graph.microsoft.com/v1.0"


def is_configured() -> bool:
    return all(os.environ.get(k) for k in
               ("GRAPH_TENANT_ID", "GRAPH_CLIENT_ID",
                "GRAPH_CLIENT_SECRET", "GRAPH_SENDER"))


def _get_token() -> str:
    tenant = os.environ["GRAPH_TENANT_ID"]
    data = urllib.parse.urlencode({
        "client_id": os.environ["GRAPH_CLIENT_ID"],
        "client_secret": os.environ["GRAPH_CLIENT_SECRET"],
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }).encode()
    req = urllib.request.Request(f"{_LOGIN}/{tenant}/oauth2/v2.0/token", data=data)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["access_token"]


def _recipients(value: str) -> List[dict]:
    return [{"emailAddress": {"address": a.strip()}}
            for a in value.split(",") if a.strip()]


def send(subject: str, html_body: str, text_body: str,
         attachments: Optional[Dict[str, str]] = None) -> bool:
    """Send via Graph. Returns True if sent, False if not configured (dry-run)."""
    if not is_configured():
        print("[graph] Not configured (set GRAPH_TENANT_ID/CLIENT_ID/"
              "CLIENT_SECRET/SENDER). Skipping Graph delivery.")
        return False

    sender = os.environ["GRAPH_SENDER"]
    to = os.environ.get("EMAIL_TO", "trushil.jani@1440sports.com")

    message: dict = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": html_body},
        "toRecipients": _recipients(to),
    }
    if os.environ.get("EMAIL_CC"):
        message["ccRecipients"] = _recipients(os.environ["EMAIL_CC"])

    atts = []
    for _label, path in (attachments or {}).items():
        if not path or not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            content = base64.b64encode(fh.read()).decode()
        ctype = ("application/pdf" if path.endswith(".pdf")
                 else "text/html" if path.endswith(".html")
                 else "application/octet-stream")
        atts.append({
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": os.path.basename(path),
            "contentType": ctype,
            "contentBytes": content,
        })
    if atts:
        message["attachments"] = atts

    token = _get_token()
    payload = json.dumps({"message": message, "saveToSentItems": True}).encode()
    req = urllib.request.Request(
        f"{_GRAPH}/users/{urllib.parse.quote(sender)}/sendMail",
        data=payload,
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        ok = resp.status in (200, 202)
    print(f"[graph] Sent '{subject}' to {to} as {sender} (HTTP {resp.status}).")
    return ok
