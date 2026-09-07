"""Tests for reading a mission control document back."""

import datetime as dt

import pytest

from regolith.builders.missioncontrolbuilder import MissionControlBuilder
from regolith.mc import DocumentError, parse_document
from tests.test_missioncontrolbuilder import GOALS, PROJECTS, SUB_TASKS, TASKS

DOCUMENT = """# Mission control — Adib Kabir

## Projects

1. **nanodiamond-pdf**  ^ak-nano
   deliverable: submit the paper

## Goals — 2026Q3

- 1.1  get clean PDFs  ^a8s8ec  (carried since 2026Q2)
- 1.2  ~~a fitting recipe~~  ^dab3ap

## Week of 2026-09-07

- [ ] 1.1.1  reprocess the September data  ^66e5ty
  - [x] ~~re-integrate the images~~  ^bfvvj6
  - [ ] check the Qmax cutoff  ^4mynvu
- [x] 1.2.1  talk to Simon  ^uxah3a

## Backburner

- 1.3  port the solver  ^gpu111

## Wishlist

- 1.4  a tutorial  ^tut222

## Archive

### Goals — 2026Q2

- 1.1  ~~get clean PDFs~~  ^a8s8ec  (→ rolled to 2026Q3)
"""


@pytest.fixture
def read():
    """Return the document above, read back."""
    return parse_document(DOCUMENT)


def test_the_document_says_who_it_is_for(read):
    # Test that the heading names the person, since the file is theirs
    assert read["person"] == "Adib Kabir"


@pytest.mark.parametrize(
    "kind, expected_ids",
    [
        # Test what is read out of each part of the document
        # C1: the projects, in the order they are written
        ("projects", ["ak-nano"]),
        # C2: the goals of the current period, the backburner and the wishlist,
        # but not the archive, which only says what a past period was
        ("goals", ["a8s8ec", "dab3ap", "gpu111", "tut222"]),
        # C3: the tasks, including the ones nested under another
        ("tasks", ["66e5ty", "bfvvj6", "4mynvu", "uxah3a"]),
    ],
)
def test_each_part_of_the_document_is_read(kind, expected_ids, read):
    assert [item["_id"] for item in read[kind]] == expected_ids


@pytest.mark.parametrize(
    "_id, expected_status",
    [
        # Test what a line's marks and its section say about its status
        # C1: a goal written plainly in the current period, expect active
        ("a8s8ec", "active"),
        # C2: a goal struck through, expect finished
        ("dab3ap", "finished"),
        # C3: a goal under the backburner heading, expect backburner
        ("gpu111", "backburner"),
        # C4: a goal under the wishlist heading, expect wishlist
        ("tut222", "wishlist"),
    ],
)
def test_a_goal_takes_its_status_from_its_marks_and_its_section(_id, expected_status, read):
    goal = next(g for g in read["goals"] if g["_id"] == _id)
    assert goal["status"] == expected_status


@pytest.mark.parametrize(
    "line, expected_status",
    [
        # Test the two ways a task is marked off, and what happens when they
        # disagree.  The strike is believed, since the box is what gets
        # forgotten.
        # C1: ticked and struck, expect finished
        ("- [x] 1.1.1  ~~done~~  ^aaa111", "finished"),
        # C2: struck but not ticked, expect finished
        ("- [ ] 1.1.1  ~~done~~  ^aaa111", "finished"),
        # C3: ticked but not struck, expect finished
        ("- [x] 1.1.1  done  ^aaa111", "finished"),
        # C4: neither, expect still going
        ("- [ ] 1.1.1  not done  ^aaa111", "active"),
    ],
)
def test_a_strike_finishes_a_task_even_without_the_box(line, expected_status):
    text = "## Projects\n\n1. **p**  ^p1\n\n## Goals — 2026Q3\n\n- 1.1  g  ^g1\n\n## Week of 2026-09-07\n\n" + line
    assert parse_document(text)["tasks"][0]["status"] == expected_status


def test_a_task_belongs_to_the_task_it_is_written_under(read):
    # Test that indentation is what says a task is a sub task, and that it
    # inherits the goal of the task above it
    by_id = {t["_id"]: t for t in read["tasks"]}
    assert by_id["bfvvj6"]["parent"] == "66e5ty"
    assert by_id["4mynvu"]["parent"] == "66e5ty"
    assert by_id["bfvvj6"]["goal"] == by_id["66e5ty"]["goal"]
    assert "parent" not in by_id["66e5ty"]


def test_a_task_is_due_in_the_week_it_is_written_under(read):
    # Test that moving a task between week headings is what moves its due date
    assert all(t["due_date"] == dt.date(2026, 9, 7) for t in read["tasks"])


def test_something_typed_without_an_id_is_given_one(read):
    # Test that a person can type a new line and have it become a record.  Ids
    # are the one thing here that is not theirs to write.
    text = DOCUMENT.replace("- 1.2  ~~a fitting recipe~~  ^dab3ap", "- 1.2  a brand new goal")
    goals = parse_document(text)["goals"]
    new = next(g for g in goals if g["text"] == "a brand new goal")
    assert new["_id"] and new["_id"] not in DOCUMENT


@pytest.mark.parametrize(
    "line, expected_message",
    [
        # Test that a line which cannot be placed says so, naming the line,
        # rather than being stored somewhere wrong
        # C1: a task under no goal that exists
        ("- [ ] 9.9.9  orphan task  ^zzz999", "there is no goal 9.9"),
        # C2: a task indented under nothing
        ("  - [ ] orphan sub task  ^zzz999", "indented under nothing"),
        # C3: a task with no number at the top level
        ("- [ ] no number  ^zzz999", "needs a number"),
    ],
)
def test_a_line_that_cannot_be_placed_says_which(line, expected_message):
    text = "## Projects\n\n1. **p**  ^p1\n\n## Goals — 2026Q3\n\n- 1.1  g  ^g1\n\n## Week of 2026-09-07\n\n" + line
    with pytest.raises(DocumentError, match=expected_message):
        parse_document(text)


def test_prose_around_the_lines_is_left_alone():
    # Test that a document is read forgivingly.  People will write notes to
    # each other in it, and that must not stop it being read.
    text = DOCUMENT.replace("## Goals — 2026Q3\n", "## Goals — 2026Q3\n\nSome note we typed in the meeting.\n")
    assert len(parse_document(text)["goals"]) == 4


@pytest.mark.parametrize(
    "projects, goals, tasks",
    [
        # Test that what is rendered can be read back as what was rendered,
        # which is what makes the document safe to edit
        # C1: goals in every section, and a task under each
        (PROJECTS, GOALS, TASKS),
        # C2: tasks nested two deep
        (PROJECTS, GOALS, SUB_TASKS),
    ],
)
def test_a_rendered_document_reads_back_as_what_was_rendered(projects, goals, tasks):
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {"mc_projects": projects, "mc_goals": goals, "mc_tasks": tasks}
    document = "\n".join(builder.documents()["pliu"])
    read = parse_document(document)
    rendered_goals = {g["_id"] for g in goals if g["period"] == "2026Q3"}
    assert {g["_id"] for g in read["goals"]} == rendered_goals
    assert {t["_id"] for t in read["tasks"]} == {t["_id"] for t in tasks}
    for task in read["tasks"]:
        original = next(t for t in tasks if t["_id"] == task["_id"])
        assert task["text"] == original["text"]
        assert task["status"] == original["status"]
        assert task.get("parent") == original.get("parent")


@pytest.mark.parametrize(
    "line, expected",
    [
        # Test reading back who is on a project, which is written under it
        # C1: several people, expect them separated
        ("   with: sgeorge, akabir, seggert", ["sgeorge", "akabir", "seggert"]),
        # C2: one person, expect a list of one
        ("   with: sgeorge", ["sgeorge"]),
        # C3: spacing somebody typed by hand, expect it ignored
        ("   with:  sgeorge ,akabir ", ["sgeorge", "akabir"]),
        # C4: a trailing comma, expect no empty person
        ("   with: sgeorge, akabir,", ["sgeorge", "akabir"]),
    ],
)
def test_who_is_on_a_project_is_read_back(line, expected):
    text = f"## Projects\n\n1. **p**  ^p1\n{line}\n"
    assert parse_document(text)["projects"][0]["collaborators"] == expected


def test_a_project_read_back_keeps_its_deliverable_and_its_people():
    # Test that the two lines under a project do not displace one another
    text = "## Projects\n\n1. **p**  ^p1\n   deliverable: submit it\n   with: sgeorge\n"
    project = parse_document(text)["projects"][0]
    assert project["project_deliverable"] == "submit it"
    assert project["collaborators"] == ["sgeorge"]
