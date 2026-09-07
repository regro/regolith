"""Tests for reading the mission control documents back in."""

import copy
import os

import pytest

from regolith.database import connect
from regolith.fsclient import dump_yaml
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile

DOCUMENT = """# Mission control — Pei Liu

## Projects

1. **a project**  ^mc-a-project
   with: ascopatz

## Goals — 2026Q3

- 1.1  a goal  ^mcg001

## Week of 2026-09-07

- [ ] 1.1.1  a task  ^mct001
"""


@pytest.fixture
def mc_repo(tmp_path):
    """Build a database with one project, goal and task, and its
    document."""
    db = tmp_path / "db"
    db.mkdir()
    mcdir = tmp_path / "mission-control"
    mcdir.mkdir()
    dump_yaml(db / "people.yaml", {"pliu": {"_id": "pliu", "name": "Pei Liu"}})
    dump_yaml(
        db / "mc_projects.yaml",
        {"mc-a-project": {"_id": "mc-a-project", "name": "a project", "lead": "pliu", "status": "active"}},
    )
    dump_yaml(
        db / "mc_goals.yaml",
        {
            "mcg001": {
                "_id": "mcg001",
                "project": "mc-a-project",
                "period": "2026Q3",
                "first_period": "2026Q3",
                "text": "a goal",
                "status": "active",
            }
        },
    )
    dump_yaml(
        db / "mc_tasks.yaml",
        {
            "mct001": {
                "_id": "mct001",
                "goal": "mcg001",
                "due_date": "2026-09-07",
                "first_due_date": "2026-09-07",
                "text": "a task",
                "status": "active",
            }
        },
    )
    import json

    (tmp_path / "regolithrc.json").write_text(
        json.dumps(
            {
                "groupname": "ERGS",
                "default_user_id": "pliu",
                "mission_control_dir": str(mcdir),
                "databases": [
                    {
                        "name": "mc",
                        "url": str(tmp_path),
                        "public": False,
                        "path": "db",
                        "local": True,
                        "backend": "filesystem",
                    }
                ],
            }
        )
    )
    (mcdir / "pei.md").write_text(DOCUMENT)
    os.chdir(tmp_path)
    yield tmp_path, mcdir


def stored(where, collection, _id):
    """Return one record straight from the collection."""
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        return rc.client.get(collection, _id)


@pytest.mark.parametrize(
    "edit, collection, _id, field, expected",
    [
        # Test that what somebody writes in a document reaches the collection
        # C1: a task struck through, expect it finished even with an empty box
        (
            lambda t: t.replace("a task  ^mct001", "~~a task~~  ^mct001"),
            "mc_tasks",
            "mct001",
            "status",
            "finished",
        ),
        # C2: a task ticked, expect it finished
        (lambda t: t.replace("- [ ] 1.1.1", "- [x] 1.1.1"), "mc_tasks", "mct001", "status", "finished"),
        # C3: a goal moved under the on-deck heading, expect it held
        (
            lambda t: t.replace(
                "## Goals — 2026Q3\n\n- 1.1  a goal  ^mcg001\n",
                "## Goals — 2026Q3\n\n## On-deck\n\n- 1.1  a goal  ^mcg001\n",
            ),
            "mc_goals",
            "mcg001",
            "status",
            "on-deck",
        ),
        # C4: the wording changed, expect the new wording
        (
            lambda t: t.replace("a goal  ^mcg001", "a better goal  ^mcg001"),
            "mc_goals",
            "mcg001",
            "text",
            "a better goal",
        ),
        # C5: somebody added to the project, expect them on it
        (
            lambda t: t.replace("with: ascopatz", "with: ascopatz, afriend"),
            "mc_projects",
            "mc-a-project",
            "collaborators",
            ["ascopatz", "afriend"],
        ),
    ],
)
def test_an_edit_reaches_the_collection(edit, collection, _id, field, expected, mc_repo):
    _, mcdir = mc_repo
    path = mcdir / "pei.md"
    path.write_text(edit(path.read_text()))
    main(["helper", "mc_sync"])
    assert stored(mc_repo, collection, _id)[field] == expected


def test_a_line_taken_out_is_dropped(mc_repo):
    # Test that removing a line marks its record rather than deleting it, so
    # nothing is lost to a slip of the keyboard
    _, mcdir = mc_repo
    path = mcdir / "pei.md"
    path.write_text(path.read_text().replace("- [ ] 1.1.1  a task  ^mct001\n", ""))
    main(["helper", "mc_sync", "--force"])
    assert stored(mc_repo, "mc_tasks", "mct001")["status"] == "dropped"


def test_a_document_that_lost_most_of_itself_is_left_alone(mc_repo, capsys):
    # Test the guard against damage: a document missing most of what it held
    # is more likely broken than edited, so nothing is written from it
    _, mcdir = mc_repo
    (mcdir / "pei.md").write_text("# Mission control — Pei Liu\n")
    main(["helper", "mc_sync"])
    assert "more like damage than editing" in capsys.readouterr().out
    assert stored(mc_repo, "mc_tasks", "mct001")["status"] == "active"


def test_a_document_that_cannot_be_read_is_skipped_whole(mc_repo, capsys):
    # Test that one bad document leaves the collections alone rather than
    # applying the half of it that made sense
    _, mcdir = mc_repo
    path = mcdir / "pei.md"
    path.write_text(path.read_text() + "- [ ] 9.9.9  a task under nothing  ^mct999\n")
    main(["helper", "mc_sync"])
    out = capsys.readouterr().out
    assert "was not read" in out and "there is no goal 9.9" in out
    assert stored(mc_repo, "mc_tasks", "mct999") is None


def test_a_dry_run_says_what_it_would_do_and_does_nothing(mc_repo, capsys):
    # Test that the run which changes nothing still reports what it found
    _, mcdir = mc_repo
    path = mcdir / "pei.md"
    path.write_text(path.read_text().replace("a task  ^mct001", "~~a task~~  ^mct001"))
    main(["helper", "mc_sync", "--dry-run"])
    assert "would write" in capsys.readouterr().out
    assert stored(mc_repo, "mc_tasks", "mct001")["status"] == "active"


def test_a_document_that_says_nothing_new_changes_nothing(mc_repo):
    # Test that reading a document straight after rendering it is a no-op,
    # which is what makes syncing on every read safe
    before = stored(mc_repo, "mc_goals", "mcg001")
    main(["helper", "mc_sync"])
    assert stored(mc_repo, "mc_goals", "mcg001") == before


def test_what_was_dropped_is_not_dropped_again(mc_repo, capsys):
    # Test that a deletion settles.  What was dropped is no longer in the
    # document, so counting it again would have every later sync report a
    # deletion nobody made, and enough of them would read as a damaged file
    _, mcdir = mc_repo
    path = mcdir / "pei.md"
    path.write_text(path.read_text().replace("- [ ] 1.1.1  a task  ^mct001\n", ""))
    main(["helper", "mc_sync"])
    capsys.readouterr()
    main(["helper", "mc_sync"])
    assert "dropped 0" in capsys.readouterr().out
    assert stored(mc_repo, "mc_tasks", "mct001")["status"] == "dropped"


def test_a_project_typed_in_is_stored_under_a_readable_id(mc_repo):
    # Test that a project somebody types into their document gets the same
    # readable id the adder helper gives one, since a project id is what names
    # it in a lister and in whatever refers to it later
    _, mcdir = mc_repo
    path = mcdir / "pei.md"
    path.write_text(
        path.read_text().replace(
            "1. **a project**  ^mc-a-project",
            "1. **a project**  ^mc-a-project\n\n2. **A Second Project**",
        )
    )
    main(["helper", "mc_sync"])
    assert stored(mc_repo, "mc_projects", "pl-a-second-project")["name"] == "A Second Project"


def test_a_document_is_read_even_when_the_collections_hold_nothing_of_its_own(mc_repo):
    # Test that a document is read on its own account.  Somebody whose project
    # has gone from the collections still has the document that describes it,
    # and that document is how they put it back, so working out which
    # documents to read from the collections would pass over the one that
    # matters most
    tmp_path, mcdir = mc_repo
    dump_yaml(tmp_path / "db" / "mc_projects.yaml", {})
    main(["helper", "mc_sync"])
    assert stored(mc_repo, "mc_projects", "mc-a-project")["name"] == "a project"


def test_a_document_named_for_nobody_says_so(mc_repo, capsys):
    # Test that a file nobody is named by is reported rather than passed over
    # in silence, since a document that is never read looks exactly like one
    # that had nothing to say
    _, mcdir = mc_repo
    (mcdir / "whoever.md").write_text("# Mission control — Whoever\n")
    main(["helper", "mc_sync"])
    assert "whoever.md is not named for anybody" in capsys.readouterr().out


def test_a_project_nobody_leads_is_named_na(mc_repo):
    # Test that a project typed into the unassigned document is named na, so
    # that it reads as nobody's until somebody picks it up, and does not clash
    # with a project of the same name that somebody leads
    _, mcdir = mc_repo
    (mcdir / "unassigned.md").write_text(
        "# Mission control — unassigned\n\n## Projects\n\n1. **Software maintenance**\n"
    )
    main(["helper", "mc_sync"])
    assert stored(mc_repo, "mc_projects", "na-software-maintenance")["status"] == "proposed"


def test_the_sync_says_how_many_lines_were_new(mc_repo, capsys):
    # Test that a sync says what it did in terms somebody typing can check.
    # "wrote 3" says nothing about whether the lines just typed were among
    # them, which is the one thing worth knowing after typing into a document
    _, mcdir = mc_repo
    path = mcdir / "pei.md"
    path.write_text(
        path.read_text().replace("- 1.1  a goal  ^mcg001", "- 1.1  a goal  ^mcg001\n- 1.2  a new goal")
    )
    main(["helper", "mc_sync"])
    assert "1 of them new" in capsys.readouterr().out


def test_a_record_is_written_where_it_is_already_stored(mc_repo):
    # Test that a sync writes a record back to the database holding it rather
    # than to whichever database is listed first, which would leave a second
    # copy shadowing the real one
    tmp_path, mcdir = mc_repo
    path = mcdir / "pei.md"
    path.write_text(path.read_text().replace("a goal", "a goal, reworded"))
    main(["helper", "mc_sync"])
    stored_in_db = (tmp_path / "db" / "mc_goals.yaml").read_text()
    assert "a goal, reworded" in stored_in_db
