"""The static app: every brief, the sponsor grid and the calendar exported from the database
into one ``data.json`` and inlined into ``app.html`` → ``index.html`` (build brief §8, MD
request 5 Sep 2026: "same front end as Mission Control — Home with today's signal, F1 / FE /
All tiles, sponsors by series with who since when and until when").

``python -m intel.site_export --out site/`` writes the two files; the daily job calls
``publish()`` after distribution and, when ``NETLIFY_AUTH_TOKEN`` + ``NETLIFY_SITE_ID`` are set,
deploys the folder to Netlify. Nothing here can fail the run: the caller wraps it.
"""

from __future__ import annotations

import datetime as dt
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from intel.config import Settings, get_settings
from intel.models import Brief, CalendarEvent, Sponsor, VerificationStatus
from intel.seed import load_team_profiles

SITE_SRC = Path(__file__).parent / "site" / "app.html"
DATA_TOKEN = "__DATA_JSON__"
REVIEW_FILE = Path(__file__).resolve().parents[2] / "data" / "history_review.json"


def load_review(path: Path = REVIEW_FILE) -> dict[str, dict[str, Any]]:
    """data/history_review.json rows keyed by 'date|normalised company'."""
    from intel.normalise import company_norm

    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8")).get("rows", {})
    out: dict[str, dict[str, Any]] = {}
    for key, decision in raw.items():
        parts = key.split("|")
        if len(parts) < 2:
            continue
        out[f"{parts[0]}|{company_norm(parts[1])}"] = decision
    return out


def review_for(review: dict[str, dict[str, Any]], date: str, company: str) -> dict[str, Any]:
    from intel.normalise import company_norm

    d = review.get(f"{date}|{company_norm(company)}")
    if not d:
        return {"status": "keep"}
    out = {
        "status": d.get("status", "keep"),
        "reason": d.get("reason"),
        "reason_code": d.get("reason_code"),
    }
    if d.get("of"):
        parts = d["of"].split("|")
        out["of"] = f"{parts[0]}|{company_norm(parts[1])}"
    return out


# spec/active_sponsor_db.md §7 — the only publicly reported end dates. Everything else is
# "not stated", never "open-ended".
RENEWALS: list[dict[str, str]] = [
    {
        "brand": "Julius Baer",
        "property": "FE championship",
        "until": "End of Season 12 (2026)",
        "kind": "confirmed",
        "source": "fiaformulae.com / Julius Baer 2022 announcement",
    },
    {
        "brand": "Liqui Moly",
        "property": "F1 championship",
        "until": "End of 2026",
        "kind": "reported",
        "source": "Public reporting on renewal extension",
    },
    {
        "brand": "Aramco",
        "property": "Aston Martin F1 title",
        "until": "End of 2028",
        "kind": "confirmed",
        "source": "Aramco / Aston Martin announcement",
    },
    {
        "brand": "Crypto.com",
        "property": "F1 championship",
        "until": "Through 2030",
        "kind": "reported",
        "source": "Public reporting",
    },
    {
        "brand": "Aramco",
        "property": "F1 championship",
        "until": "Through 2030",
        "kind": "reported",
        "source": "Public reporting",
    },
    {
        "brand": "LVMH",
        "property": "F1 championship",
        "until": "Through 2030",
        "kind": "reported",
        "source": "Public reporting",
    },
    {
        "brand": "Salesforce",
        "property": "F1 championship",
        "until": "Through 2030",
        "kind": "confirmed",
        "source": "Salesforce announcement",
    },
]

_SINCE = re.compile(
    r"\b(?:since|from|joined(?: in| for)?|partner since|continued from)\s+"
    r"(?:end[- ]of\s+)?(20\d\d)",
    re.I,
)
_UNTIL = re.compile(
    r"\b(?:through|until|to|expires?|expected to expire|end of|runs? through|renewed (?:for|to)"
    r"|commitment[^.]*?at least)\s+(?:end[- ]of\s+)?(?:the\s+)?(20\d\d)",
    re.I,
)
_CONFIRMED = re.compile(r"\b(confirmed|announced|extended|renewed|signed)\b", re.I)
_REPORTED = re.compile(r"\b(reported|reportedly|per public reporting|expected|linked)\b", re.I)

_FE_WORDS = re.compile(
    r"formula e|e-prix|\bev\b|electric|batter|charging|grid|solar|energy|sustainab|carbon|hydrogen"
    r"|mobility|fleet|micromobility|renewable|clean ?tech|climate|nuclear|fusion|reactor"
    r"|geothermal|power plant|lithium|electrif",
    re.I,
)
_FE_TEAMS = (
    "porsche",
    "jaguar",
    "nissan",
    "ds penske",
    "andretti",
    "envision",
    "mahindra",
    "cupra",
    "lola",
    "abt",
    "citro",
    "maserati",
    "mclaren formula e",
)


def since_until(notes: str | None) -> dict[str, Any]:
    """Parse 'since YYYY' / 'through YYYY' from a sponsor row's notes. Absent → not stated."""
    text = notes or ""
    since = _SINCE.search(text)
    until = _UNTIL.search(text)
    kind = None
    if until:
        window = text[max(0, until.start() - 60) : until.end() + 40]
        kind = (
            "reported"
            if _REPORTED.search(window)
            else ("confirmed" if _CONFIRMED.search(window) else "reported")
        )
    return {
        "since": since.group(1) if since else None,
        "until": until.group(1) if until else None,
        "until_kind": kind,
    }


def _renewal_for(brand: str, team: str | None, level: str | None) -> dict[str, str] | None:
    b = (brand or "").strip().lower()
    for r in RENEWALS:
        if r["brand"].lower() != b:
            continue
        prop = r["property"].lower()
        if team and ("title" in prop or (team.split()[0].lower() in prop)):
            return r
        if not team and "championship" in prop:
            return r
    return None


def sponsor_row(s: Sponsor) -> dict[str, Any]:
    parsed = since_until(s.notes)
    renewal = _renewal_for(s.brand, s.team, s.level.value if hasattr(s.level, "value") else s.level)
    if renewal:
        parsed["until"] = renewal["until"]
        parsed["until_kind"] = renewal["kind"]
        parsed["until_source"] = renewal["source"]
    return {
        "series": s.series.value,
        "level": s.level.value if hasattr(s.level, "value") else str(s.level or ""),
        "team": s.team,
        "brand": s.brand,
        "category": s.category,
        "status": s.status.value,
        "season": s.season,
        "notes": s.notes,
        "source": s.source,
        "verified_at": s.verified_at.isoformat() if s.verified_at else None,
        **parsed,
    }


def infer_series(card: dict[str, Any], data: dict[str, Any]) -> tuple[str | None, bool]:
    """Recorded series when the brief has one; otherwise a flagged inference from the text."""
    if card.get("series") in ("F1", "FE"):
        return card["series"], False
    blob = " ".join(
        str(x or "")
        for x in (
            card.get("team"),
            card.get("industry"),
            card.get("take"),
            data.get("trigger"),
            data.get("the_case_p1"),
        )
    ).lower()
    if any(t in blob for t in _FE_TEAMS) or "formula e" in blob:
        return "FE", True
    if _FE_WORDS.search(blob):
        return "FE", True
    if blob.strip():
        return "F1", True
    return None, False


def brief_label(brief: Brief) -> str:
    d = brief.brief_data or {}
    if brief.historical and d.get("historical_label"):
        return str(d["historical_label"])
    if brief.historical:
        return "historical"
    return f"N° {brief.brief_number:03d}"


def brief_card(brief: Brief) -> dict[str, Any]:
    """Same shape as the API's card (kept here so the pipeline image needs no api package)."""
    from intel.score import tier_for

    d = brief.brief_data or {}
    cand = brief.candidate
    score = d.get("score", cand.score_total)
    return {
        "number": brief.brief_number,
        "label": brief_label(brief),
        "date": brief.run_date.isoformat(),
        "company": d.get("company") or cand.company_raw,
        "score": score,
        "tier": tier_for(int(score)) if score is not None else None,
        "series": d.get("series_label") or (cand.series.value if cand.series else None),
        "team": d.get("team_label") or cand.recommended_team,
        "person": d.get("decision_maker_name"),
        "role": d.get("decision_maker_role"),
        "take": d.get("deck"),
        "verification": brief.verification_status.value,
        "audit": brief.audit_status.value,
        "track": 2 if cand.track == 2 else 1,
        "historical": brief.historical,
        "industry": d.get("industry_meta"),
        "confidence": d.get("confidence_level"),
    }


def brief_entry(
    brief: Brief, include_page: bool, review: dict[str, dict[str, Any]] | None = None
) -> dict[str, Any]:
    from intel.normalise import company_norm

    card = brief_card(brief)
    d = brief.brief_data or {}
    series, inferred = infer_series(card, d)
    rv = (
        review_for(review or {}, card["date"], card["company"])
        if brief.historical
        else {"status": "keep"}
    )
    entry = {
        **card,
        "key": f"{card['date']}|{company_norm(card['company'])}",
        "review": rv,
        "source_label": d.get("historical_source") if brief.historical else "engine",
        "series": series,
        "series_inferred": inferred,
        "deck": d.get("deck"),
        "bottom_line": d.get("bottom_line"),
        "trigger": brief.candidate.trigger_reason_raw,
        "trigger_date": brief.candidate.trigger_date.isoformat()
        if brief.candidate.trigger_date
        else None,
        "source_url": brief.candidate.source_url,
        "horizon": d.get("horizon_label"),
        "signals": d.get("signals") or [],
        "has_page": bool(brief.web_html_path),
    }
    if include_page and brief.web_html_path and Path(brief.web_html_path).exists():
        entry["page_html"] = Path(brief.web_html_path).read_text(encoding="utf-8")
    return entry


def export_data(session: Session, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    briefs = session.scalars(
        select(Brief)
        .options(selectinload(Brief.candidate))
        .where(Brief.verification_status != VerificationStatus.blocked)
        .order_by(Brief.run_date.desc(), Brief.id.desc())
    ).all()
    review = load_review()
    entries = [brief_entry(b, include_page=True, review=review) for b in briefs]
    # duplicates fold into the row they duplicate; screened rows leave the main lists
    kept = {e["key"] for e in entries if e["review"]["status"] in ("keep", "keep_flagged")}
    for e in entries:
        if e["review"]["status"] == "duplicate_of" and e["review"].get("of") not in kept:
            e["review"] = {
                "status": "keep_flagged",
                "reason": "duplicate of a row that was itself screened",
            }
    today = next(
        (
            e
            for e, b in zip(entries, briefs, strict=True)
            if not b.historical and e["review"]["status"] != "screened_out"
        ),
        None,
    )
    sponsors = [
        sponsor_row(s)
        for s in session.scalars(
            select(Sponsor).order_by(Sponsor.series, Sponsor.team, Sponsor.brand)
        )
    ]
    calendar = [
        {
            "series": c.series.value,
            "season": c.season,
            "round": c.round,
            "name": c.name,
            "title_sponsor": c.title_sponsor,
            "status": c.status,
            "date_start": c.date_start.isoformat() if c.date_start else None,
            "date_end": c.date_end.isoformat() if c.date_end else None,
            "notes": getattr(c, "notes", None),
        }
        for c in session.scalars(
            select(CalendarEvent).order_by(CalendarEvent.series, CalendarEvent.round)
        )
    ]
    teams = load_team_profiles()
    display = {t["team"]: t.get("display_name") or t["team"] for t in teams}
    for row in sponsors:
        row["team_display"] = display.get(row["team"], row["team"]) if row["team"] else None
    return {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "execution_mode": settings.execution_mode,
        "operator_email": settings.operator_email,
        "today": today,
        "briefs": entries,
        "sponsors": sponsors,
        "calendar": calendar,
        "teams": teams,
        "team_display": display,
        "renewals": RENEWALS,
        "review_meta": {
            "reviewed_at": "2026-09-05",
            "screened": sum(1 for e in entries if e["review"]["status"] == "screened_out"),
            "duplicates": sum(1 for e in entries if e["review"]["status"] == "duplicate_of"),
            "flagged": sum(1 for e in entries if e["review"]["status"] == "keep_flagged"),
        },
    }


ASSETS = Path(__file__).parent / "assets"


def _svg_data_uri(name: str) -> str:
    import base64

    path = ASSETS / name
    if not path.exists():
        return ""
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def write_site(data: dict[str, Any], out_dir: Path, src: Path = SITE_SRC) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, default=str)
    (out_dir / "data.json").write_text(payload, encoding="utf-8")
    # first occurrence only: the data <script>; the app's own fallback check spells the
    # token in two halves so it never matches here.
    html = (
        src.read_text(encoding="utf-8")
        .replace("__LOGO_BLUE_GOLD__", _svg_data_uri("1440_logo.svg"))
        .replace("__LOGO_WHITE__", _svg_data_uri("1440_logo_white.svg"))
        .replace(DATA_TOKEN, payload.replace("</", "<\\/"), 1)
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    return out_dir / "index.html"


def zip_dir(folder: Path) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(folder).as_posix())
    return buf.getvalue()


def publish(settings: Settings | None = None, session: Session | None = None) -> dict[str, Any]:
    """Export + (optionally) deploy. Returns what happened; never raises past the caller's guard."""
    from intel.db import session_scope

    settings = settings or get_settings()
    out_dir = Path(settings.site_dir)
    if session is None:
        with session_scope(settings.database_url) as s:
            data = export_data(s, settings)
    else:
        data = export_data(session, settings)
    index = write_site(data, out_dir)
    result: dict[str, Any] = {"index": str(index), "briefs": len(data["briefs"])}
    if settings.netlify_auth_token and settings.netlify_site_id:
        from intel.netlify import deploy

        result["netlify"] = deploy(
            zip_dir(out_dir), settings.netlify_auth_token, settings.netlify_site_id
        )
    return result


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else Path(get_settings().site_dir)
    settings = get_settings().model_copy(update={"site_dir": str(out)})
    res = publish(settings)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
