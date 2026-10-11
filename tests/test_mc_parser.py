"""Tests for reading a mission control document back."""

import datetime as dt

import pytest

from regolith.builders.missioncontrolbuilder import MissionControlBuilder
from regolith.mc import DocumentError, parse_document, period_of
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

## On-deck tasks

- [ ] 1.1.2  look at the new detector data  ^d3ck01

## Wishlist goals

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
        # C2: the goals of the current period and the wishlist, but not the
        # archive, which only says what a past period was
        ("goals", ["a8s8ec", "dab3ap", "tut222"]),
        # C3: the tasks, including the ones nested under another and the one
        # on deck
        ("tasks", ["66e5ty", "bfvvj6", "4mynvu", "uxah3a", "d3ck01"]),
    ],
)
def test_each_part_of_the_document_is_read(kind, expected_ids, read):
    assert [item["_id"] for item in read[kind]] == expected_ids


HELD_ABOVE_AND_BELOW = """# Mission control — Adib Kabir

## Projects

1. **nanodiamond-pdf**  ^ak-nano

## Wishlist goals

- 1.4  a tutorial  ^tut222

## Goals — 2026Q3

- 1.1  get clean PDFs  ^a8s8ec

## On-deck tasks

- [ ] 1.1.1  look at the new detector data  ^d3ck01
"""


@pytest.mark.parametrize(
    "period, expected_periods",
    [
        # Test the period a wishlist line is given.  A holding section has no
        # heading saying one, so it must not depend on which heading happens
        # to come before it: above the goals it would get none, and none does
        # not validate
        # C1: a period given, expect it on the wishlist line above the goals,
        # and the goals heading's on its own
        ("2026Q4", {"tut222": "2026Q4", "a8s8ec": "2026Q3"}),
        # C2: none given, expect the period today falls in
        (None, {"tut222": "today", "a8s8ec": "2026Q3"}),
    ],
)
def test_a_held_line_is_given_a_period_whatever_heading_came_before(period, expected_periods):
    today = period_of(dt.date.today())
    read = parse_document(HELD_ABOVE_AND_BELOW, period=period)
    periods = {goal["_id"]: goal["period"] for goal in read["goals"]}
    assert periods == {_id: (today if p == "today" else p) for _id, p in expected_periods.items()}


@pytest.mark.parametrize(
    "_id, expected_status",
    [
        # Test what a line's marks and its section say about its status
        # C1: a goal written plainly in the current period, expect active
        ("a8s8ec", "active"),
        # C2: a goal struck through, expect finished
        ("dab3ap", "finished"),
        # C3: a goal under the wishlist heading, expect wishlist
        ("tut222", "wishlist"),
    ],
)
def test_a_goal_takes_its_status_from_its_marks_and_its_section(_id, expected_status, read):
    goal = next(g for g in read["goals"] if g["_id"] == _id)
    assert goal["status"] == expected_status


@pytest.mark.parametrize(
    "line, expected",
    [
        # Test a task pasted down on deck, which keeps the number and the id it
        # came with and says nothing a sync should read about which goal or
        # which week it is of: the id keeps it the same record
        # C1: a task with its number and id, expect it on deck under its id,
        # with no goal and no week read from the line
        ("- [ ] 1.1.1  a task pasted down  ^66e5ty", {"_id": "66e5ty", "status": "on-deck"}),
        # C2: a task typed with no number, expect it on deck all the same
        ("- [ ] typed on deck  ^d3ck02", {"_id": "d3ck02", "status": "on-deck"}),
        # C3: a task ticked, expect it finished wherever it is
        ("- [x] 1.1.1  ~~done~~  ^66e5ty", {"_id": "66e5ty", "status": "finished"}),
    ],
)
def test_a_task_on_deck_keeps_its_id_and_says_nothing_else(line, expected):
    text = "## Projects\n\n1. **p**  ^p1\n\n## Goals — 2026Q3\n\n- 1.1  g  ^g1\n\n## On-deck tasks\n\n" + line
    task = parse_document(text)["tasks"][0]
    assert {k: task[k] for k in expected} == expected
    assert "goal" not in task
    assert "due_date" not in task


def test_a_sub_task_on_deck_hangs_under_the_task_above_it():
    # Test a task pasted down with its pieces, expect the pieces under it as
    # they are in a week
    text = (
        "## Projects\n\n1. **p**  ^p1\n\n## On-deck tasks\n\n"
        "- [ ] 1.1.1  a task  ^66e5ty\n  - [ ] a piece of it  ^bfvvj6\n"
    )
    tasks = {t["_id"]: t for t in parse_document(text)["tasks"]}
    assert tasks["bfvvj6"]["parent"] == "66e5ty"
    assert tasks["bfvvj6"]["status"] == "on-deck"


@pytest.mark.parametrize(
    "first, second, expected_message",
    [
        # Test a line whose id is in two places.  A thing is moved on deck or
        # to the wishlist by cutting it, and a copy left behind cannot be told
        # from a paste back up, so neither is guessed at
        # C1: a task in a week and on deck, expect the document refused naming
        # both places
        (
            "## Week of 2026-09-07\n\n- [ ] 1.1.1  a task  ^66e5ty\n",
            "## On-deck tasks\n\n- [ ] 1.1.1  a task  ^66e5ty\n",
            r"\^66e5ty is under the week of 2026-09-07 and under On-deck tasks",
        ),
        # C2: a goal in the period and on the wishlist, expect the same
        (
            "## Goals — 2026Q3\n\n- 1.1  g  ^g1\n",
            "## Wishlist goals\n\n- 1.1  g  ^g1\n",
            r"\^g1 is under Goals — 2026Q3 and under Wishlist goals",
        ),
        # C3: a task in two weeks, expect no refusal, since that is a roll
        (
            "## Week of 2026-09-14\n\n- [ ] 1.1.1  a task  ^66e5ty\n",
            "## Week of 2026-09-07\n\n- [ ] 1.1.1  a task  ^66e5ty\n",
            None,
        ),
    ],
)
def test_a_thing_is_in_one_place_at_a_time(first, second, expected_message):
    text = "## Projects\n\n1. **p**  ^p1\n\n## Goals — 2026Q3\n\n- 1.1  g  ^g1\n\n" + first + "\n" + second
    if expected_message is None:
        parse_document(text)
    else:
        with pytest.raises(DocumentError, match=expected_message):
            parse_document(text)


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
    # Test that moving a task between week headings is what moves its due
    # date, and that a task on deck has no week to be due in
    weekly = [t for t in read["tasks"] if t["_id"] != "d3ck01"]
    assert all(t["due_date"] == dt.date(2026, 9, 7) for t in weekly)


def test_something_typed_without_an_id_is_given_one(read):
    # Test that a person can type a new line and have it become a record.  Ids
    # are the one thing here that is not theirs to write.
    text = DOCUMENT.replace("- 1.2  ~~a fitting recipe~~  ^dab3ap", "- 1.2  a brand new goal")
    goals = parse_document(text)["goals"]
    new = next(g for g in goals if g["text"] == "a brand new goal")
    assert new["_id"] and new["_id"] not in DOCUMENT


COPIED = """# Mission control — Caden Myers

## Projects

1. **one**  ^p1

2. **two**  ^p1

## Goals — 2026fall

- 1.1  separate the srreal from the srfit  ^g1
- 1.2  add a few features  ^g1

## Week of 2026-09-14

- [ ] 1.1.1  a task  ^t1
- [ ] 1.1.2  a task copied from it  ^t1

## Archive

### Goals — 2026summer

- 1.1  ~~separate the srreal from the srfit~~  ^g1  (→ rolled to 2026fall)
"""


@pytest.mark.parametrize(
    "kind, expected_texts, collection",
    [
        # Test how the reader handles two lines that carry the same id, which
        # is what somebody leaves behind when they copy a line to make a new
        # one and forget to take the id off.  The reader cannot tell which of
        # the two was there first -- that needs the collections -- so it keeps
        # both, gives the second an id of its own, and notes the pair for
        # changes to settle.
        # C1: two goals share an id, expect both read, the second under a new
        # id, and the pair noted as goals
        ("goals", ["separate the srreal from the srfit", "add a few features"], "mc_goals"),
        # C2: two tasks share an id, expect the same for tasks
        ("tasks", ["a task", "a task copied from it"], "mc_tasks"),
        # C3: two projects share an id, expect the same for projects
        ("projects", ["one", "two"], "mc_projects"),
    ],
)
def test_two_lines_sharing_an_id_are_both_read(kind, expected_texts, collection):
    read = parse_document(COPIED)
    records = read[kind]
    assert [r.get("text") or r.get("name") for r in records] == expected_texts
    ids = [r["_id"] for r in records]
    assert len(set(ids)) == len(ids)
    noted = [c for c in read["copied"] if c["collection"] == collection]
    assert len(noted) == 1
    assert noted[0]["id"] == ids[0]
    assert noted[0]["copy"] == ids[1]


@pytest.mark.parametrize(
    "line, expected_message",
    [
        # Test a line copied, id and all, to where a line is of another kind,
        # which no collection can hold and no guess should settle.  Expect the
        # document refused with a message naming the line, both kinds and what
        # to do, rather than the sync falling over
        # C1: a task's id on a goal line of a later period
        (
            "## Goals — 2026Q4\n\n- 1.1  a task  ^66e5ty",
            r"line \d+: \^66e5ty is the id of a task written earlier.*read as a goal.*Take the id off",
        ),
        # C2: a goal copied into a week, where a line is a task
        (
            "## Week of 2026-09-14\n\n- [ ] 1.1.1  get clean PDFs  ^a8s8ec",
            r"line \d+: \^a8s8ec is the id of a goal written earlier.*read as a task",
        ),
    ],
)
def test_a_line_copied_to_where_it_is_another_kind_is_refused(line, expected_message):
    text = DOCUMENT.split("## On-deck tasks")[0] + line + "\n"
    with pytest.raises(DocumentError, match=expected_message):
        parse_document(text)


def test_a_rolled_goal_in_the_archive_is_not_taken_for_a_copy():
    # Test that a goal shown in the archive under the same id as its live line
    # is not noted as a copy.  A goal that rolled appears in the period it left
    # and in the period it is in, under one id on purpose, and the archive only
    # mentions what it shows.
    # Expect the live line to keep the id and the archive line not to be noted.
    read = parse_document(COPIED)
    assert "g1" in read["mentioned"]
    assert read["goals"][0]["_id"] == "g1"
    assert [c["id"] for c in read["copied"] if c["collection"] == "mc_goals"] == ["g1"]


@pytest.mark.parametrize(
    "line, expected_message",
    [
        # Test that a line which cannot be placed says so, naming the line,
        # rather than being stored somewhere wrong
        # C1: a task under no goal that exists
        ("- [ ] 9.9.9  orphan task  ^zzz999", "there is no goal 9.9"),
        # C2: a task with nothing above it to belong to, and no number saying
        # which goal it is of.  An indent alone does not place it, since there
        # is nothing there to indent it under.
        ("- [ ] no number  ^zzz999", "needs a number"),
        ("  - [ ] indented under nothing  ^zzz999", "needs a number"),
        # C3: a task numbered like a goal, expect a refusal naming the number
        # and the three-part shape, not a task hung under the project
        ("- [ ] 1.1  numbered like a goal  ^zzz999", r"the number 1.1 names a goal or a project.*such as 1.1.1"),
        # C4: a task numbered like a project, expect the same refusal
        ("- [ ] 1  numbered like a project  ^zzz999", r"the number 1 names a goal or a project.*such as 1.1.1"),
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
    assert len(parse_document(text)["goals"]) == 3


@pytest.mark.parametrize(
    "line, expected_text, expected_status",
    [
        # Test the notes a render writes at the end of a goal line, which say
        # what became of the goal and are not part of its words
        # C1: one note, expect the words and the id read without it
        ("- 1.1  get clean PDFs  ^g1  (carried since 2026Q2)", "get clean PDFs", "active"),
        # C2: two notes, as a render writes for a goal carried from an earlier
        # period and finished in this one, expect both left out and the id
        # still read, rather than the first note and the id becoming the words
        (
            "- 1.1  ~~get clean PDFs~~  ^g1  (carried since 2026Q2)  (finished 2026-09-12)",
            "get clean PDFs",
            "finished",
        ),
        # C3: a parenthesis somebody typed, expect it kept as part of the words
        ("- 1.1  get clean PDFs (by Friday)  ^g1", "get clean PDFs (by Friday)", "active"),
    ],
)
def test_the_notes_at_the_end_of_a_goal_are_not_its_words(line, expected_text, expected_status):
    text = "## Projects\n\n1. **p**  ^p1\n\n## Goals — 2026Q3\n\n" + line
    goal = parse_document(text)["goals"][0]
    assert goal["_id"] == "g1"
    assert goal["text"] == expected_text
    assert goal["status"] == expected_status


def test_a_goal_carried_and_then_finished_reads_back_as_itself():
    # Test the round trip of a goal that was carried from an earlier period and
    # finished in this one, which a render writes with two notes.  Expect it
    # read back under its own id, rather than as a new goal whose words hold
    # the first note
    carried_and_finished = dict(GOALS[0], status="finished", end_date="2026-09-12")
    builder = MissionControlBuilder.__new__(MissionControlBuilder)
    builder.gtx = {"mc_projects": PROJECTS, "mc_goals": [carried_and_finished], "mc_tasks": []}
    document = "\n".join(builder.documents()["pliu"])
    # the build wraps a long line, so the notes are looked for one at a time
    assert "carried since 2026Q2" in document
    assert "(finished 2026-09-12)" in document
    read = parse_document(document)["goals"]
    assert [g["_id"] for g in read] == [GOALS[0]["_id"]]
    assert read[0]["text"] == GOALS[0]["text"]
    assert read[0]["status"] == "finished"


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


@pytest.mark.parametrize(
    "under_the_project, expected",
    [
        # Test how what a project is about is written.  People type a
        # paragraph under the project without labelling it, so that is what a
        # bare line means, and an explicit label works too.
        # C1: prose with no label, which is what people type
        ("   it is about the friction of things", "it is about the friction of things"),
        # C2: the same with a label, for anybody who prefers to be explicit
        ("   description: it is about the friction of things", "it is about the friction of things"),
        # C3: a paragraph wrapped over lines, expect it joined rather than the
        # last line winning
        ("   it is about the friction\n   of things", "it is about the friction of things"),
    ],
)
def test_what_a_project_is_about_is_read(under_the_project, expected):
    text = f"## Projects\n\n1. **p**  ^p1\n{under_the_project}\n"
    assert parse_document(text)["projects"][0]["project_description"] == expected


def test_the_labelled_lines_are_not_mistaken_for_prose():
    # Test that the two labelled lines keep their meaning rather than being
    # swallowed into the description
    text = (
        "## Projects\n\n1. **p**  ^p1\n"
        "   deliverable: submit it\n"
        "   with: sgeorge\n"
        "   and this is what it is about\n"
    )
    project = parse_document(text)["projects"][0]
    assert project["project_deliverable"] == "submit it"
    assert project["collaborators"] == ["sgeorge"]
    assert project["project_description"] == "and this is what it is about"


def test_a_project_with_nothing_written_under_it_has_no_description():
    # Test that a project nobody has described does not gain an empty one
    project = parse_document("## Projects\n\n1. **p**  ^p1\n")["projects"][0]
    assert "project_description" not in project


HEAD = "## Projects\n\n1. **p**  ^p1\n\n## Goals — 2026Q3\n\n- 1.1  g  ^g1\n\n## Week of 2026-09-07\n\n"


@pytest.mark.parametrize(
    "indent",
    [
        # Test that any indent puts a task under the one above it.  Nobody
        # counts spaces while typing in a meeting, so what matters is deeper
        # or not, never how much deeper.
        # C1: one space, which is what a hurried hand produces
        " ",
        # C2: two, which is what the renderer writes
        "  ",
        # C3: three, from a stray keypress
        "   ",
        # C4: four, which an editor may insert
        "    ",
        # C5: a tab
        "\t",
    ],
)
def test_any_indent_makes_a_sub_task(indent):
    text = HEAD + "- [ ] 1.1.1  a task  ^t1\n" + f"{indent}- [ ] a sub task  ^t2\n"
    tasks = {t["_id"]: t for t in parse_document(text)["tasks"]}
    assert tasks["t2"]["parent"] == "t1"
    assert tasks["t2"]["goal"] == tasks["t1"]["goal"]


def test_sub_tasks_at_the_same_indent_are_siblings():
    # Test that two lines indented the same both hang off the task above them
    text = HEAD + "- [ ] 1.1.1  a task  ^t1\n - [ ] one  ^t2\n - [ ] two  ^t3\n"
    tasks = {t["_id"]: t for t in parse_document(text)["tasks"]}
    assert tasks["t2"]["parent"] == "t1"
    assert tasks["t3"]["parent"] == "t1"


def test_going_deeper_and_back_out_again_follows_the_indent():
    # Test that an indent that grows and shrinks nests and unnests, however
    # many spaces somebody happened to use
    text = (
        HEAD
        + "- [ ] 1.1.1  a task  ^t1\n"
        + "  - [ ] under it  ^t2\n"
        + "      - [ ] under that  ^t3\n"
        + "  - [ ] back out again  ^t4\n"
        + "- [ ] 1.1.2  another task  ^t5\n"
    )
    tasks = {t["_id"]: t for t in parse_document(text)["tasks"]}
    assert tasks["t2"]["parent"] == "t1"
    assert tasks["t3"]["parent"] == "t2"
    assert tasks["t4"]["parent"] == "t1"
    assert "parent" not in tasks["t5"]


def test_a_project_typed_into_a_document_is_named_by_its_name():
    # Test that typing a project in gives it the same readable id the adder
    # helper would give it.  A project id is the one id somebody reads and
    # types, so a drawn one would make the collections hard to work with
    text = DOCUMENT.replace("1. **nanodiamond-pdf**  ^ak-nano", "1. **Nanodiamond PDF**")
    project = parse_document(text)["projects"][0]
    assert project["_id"] == "nanodiamond-pdf"


def test_a_project_does_not_take_an_id_another_one_has():
    # Test that a name somebody else has used already is numbered rather than
    # written over, since two people can name a project the same thing
    text = DOCUMENT.replace("1. **nanodiamond-pdf**  ^ak-nano", "1. **Nanodiamond PDF**")
    project = parse_document(text, taken={"nanodiamond-pdf"})["projects"][0]
    assert project["_id"] == "nanodiamond-pdf-2"


@pytest.mark.parametrize(
    "heading, expected_status",
    [
        # Test which heading holds a goal back.  On-deck and the backburner
        # held goals before on-deck came to hold tasks, so a document written
        # then still reads, into the wishlist
        # C1: the heading the renderer writes now
        ("Wishlist goals", "wishlist"),
        # C2: what it used to write
        ("Wishlist", "wishlist"),
        ("On-deck", "wishlist"),
        ("Backburner", "wishlist"),
        # C3: written in whatever case somebody typed
        ("wishlist GOALS", "wishlist"),
    ],
)
def test_a_goal_is_held_by_whichever_heading_it_is_under(heading, expected_status):
    document = (
        "# Mission control — Adib Kabir\n\n## Projects\n\n1. **a project**  ^p1\n\n"
        f"## {heading}\n\n- 1.1  a held goal  ^g1\n"
    )
    goal = next(g for g in parse_document(document)["goals"] if g["_id"] == "g1")
    assert goal["status"] == expected_status


HELD_DOCUMENT = """# Mission control — Adib Kabir

## Projects

1. **a project**  ^p1

## Goals — 2026fall

- 1.1  a goal of the project  ^g1

## Wishlist goals

- an idea nobody has taken on
- 1.2  one pasted down with its number  ^g2
"""


@pytest.mark.parametrize(
    "text",
    [
        # Test that a line on the wishlist says nothing about which project it
        # is of.  An idea need not be numbered, and a goal pasted down keeps
        # the number it came with without the number being read: the numbers
        # of a period move, and the id already says which goal it is
        # C1: no number, expect no project read
        "an idea nobody has taken on",
        # C2: a number, expect no project read either
        "one pasted down with its number",
    ],
)
def test_a_wishlist_line_says_nothing_about_its_project(text):
    goal = next(g for g in parse_document(HELD_DOCUMENT)["goals"] if g["text"] == text)
    assert "project" not in goal
    assert goal["status"] == "wishlist"


BREAKDOWN = """# Mission control — Caden Myers

## Projects

1. **diffpy.cmi relaunch**  ^p1

## Wishlist goals

- [ ] 1. Relaunch with these from the wishlist:
  - [ ] XANESCalculator
  - [x] LJCalculator
- 1. Merge the ase adapter (please update the below, copied from the old MC)
"""


@pytest.mark.parametrize(
    "text, expected",
    [
        # Test a wishlist somebody wrote as a list with a list under it, which
        # is how anybody writes one down.  Every indented line used to be
        # passed over in silence, so a build would not write the document and
        # a sync would not store what was in it.
        # C1: the line the others hang under
        ("Relaunch with these from the wishlist:", {"parent": None, "status": "wishlist"}),
        # C2: a piece of it, which says which goal it is of by hanging off it
        # rather than by carrying a number
        ("XANESCalculator", {"parent": "the one above", "status": "wishlist"}),
        # C3: a piece somebody has ticked, which is done whatever section it
        # is in, the way a ticked task is
        ("LJCalculator", {"parent": "the one above", "status": "finished"}),
        # C4: a line ending in a parenthesis of its own, which is what
        # somebody typed and not the note a render writes there
        (
            "Merge the ase adapter (please update the below, copied from the old MC)",
            {"parent": None, "status": "wishlist"},
        ),
    ],
)
def test_a_held_thing_can_have_a_breakdown_under_it(text, expected):
    goals = {g["text"]: g for g in parse_document(BREAKDOWN)["goals"]}
    goal = goals[text]
    assert goal["status"] == expected["status"]
    if expected["parent"] is None:
        assert "parent" not in goal
    else:
        assert goal["parent"] == goals["Relaunch with these from the wishlist:"]["_id"]


def test_a_goal_of_the_period_still_needs_its_number():
    # Test that only the holding sections take a line with no number.  A goal
    # of the period is work somebody is doing, and which project it is of is
    # the thing that says who is doing it
    without = HELD_DOCUMENT.replace("- 1.1  a goal of the project  ^g1", "- a goal with no number")
    with pytest.raises(DocumentError, match="needs a number saying which project"):
        parse_document(without)
