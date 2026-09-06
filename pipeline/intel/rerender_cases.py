"""Re-render recorded cases from their own ``brief_data`` after a renderer fix — no model,
no database, no change to any verified fact.

    python -m intel.rerender_cases                 # every record whose output would change
    python -m intel.rerender_cases --stem lovable  # one case

Today's only rule: GRID FIT rows carry the 2026 entry names from ``seeds/team_profiles.json``
(``display_name``) instead of the sponsor-table keys, so the block agrees with the
recommended-team label. The record's ``brief_data`` is updated in place and the PDF / HTML /
app page are rendered again from it; the PDF must still be exactly 2 pages.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from intel.brief_data import BriefData
from intel.render import load_team_profiles, render_brief, render_web

CASES_DIR = Path(__file__).resolve().parent / "cases"


def display_names() -> dict[str, str]:
    return {
        p["team"]: p["display_name"]
        for p in load_team_profiles()
        if p.get("team") and p.get("display_name") and p["display_name"] != p["team"]
    }


def fix_gridfit(brief_data: dict[str, Any], names: dict[str, str]) -> bool:
    changed = False
    for row in brief_data.get("gridfit") or []:
        new = names.get(row.get("team") or "")
        if new and row.get("team") != new:
            row["team"] = new
            changed = True
    return changed


def rerender(record: Path, names: dict[str, str] | None = None, force: bool = False) -> dict:
    names = display_names() if names is None else names
    data = json.loads(record.read_text(encoding="utf-8"))
    bd = (data.get("brief") or {}).get("brief_data") or {}
    changed = fix_gridfit(bd, names)
    if not changed and not force:
        return {"record": str(record), "changed": False}
    stem = record.name.replace(".run.json", "")
    folder = record.parent
    brief_data = BriefData.model_validate(bd)
    out = render_brief(brief_data, folder, stem, font_stack="brand")
    render_web(brief_data, folder / f"{stem}.web.html")
    data["brief"]["brief_data"] = bd
    data["brief"]["pages"] = out["pages"]
    record.write_text(json.dumps(data, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    return {"record": str(record), "changed": True, "pages": out["pages"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m intel.rerender_cases", description=__doc__)
    parser.add_argument("--stem", default=None)
    parser.add_argument("--cases", default=str(CASES_DIR))
    parser.add_argument("--force", action="store_true", help="render even when unchanged")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    names = display_names()
    results = []
    for rec in sorted(Path(args.cases).glob("*/*.run.json")):
        if args.stem and rec.name != f"{args.stem}.run.json":
            continue
        results.append(rerender(rec, names, force=args.force))
    print(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
