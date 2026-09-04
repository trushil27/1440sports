"""Real cases from production history (build brief §9: "Do not invent alternatives").

Every row below is copied verbatim from the n8n engine's audit log — the Google Sheet
"1440 Intellgence Pipeline", tab "Daily Signals" (columns Date, Company, Score, Tier,
Track, Person, Role, Action, Horizon, Source). ``Action`` is the logged trigger text.

The log records each signal's TOTAL score but not the five-dimension split. Where a test
needs a candidate to reach the scoring stage, ``with_breakdown`` attaches a labelled
synthetic split that sums to the recorded total (brand_fit ≥ 12 so the OF gate applies).
That split is test scaffolding, not a company fact, and is never used as one.
"""

from __future__ import annotations

from intel.parse import ScannedSignal

# --- §9.3 Lime / "Lime (Neutron Holdings)" -----------------------------------------------
LIME_S1_A = {
    "signal_date": "2026-05-08",
    "company": "Lime",
    "score": 84,
    "tier": "HOT",
    "track": 1,
    "person": "Wayne Ting",
    "role": "CEO",
    "horizon_weeks": "4-8",
    "source_url": "https://techcrunch.com/2026/05/08/lime-the-uber-backed-micromobility-company-files-for-ipo/",
    "trigger_reason": (
        "Filed Nasdaq S-1 — first micromobility IPO attempt in years; positive FCF three "
        "consecutive years; operations across 230 cities and 29 countries; Uber, Google "
        "Ventures and Andreessen Horowitz on cap table"
    ),
}
LIME_S1_B = {
    "signal_date": "2026-05-08",
    "company": "Lime (Neutron Holdings)",
    "score": 83,
    "tier": "HOT",
    "track": 1,
    "person": "Wayne Ting",
    "role": "CEO",
    "horizon_weeks": "3-6",
    "source_url": "https://techcrunch.com/2026/05/10/techcrunch-mobility-limes-ipo-gamble/",
    "trigger_reason": (
        "S-1 filed 8 May 2026; June 2026 Nasdaq debut anticipated; pre-IPO brand profile "
        "urgency identified"
    ),
}
LIME_ROADSHOW = {
    "signal_date": "2026-06-22",
    "company": "Lime (Neutron Holdings)",
    "score": 84,
    "tier": "HOT",
    "track": 1,
    "person": "Wayne Ting",
    "role": "CEO",
    "horizon_weeks": "2-4",
    "source_url": "https://techcrunch.com/2026/05/08/lime-the-uber-backed-micromobility-company-files-for-ipo/",
    "trigger_reason": (
        "IPO roadshow live 22 June 2026; Nasdaq listing (LIME) imminent targeting ~$1.66B "
        "market cap and ~$250M raise"
    ),
}

# --- §9.4 Primer duplicate (three rows logged the same day) -------------------------------
PRIMER_A = {
    "signal_date": "2026-05-20",
    "company": "Primer",
    "score": 85,
    "tier": "HOT TOP TIER",
    "track": 1,
    "person": "Gabriel Le Roux",
    "role": "Co-Founder & CEO",
    "horizon_weeks": "6-10",
    "source_url": "https://letsdatascience.com/news/primer-raises-100m-to-ai-enable-payments-19e1ab6c",
    "trigger_reason": (
        "Closed $100M oversubscribed Series C; declared US expansion with 50 hires; "
        "launched Primer Companion AI agent"
    ),
}
PRIMER_B = {
    "signal_date": "2026-05-20",
    "company": "Primer",
    "score": 79,
    "tier": "HOT",
    "track": 1,
    "person": "Gabriel Le Roux",
    "role": "Co-Founder & CEO",
    "horizon_weeks": "6-10",
    "source_url": "https://www.businesswire.com/news/home/20260519989278/en/",
    "trigger_reason": (
        "Closed $100M Series C led by Sofina; explicit mandate to accelerate US enterprise "
        "expansion of AI payments orchestration platform"
    ),
}
PRIMER_C = {
    "signal_date": "2026-05-20",
    "company": "Primer",
    "score": 76,
    "tier": "HOT",
    "track": 1,
    "person": "Gabriel Le Roux",
    "role": "CEO & Co-founder",
    "horizon_weeks": "8-14",
    "source_url": "https://www.axios.com/pro/all-deals/2026/05/20/pro-rata-premium-first-look",
    "trigger_reason": (
        "$100M Series C closed; US market expansion declared; AI payments orchestration "
        "layer scaling globally"
    ),
}

# --- §9.5 stale triggers ---------------------------------------------------------------
# Strava was logged with signal_date 2026-01-01 and the trigger "Confidential IPO S-1 filed
# January 2026". 1Komma5° was logged on 2026-05-26; the build brief records its trigger as
# July 2025 (month precision — no day is on record, and none is invented here).
STRAVA = {
    "signal_date": "2026-01-01",
    "company": "Strava",
    "score": 74,
    "tier": "WARM",
    "track": 1,
    "person": "Michael Horvath",
    "role": "CEO",
    "horizon_weeks": "8-12",
    "source_url": (
        "https://acquinox.capital/insights/market-insights/"
        "the-2026-ipo-pipeline-which-tech-giants-are-heading-to-public-markets-1"
    ),
    "trigger_reason": (
        "Confidential IPO S-1 filed January 2026; pre-IPO brand-building window open; "
        "AI coaching product launch planned post-funding"
    ),
}
ONEKOMMA5 = {
    "signal_date": "July 2025",
    "company": "1Komma5°",
    "score": 75,
    "tier": "WARM",
    "track": 1,
    "person": "Philipp Schröder",
    "role": "CEO & Co-Founder",
    "horizon_weeks": "6-10",
    "source_url": "https://www.evinfrastructurenews.com/ev-technology/ev-startups-2026",
    "trigger_reason": (
        "Australia market expansion confirmed; FE GEN4 Season 13 electrification narrative "
        "at peak relevance; EV home-charging category entirely uncontested on FE team rosters"
    ),
}

# --- §9.1 Ramp N° 025 — the phantom "F1 London race" (used from M3) -----------------------
RAMP_PHANTOM_RACE = {
    "signal_date": "2026-05-28",
    "company": "Ramp",
    "score": 87,
    "tier": "HOT TOP TIER",
    "track": 1,
    "person": "Eric Glyman",
    "role": "CEO & Co-Founder",
    "horizon_weeks": "6-10",
    "source_url": "https://sacra.com/c/ramp/",
    "trigger_reason": (
        "Active $750M raise at >$40B pre-money valuation; UK/EU onboarding launch summer "
        "2026; Visa stablecoin card partnership live; F1 London race August 2026 activation "
        "window identified"
    ),
}


def synthetic_split(total: int) -> dict:
    """Test scaffolding: a labelled five-way split summing to ``total`` (see module docstring)."""
    if not 60 <= total <= 100:
        raise ValueError("synthetic split supports the logged HOT/WARM range only")
    base, rem = divmod(total, 5)
    dims = [base] * 5
    for i in range(rem):
        dims[i] += 1
    timing, capacity, brand_fit, urgency, ops_fit = dims
    return {
        "timing": timing,
        "capacity": capacity,
        "brand_fit": brand_fit,
        "urgency": urgency,
        "ops_fit": ops_fit,
        "_note": "synthetic split of the logged total; not a recorded fact",
    }


def with_breakdown(row: dict, series: str | None = None) -> ScannedSignal:
    data = dict(row)
    data["score_breakdown"] = synthetic_split(row["score"])
    if series:
        data["recommended_series"] = series
    return ScannedSignal.model_validate(data)


def bare(row: dict) -> ScannedSignal:
    """A candidate as logged (no breakdown): enough for freshness / blocklist / dedup stages."""
    return ScannedSignal.model_validate(dict(row))
