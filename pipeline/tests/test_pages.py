"""The daily job publishes the exported app to the gh-pages branch through the Git Data API."""

from __future__ import annotations

import json

import httpx

from intel import pages


def _fake_github(calls: list[dict]) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content) if request.content else None
        calls.append({"method": request.method, "url": str(request.url), "body": body})
        url = str(request.url)
        if request.method == "GET" and url.endswith("/git/ref/heads/gh-pages"):
            return httpx.Response(200, json={"object": {"sha": "oldsha"}})
        if url.endswith("/git/blobs"):
            return httpx.Response(201, json={"sha": f"blob{len(calls)}"})
        if url.endswith("/git/trees"):
            return httpx.Response(201, json={"sha": "treesha"})
        if url.endswith("/git/commits"):
            return httpx.Response(201, json={"sha": "newsha"})
        if url.endswith("/git/refs/heads/gh-pages"):
            return httpx.Response(200, json={"object": {"sha": "newsha"}})
        return httpx.Response(500, json={"message": f"unexpected {url}"})

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_publish_pages_replaces_the_branch_with_the_site_folder(tmp_path):
    (tmp_path / "index.html").write_text("<title>1440 Intelligence Desk</title>", "utf-8")
    (tmp_path / "data.json").write_text("{}", "utf-8")
    calls: list[dict] = []
    out = pages.publish_pages(tmp_path, "tok", http=_fake_github(calls))
    assert out == {"repo": pages.DEFAULT_REPO, "branch": "gh-pages", "commit": "newsha", "files": 3}
    tree_call = next(c for c in calls if c["url"].endswith("/git/trees"))
    paths = sorted(t["path"] for t in tree_call["body"]["tree"])
    assert paths == [".nojekyll", "data.json", "index.html"]
    assert "base_tree" not in tree_call["body"]  # full replace, nothing stale survives
    commit_call = next(c for c in calls if c["url"].endswith("/git/commits"))
    assert commit_call["body"]["parents"] == ["oldsha"]
    ref_call = calls[-1]
    assert ref_call["method"] == "PATCH" and ref_call["body"] == {"sha": "newsha", "force": True}
    assert calls[0]["url"].startswith("https://api.github.com/repos/trushil27/1440sports/")


def test_publish_pages_creates_the_branch_when_missing(tmp_path):
    (tmp_path / "index.html").write_text("x", "utf-8")
    calls: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append({"method": request.method, "url": str(request.url)})
        url = str(request.url)
        if request.method == "GET":
            return httpx.Response(404, json={"message": "Not Found"})
        if url.endswith("/git/refs"):
            return httpx.Response(201, json={"ref": "refs/heads/gh-pages"})
        return httpx.Response(201, json={"sha": "s"})

    out = pages.publish_pages(
        tmp_path, "tok", http=httpx.Client(transport=httpx.MockTransport(handler))
    )
    assert out["commit"] == "s" and calls[-1]["url"].endswith("/git/refs")


def test_settings_read_github_token(monkeypatch):
    from intel.config import Settings

    s = Settings.from_env({"GITHUB_TOKEN": "abc", "PAGES_BRANCH": "gh-pages"})
    assert s.github_token == "abc" and s.pages_repo == "trushil27/1440sports"
