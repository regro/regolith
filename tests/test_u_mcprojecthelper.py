"""Tests for updating a project in mission control from the command
line."""

import copy
import os

import pytest

from regolith.database import connect
from regolith.main import main
from regolith.mc import slug
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile

ADD = ["helper", "a_mcproject", "a project to update", "-l", "sbillinge"]
PROJECT_ID = "sb-a-project-to-update"


def stored(_id):
    """Return one project straight from the collection."""
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        return rc.client.get("mc_projects", _id)


@pytest.mark.parametrize(
    "args, field, expected",
    [
        # Test the fields the command line can set.  The document is where a
        # project is described, so this is for what the document does not show
        # and for changing one field without touching anything else.
        # C1: the status, which the document cannot say on its own
        (["-s", "backburner"], "status", "backburner"),
        # C2: who pays for it
        (["-g", "dmref15", "sym"], "grants", ["dmref15", "sym"]),
        # C3: the principal investigator
        (["--pi", "scopatz"], "pi_id", "scopatz"),
        # C4: who leads it, which is how a project is reassigned
        (["-l", "ascopatz"], "lead", "ascopatz"),
        # C5: the fields the document owns, for changing many at once rather
        # than opening each document
        (["--name", "A better name"], "name", "A better name"),
        (["--description", "what it is"], "project_description", "what it is"),
        (["-d", "a paper"], "project_deliverable", "a paper"),
        (["-w", "ascopatz", "afriend"], "collaborators", ["ascopatz", "afriend"]),
        # C6: when it began and ended
        (["--begin-date", "2026-01-01"], "begin_date", "2026-01-01"),
        (["--end-date", "2026-12-31"], "end_date", "2026-12-31"),
        # C7: where the work lives and what was said about it
        (
            ["--url", "the paper", "https://example.com/a"],
            "urls",
            [{"name": "the paper", "url": "https://example.com/a"}],
        ),
        (["--notes", "a note"], "notes", ["a note"]),
    ],
)
def test_a_field_given_on_the_command_line_reaches_the_project(args, field, expected, make_db):
    os.chdir(make_db)
    # the adder puts an id given by hand through slug, so an underscore in a
    # field name comes back as a hyphen
    _id = slug(f"{PROJECT_ID}-{field}")
    main(ADD + ["--id", _id])
    main(["helper", "u_mcproject", _id] + args)
    assert stored(_id)[field] == expected


def test_only_what_was_given_is_written(make_db):
    # Test that updating one field leaves the rest of the project alone, since
    # an updater that blanked what it was not told would be worse than useless
    os.chdir(make_db)
    main(ADD + ["--id", "sb-untouched", "-d", "the original deliverable"])
    main(["helper", "u_mcproject", "sb-untouched", "-s", "active"])
    project = stored("sb-untouched")
    assert project["status"] == "active"
    assert project["project_deliverable"] == "the original deliverable"
    assert project["lead"] == "sbillinge"


@pytest.mark.parametrize(
    "args, expected_message",
    [
        # Test that a mistake says what to do about it rather than writing
        # something wrong.
        # C1: an id nothing is stored under, expect it says how to find one
        (["helper", "u_mcproject", "no-such-project", "-s", "active"], "no project called"),
        # C2: a status outside the vocabulary, expect the allowed ones
        (["helper", "u_mcproject", "sb-untouched", "-s", "nonsense"], "should be one of"),
        # C3: nothing to change at all, expect it asks for something
        (["helper", "u_mcproject", "sb-untouched"], "Nothing was given"),
    ],
)
def test_a_mistake_says_what_to_do_about_it(args, expected_message, make_db):
    os.chdir(make_db)
    with pytest.raises(ValueError, match=expected_message):
        main(args)
