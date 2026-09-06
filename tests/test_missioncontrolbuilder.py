"""Tests for rendering the mission control documents."""

import datetime as dt

import pytest

from regolith.builders.missioncontrolbuilder import MissionControlBuilder, as_date, week_of

PROJECTS = [
    {
        "_id": "p-pdf",
        "name": "Nanoparticle structure from the PDF",
        "project_deliverable": "Submit the paper",
        "lead": "pliu",
        "status": "active",
    },
    {"_id": "p-orphan", "name": "GPU solver", "status": "proposed"},
]

GOALS = [
    {
        "_id": "g-converge",
        "project": "p-pdf",
        "period": "2026Q3",
        "first_period": "2026Q2",
        "text": "Get the fits converging",
        "status": "active",
    },
    {
        "_id": "g-methods",
        "project": "p-pdf",
        "period": "2026Q3",
        "first_period": "2026Q3",
        "text": "Draft the methods section",
        "status": "active",
    },
    {
        "_id": "g-gpu",
        "project": "p-pdf",
        "period": "2026Q3",
        "first_period": "2026Q3",
        "text": "Port the solver to GPU",
        "status": "backburner",
    },
    {
        "_id": "g-tutorial",
        "project": "p-pdf",
        "period": "2026Q3",
        "first_period": "2026Q3",
        "text": "A tutorial notebook",
        "status": "wishlist",
    },
    {
        "_id": "g-repro",
        "project": "p-pdf",
        "period": "2026Q2",
        "first_period": "2026Q2",
        "text": "Reproduce the 2019 result",
        "status": "finished",
        "end_date": "2026-06-30",
    },
]

TASKS = [
    {
        "_id": "t-bg",
        "goal": "g-converge",
        "due_date": "2026-09-11",
        "first_due_date": "2026-09-04",
        "text": "Re-run the fits",
        "status": "active",
    },
    {
        "_id": "t-plot",
        "goal": "g-converge",
        "due_date": "2026-09-11",
        "first_due_date": "2026-09-11",
        "text": "Send the convergence plot",
        "status": "finished",
    },
    {
        "_id": "t-outline",
        "goal": "g-methods",
        "due_date": "2026-09-04",
        "first_due_date": "2026-09-04",
        "text": "Outline the methods section",
        "status": "finished",
    },
]


@pytest.fixture
def documents():
    """Return the rendered documents, keyed by the person they are
    for."""
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {"mc_projects": PROJECTS, "mc_goals": GOALS, "mc_tasks": TASKS}
    return {person: "\n".join(lines) for person, lines in builder.documents().items()}


@pytest.mark.parametrize(
    "date, expected_monday",
    [
        # Test which week a date is rendered under, since a task is grouped by
        # the week its due date falls in
        # C1: a Monday, expect itself
        (dt.date(2026, 9, 7), dt.date(2026, 9, 7)),
        # C2: midweek, expect the Monday before it
        (dt.date(2026, 9, 9), dt.date(2026, 9, 7)),
        # C3: the Sunday that ends the week, expect the same Monday
        (dt.date(2026, 9, 13), dt.date(2026, 9, 7)),
        # C4: the next Monday, expect the following week
        (dt.date(2026, 9, 14), dt.date(2026, 9, 14)),
    ],
)
def test_week_of_places_a_date_in_its_week(date, expected_monday):
    assert week_of(date) == expected_monday


@pytest.mark.parametrize(
    "value, expected",
    [
        # Test reading a date from a collection, which stores them as dates on
        # the filesystem backend and as iso strings on mongo
        # C1: an iso string, as mongo returns
        ("2026-09-11", dt.date(2026, 9, 11)),
        # C2: a date, as the filesystem returns
        (dt.date(2026, 9, 11), dt.date(2026, 9, 11)),
        # C3: nothing, expect nothing rather than an error
        (None, None),
    ],
)
def test_as_date_reads_either_backend(value, expected):
    assert as_date(value) == expected


def test_a_project_with_no_lead_goes_to_the_unassigned_document(documents):
    # Test that an unled project is an orphan, which is how they are found and
    # assigned
    assert "GPU solver" in documents["unassigned"]
    assert "GPU solver" not in documents["pliu"]


@pytest.mark.parametrize(
    "heading, expected_goal",
    [
        # Test that each goal is rendered under the heading its status puts it
        # under, so the document follows the meeting
        # C1: an open goal in the current period, expect the goals section
        ("## Goals — 2026Q3", "Get the fits converging"),
        # C2: a goal held back, expect the backburner
        ("## Backburner", "Port the solver to GPU"),
        # C3: a goal not being worked on, expect the wishlist
        ("## Wishlist", "A tutorial notebook"),
        # C4: a goal from a past period, expect the archive
        ("### Goals — 2026Q2", "Reproduce the 2019 result"),
    ],
)
def test_a_goal_is_rendered_under_its_status(heading, expected_goal, documents):
    doc = documents["pliu"]
    section = doc.split(heading)[1].split("\n##")[0]
    assert expected_goal in section


@pytest.mark.parametrize(
    "expected_line",
    [
        # Test the notes that make a rolled goal legible without a second
        # record, since a goal that moves period is one record that moved
        # C1: in the current period, expect how long it has been carried
        "Get the fits converging  ^g-converge  (carried since 2026Q2)",
        # C2: in the period it came from, expect where it went
        "Get the fits converging  ^g-converge  (→ rolled to 2026Q3)",
        # C3: a goal that closed, expect when
        "Reproduce the 2019 result  ^g-repro  (finished 2026-06-30)",
    ],
)
def test_a_carried_goal_says_so_in_both_periods(expected_line, documents):
    assert expected_line in documents["pliu"]


@pytest.mark.parametrize(
    "expected_line",
    [
        # Test that a task carries its checkbox state and its stable id, and is
        # numbered against the goal it belongs to
        # C1: an unfinished task, expect an empty box
        "- [ ] 1.1.1  Re-run the fits  ^t-bg",
        # C2: a finished task, expect a ticked box
        "- [x] 1.1.2  Send the convergence plot  ^t-plot",
    ],
)
def test_a_task_is_rendered_with_its_state_and_id(expected_line, documents):
    assert expected_line in documents["pliu"]


def test_weeks_run_backwards_from_the_most_recent(documents):
    # Test that the newest week is nearest the top, which is the order the
    # meeting reads in
    doc = documents["pliu"]
    assert doc.index("## Week of 2026-09-07") < doc.index("## Week of 2026-08-31")


def test_nobody_has_to_type_the_numbers_or_the_ids(documents):
    # Test that every goal and task line carries the id it will be matched back
    # by, since the numbers beside them are positional and get rewritten
    doc = documents["pliu"]
    for _id in ["g-converge", "g-methods", "g-gpu", "g-tutorial", "t-bg", "t-plot"]:
        assert f"^{_id}" in doc
