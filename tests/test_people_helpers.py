"""Tests for adding and updating people with the a_person, a_service and
u_person helpers, where a person's record is split between a public and
a private database."""

import copy
import datetime as dt

import pytest

from regolith.database import connect
from regolith.helpers.a_personhelper import default_id
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile


def _client_call(method, *args):
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        return getattr(rc.client, method)(*args)


def stored_part(database, person_id):
    return _client_call("find_one", database, "people", {"_id": person_id}) or {}


def services(database, person_id):
    return [entry["name"] for entry in stored_part(database, person_id).get("service") or []]


# Test making an id from a name's first initial and last name
@pytest.mark.parametrize(
    "name, expected_id",
    [
        # C1: a plain name, expect the first initial and last name in lower case
        pytest.param("Ada Lovelace", "alovelace", id="plain"),
        # C2: a name with accents and a middle name, expect the accents dropped and the middle name left out
        pytest.param("José María Pérez", "jperez", id="accents"),
        # C3: a hyphenated name, expect the hyphen dropped
        pytest.param("Jean-Luc Picard", "jpicard", id="hyphen"),
    ],
)
def test_default_id(name, expected_id):
    assert default_id(name) == expected_id


# Test adding a person, who goes to the public database with their position in the group
def test_person_added(make_split_grants_db, capsys):
    main(
        [
            "helper",
            "a_person",
            "Ada Lovelace",
            "--organization",
            "columbiau",
            "--email",
            "ada@example.com",
            "--begin-date",
            "2026-09-01",
            "--end-date",
            "2031-06-30",
        ]
    )
    expected_person = {
        "_id": "alovelace",
        "name": "Ada Lovelace",
        "aka": ["Ada Lovelace"],
        "active": True,
        "position": "graduate research assistant",
        "email": "ada@example.com",
        "avatar": "",
        "bio": "",
        "education": [],
        "employment": [
            {
                "position": "graduate research assistant",
                "organization": "columbiau",
                "group": "ergs",
                "begin_date": dt.date(2026, 9, 1),
                "end_date": dt.date(2031, 6, 30),
                "status": "phd",
            }
        ],
    }
    assert stored_part("public", "alovelace") == expected_person
    assert stored_part("private", "alovelace") == {}
    assert "Plan their appointments with u_appointments alovelace --edit" in capsys.readouterr().out


# Test that a person who may already be there is refused
@pytest.mark.parametrize(
    "extra_args, expected_message",
    [
        # C1: the name of someone there, in another case, expect them named
        pytest.param(["anthony scopatz", "--organization", "x"], "as scopatz", id="name"),
        # C2: a new name but an id in use, expect the person with that id named
        pytest.param(["Someone New", "--id", "sbillinge", "--organization", "x"], "as sbillinge", id="id"),
    ],
)
def test_person_add_refused(extra_args, expected_message, make_split_grants_db):
    with pytest.raises(RuntimeError, match=expected_message):
        main(["helper", "a_person"] + extra_args)


# Test adding service, to the public database by default and to the private one when asked
@pytest.mark.parametrize(
    "extra_args, expected_database",
    [
        # C1: no --private, expect it in the public database
        pytest.param([], "public", id="public"),
        # C2: --private, expect it in the private database
        pytest.param(["--private", "--type", "school"], "private", id="private"),
    ],
)
def test_service_added(extra_args, expected_database, make_split_grants_db):
    public_before = services("public", "sbillinge")
    main(
        ["helper", "a_service", "Program committee, ACA 2027", "--role", "chair", "--date", "2027-07-20"]
        + extra_args
    )
    entry = stored_part(expected_database, "sbillinge")["service"][-1]
    assert entry["name"] == "Program committee, ACA 2027" and entry["role"] == "chair"
    assert len(entry["uuid"]) == 36
    if expected_database == "private":
        assert services("public", "sbillinge") == public_before
    else:
        assert services("public", "sbillinge") == public_before + ["Program committee, ACA 2027"]


# Test that a service entry that cannot be added is refused with a message saying what to do
@pytest.mark.parametrize(
    "extra_args, expected_message",
    [
        # C1: both a date and a begin date, expect it refused
        pytest.param(
            ["New thing", "--date", "2027-01-01", "--begin-date", "2027-01-01"], "Both a date and", id="dates"
        ),
        # C2: a person no one is, expect it refused
        pytest.param(["New thing", "--person", "nobody"], "No single person", id="no-person"),
    ],
)
def test_service_add_refused(extra_args, expected_message, make_split_grants_db):
    with pytest.raises(RuntimeError, match=expected_message):
        main(["helper", "a_service"] + extra_args)


# Test that adding the same service with the same dates twice is refused the second time
def test_service_added_twice(make_split_grants_db):
    args = ["helper", "a_service", "Panel review", "--date", "2027-02-01", "--person", "scopatz"]
    main(args)
    with pytest.raises(RuntimeError, match="scopatz already has the service Panel review with these dates"):
        main(args)


# Test updating simple details, written to the database already holding them
def test_person_details_updated(make_split_grants_db):
    main(["helper", "u_person", "Billinge", "--email", "sb@example.com", "--add-aka", "S. Billinge", "--inactive"])
    part = stored_part("public", "sbillinge")
    assert part["email"] == "sb@example.com" and part["aka"][-1] == "S. Billinge" and part["active"] is False


# Test setting the end of a person's current position in the group, which replaces any end year
def test_position_end_date(make_split_grants_db):
    main(["helper", "u_person", "scopatz", "--end-date", "2027-06-30"])
    position = next(
        entry for entry in stored_part("public", "scopatz")["employment"] if entry.get("group") == "ergs"
    )
    assert position["end_date"] == dt.date(2027, 6, 30) and "end_year" not in position


# Test moving a service entry from the public database to the private one by editing the list from a file
def test_service_moved_to_private(make_split_grants_db):
    (make_split_grants_db / "service.yml").write_text(
        "public:\n"
        "  - {type: profession, name: Co-organizer JUAMI}\n"
        "private:\n"
        "  - {type: school, name: Ad hoc tenure committee, date: 2017-06-01, notes: Albert Einstein}\n"
    )
    main(["helper", "u_person", "sbillinge", "--edit", "service", "--file", "service.yml"])
    assert services("public", "sbillinge") == ["Co-organizer JUAMI"]
    assert services("private", "sbillinge") == ["Ad hoc tenure committee"]


# Test that an edited list with problems is refused with every problem listed
def test_edit_problems(make_split_grants_db):
    (make_split_grants_db / "service.yml").write_text(
        "public:\n  - {type: profession, name: A thing, year: soon}\n  - {type: profession}\nelsewhere: []\n"
    )
    with pytest.raises(ValueError) as error:
        main(["helper", "u_person", "sbillinge", "--edit", "service", "--file", "service.yml"])
    message = str(error.value)
    expected_problems = [
        "elsewhere is not one of the databases, which are public, private.",
        "In public, service, entry 1, year: must be of integer type",
        "In public, service, entry 2, name: required field",
    ]
    for expected_problem in expected_problems:
        assert expected_problem in message


# Test that the editor shows each database's part and that closing it without saving changes nothing
def test_edit_unchanged(make_split_grants_db, monkeypatch, capsys):
    shown_texts = []
    monkeypatch.setattr("regolith.helpers.u_personhelper.edit_text", lambda text: shown_texts.append(text) or text)
    main(["helper", "u_person", "sbillinge", "--edit", "service"])
    assert (
        "#   private is private\n#   public is public\n" in shown_texts[0]
        or "#   public is public" in shown_texts[0]
    )
    assert "public:\n  - type: profession\n" in shown_texts[0]
    assert "The service of sbillinge was not changed." in capsys.readouterr().out


# Test listing a person, with where each part of their record is stored and, when asked, a field in full
@pytest.mark.parametrize(
    "extra_args, expected_texts, unexpected_texts",
    [
        # C1: no options, expect the summary and where each list is stored, but no list in full
        pytest.param(
            [],
            ["sbillinge: Simon J. L. Billinge\n", "        service: 4 entries in public\n"],
            ["# service, under the database"],
            id="summary",
        ),
        # C2: --field service, expect it in full under its database, as the editor shows it
        pytest.param(
            ["--field", "service"],
            ["# service, under the database each part is stored in", "public:\n  - type: profession\n"],
            [],
            id="field",
        ),
        # C3: --since in mid December 2017, expect entries ending before it left out, the one in December 2017
        # kept, and a warning not to use the listing as a file
        pytest.param(
            ["--field", "service", "--since", "2017-12-15"],
            ["do not use this as a --file", "Co-organizer JUAMI", "Applied Physics program committee"],
            ["Ad hoc tenure committee", "Believe it or Not"],
            id="since",
        ),
    ],
)
def test_person_listed(extra_args, expected_texts, unexpected_texts, make_split_grants_db, capsys):
    main(["helper", "l_person", "sbillinge"] + extra_args)
    output = capsys.readouterr().out
    for expected_text in expected_texts:
        assert expected_text in output
    for unexpected_text in unexpected_texts:
        assert unexpected_text not in output


# Test that part of a name lists the one person it matches, or offers the people it might mean
@pytest.mark.parametrize(
    "wanted, expected_text",
    [
        # C1: part of one person's name, expect them listed
        pytest.param("scopa", "scopatz: Anthony Scopatz\n", id="one-match"),
        # C2: part shared by several, expect them offered
        pytest.param("a", "People it might mean:", id="several"),
    ],
)
def test_person_listed_by_fragment(wanted, expected_text, make_split_grants_db, capsys):
    main(["helper", "l_person", wanted])
    assert expected_text in capsys.readouterr().out
