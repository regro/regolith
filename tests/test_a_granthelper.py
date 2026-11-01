"""Tests for adding a grant, and seeding one from a funded proposal,
with the a_grant helper."""

import copy
import datetime as dt
import json
import os

import pytest

from regolith.database import connect
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile
from tests.conftest import exemplars_to_fs


@pytest.fixture
def grants_db(tmp_path):
    cwd = os.getcwd()
    rc = {
        "default_user_id": "sbillinge",
        "groupname": "ERGS",
        "databases": [
            {
                "name": "test",
                "url": str(tmp_path),
                "public": True,
                "path": "db",
                "local": True,
                "backend": "filesystem",
            }
        ],
    }
    (tmp_path / "regolithrc.json").write_text(json.dumps(rc))
    fspath = tmp_path / "db"
    fspath.mkdir()
    exemplars_to_fs(fspath, ["people", "proposals", "grants", "contacts", "institutions", "groups"])
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


def _client_call(method, *args):
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        return getattr(rc.client, method)(*args)


def stored(collection, doc_id):
    return _client_call("get", collection, doc_id)


def add_contact(contact):
    _client_call("insert_one", "test", "contacts", contact)


def with_iso_dates(doc):
    return {
        key: (
            (value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value)))
            if key.endswith("_date")
            else value
        )
        for key, value in doc.items()
    }


# Test that a grant seeded from a proposal copies the proposal and takes the overrides given
def test_grant_seeded_from_proposal(grants_db):
    main(
        [
            "helper",
            "a_grant",
            "sympy21",
            "--from-proposal",
            "SymPy-2.1",
            "--funder",
            "NumFOCUS",
            "--begin-date",
            "2019-09-01",
            "--awardnr",
            "NF-2.1",
        ]
    )
    expected_grant = {
        "_id": "sympy21",
        "amount": 3000.0,
        "awardnr": "NF-2.1",
        "begin_date": dt.date(2019, 9, 1),
        "currency": "USD",
        "end_date": dt.date(2030, 12, 31),
        "funder": "NumFOCUS",
        "institution": "Columbia University",
        "person_months_academic": 0,
        "person_months_summer": 1,
        "proposal_id": "SymPy-2.1",
        "status": "accepted",
        "team": [{"name": "Anthony Scopatz 2.1", "position": "pi", "institution": "University of 2.1"}],
        "title": "SymPy 2.1 Release Support",
    }
    assert with_iso_dates(stored("grants", "sympy21")) == expected_grant


# Test that a proposal with legacy dates and no team gives a grant with ISO dates and a team built from
# its pi and authors, where the pi also listed among the authors appears once, and that the proposal
# is marked accepted
def test_grant_seeded_from_legacy_proposal(grants_db):
    add_contact({"_id": "rflanagan", "name": "Robert Flanagan", "institution": "columbiau"})
    main(["helper", "a_grant", "myaward", "--from-proposal", "mypropsal", "--funder", "NSF"])
    grant = with_iso_dates(stored("grants", "myaward"))
    expected_dates = {"begin_date": dt.date(2030, 5, 1), "end_date": dt.date(2030, 12, 31)}
    expected_team_positions = [("Anthony Scopatz", "pi"), ("Robert Flanagan", "copi")]
    assert {key: grant[key] for key in expected_dates} == expected_dates
    assert [(member["name"], member["position"]) for member in grant["team"]] == expected_team_positions
    assert grant["team"][1]["institution"] == "Columbia University"
    assert all(member["institution"] for member in grant["team"])
    assert "begin_year" not in grant
    assert stored("proposals", "mypropsal")["status"] == "accepted"


def stored_part(database, grant_id):
    return _client_call("find_one", database, "grants", {"_id": grant_id})


# Test that a grant is split into a public part and a private part, which read back as one grant
def test_grant_split_between_databases(make_split_grants_db):
    main(
        [
            "helper",
            "a_grant",
            "sympy21",
            "--from-proposal",
            "SymPy-2.1",
            "--funder",
            "NumFOCUS",
            "--awardnr",
            "NF-2.1",
            "--account",
            "GG-21",
        ]
    )
    expected_public_part = {
        "_id": "sympy21",
        "amount": 3000.0,
        "awardnr": "NF-2.1",
        "begin_date": dt.date(2019, 6, 1),
        "currency": "USD",
        "end_date": dt.date(2030, 12, 31),
        "funder": "NumFOCUS",
        "team": [{"name": "Anthony Scopatz 2.1", "position": "pi", "institution": "University of 2.1"}],
        "title": "SymPy 2.1 Release Support",
    }
    expected_private_part = {
        "_id": "sympy21",
        "account": "GG-21",
        "institution": "Columbia University",
        "person_months_academic": 0,
        "person_months_summer": 1,
        "proposal_id": "SymPy-2.1",
        "status": "accepted",
    }
    assert with_iso_dates(stored_part("public", "sympy21")) == expected_public_part
    assert stored_part("private", "sympy21") == expected_private_part
    assert with_iso_dates(stored("grants", "sympy21")) == {**expected_public_part, **expected_private_part}


# Test adding a grant with no proposal behind it, where the pi defaults to the group pi, scopatz
def test_grant_without_proposal(grants_db):
    main(
        [
            "helper",
            "a_grant",
            "newgrant",
            "--title",
            "A new grant",
            "--amount",
            "1000",
            "--funder",
            "DOE",
            "--begin-date",
            "2026-09-01",
            "--end-date",
            "2029-08-31",
            "--institution",
            "Columbia University",
        ]
    )
    grant = stored("grants", "newgrant")
    expected_team = [{"name": "Anthony Scopatz", "position": "pi", "institution": "Columbia University"}]
    assert grant["team"] == expected_team
    assert "proposal_id" not in grant


# Test that everything missing from a seeded grant is reported together, so it can be fixed in one go
def test_grant_reports_everything_missing(grants_db):
    with pytest.raises(RuntimeError) as error:
        main(["helper", "a_grant", "myaward", "--from-proposal", "mypropsal"])
    message = str(error.value)
    assert "the funder (give it with --funder)" in message
    assert "the institution of team member Robert Flanagan" in message
    assert "Please supply them and re-run" in message
    assert stored("grants", "myaward") is None


# Test that a grant that cannot be added is refused with a message saying what to do
@pytest.mark.parametrize(
    "extra_args, expected_error, expected_message",
    [
        # C1: a grant id already in use, expect a RuntimeError asking for a different id
        pytest.param(
            ["SymPy-1.1", "--from-proposal", "SymPy-2.1", "--funder", "X"],
            RuntimeError,
            "Please re-run with a different grant id",
            id="grant-id-taken",
        ),
        # C2: a proposal that already has a grant, expect a RuntimeError naming that grant
        pytest.param(
            ["abc42b", "--from-proposal", "abc42"],
            RuntimeError,
            "The proposal abc42 already has the grant abc42",
            id="already-seeded",
        ),
        # C3: part of a proposal id, expect a RuntimeError listing the proposals it matches
        pytest.param(
            ["sympy", "--from-proposal", "SymPy"],
            RuntimeError,
            "Proposals with similar ids: SymPy-1.1, SymPy-2.1",
            id="partial-proposal-id",
        ),
        # C4: a begin date override after the proposed end date, expect a ValueError asking for an earlier one
        pytest.param(
            ["sympy21", "--from-proposal", "SymPy-2.1", "--funder", "X", "--begin-date", "2031-01-01"],
            ValueError,
            "Please re-run with a begin date that is before the end date",
            id="begin-after-end",
        ),
    ],
)
def test_grant_refused(extra_args, expected_error, expected_message, grants_db):
    with pytest.raises(expected_error, match=expected_message):
        main(["helper", "a_grant"] + extra_args)
