"""Structured sources (15 Sep 2026): CB Insights API v2 (intel.cbi) and SEC Form D
(intel.edgar_watch) — dates, rounds and people from data, not from web search."""

from __future__ import annotations

import datetime as dt
import json

from intel import cbi, edgar_watch
from intel.config import Settings

TODAY = dt.date(2026, 9, 16)

ORGS = [
    {
        "orgId": 501,
        "summary": {
            "name": "Walden Robotics",
            "url": "waldenrobotics.com",
            "description": "General-purpose robots for factories.",
            "address": {"city": "Cambridge", "stateProvince": "MA", "country": "United States"},
            "status": "Private",
        },
        "financials": {"valuationInMillions": 1100, "totalFundingInMillions": 300},
        "headcount": {"current": 120},
        "taxonomy": {"sector": "Industrials", "industry": "Robotics", "subindustry": "Humanoid"},
    },
    {
        "orgId": 502,
        "summary": {"name": "Quiet Co", "url": "quiet.example"},
        "financials": {"valuationInMillions": 2000},
    },
]
FUNDINGS = [
    {
        "dealId": 9001,
        "recipient": {"orgId": 501},
        "date": "2026-09-12",
        "amountInMillions": 300,
        "valuationInMillions": 1100,
        "round": "Seed",
        "investors": [
            {"name": "Toyota", "isLead": True, "isNew": True},
            {"name": "Deviation Capital", "isLead": True, "isNew": True},
            {"name": "Nvidia", "isLead": False, "isNew": True},
        ],
        "sources": ["https://www.businesswire.com/walden", "https://bloomberg.com/walden"],
    },
    {  # an old round for the quiet company: no trigger
        "dealId": 9002,
        "recipient": {"orgId": 502},
        "date": "2026-01-10",
        "amountInMillions": 90,
        "round": "Series B",
        "investors": [],
        "sources": ["https://example.com/old"],
    },
]
MANAGEMENT = [
    {
        "orgId": 501,
        "people": [
            {
                "givenName": "Russ",
                "surname": "Tedrake",
                "linkedInUrl": "https://linkedin.com/in/tedrake",
                "workExperience": [
                    {
                        "orgName": "Walden Robotics",
                        "title": "Co-founder and Chief Executive Officer",
                        "startDate": "2026-01-15",
                        "isCurrent": True,
                    },
                    {
                        "orgName": "Toyota Research Institute",
                        "title": "SVP",
                        "startDate": "2016-01-01",
                        "endDate": "2026-01-01",
                        "isCurrent": False,
                    },
                ],
            },
            {
                "givenName": "Jane",
                "surname": "Doe",
                "workExperience": [
                    {
                        "orgName": "Walden Robotics",
                        "title": "Chief Marketing Officer",
                        "startDate": "2026-09-01",
                        "isCurrent": True,
                    },
                    {
                        "orgName": "Oracle",
                        "title": "VP Marketing",
                        "startDate": "2020-01-01",
                        "endDate": "2026-08-01",
                        "isCurrent": False,
                    },
                ],
            },
        ],
    },
    {"orgId": 502, "people": []},
]


class FakeTransport:
    """Canned responses per path; records every call so the credit maths can be checked."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def __call__(self, url: str, body: dict, headers: dict) -> dict:
        path = url.replace(cbi.BASE, "")
        self.calls.append((path, body))
        if path == "/v2/authorize":
            return {"token": "t0k"}
        assert headers.get("Authorization") == "Bearer t0k"
        if path == "/v2/organizations":
            return {"orgs": [{"orgId": 501, "name": "Walden Robotics"}]}
        if path == "/v2/firmographics":
            assert body["minValuationInMillions"] == 1000.0
            assert body["minLastFundingDate"] == "2026-09-09"
            return {"orgs": ORGS, "nextPageToken": None}
        if path == "/v2/financialtransactions/fundings":
            return {"fundings": FUNDINGS}
        if path == "/v2/managementandboard":
            return {"orgs": MANAGEMENT}
        raise AssertionError(path)


def test_rows_carry_the_round_the_decision_path_and_the_ties():
    names = {"oracle": "Oracle", "toyotagazooracing": "Toyota Gazoo Racing"}
    rows = cbi.build_rows(ORGS, FUNDINGS, MANAGEMENT, TODAY, lookback_days=7, names=names)
    assert [r["company"] for r in rows] == ["Walden Robotics"]  # Quiet Co: no trigger
    row = rows[0]
    kinds = [t["type"] for t in row["triggers"]]
    assert kinds == ["funding_round", "new_cmo"]  # the CMO started 15 days ago
    t = row["triggers"][0]
    assert t["text"].startswith("$300M Seed at a $1.1B valuation on 2026-09-12, led by Toyota")
    assert "new investors Nvidia" in t["text"]
    assert t["sources"][0] == "https://www.businesswire.com/walden"
    # the marketing owner signs when listed; the CEO is on the path
    dp = row["decision_path"]
    assert dp["buyer"]["name"] == "Jane Doe" and dp["marketing_owner_listed"]
    assert [p["name"] for p in dp["path"]] == ["Russ Tedrake"]
    # the CMO's Oracle years are a leadership tie (Oracle is on the sponsor table)
    assert row["leadership_ties"] == [
        {
            "person": "Jane Doe",
            "at": "Oracle",
            "title": "VP Marketing",
            "from": "2020-01-01",
            "to": "2026-08-01",
        }
    ]
    assert row["hq"] == "Cambridge, MA, United States"
    assert row["valuation_musd"] == 1100 and row["industry"].startswith("Industrials")


def test_the_sweep_counts_credits_and_stops_at_the_cap():
    tr = FakeTransport()
    client = cbi.Client("id", "secret", transport=tr, credit_cap=10)
    rows, note = cbi.sweep(client, TODAY, days=7)
    assert [r["company"] for r in rows] == ["Walden Robotics"]
    # firmographics (1) + fundings for 2 orgs (2) + management for 2 orgs (2) = 5 credits
    assert note["credits_used"] == 5 and client.credits_used == 5
    assert [p for p, _ in tr.calls] == [
        "/v2/authorize",
        "/v2/firmographics",
        "/v2/financialtransactions/fundings",
        "/v2/managementandboard",
    ]
    # the free lookup never counts, and a repeated call is served from the cache
    client.lookup(["Walden Robotics"])
    client.lookup(["Walden Robotics"])
    assert client.credits_used == 5 and sum(1 for p, _ in tr.calls if p == "/v2/organizations") == 1

    tight = cbi.Client("id", "secret", transport=FakeTransport(), credit_cap=2)
    rows, note = cbi.sweep(tight, TODAY, days=7)
    assert rows == [] and "credit_cap" in note and tight.credits_used == 1


def test_leads_for_the_pool_carry_the_facts_as_the_hint_and_skip_known_names():
    rows = cbi.build_rows(ORGS, FUNDINGS, MANAGEMENT, TODAY, names={})
    out = cbi.leads(rows, known=set())
    assert len(out) == 1
    lead = out[0]
    assert lead.source == "cbi" and lead.is_candidate
    assert lead.trigger.startswith("funding round: $300M Seed at a $1.1B valuation on 2026-09-12")
    assert "CB Insights; sources: https://www.businesswire.com/walden" in lead.trigger
    assert lead.source_url == "https://www.businesswire.com/walden"
    assert lead.person == "Jane Doe" and lead.role == "Chief Marketing Officer"
    from intel.inbox import as_signals

    sig = as_signals(out)[0]
    assert sig.company == "Walden Robotics" and sig.signal_date == "2026-09-12"
    assert cbi.leads(rows, known={"waldenrobotics"}) == []


def test_off_without_credentials_and_on_with_them(tmp_path, monkeypatch):
    assert cbi.client_for(Settings()) is None
    signals, note = cbi.collect(None, Settings(), TODAY)
    assert signals == [] and note["status"].startswith("off")

    monkeypatch.setattr(cbi, "INBOX_FILE", tmp_path / "cbi_inbox.json")
    monkeypatch.setattr("intel.inbox.known_companies", lambda session: set())
    settings = Settings(cbi_client_id="id", cbi_client_secret="s", cbi_credit_cap=10)
    signals, note = cbi.collect(None, settings, TODAY, transport=FakeTransport())
    assert note["status"] == "read" and note["candidates"] == 1 and note["new_in_inbox"] == 1
    inbox = json.loads((tmp_path / "cbi_inbox.json").read_text(encoding="utf-8"))
    assert inbox["_meta"]["swept_at"] == TODAY.isoformat()
    assert [h["company"] for h in cbi.unjudged(inbox)] == ["Walden Robotics"]
    # a second sweep updates the row and keeps the desk's judgment
    inbox["hits"][0]["judged"] = True
    assert cbi.merge(inbox, cbi.build_rows(ORGS, FUNDINGS, MANAGEMENT, TODAY, names={})) == 0
    assert inbox["hits"][0]["judged"] is True and cbi.unjudged(inbox) == []


FORM_D = """<?xml version="1.0"?>
<edgarSubmission>
  <primaryIssuer>
    <entityName>Acme Grid, Inc.</entityName>
    <entityType>Corporation</entityType>
    <issuerAddress><stateOrCountry>CA</stateOrCountry></issuerAddress>
  </primaryIssuer>
  <relatedPersonsList>
    <relatedPersonInfo>
      <relatedPersonName><firstName>Ada</firstName><lastName>Lovelace</lastName></relatedPersonName>
      <relatedPersonRelationshipList><relationship>Executive Officer</relationship>
        <relationship>Director</relationship></relatedPersonRelationshipList>
      <relationshipClarification>Chief Executive Officer</relationshipClarification>
    </relatedPersonInfo>
    <relatedPersonInfo>
      <relatedPersonName><firstName>Grace</firstName><lastName>Hopper</lastName></relatedPersonName>
      <relatedPersonRelationshipList><relationship>Director</relationship></relatedPersonRelationshipList>
    </relatedPersonInfo>
  </relatedPersonsList>
  <offeringData>
    <industryGroup><industryGroupType>{group}</industryGroupType></industryGroup>
    <typeOfFiling><newOrAmendment><isAmendment>false</isAmendment></newOrAmendment>
      <dateOfFirstSale><value>2026-09-10</value></dateOfFirstSale></typeOfFiling>
    <typesOfSecuritiesOffered><isEquityType>true</isEquityType></typesOfSecuritiesOffered>
    <offeringSalesAmounts><totalOfferingAmount>{offered}</totalOfferingAmount>
      <totalAmountSold>{sold}</totalAmountSold></offeringSalesAmounts>
  </offeringData>
</edgarSubmission>"""


def _efts(form: str, names: list[str]) -> dict:
    return {
        "hits": {
            "hits": [
                {
                    "_id": f"0001234567-26-00000{i}:primary_doc.xml",
                    "_source": {
                        "form": form,
                        "file_date": "2026-09-15",
                        "display_names": [n],
                        "ciks": ["0001234567"],
                        "sics": [],
                    },
                }
                for i, n in enumerate(names, 1)
            ]
        }
    }


def test_form_d_keeps_real_rounds_and_drops_funds_small_placements_and_amendments():
    pages = {
        "0001234567-26-000001": FORM_D.format(group="Other Technology", offered=300e6, sold=250e6),
        "0001234567-26-000002": FORM_D.format(group="Pooled Investment Fund", offered=5e8, sold=5e8),
        "0001234567-26-000003": FORM_D.format(group="Other Technology", offered=1e7, sold=8e6),
    }

    def fetch_page(url):
        assert url.endswith("/primary_doc.xml"), url
        folder = url.rsplit("/", 2)[-2]
        key = f"{folder[:10]}-{folder[10:12]}-{folder[12:]}"
        return pages[key]

    # only the Form D query answers in this test; the others return no hits
    def fetch_all(url):
        if "forms=D" in url:
            return _efts("D", ["Acme Grid, Inc.", "Some Fund LP", "Tiny Co"])
        return {"hits": {"hits": []}}

    rows = edgar_watch.sweep(
        days=2, today=dt.date(2026, 9, 16), fetch=fetch_all, fetch_page=fetch_page
    )
    assert [r["company"] for r in rows] == ["Acme Grid, Inc."]
    row = rows[0]
    assert row["type"] == "funding_round" and row["form"] == "D"
    assert row["amount_sold_usd"] == 250e6 and row["offering_total_usd"] == 300e6
    assert row["first_sale"] == "2026-09-10" and row["state"] == "CA"
    assert row["officers"][0]["name"] == "Ada Lovelace"
    assert row["officers"][0]["title"] == "Chief Executive Officer"
    assert [d["name"] for d in row["directors"]] == ["Grace Hopper"]
    assert row["description"].startswith("Form D: $250M sold of $300M offered; first sale 2026-09")
    assert row["url"].endswith("/0001234567-26-000001-index.htm")
    assert edgar_watch.form_d_url(row).endswith("/000123456726000001/primary_doc.xml")
    # the inbox keeps it under the funding_round type the app already labels
    inbox = {"_meta": {}, "hits": []}
    assert edgar_watch.merge(inbox, rows, today=dt.date(2026, 9, 16)) == 1
    assert edgar_watch.unjudged(inbox)[0]["type"] == "funding_round"
