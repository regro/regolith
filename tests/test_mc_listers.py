"""Tests for listing the mission control projects and goals."""

import os

import pytest

from regolith.helpers.l_mcgoalshelper import MCGoalsListerHelper
from regolith.helpers.l_mcprojectshelper import MCProjectsListerHelper, as_list
from regolith.main import main
from regolith.mc import in_the_group, orphaned, unled

PEOPLE = [
    {"_id": "here", "name": "Still Here", "active": True},
    {"_id": "gone", "name": "Has Left", "active": False},
]


@pytest.mark.parametrize(
    "project, expected",
    [
        # Test who counts as having nobody leading them.  Old projecta wrote a
        # placeholder rather than leaving the field out, so those count too.
        # C1: no lead at all, as a mission control project has
        ({}, True),
        # C2: the placeholders projecta used
        ({"lead": "na"}, True),
        ({"lead": "tbd"}, True),
        ({"lead": "TBD"}, True),
        # C3: an empty string, which a form leaves behind
        ({"lead": ""}, True),
        # C4: somebody, expect it is led
        ({"lead": "here"}, False),
    ],
)
def test_a_project_with_nobody_leading_it_is_recognised(project, expected):
    assert unled(project) is expected


@pytest.mark.parametrize(
    "person_id, expected",
    [
        # Test who is in the group at the moment, which is what decides
        # whether their unfinished work is orphaned
        # C1: somebody active, expect they are
        ("here", True),
        # C2: somebody who has left, expect they are not
        ("gone", False),
        # C3: somebody the people collection has never heard of
        ("stranger", False),
    ],
)
def test_who_is_in_the_group(person_id, expected):
    assert in_the_group(person_id, PEOPLE) is expected


@pytest.mark.parametrize(
    "project, expected",
    [
        # Test what needs somebody.  A project is orphaned when it is not done
        # with and either nobody leads it or whoever does has gone.
        # C1: nobody leads it, expect it needs somebody
        ({"status": "active"}, True),
        # C2: led by somebody who has left, expect it comes back by itself,
        # which is the point: nobody has to reassign anything when they go
        ({"status": "active", "lead": "gone"}, True),
        # C3: led by somebody who is here, expect it does not
        ({"status": "active", "lead": "here"}, False),
        # C4: nobody leads it but it is finished, expect it is done with
        ({"status": "finished"}, False),
        # C5: led by somebody who left, but dropped, expect it is done with
        ({"status": "dropped", "lead": "gone"}, False),
        # C6: proposed and unled, expect it still needs somebody
        ({"status": "proposed"}, True),
    ],
)
def test_what_counts_as_orphaned(project, expected):
    assert orphaned(project, PEOPLE) is expected


@pytest.mark.parametrize(
    "value, expected",
    [
        # Test reading a grant field, which projecta wrote as one or as several
        # C1: several, expect them as they are
        (["a", "b"], ["a", "b"]),
        # C2: one, written bare, expect a list of it
        ("a", ["a"]),
        # C3: none, expect nothing rather than an error
        (None, []),
    ],
)
def test_a_grant_may_be_one_or_several(value, expected):
    assert as_list(value) == expected


def test_a_project_line_says_who_and_what():
    # Test the line a project is listed as, which is what gets read in a
    # conversation about what needs doing
    line = MCProjectsListerHelper.line(
        {"_id": "a-project", "name": "A project", "lead": "here", "status": "active"}
    )
    assert line == "a-project  (here, active)  A project"
    unassigned = MCProjectsListerHelper.line({"_id": "b-project", "name": "B", "status": "proposed"})
    assert "(nobody, proposed)" in unassigned


@pytest.mark.parametrize(
    "goal, expected_ending",
    [
        # Test that a goal says how long it has been carried, since that is
        # the thing worth noticing when reading a list of them
        # C1: carried from an earlier period, expect it says since when
        (
            {"_id": "g1", "status": "active", "text": "a goal", "period": "2026Q3", "first_period": "2026Q2"},
            "(carried since 2026Q2)",
        ),
        # C2: set this period, expect nothing added
        (
            {"_id": "g1", "status": "active", "text": "a goal", "period": "2026Q3", "first_period": "2026Q3"},
            "a goal",
        ),
    ],
)
def test_a_goal_line_says_how_long_it_has_been_carried(goal, expected_ending):
    assert MCGoalsListerHelper.line(goal).endswith(expected_ending)


def test_goals_are_grouped_under_their_project():
    # Test that goals are read project by project, the way the meeting goes
    goals = [
        {"_id": "g2", "project": "p1"},
        {"_id": "g1", "project": "p1"},
        {"_id": "g3", "project": "p2"},
    ]
    grouped = MCGoalsListerHelper.by_project(goals)
    assert [project for project, _ in grouped] == ["p1", "p2"]
    assert [g["_id"] for g in grouped[0][1]] == ["g1", "g2"]


def test_projects_are_grouped_under_their_lead():
    # Test the grouping that gets read out in a meeting: whose work is it, and
    # what of it is there.  A project nobody leads is written under nobody
    # rather than left out
    lines = MCProjectsListerHelper.by_lead(
        [
            {"_id": "hs-solver", "name": "Solver", "lead": "here", "status": "active"},
            {"_id": "hs-fits", "name": "Fits", "lead": "here", "status": "proposed"},
            {"_id": "na-idea", "name": "An idea", "status": "proposed"},
        ]
    )
    assert lines == [
        "here:",
        "    hs-solver  (active)  Solver",
        "    hs-fits  (proposed)  Fits",
        "nobody:",
        "    na-idea  (proposed)  An idea",
    ]


@pytest.mark.parametrize(
    "args, expected_in_output",
    [
        # Test the two ways of listing that read differently from one line per
        # project, driven through the command line so that the arguments
        # themselves are covered.  The database is shared with the tests that
        # add projects to it, so each case looks for what it asked for rather
        # than for the whole of what comes back.
        # C1: grouped under the lead, expect the lead written as a heading and
        # their project indented under it
        (["helper", "l_mcprojects", "--grp-by-lead"], ["sbillinge:", "    sb-nanoparticle-pdf  (active)"]),
        # C2: the spelling l_projecta took, expect it works the same, since
        # people have been typing it for years
        (["helper", "l_mcprojects", "--grp_by_lead"], ["sbillinge:", "    sb-nanoparticle-pdf  (active)"]),
        # C3: named keys, expect the id and those keys and nothing else
        (["helper", "l_mcprojects", "-k", "status"], ["sb-nanoparticle-pdf    status: active"]),
    ],
)
def test_the_projects_are_listed_the_way_that_was_asked_for(args, expected_in_output, make_db, capsys):
    os.chdir(make_db)
    main(args)
    written = capsys.readouterr().out
    assert all(expected in written for expected in expected_in_output)
