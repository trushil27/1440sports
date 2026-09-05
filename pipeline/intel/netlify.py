"""Netlify zip deploy — one POST, no CLI, no git in the container.

POST https://api.netlify.com/api/v1/sites/{site_id}/deploys with the folder zipped and
Content-Type application/zip publishes it as the site's production deploy.
"""

from __future__ import annotations

from typing import Any

import httpx

API = "https://api.netlify.com/api/v1"


def deploy(
    zip_bytes: bytes, token: str, site_id: str, http: httpx.Client | None = None
) -> dict[str, Any]:
    client = http or httpx.Client(timeout=120)
    r = client.post(
        f"{API}/sites/{site_id}/deploys",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/zip"},
        content=zip_bytes,
    )
    r.raise_for_status()
    body = r.json()
    return {
        "id": body.get("id"),
        "state": body.get("state"),
        "url": body.get("ssl_url") or body.get("url"),
        "deploy_url": body.get("deploy_ssl_url") or body.get("deploy_url"),
    }
