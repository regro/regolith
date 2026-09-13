"""Tests for finishing a project in mission control from the command
line."""

import copy
import datetime as dt
import os

import pytest

from regolith.database import connect
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile

TODAY = dt.date.today()


def a_project(make_db, _id):
    """Add a project with a goal and a task, and return their ids.

    Each test gets an id of its own: the database is shared for the whole
    session, so a project added twice is a project that already exists.
    """
    os.chdir(make_db)
    main(["helper", "a_mcproject", f"a project to finish, {_id}", "-l", "sbillinge", "--id", _id])
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        goal = next(g for g in rc.client.all_documents("mc_goals") if g["project"] == _id)
        task = next(t for t in rc.client.all_documents("mc_tasks") if t["goal"] == goal["_id"])
    return goal["_id"], task["_id"]


def stored(collection, _id):
    """Return one record straight from the collection."""
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        return rc.client.get(collection, _id)


def test_finishing_a_project_finishes_what_is_under_it(make_db):
    # Test the whole point of the helper: finishing a project by hand means
    # striking through its goals, and the tasks under those, and then the
    # project, which is three kinds of thing to remember
    goal_id, task_id = a_project(make_db, "sb-cascade")
    main(["helper", "f_mcproject", "sb-cascade"])
    for collection, _id in [("mc_projects", "sb-cascade"), ("mc_goals", goal_id), ("mc_tasks", task_id)]:
        record = stored(collection, _id)
        assert record["status"] == "finished"
        assert record["end_date"] == TODAY


def test_a_day_can_be_given_for_when_it_finished(make_db):
    # Test that a project finished last week is dated last week, since
    # nobody runs the helper the moment the work is done
    a_project(make_db, "sb-dated")
    main(["helper", "f_mcproject", "sb-dated", "--end-date", "2026-06-30"])
    assert stored("mc_projects", "sb-dated")["end_date"] == dt.date(2026, 6, 30)


def test_what_was_over_already_is_left_as_it_was(make_db):
    # Test that finishing a project does not move the day an earlier goal was
    # finished on, and does not bring a dropped one back as finished
    goal_id, task_id = a_project(make_db, "sb-already-over")
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        rc.client.update_one(rc.databases[0]["name"], "mc_goals", {"_id": goal_id}, {"status": "dropped"})
    main(["helper", "f_mcproject", "sb-already-over"])
    assert stored("mc_goals", goal_id)["status"] == "dropped"
    assert stored("mc_projects", "sb-already-over")["status"] == "finished"


@pytest.mark.parametrize(
    "add, given, expected_said",
    [
        # Test that an id naming no project says so rather than finishing the
        # wrong thing, and that enough of one is enough.  Each case adds a
        # project of its own, since the database is shared for the session.
        # C1: enough of an id to name the one project, expect it finished
        ("sb-fragment", "sb-frag", "finished sb-fragment"),
        # C2: an id nothing is stored under, expect it says how to find one
        ("sb-not-this-one", "no-such-project", "no project called"),
    ],
)
def test_an_id_names_one_project_or_says_so(add, given, expected_said, make_db, capsys):
    a_project(make_db, add)
    if "no project" in expected_said:
        with pytest.raises(ValueError, match=expected_said):
            main(["helper", "f_mcproject", given])
    else:
        main(["helper", "f_mcproject", given])
        assert expected_said in capsys.readouterr().out


def test_a_dry_run_says_what_it_would_do_and_does_nothing(make_db, capsys):
    # Test that somebody can see what a finish would take with it before
    # taking it, since it reaches records they are not looking at
    a_project(make_db, "sb-dry-run")
    main(["helper", "f_mcproject", "sb-dry-run", "--dry-run"])
    assert "would finish sb-dry-run" in capsys.readouterr().out
    assert stored("mc_projects", "sb-dry-run")["status"] != "finished"
