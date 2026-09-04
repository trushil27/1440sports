"""Reference-data seeds: spec files mirrored into the DB, idempotently."""

from __future__ import annotations

from sqlalchemy import func, select

from intel.models import (
    Alumni,
    AlumniTier,
    Blocklist,
    BlocklistStatus,
    CalendarEvent,
    Series,
    Sponsor,
    SponsorLevel,
    SponsorStatus,
)
from intel.normalise import company_norm
from intel.seed import load_seeds

MERCEDES = "Mercedes-AMG Petronas F1 Team"
WILLIAMS = "Atlassian Williams Racing"


def _counts(session) -> dict[str, int]:
    return {
        model.__tablename__: session.execute(select(func.count()).select_from(model)).scalar_one()
        for model in (Sponsor, Alumni, Blocklist, CalendarEvent)
    }


def _sponsor_rows(session, brand: str) -> list[Sponsor]:
    stmt = select(Sponsor).where(Sponsor.brand_norm == company_norm(brand))
    return list(session.execute(stmt).scalars())


def test_load_seeds_is_idempotent(session):
    first = load_seeds(session)
    session.commit()
    after_first = _counts(session)
    assert after_first["sponsors"] > 0 and after_first["calendar_events"] > 0
    assert after_first == first

    second = load_seeds(session)
    session.commit()
    assert second == first
    assert _counts(session) == after_first


def test_sponsor_rows_match_spec(session):
    load_seeds(session)

    petronas = [s for s in _sponsor_rows(session, "Petronas") if s.team == MERCEDES]
    assert len(petronas) == 1
    assert petronas[0].level == SponsorLevel.team_title
    assert petronas[0].status == SponsorStatus.active

    aws = [s for s in _sponsor_rows(session, "AWS") if s.level == SponsorLevel.championship_global]
    assert len(aws) == 1
    assert aws[0].series == Series.F1
    assert aws[0].team is None
    assert "Cloud" in aws[0].category

    jb = _sponsor_rows(session, "Julius Baer")
    assert len(jb) == 1
    assert jb[0].series == Series.FE
    assert jb[0].level == SponsorLevel.championship_global

    atlassian = [s for s in _sponsor_rows(session, "Atlassian") if s.team == WILLIAMS]
    assert len(atlassian) == 1
    assert atlassian[0].level == SponsorLevel.team_title

    claude = [s for s in _sponsor_rows(session, "Claude") if s.team == WILLIAMS]
    assert len(claude) == 1
    assert claude[0].status == SponsorStatus.joined
    assert "Anthropic" in claude[0].notes

    # Every row carries provenance.
    assert (
        session.execute(
            select(func.count()).select_from(Sponsor).where(Sponsor.source.is_(None))
        ).scalar_one()
        == 0
    )


def test_blocklist_has_factory_ai_active(session):
    load_seeds(session)
    row = session.execute(
        select(Blocklist).where(Blocklist.company_norm == company_norm("Factory AI"))
    ).scalar_one()
    assert row.status == BlocklistStatus.active
    assert row.added_at.isoformat() == "2026-04-30"


def test_alumni_has_genefa_murphy_strict_at_jfrog(session):
    load_seeds(session)
    row = session.execute(select(Alumni).where(Alumni.name == "Genefa Murphy")).scalar_one()
    assert row.tier == AlumniTier.strict
    assert row.current_company == "JFrog"
    assert row.company_norm == company_norm("JFrog")
    assert row.move_date.isoformat() == "2026-01-05"


def test_f1_2026_calendar_has_24_rounds_and_no_london(session):
    load_seeds(session)
    rows = list(
        session.execute(
            select(CalendarEvent)
            .where(CalendarEvent.series == Series.F1, CalendarEvent.season == 2026)
            .order_by(CalendarEvent.round)
        ).scalars()
    )
    assert len(rows) == 24
    assert [r.round for r in rows] == list(range(1, 25))
    assert not any("london" in r.name.lower() for r in rows)
    # The spec gives no dates: none may be invented.
    assert all(r.date_start is None and r.date_end is None for r in rows)
