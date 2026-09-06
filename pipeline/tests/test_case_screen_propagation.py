"""A company screened out after a full check stays screened on its other thin rows."""

from __future__ import annotations

from intel.site_export import propagate_case_screens


def _row(company, date, status="keep", **kw):
    review = {"status": status}
    review.update(kw.pop("review", {}))
    return {"company": company, "date": date, "review": review, **kw}


def test_screen_travels_to_the_other_rows_of_the_same_company():
    screened = _row(
        "Sila Nanotechnologies",
        "2026-06-24",
        status="screened_out",
        review={
            "status": "screened_out",
            "reason_code": "case_screen",
            "reason": "stale: the round is 180 days before the row",
            "sources": ["https://example.com/a"],
            "screened_at": "2026-09-06",
        },
    )
    thin = _row("Sila Nanotechnologies", "2026-07-21")
    other = _row("Nebius Group", "2026-06-25")
    n = propagate_case_screens([screened, thin, other])
    assert n == 1
    assert thin["review"]["status"] == "screened_out"
    assert "checked on the 2026-06-24 row" in thin["review"]["reason"]
    assert thin["review"]["sources"] == ["https://example.com/a"]
    assert other["review"]["status"] == "keep"


def test_a_built_case_outranks_a_screen_on_another_date():
    screened = _row(
        "Crusoe",
        "2026-06-20",
        status="screened_out",
        review={"status": "screened_out", "reason_code": "case_screen", "reason": "duplicate"},
    )
    built = _row("Crusoe", "2026-09-05", page_html="<html></html>")
    assert propagate_case_screens([screened, built]) == 0
    assert built["review"]["status"] == "keep"
