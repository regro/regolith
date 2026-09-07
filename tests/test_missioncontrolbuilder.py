"""Tests for rendering the mission control documents."""

import datetime as dt

import pytest

from regolith.builders.missioncontrolbuilder import (
    MissionControlBuilder,
    as_date,
    ids_in_document,
    in_document_order,
    keys_in_document,
)
from regolith.mc import WIDTH, parse_document, week_of

PROJECTS = [
    {
        "_id": "p-pdf",
        "name": "Nanoparticle structure from the PDF",
        "project_deliverable": "Submit the paper",
        "collaborators": ["ascopatz", "afriend"],
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
        # C2: in the period it came from, expect it struck through and where
        # it went, since that period is done with it
        "~~Get the fits converging~~  ^g-converge  (→ rolled to 2026Q3)",
        # C3: a goal that closed, expect it struck through and dated
        "~~Reproduce the 2019 result~~  ^g-repro  (finished 2026-06-30)",
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
        # C2: a finished task, expect a ticked box and a strike through it,
        # since that is how the group marks something off
        "- [x] 1.1.2  ~~Send the convergence plot~~  ^t-plot",
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


@pytest.mark.parametrize(
    "text, expected_ids",
    [
        # Test reading the ids a document carries, which is how a render keeps
        # an order somebody chose in a meeting
        # C1: ids in the order they appear, expect that order
        ("- one ^g-b\n- two ^g-a\n", ["g-b", "g-a"]),
        # C2: an id repeated, as a rolled goal is, expect it once
        ("- one ^g-b\n- again ^g-b\n- two ^g-a\n", ["g-b", "g-a"]),
        # C3: nothing to read, expect nothing
        ("# Mission control — pliu\n", []),
    ],
)
def test_ids_in_document_reads_the_order(text, expected_ids):
    assert ids_in_document(text) == expected_ids


@pytest.mark.parametrize(
    "order, expected_ids",
    [
        # Test the ordering rule: the document wins for what it mentions, and
        # anything else follows it
        # C1: the document names both, expect its order rather than the default
        (["p-orphan", "p-pdf"], ["p-orphan", "p-pdf"]),
        # C2: the document names one, expect it first and the rest after
        (["p-orphan"], ["p-orphan", "p-pdf"]),
        # C3: the document names none, expect the fallback order
        ([], ["p-orphan", "p-pdf"]),
        # C4: the document names something that is gone, expect it ignored
        (["p-deleted", "p-pdf"], ["p-pdf", "p-orphan"]),
    ],
)
def test_in_document_order_puts_the_document_first(order, expected_ids):
    ordered = in_document_order(PROJECTS, order, lambda p: p["_id"])
    assert [p["_id"] for p in ordered] == expected_ids


def test_a_render_keeps_the_order_the_document_chose():
    # Test the whole rule through a render: a person who has reordered their
    # projects keeps that order, and a new project joins the end
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {"mc_projects": PROJECTS, "mc_goals": GOALS, "mc_tasks": TASKS}
    both = [dict(p, lead="pliu") for p in PROJECTS]
    builder.gtx["mc_projects"] = both
    reordered = builder.documents({"pliu": ["p-orphan"]})["pliu"]
    projects = [line for line in reordered if line.startswith(("1. ", "2. "))]
    assert projects[0].endswith("^p-orphan")
    assert projects[1].endswith("^p-pdf")


def test_a_goal_finished_this_period_is_still_shown():
    # Test that closing a goal does not make it disappear.  The goals section
    # used to show only open ones and the archive only past periods, so a goal
    # finished in the current period appeared nowhere, and reviewing the period
    # is most of what the meeting is for.
    finished_now = dict(GOALS[1], status="finished", end_date="2026-09-11")
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {"mc_projects": PROJECTS, "mc_goals": [GOALS[0], finished_now], "mc_tasks": []}
    doc = "\n".join(builder.documents()["pliu"])
    section = doc.split("## Goals — 2026Q3")[1].split("\n##")[0]
    assert "Draft the methods section" in section
    assert "(finished 2026-09-11)" in section


@pytest.mark.parametrize(
    "people, expected_name, expected_heading",
    [
        # Test what a document is called and headed.  It is for a person to
        # open, so it carries their name rather than their id.
        # C1: the people collection knows them, expect their first name
        ([{"_id": "pliu", "name": "Pei Liu"}], "pei", "Pei Liu"),
        # C2: it does not know them, expect the id, so a document is still written
        ([], "pliu", "pliu"),
    ],
)
def test_a_document_is_named_for_the_person(people, expected_name, expected_heading):
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {"mc_projects": PROJECTS, "mc_goals": GOALS, "mc_tasks": TASKS, "people": people}
    assert builder.document_name("pliu") == expected_name
    assert builder.documents()["pliu"][0] == f"# Mission control — {expected_heading}"


def test_the_unassigned_document_is_not_named_for_a_person():
    # Test that the orphans document keeps its own name, since no person owns it
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {"mc_projects": PROJECTS, "mc_goals": GOALS, "mc_tasks": TASKS, "people": []}
    assert builder.document_name("unassigned") == "unassigned"


SUB_TASKS = [
    {
        "_id": "t-bg",
        "goal": "g-converge",
        "due_date": "2026-09-11",
        "first_due_date": "2026-09-11",
        "text": "Re-run the fits",
        "status": "active",
    },
    {
        "_id": "t-sub1",
        "goal": "g-converge",
        "parent": "t-bg",
        "due_date": "2026-09-11",
        "first_due_date": "2026-09-11",
        "text": "Rebuild the background model",
        "status": "finished",
    },
    {
        "_id": "t-sub2",
        "goal": "g-converge",
        "parent": "t-bg",
        "due_date": "2026-09-11",
        "first_due_date": "2026-09-11",
        "text": "Check it against the standard",
        "status": "active",
    },
    {
        "_id": "t-subsub",
        "goal": "g-converge",
        "parent": "t-sub2",
        "due_date": "2026-09-11",
        "first_due_date": "2026-09-11",
        "text": "Fetch the standard from the archive",
        "status": "active",
    },
]


@pytest.fixture
def nested():
    """Return a document whose tasks are nested two deep."""
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {"mc_projects": PROJECTS, "mc_goals": GOALS, "mc_tasks": SUB_TASKS}
    return "\n".join(builder.documents()["pliu"])


@pytest.mark.parametrize(
    "expected_line",
    [
        # Test that sub tasks are written under the task they belong to, as
        # deep as they go, since a meeting wanders into sub sub tasks
        # C1: the task itself, at the top level
        "- [ ] 1.1.1  Re-run the fits  ^t-bg",
        # C2: a sub task, indented once and not numbered, since a number says
        # which goal and which of its tasks and a sub task is neither
        "  - [x] ~~Rebuild the background model~~  ^t-sub1",
        # C3: another sub task alongside it
        "  - [ ] Check it against the standard  ^t-sub2",
        # C4: a sub sub task, indented twice and still not numbered
        "    - [ ] Fetch the standard from the archive  ^t-subsub",
    ],
)
def test_a_task_carries_the_tasks_under_it(expected_line, nested):
    assert expected_line in nested


def test_a_sub_task_is_not_listed_as_a_task_of_its_own(nested):
    # Test that a sub task appears once, under its parent, rather than also as
    # one of the week's tasks
    assert nested.count("^t-sub1") == 1
    assert "1.1.2" not in nested


@pytest.mark.parametrize(
    "expected_line",
    [
        # Test that the archive strikes through everything a past period is
        # done with, which is what finished in it and what rolled out of it
        # C1: a goal that finished in that period
        "- 1.4  ~~Reproduce the 2019 result~~  ^g-repro  (finished 2026-06-30)",
        # C2: a goal that rolled out of it, which that period is equally done
        # with even though the goal itself is still going
        "- 1.1  ~~Get the fits converging~~  ^g-converge  (→ rolled to 2026Q3)",
    ],
)
def test_the_archive_strikes_through_what_left_the_period(expected_line, documents):
    assert expected_line in documents["pliu"]


def test_a_rolled_goal_is_not_struck_in_the_period_it_moved_to(documents):
    # Test that striking it in the archive does not strike it where it is now,
    # since it is still to be done
    current = documents["pliu"].split("## Goals — 2026Q3")[1].split("\n##")[0]
    assert "- 1.1  Get the fits converging  ^g-converge  (carried since 2026Q2)" in current


def test_a_project_lists_who_is_on_it(documents):
    # Test that the people on a project are written under it, as a reminder
    # when talking about it
    assert "   with: ascopatz, afriend" in documents["pliu"]


def test_a_project_with_nobody_on_it_says_nothing(documents):
    # Test that an empty list leaves the line out rather than writing a bare
    # heading with nothing after it
    assert "   with: \n" not in documents["unassigned"]
    assert "with:" not in documents["unassigned"]


def test_what_a_project_is_about_is_written_under_it():
    # Test that the description goes back into the document, so that reading
    # one and writing it again does not lose the paragraph somebody typed
    described = dict(PROJECTS[0], project_description="what this project is about")
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {"mc_projects": [described], "mc_goals": [], "mc_tasks": []}
    document = "\n".join(builder.documents()["pliu"])
    assert "   what this project is about" in document


@pytest.mark.parametrize(
    "collection, dropped_id, gone, kept",
    [
        # Test that a thing somebody deleted from their document does not come
        # back the next time the document is built.  Deleting a line is how a
        # thing is deleted, and the sync marks it dropped rather than removing
        # it, so the render is what has to honour the deletion.
        # C1: a project was dropped, expect the document without it
        ("mc_projects", "p-orphan", "^p-orphan", "^p-pdf"),
        # C2: a goal was dropped, expect the document without it
        ("mc_goals", "g-methods", "^g-methods", "^g-converge"),
        # C3: a task was dropped, expect the document without it
        ("mc_tasks", "t-bg", "^t-bg", "^t-plot"),
    ],
)
def test_a_dropped_thing_does_not_come_back(collection, dropped_id, gone, kept):
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    records = {
        "mc_projects": [dict(p, lead="pliu") for p in PROJECTS],
        "mc_goals": GOALS,
        "mc_tasks": TASKS,
    }
    builder.gtx = {
        name: [dict(r, status="dropped") if r["_id"] == dropped_id else r for r in rs]
        for name, rs in records.items()
    }
    document = "\n".join(builder.documents()["pliu"])
    assert gone not in document
    assert kept in document


def test_a_sub_task_outlives_the_task_it_hung_off():
    # Test that deleting a task does not silently take an unrelated sub task
    # with it.  A sub task with no task above it is shown in its own right,
    # numbered like any other, rather than disappearing from the document
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {
        "mc_projects": PROJECTS,
        "mc_goals": GOALS,
        "mc_tasks": [dict(t, status="dropped") if t["_id"] == "t-bg" else t for t in SUB_TASKS],
    }
    document = "\n".join(builder.documents()["pliu"])
    assert "^t-bg" not in document
    assert "\n- [x] 1.1.1  ~~Rebuild the background model~~  ^t-sub1" in document


def test_a_project_is_written_as_paragraphs_markdown_can_render():
    # Test that what is written under a project is separated by blank lines.
    # Markdown runs consecutive lines into one paragraph, so without them a
    # project reads as a single block wherever the document is rendered
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    described = dict(PROJECTS[0], project_description="what this project is about")
    builder.gtx = {"mc_projects": [described], "mc_goals": [], "mc_tasks": []}
    document = "\n".join(builder.documents()["pliu"])
    assert "^p-pdf\n\n   deliverable: Submit the paper\n\n   with: " in document
    assert "ascopatz, afriend\n\n   what this project is about\n" in document


LONG = (
    "build an AI campaign using simple models such as random forest to predict "
    "which of the samples in the matrix are worth measuring at the beamline"
)


def test_a_wrapped_document_reads_back_the_same():
    # Test the two halves against each other over text long enough to be
    # broken several times: a project's description, a goal, a task and the sub
    # task under it all come back whole, and no line is wider than the width
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {
        "mc_projects": [dict(PROJECTS[0], project_description=LONG)],
        "mc_goals": [dict(GOALS[0], text=LONG)],
        "mc_tasks": [
            dict(TASKS[0], text=LONG),
            dict(TASKS[0], _id="t-sub", parent="t-bg", text=f"a sub task, {LONG}"),
        ],
    }
    lines = builder.documents()["pliu"]
    read = parse_document("\n".join(lines) + "\n")
    assert max(len(line) for line in lines) <= WIDTH
    assert read["projects"][0]["project_description"] == LONG
    assert read["goals"][0]["text"] == LONG
    assert [task["text"] for task in read["tasks"]] == [LONG, f"a sub task, {LONG}"]
    assert read["tasks"][1]["parent"] == read["tasks"][0]["_id"]


TYPED_BY_HAND = """# Mission control — Pei Liu

## Projects

1. **GPU solver**

2. **Nanoparticle structure from the PDF**

## Goals — 2026Q3

- 2.1  Draft the methods section
- 2.2  Get the fits converging
"""


def test_a_document_with_no_ids_still_says_what_order_it_is_in():
    # Test that a document somebody typed keeps the order they typed.  A line
    # carries an id only once a render has put one there, so until then the
    # text of the line is what says which thing it is, and without that a
    # render sorts by id and hands back an order nobody chose
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {
        "mc_projects": [dict(p, lead="pliu") for p in PROJECTS],
        "mc_goals": GOALS,
        "mc_tasks": TASKS,
    }
    document = "\n".join(builder.documents({"pliu": keys_in_document(TYPED_BY_HAND)})["pliu"])
    assert "1. **GPU solver**  ^p-orphan" in document
    assert "2. **Nanoparticle structure from the PDF**  ^p-pdf" in document
    assert "- 2.1  Draft the methods section  ^g-methods" in document


@pytest.mark.parametrize(
    "document, expected_keys",
    [
        # Test what a document is read as naming, which is what a render puts
        # back in order.
        # C1: lines carrying ids, expect the ids and the texts both, so that
        # either finds the thing again
        (
            "## Projects\n\n1. **A project**  ^p1\n",
            ["p1", "A project"],
        ),
        # C2: a line carrying no id, expect its text, since that is all it
        # says about which thing it is
        (
            "## Projects\n\n1. **A project**\n",
            ["A project"],
        ),
        # C3: a document that cannot be read at all, expect the ids it carries
        # rather than nothing, since a broken file still says something
        (
            "## Goals — 2026Q3\n\n- 9.9  a goal of no project  ^g9\n",
            ["g9"],
        ),
    ],
)
def test_keys_in_document_reads_ids_and_texts(document, expected_keys):
    keys = keys_in_document(document)
    assert [key for key in keys if key in expected_keys] == expected_keys


@pytest.mark.parametrize(
    "lead",
    [
        # Test that a placeholder lead is not taken for a person.  The adder
        # writes tbd into a stub, and projecta wrote na, and neither is
        # somebody whose document should be written.
        # C1: the adder's placeholder
        "tbd",
        # C2: the one projecta used
        "na",
        # C3: what a form leaves behind
        "",
    ],
)
def test_a_project_nobody_leads_goes_to_the_unassigned_document(lead):
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {
        "mc_projects": [dict(PROJECTS[0], lead=lead)],
        "mc_goals": [],
        "mc_tasks": [],
        "people": [],
    }
    documents = builder.documents()
    assert list(documents) == ["unassigned"]
