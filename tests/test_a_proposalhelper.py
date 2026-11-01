"""Tests for adding a proposal with the a_proposal helper."""

import copy
import datetime as dt
import json
import os

import pytest

from regolith.database import connect
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile
from tests.conftest import exemplars_to_fs

PROPOSAL_ID = "26_newprop"
BASE_ARGS = ["helper", "a_proposal", "new prop", "500000", "A new proposal", "--date", "2026-08-01"]


@pytest.fixture
def proposals_db(tmp_path):
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
    exemplars_to_fs(fspath, ["people", "proposals", "groups"])
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


def stored_proposal(proposal_id):
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        return rc.client.get("proposals", proposal_id)


def as_date(value):
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(value)


# Test the dates stored for a new proposal
@pytest.mark.parametrize(
    "extra_args, expected_dates",
    [
        # C1: a begin date and an end date, expect both stored as given
        pytest.param(
            ["--begin-date", "2026-09-01", "--end-date", "2029-08-31"],
            {"begin_date": dt.date(2026, 9, 1), "end_date": dt.date(2029, 8, 31)},
            id="begin-and-end",
        ),
        # C2: a begin date and a duration of 36 months, expect the end date to be the day before the
        # third anniversary of the begin date
        pytest.param(
            ["--begin-date", "2026-09-01", "--duration", "36"],
            {"begin_date": dt.date(2026, 9, 1), "end_date": dt.date(2029, 8, 31)},
            id="begin-and-duration",
        ),
        # C3: due and submitted dates, expect both stored
        pytest.param(
            ["--due-date", "2026-10-15", "--submitted-date", "2026-10-14"],
            {"due_date": dt.date(2026, 10, 15), "submitted_date": dt.date(2026, 10, 14)},
            id="due-and-submitted",
        ),
        # C4: no dates, expect no date fields rather than tbd placeholders
        pytest.param([], {}, id="no-dates"),
    ],
)
def test_proposal_dates(extra_args, expected_dates, proposals_db):
    main(BASE_ARGS + extra_args)
    proposal = stored_proposal(PROPOSAL_ID)
    actual_dates = {
        key: as_date(proposal[key])
        for key in ("begin_date", "end_date", "due_date", "submitted_date")
        if key in proposal
    }
    assert actual_dates == expected_dates


# Test the team, status and call stored for a new proposal
def test_proposal_team_status_and_call(proposals_db):
    main(
        BASE_ARGS
        + [
            "--pi",
            "sbillinge",
            "--institution",
            "columbiau",
            "--authors",
            "scopatz",
            "Ada Lovelace",
            "--status",
            "pending",
            "--call-for-proposals",
            "https://nsf.gov/call",
        ]
    )
    proposal = stored_proposal(PROPOSAL_ID)
    expected_team = [
        {"name": "Simon J. L. Billinge", "position": "pi", "institution": "columbiau"},
        {"name": "Anthony Scopatz", "position": "copi"},
        {"name": "Ada Lovelace", "position": "copi"},
    ]
    assert proposal["team"] == expected_team
    assert proposal["pi"] == "sbillinge"
    assert proposal["status"] == "pending"
    assert proposal["call_for_proposals"] == "https://nsf.gov/call"


# Test that inconsistent or duplicate input is refused with a message saying what to do
@pytest.mark.parametrize(
    "extra_args, expected_error, expected_message",
    [
        # C1: a begin date after the end date, expect a ValueError asking for a begin date before the end
        pytest.param(
            ["--begin-date", "2027-01-01", "--end-date", "2026-01-01"],
            ValueError,
            "Please re-run with a begin date that is before the end date",
            id="begin-after-end",
        ),
        # C2: a duration that disagrees with the begin and end dates, expect a ValueError asking for one
        pytest.param(
            ["--begin-date", "2026-09-01", "--end-date", "2029-08-31", "--duration", "24"],
            ValueError,
            "Please re-run giving either --duration or --end-date, not both",
            id="duration-mismatch",
        ),
    ],
)
def test_proposal_refuses_bad_dates(extra_args, expected_error, expected_message, proposals_db):
    with pytest.raises(expected_error, match=expected_message):
        main(BASE_ARGS + extra_args)


def test_proposal_refuses_duplicate_id(proposals_db):
    # Test that adding the same proposal twice is refused rather than overwriting the first
    main(BASE_ARGS)
    with pytest.raises(RuntimeError, match="is already in the proposals collection"):
        main(BASE_ARGS)
