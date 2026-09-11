"""intel.edgar_watch — 8-K Item 5.02 and registration statements from EDGAR full-text search."""

from __future__ import annotations

import datetime as dt

from intel import edgar_watch


def _efts(company: str, adsh: str, form: str, filed: str, cik: str = "1805077"):
    return {
        "hits": {
            "hits": [
                {
                    "_id": f"{adsh}:{adsh}.htm",
                    "_source": {
                        "ciks": [cik.zfill(10)],
                        "display_names": [f"{company}  (EOSE)  (CIK {cik})"],
                        "file_date": filed,
                        "form": form,
                        "file_description": "8-K" if form == "8-K" else "REGISTRATION STATEMENT",
                    },
                }
            ]
        }
    }


def test_the_query_urls_are_what_efts_expects():
    url = edgar_watch.efts_url(
        '"Item 5.02" "Chief Marketing Officer"', "8-K", dt.date(2026, 9, 9), dt.date(2026, 9, 11)
    )
    assert url.startswith("https://efts.sec.gov/LATEST/search-index?")
    assert "forms=8-K" in url and "startdt=2026-09-09" in url and "enddt=2026-09-11" in url
    assert "q=%22Item+5.02%22" in url
    assert "q=" not in edgar_watch.efts_url("", "S-1", dt.date(2026, 9, 9), dt.date(2026, 9, 11))


def test_a_sweep_parses_hits_dedupes_and_survives_a_failed_query(tmp_path):
    calls = []

    def fake(url):
        calls.append(url)
        if "Chief+Marketing+Officer" in url:
            return _efts(
                "Eos Energy Enterprises, Inc.", "0001628280-26-058890", "8-K", "2026-08-25"
            )
        if "Chief+Commercial+Officer" in url:
            return _efts(
                "Eos Energy Enterprises, Inc.", "0001628280-26-058890", "8-K", "2026-08-25"
            )  # same filing
        if "forms=S-1" in url:
            return _efts(
                "Blockchain.com Inc.", "0001234567-26-000001", "S-1", "2026-09-10", cik="1234567"
            )
        if "Chief+Executive+Officer" in url:
            raise OSError("blocked")
        return {"hits": {"hits": []}}

    hits = edgar_watch.sweep(days=2, today=dt.date(2026, 9, 11), fetch=fake)
    assert [h["company"] for h in hits] == [
        "Blockchain.com Inc.  (EOSE)  (CIK 1234567)",
        "Eos Energy Enterprises, Inc.  (EOSE)  (CIK 1805077)",
    ]
    eos = hits[1]
    assert eos["type"] == "new_cmo" and eos["form"] == "8-K" and eos["cik"] == "1805077"
    assert (
        eos["url"]
        == "https://www.sec.gov/Archives/edgar/data/1805077/000162828026058890/0001628280-26-058890-index.htm"
    )
    assert len(calls) == len(edgar_watch.QUERIES)

    inbox = edgar_watch.load_inbox(tmp_path / "inbox.json")
    assert edgar_watch.merge(inbox, hits, today=dt.date(2026, 9, 11)) == 2
    inbox["hits"][0]["judged"] = True  # the desk looked at Blockchain.com
    assert (
        edgar_watch.merge(inbox, hits, today=dt.date(2026, 9, 11)) == 0
    )  # nothing new, judgment kept
    assert [h["judged"] for h in inbox["hits"]] == [True, False]
    assert len(edgar_watch.unjudged(inbox)) == 1
    # a hit older than the keep window falls out
    old = dict(hits[1], id="8-K:old", filed="2026-06-01")
    edgar_watch.merge(inbox, [old], keep_days=60, today=dt.date(2026, 9, 11))
    assert "8-K:old" not in {h["id"] for h in inbox["hits"]}
    path = edgar_watch.save_inbox(inbox, tmp_path / "inbox.json")
    assert path.exists()
