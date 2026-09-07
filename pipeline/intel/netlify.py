"""Netlify zip deploy — one POST, no CLI, no git in the container.

POST https://api.netlify.com/api/v1/sites/{site_id}/deploys with the folder zipped and
Content-Type application/zip publishes it as the site's production deploy.

``site_id`` may be the site's default domain (``1440-intelligence.netlify.app``) as well as
its UUID, which is what lets the desk find — or create — its own site from a token alone.
Setting up the link is then ONE secret, ``NETLIFY_AUTH_TOKEN``: no clicking through the
dashboard to claim a name, copy a site id and paste it back as a second secret.
"""

from __future__ import annotations

from typing import Any, Protocol

import httpx

API = "https://api.netlify.com/api/v1"

#: The site the desk claims when it is given a token and no site id. It is the name the
#: operator chose on 7 Sep 2026, so the emailed link reads 1440-intelligence.netlify.app.
DEFAULT_SITE_NAME = "1440-intelligence"


class _HasNetlify(Protocol):  # a Settings-shaped object, without importing config
    netlify_auth_token: str | None
    netlify_site_id: str | None
    netlify_site_name: str


def _client(http: httpx.Client | None) -> httpx.Client:
    return http or httpx.Client(timeout=120)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def find_site(token: str, name: str, http: httpx.Client | None = None) -> dict[str, Any] | None:
    """The site called ``name``, or None if this account has no such site."""
    r = _client(http).get(f"{API}/sites/{name}.netlify.app", headers=_auth(token))
    if r.status_code in (401, 403, 404):
        return None
    r.raise_for_status()
    return r.json()


def ensure_site(
    token: str, name: str = DEFAULT_SITE_NAME, http: httpx.Client | None = None
) -> dict[str, Any]:
    """Return the account's ``name`` site, creating it on the first run.

    Netlify site names are global, so a name somebody else already owns cannot be claimed;
    that comes back as a 422 and is re-raised with the name in the message rather than
    swallowed — a silent fallback would publish the desk to an address nobody was told about.
    """
    existing = find_site(token, name, http)
    if existing:
        return existing
    r = _client(http).post(f"{API}/sites", headers=_auth(token), json={"name": name})
    if r.status_code == 422:
        raise RuntimeError(
            f"Netlify will not create a site named {name!r} (it is taken, or the token cannot "
            f"create sites). Pick another name with NETLIFY_SITE_NAME, or set NETLIFY_SITE_ID "
            f"to a site that already exists. Netlify said: {r.text[:200]}"
        )
    r.raise_for_status()
    return r.json()


def resolve_site_id(settings: _HasNetlify, http: httpx.Client | None = None) -> str | None:
    """The site to deploy to: the configured id if there is one, else the desk's own site."""
    if settings.netlify_site_id:
        return settings.netlify_site_id
    if not settings.netlify_auth_token:
        return None
    site = ensure_site(settings.netlify_auth_token, settings.netlify_site_name, http)
    return site.get("id") or site.get("site_id")


def deploy(
    zip_bytes: bytes, token: str, site_id: str, http: httpx.Client | None = None
) -> dict[str, Any]:
    client = _client(http)
    r = client.post(
        f"{API}/sites/{site_id}/deploys",
        headers={**_auth(token), "Content-Type": "application/zip"},
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
