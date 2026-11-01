"""Tests for updating a grant with the u_grant helper, where each grant
is split between a public and a private database."""

import copy
import datetime as dt

import pytest

from regolith.database import connect
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile


def _client_call(method, *args):
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        return getattr(rc.client, method)(*args)


def stored_part(database, grant_id):
    return _client_call("find_one", database, "grants", {"_id": grant_id}) or {}


# Test that each detail is written to the database already holding it, and a new detail to the public or
# private database according to whether it may be shown publicly
@pytest.mark.parametrize(
    "grant_id, extra_args, expected_public_fields, expected_private_fields",
    [
        # C1: an award number the grant has, expect it changed in the public database
        pytest.param("dmref15", ["--awardnr", "DMR-1"], {"awardnr": "DMR-1"}, {}, id="public-field-held"),
        # C2: an account the grant has, expect it changed in the private database
        pytest.param("dmref15", ["--account", "GG-1"], {}, {"account": "GG-1"}, id="private-field-held"),
        # C3: an award number and account the grant does not have yet, expect the award number in the public
        # database and the account in the private one
        pytest.param(
            "abc42",
            ["--awardnr", "ABC-42", "--account", "GG-42"],
            {"awardnr": "ABC-42"},
            {"account": "GG-42"},
            id="new-fields-routed",
        ),
        # C4: 1. a new end date, 2. an amount and 3. a status, expect the date and amount public and the
        # status private
        pytest.param(
            "abc42",
            ["--end-date", "2021-12-31", "--amount", "50000", "--status", "accepted"],
            {"end_date": "2021-12-31", "amount": 50000.0},
            {"status": "accepted"},
            id="dates-amount-status",
        ),
        # C5: a note, expect it added after the grant's existing notes in the private database
        pytest.param("dmref15", ["--notes", "renewed"], {}, {"notes": "renewed"}, id="notes"),
    ],
)
def test_grant_updated(
    grant_id, extra_args, expected_public_fields, expected_private_fields, make_split_grants_db
):
    public_before = stored_part("public", grant_id)
    private_before = stored_part("private", grant_id)
    if "notes" in expected_private_fields and private_before.get("notes"):
        expected_private_fields = {"notes": f"{private_before['notes']} {expected_private_fields['notes']}"}
    main(["helper", "u_grant", grant_id] + extra_args)
    public_after = {
        key: str(value) if isinstance(value, dt.date) else value
        for key, value in stored_part("public", grant_id).items()
    }
    assert public_after == {**public_before, **expected_public_fields}
    assert stored_part("private", grant_id) == {**private_before, **expected_private_fields}


# Test that a fragment of a grant id lists the grants it matches and changes nothing
def test_grant_fragment_lists_matches(make_split_grants_db, capsys):
    main(["helper", "u_grant", "sym", "--awardnr", "X"])
    expected_output = (
        "There is no grant with the id sym. Grants with similar ids:\n"
        "    SymPy-1.1     alias: sym\n"
        "    SymPy-2.0     alias: sym2.0\n"
        "Please re-run the helper giving the complete id.\n"
    )
    assert capsys.readouterr().out.endswith(expected_output)
    assert stored_part("public", "SymPy-1.1")["awardnr"] == "NF-1234"


# Test that an update that cannot be made is refused with a message saying what to do
@pytest.mark.parametrize(
    "extra_args, expected_error, expected_message",
    [
        # C1: no options, expect a RuntimeError asking for at least one
        pytest.param(["dmref15"], RuntimeError, "Please re-run with at least one option", id="nothing-to-update"),
        # C2: an id matching no grant, expect a RuntimeError asking for an existing one
        pytest.param(["nogrant", "--awardnr", "X"], RuntimeError, "No grant matches nogrant", id="no-match"),
        # C3: a begin date after the grant's end date, expect a ValueError asking for an earlier one
        pytest.param(
            ["abc42", "--begin-date", "2025-01-01"],
            ValueError,
            "Please re-run with a begin date that is before the end date",
            id="begin-after-end",
        ),
        # C4: a private database not in regolithrc.json, expect a ValueError naming the ones there are
        pytest.param(
            ["abc42", "--account", "X", "--private-database", "secret"],
            ValueError,
            "Please re-run with one of: public, private",
            id="unknown-database",
        ),
    ],
)
def test_grant_update_refused(extra_args, expected_error, expected_message, make_split_grants_db):
    with pytest.raises(expected_error, match=expected_message):
        main(["helper", "u_grant"] + extra_args)
