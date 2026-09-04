"""Build brief §5 + §9.3: the normaliser is a database rule, so it gets unit tests."""

import pytest

from intel.normalise import company_norm, trigger_norm


def test_lime_and_lime_neutron_holdings_share_a_key():
    # §9.3 — the production duplicate-guard bug.
    assert company_norm("Lime") == company_norm("Lime (Neutron Holdings)") == "lime"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Primer", "primer"),
        ("Primer ", "primer"),
        ("PRIMER", "primer"),
        ("The Trade Desk Inc.", "tradedesk"),
        ("Cerebras Systems", "cerebrassystems"),
        ("Neutron Holdings, Inc.", "neutron"),
        ("Datadog, Inc.", "datadog"),
        ("Ramp Business Corp", "rampbusiness"),
        ("Snowflake Technologies Ltd", "snowflake"),
        ("1Komma5°", "1komma5"),
        ("Citroën Racing", "citroenracing"),
        ("Horizon3.ai", "horizon3ai"),  # "ai" is NOT a stripped suffix (see module docstring)
        ("Factory AI", "factoryai"),
        ("", ""),
        (None, ""),
    ],
)
def test_company_norm(raw, expected):
    assert company_norm(raw) == expected


def test_parenthetical_stripped_before_suffixes():
    # "(Holdings)" is inside parens → removed as a block, not as a suffix.
    assert company_norm("Acme (Holdings) Technologies plc") == "acme"


def test_suffix_only_matches_whole_words():
    assert company_norm("Zinc Inc") == "zinc"
    assert company_norm("Corporation Street") == "corporationstreet"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("S-1 filed 8 May 2026", "s 1 filed 8 may 2026"),
        ("  Closed $100M  Series C  ", "closed 100m series c"),
        ("IPO roadshow live; listing 14 May", "ipo roadshow live listing 14 may"),
        (None, ""),
    ],
)
def test_trigger_norm(raw, expected):
    assert trigger_norm(raw) == expected
