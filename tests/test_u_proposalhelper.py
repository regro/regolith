"""Tests for updating a proposal with the u_proposal helper."""

import copy
import datetime as dt
import json
import os

import pytest

from regolith.database import connect
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile
from tests.conftest import exemplars_to_fs

TODAY = "2026-11-01"


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
    exemplars_to_fs(fspath, ["proposals"])
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
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value))


# Test the fields a proposal has after an update
@pytest.mark.parametrize(
    "proposal_id, extra_args, expected_fields",
    [
        # C1: status set to pending on a proposal with no submitted_date, expect today recorded as submitted
        pytest.param(
            "SymPy-1.1",
            ["--status", "pending"],
            {"status": "pending", "submitted_date": dt.date(2026, 11, 1)},
            id="pending-records-submission",
        ),
        # C2: status set to pending on a proposal that has a submitted_date, expect that date kept
        pytest.param(
            "dmref15",
            ["--status", "pending"],
            {"status": "pending", "submitted_date": dt.date(2015, 2, 2)},
            id="pending-keeps-submission",
        ),
        # C3: 1. status declined, 2. new begin and end dates, expect them stored and no submitted date added
        pytest.param(
            "SymPy-1.1",
            ["--status", "declined", "--begin-date", "2031-01-01", "--end-date", "2031-12-31"],
            {"status": "declined", "begin_date": dt.date(2031, 1, 1), "end_date": dt.date(2031, 12, 31)},
            id="declined-with-new-dates",
        ),
        # C4: notes on a proposal whose notes are a single string, expect the new note added after it
        pytest.param(
            "mypropsal",
            ["--notes", "resubmit next year"],
            {"notes": ["Quite an idea", "resubmit next year"]},
            id="notes-appended",
        ),
        # C5: amount and title, expect both replaced
        pytest.param(
            "abc42",
            ["--amount", "1234.5", "--title", "A better title"],
            {"amount": 1234.5, "title": "A better title"},
            id="amount-and-title",
        ),
    ],
)
def test_proposal_update(proposal_id, extra_args, expected_fields, proposals_db):
    main(["helper", "u_proposal", proposal_id, "--date", TODAY] + extra_args)
    proposal = stored_proposal(proposal_id)
    actual_fields = {
        key: as_date(proposal[key]) if key.endswith("_date") else proposal[key] for key in expected_fields
    }
    assert actual_fields == expected_fields
    if "submitted_date" not in expected_fields:
        assert "submitted_date" not in proposal


# Test that a new ISO date on a legacy-dated proposal is stored, and the leftover legacy fields are pointed out
def test_proposal_update_notes_legacy_fields(proposals_db, capsys):
    main(["helper", "u_proposal", "mypropsal", "--begin-date", "2030-06-01"])
    out = capsys.readouterr().out
    assert as_date(stored_proposal("mypropsal")["begin_date"]) == dt.date(2030, 6, 1)
    assert "mypropsal still has begin_year, begin_month, begin_day" in out


# Test that a fragment of an id lists the matching proposals without changing anything
def test_proposal_update_fragment_lists_matches(proposals_db, capsys):
    expected_proposal = stored_proposal("SymPy-1.1")
    main(["helper", "u_proposal", "SymPy", "--status", "declined"])
    out = capsys.readouterr().out
    assert "SymPy-1.1" in out and "SymPy-2.1" in out
    assert "Please re-run the helper giving the complete id" in out
    assert stored_proposal("SymPy-1.1") == expected_proposal


# Test that an update that cannot be made is refused with a message saying what to do
@pytest.mark.parametrize(
    "proposal_id, extra_args, expected_error, expected_message",
    [
        # C1: no options, expect a RuntimeError asking for at least one
        pytest.param("abc42", [], RuntimeError, "Please re-run with at least one option", id="nothing-to-do"),
        # C2: an id matching no proposal, expect a RuntimeError asking for an existing one
        pytest.param("zzz", ["--status", "pending"], RuntimeError, "No proposal matches zzz", id="unknown-id"),
        # C3: a begin date after the stored end date, expect a ValueError asking for an earlier begin
        pytest.param(
            "abc42",
            ["--begin-date", "2021-06-01"],
            ValueError,
            "Please re-run with a begin date that is before the end date",
            id="begin-after-end",
        ),
    ],
)
def test_proposal_update_refused(proposal_id, extra_args, expected_error, expected_message, proposals_db):
    with pytest.raises(expected_error, match=expected_message):
        main(["helper", "u_proposal", proposal_id] + extra_args)
