"""Tests for planning and updating appointments with the u_appointments
helper, where people's appointments are kept in a private database."""

import copy

import pytest

from regolith.database import connect
from regolith.fsclient import dump_yaml, load_yaml
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile

TODAY = "2026-11-01"
STUDENT = {
    "_id": "stu",
    "name": "A Student",
    "aka": ["Stu"],
    "employment": [
        {
            "organization": "Columbia University",
            "position": "graduate research assistant",
            "group": "ergs",
            "begin_date": "2025-09-01",
            "end_date": "2027-06-30",
        }
    ],
}
STUDENT_APPOINTMENTS = {
    "s26": {
        "begin_date": "2026-04-01",
        "end_date": "2026-06-30",
        "type": "gra",
        "loading": 1.0,
        "grant": "sym2.0",
        "status": "finalized",
    },
    "f26": {
        "begin_date": "2026-10-01",
        "end_date": "2026-12-31",
        "type": "gra",
        "loading": 0.5,
        "outside_funding": "NSF GRFP",
        "status": "appointed",
    },
    "f26-2": {
        "begin_date": "2026-10-01",
        "end_date": "2026-12-31",
        "type": "gra",
        "loading": 0.5,
        "grant": "sym2.0",
        "status": "appointed",
    },
}


@pytest.fixture
def appointments_db(make_split_grants_db):
    public_people = load_yaml(str(make_split_grants_db / "public" / "people.yaml"))
    public_people["stu"] = copy.deepcopy(STUDENT)
    dump_yaml(str(make_split_grants_db / "public" / "people.yaml"), public_people)
    private_people = {"stu": {"_id": "stu", "appointments": copy.deepcopy(STUDENT_APPOINTMENTS)}}
    dump_yaml(str(make_split_grants_db / "private" / "people.yaml"), private_people)
    yield make_split_grants_db


def _client_call(method, *args):
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        return getattr(rc.client, method)(*args)


def stored_appointments(database, person_id):
    person = _client_call("find_one", database, "people", {"_id": person_id}) or {}
    return {
        appointment_id: {key: str(value) if key.endswith("_date") else value for key, value in appointment.items()}
        for appointment_id, appointment in (person.get("appointments") or {}).items()
    }


def run_with_editor(edit, extra_args=(), monkeypatch=None, person="stu"):
    shown_texts = []

    def stand_in_editor(text):
        shown_texts.append(text)
        return edit(text)

    monkeypatch.setattr("regolith.helpers.u_appointmentshelper.edit_text", stand_in_editor)
    main(["helper", "u_appointments", person, "--edit", "--date", TODAY, *extra_args])
    return shown_texts


# Test that without --edit the appointments from today and the alerts about them are printed
def test_appointments_shown(appointments_db, capsys):
    main(["helper", "u_appointments", "Stu", "--date", TODAY])
    output = capsys.readouterr().out
    assert "# Appointments for A Student from today until their position ends on 2027-06-30" in output
    assert "- _id: f26\n" in output and "- _id: s26\n" not in output
    assert "# ALERT: There is a gap in the appointments from 2027-01-01 to 2027-06-30." in output


# Test that the editor starts with the gaps filled, and that the appointments saved replace those from today
# in the private database, given ids from their quarters, while earlier appointments are kept
def test_appointments_edited(appointments_db, monkeypatch, capsys):
    shown_texts = run_with_editor(lambda text: text.replace("future_grant", "sym2.0"), monkeypatch=monkeypatch)
    expected_gap = (
        "- begin_date: 2027-01-01\n  end_date: 2027-03-31\n  type: gra\n  loading: 1\n  grant: future_grant\n"
    )
    assert expected_gap in shown_texts[0]
    expected_appointments = {
        **STUDENT_APPOINTMENTS,
        "w27": {
            "begin_date": "2027-01-01",
            "end_date": "2027-03-31",
            "type": "gra",
            "loading": 1.0,
            "grant": "sym2.0",
            "status": "proposed",
        },
        "s27": {
            "begin_date": "2027-04-01",
            "end_date": "2027-06-30",
            "type": "gra",
            "loading": 1.0,
            "grant": "sym2.0",
            "status": "proposed",
        },
    }
    assert stored_appointments("private", "stu") == expected_appointments
    assert "appointments" not in (_client_call("find_one", "public", "people", {"_id": "stu"}) or {})
    assert "The appointments of stu have been updated: 4 from today on." in capsys.readouterr().out


# Test that appointments are left as they were when the editor is closed without saving, or when the
# problems found are not fixed
@pytest.mark.parametrize(
    "edits, answers",
    [
        # C1: closed without saving, expect nothing changed
        pytest.param([None], [], id="unchanged"),
        # C2: an entry with no type, then q, expect nothing changed
        pytest.param(
            ["- begin_date: 2027-01-01\n  end_date: 2027-03-31\n  loading: 1\n  grant: g\n"], ["q"], id="quit"
        ),
    ],
)
def test_appointments_left_unchanged(edits, answers, appointments_db, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt: answers.pop(0))
    edits_left = list(edits)
    run_with_editor(lambda text: edits_left.pop(0) or text, monkeypatch=monkeypatch)
    assert "The appointments of stu were not changed." in capsys.readouterr().out
    assert stored_appointments("private", "stu") == STUDENT_APPOINTMENTS


# Test that appointments kept in the public database are moved to the private one when they are updated
def test_appointments_moved_to_private(appointments_db, monkeypatch, capsys):
    new_appointment = (
        "- begin_date: 2027-01-01\n  end_date: 2027-03-31\n  type: pd\n  loading: 1\n  grant: dmref15\n"
    )
    run_with_editor(lambda text: text.replace("[]\n", new_appointment), monkeypatch=monkeypatch, person="scopatz")
    private_appointments = stored_appointments("private", "scopatz")
    assert sorted(private_appointments) == ["f19", "s20", "ss20", "ss21", "w27"]
    assert stored_appointments("public", "scopatz") == {}
    assert "their appointments were moved from public to private" in capsys.readouterr().out


# Test that appointments that cannot be stored are refused with a message saying what to do
@pytest.mark.parametrize(
    "extra_args, file_text, expected_error, expected_message",
    [
        # C1: a file reusing the id of an earlier appointment, expect a ValueError asking for another id
        pytest.param(
            ["--file", "appointments.yml"],
            "- _id: s26\n  begin_date: 2027-01-01\n  end_date: 2027-03-31\n"
            "  type: gra\n  loading: 1\n  grant: g\n",
            ValueError,
            "s26 is the id of an earlier appointment",
            id="earlier-id",
        ),
        # C2: both --edit and --file, expect a RuntimeError asking for one
        pytest.param(
            ["--edit", "--file", "appointments.yml"],
            "[]\n",
            RuntimeError,
            "Only one of --edit and --file",
            id="edit-and-file",
        ),
    ],
)
def test_appointments_refused(extra_args, file_text, expected_error, expected_message, appointments_db):
    (appointments_db / "appointments.yml").write_text(file_text)
    with pytest.raises(expected_error, match=expected_message):
        main(["helper", "u_appointments", "stu", "--date", TODAY, *extra_args])
    assert stored_appointments("private", "stu") == STUDENT_APPOINTMENTS
