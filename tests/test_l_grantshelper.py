"""Tests for the l_grants helper."""

import pytest

from regolith.helpers.l_grantshelper import missing_fields

COMPLETE_GRANT = {
    "_id": "dmref26",
    "title": "A grant",
    "amount": 1000.0,
    "currency": "USD",
    "funder": "NSF",
    "program": "DMREF",
    "awardnr": "DMR-0001",
    "account": "GG001",
    "alias": "dmref",
    "admin": "physics",
    "institution": "columbiau",
    "status": "accepted",
    "team": [{"name": "Simon Billinge", "position": "pi"}],
    "begin_date": "2026-09-01",
    "end_date": "2029-08-31",
}


# Test that the fields a grant still needs are reported, whichever date style it uses
@pytest.mark.parametrize(
    "changes, expected_missing",
    [
        # C1: a grant with every expected field, expect nothing missing
        pytest.param({}, [], id="complete"),
        # C2: dates in the legacy day, month and year style, expect nothing missing
        pytest.param(
            {"begin_date": None, "end_date": None, "begin_year": 2026, "begin_month": 9, "end_year": 2029},
            [],
            id="legacy-dates",
        ),
        # C3: 1. an empty awardnr, 2. no account and 3. an empty team, expect all three missing
        pytest.param({"awardnr": "", "account": None, "team": []}, ["awardnr", "account", "team"], id="unset"),
        # C4: no end date, expect only the end date missing
        pytest.param({"end_date": None}, ["end_date"], id="no-end-date"),
    ],
)
def test_missing_fields(changes, expected_missing):
    grant = {key: value for key, value in {**COMPLETE_GRANT, **changes}.items() if value is not None}
    assert missing_fields(grant) == expected_missing
