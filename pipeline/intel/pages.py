"""Publish the exported desk app to GitHub Pages from the daily job — no git binary needed.

The live site is the ``gh-pages`` branch of the repo (served at
https://trushil27.github.io/1440sports/). After every run the job exports ``index.html`` +
``data.json`` and, when ``GITHUB_TOKEN`` is set (a fine-grained token with *Contents:
read/write* on the repo), writes them to that branch through the Git Data API: blobs → tree
→ commit → force-update ref. Three requests per file plus three per publish; no build step.
"""

from __future__ import annotations

import base64
import datetime as dt
from pathlib import Path
from typing import Any

import httpx

API = "https://api.github.com"
DEFAULT_REPO = "trushil27/1440sports"
DEFAULT_BRANCH = "gh-pages"


def _client(http: httpx.Client | None, token: str) -> httpx.Client:
    if http is not None:
        http.headers.update(
            {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        )
        return http
    return httpx.Client(
        timeout=120,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )


def publish_pages(
    site_dir: Path | str,
    token: str,
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    http: httpx.Client | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    """Replace the whole ``branch`` with the files in ``site_dir`` (+ ``.nojekyll``)."""
    folder = Path(site_dir)
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    if not files:
        raise ValueError(f"nothing to publish in {folder}")
    client = _client(http, token)
    base = f"{API}/repos/{repo}"

    parent: str | None = None
    r = client.get(f"{base}/git/ref/heads/{branch}")
    if r.status_code == 200:
        parent = r.json()["object"]["sha"]
    elif r.status_code != 404:
        r.raise_for_status()

    tree: list[dict[str, str]] = []
    for path in files:
        blob = client.post(
            f"{base}/git/blobs",
            json={
                "content": base64.b64encode(path.read_bytes()).decode("ascii"),
                "encoding": "base64",
            },
        )
        blob.raise_for_status()
        tree.append(
            {
                "path": path.relative_to(folder).as_posix(),
                "mode": "100644",
                "type": "blob",
                "sha": blob.json()["sha"],
            }
        )
    if not any(t["path"] == ".nojekyll" for t in tree):
        blob = client.post(f"{base}/git/blobs", json={"content": "", "encoding": "utf-8"})
        blob.raise_for_status()
        tree.append(
            {"path": ".nojekyll", "mode": "100644", "type": "blob", "sha": blob.json()["sha"]}
        )

    t = client.post(f"{base}/git/trees", json={"tree": tree})
    t.raise_for_status()
    stamp = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    c = client.post(
        f"{base}/git/commits",
        json={
            "message": message or f"desk: daily export {stamp}",
            "tree": t.json()["sha"],
            "parents": [parent] if parent else [],
        },
    )
    c.raise_for_status()
    sha = c.json()["sha"]
    if parent:
        u = client.patch(f"{base}/git/refs/heads/{branch}", json={"sha": sha, "force": True})
    else:
        u = client.post(f"{base}/git/refs", json={"ref": f"refs/heads/{branch}", "sha": sha})
    u.raise_for_status()
    return {"repo": repo, "branch": branch, "commit": sha, "files": len(tree)}
