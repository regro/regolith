"""Tests for the pieces the mission control tools share."""

import pytest

from regolith.mc import (
    ID_ALPHABET,
    ID_LENGTH,
    WIDTH,
    logical_lines,
    project_id,
    short_id,
    struck,
    wrap,
)


@pytest.mark.parametrize(
    "text, status, expected",
    [
        # Test how a line is marked off.  Striking through is how the group has
        # always done it, so a rendered document does the same.
        # C1: finished, expect a strike through it
        ("Send the plot", "finished", "~~Send the plot~~"),
        # C2: still going, expect the text alone
        ("Send the plot", "active", "Send the plot"),
        # C3: dropped, expect the text alone, since a strike means finished
        ("Send the plot", "dropped", "Send the plot"),
    ],
)
def test_struck_marks_only_what_is_finished(text, status, expected):
    assert struck(text, status) == expected


def test_short_id_is_short_and_readable():
    # Test the shape of an id.  It sits beside every line of a document, so it
    # is short, and it avoids the characters that are read for one another so
    # it can be said aloud and typed back.
    _id = short_id()
    assert len(_id) == ID_LENGTH
    assert set(_id) <= set(ID_ALPHABET)
    assert not set(_id) & set("lo01")


@pytest.mark.parametrize(
    "taken, length",
    [
        # Test that an id already in use is never handed out again
        # C1: everything but one id of length one is taken, expect the last one
        (set(ID_ALPHABET) - {"k"}, 1),
        # C2: nothing is taken, expect any id
        (set(), 1),
    ],
)
def test_short_id_avoids_what_is_taken(taken, length):
    assert short_id(taken, length=length) not in taken


def test_short_ids_do_not_repeat():
    # Test that ids drawn together are distinct, which is what makes them
    # usable as the identity of a line
    ids = set()
    for _ in range(500):
        ids.add(short_id(ids))
    assert len(ids) == 500


LONG_TASK = (
    "- [ ] 1.1.1  build an AI campaign using simple models such as random forest "
    "to predict which samples are worth measuring  ^t1"
)


@pytest.mark.parametrize(
    "line, expected",
    [
        # Test how a rendered line is broken to fit an editor that does not
        # fold.  What carries on from a line is indented two further than it,
        # which is what tells a reader, and the parser, that it is not new.
        # C1: a line that already fits, expect it written as it is
        ("- 1.1  a short goal  ^g1", ["- 1.1  a short goal  ^g1"]),
        # C2: a long task, expect it broken with the rest indented under it
        (
            LONG_TASK,
            [
                "- [ ] 1.1.1  build an AI campaign using simple models such as random forest to",
                "  predict which samples are worth measuring  ^t1",
            ],
        ),
        # C3: a long sub task, expect the rest indented two further than it is
        (
            "  - [x] ~~a sub task whose text runs on well past the width a person can read " "comfortably~~  ^t2",
            [
                "  - [x] ~~a sub task whose text runs on well past the width a person can read",
                "    comfortably~~  ^t2",
            ],
        ),
        # C4: a heading longer than the width, expect it left alone, since a
        # heading broken in two is no longer a heading
        (
            "# Mission control — Somebody With A Name That Runs On Much Longer Than It Needs To",
            ["# Mission control — Somebody With A Name That Runs On Much Longer Than It Needs To"],
        ),
        # C5: the line naming a project, expect it left alone, since what is
        # indented under a project is the project's description
        (
            "1. **a project whose name is far longer than anybody would want to type twice " "over**  ^p1",
            ["1. **a project whose name is far longer than anybody would want to type twice " "over**  ^p1"],
        ),
        # C6: one word longer than the width, expect it left whole rather than
        # broken, since a url or an id split in two is worse than a long line
        (
            "- 1.1  see https://example.com/a/path/that/is/far/longer/than/the/width/we/wrap/at/x  ^g1",
            [
                "- 1.1  see",
                "  https://example.com/a/path/that/is/far/longer/than/the/width/we/wrap/at/x",
                "  ^g1",
            ],
        ),
    ],
)
def test_wrap_breaks_a_line_where_it_can_be_joined_back(line, expected):
    assert wrap(line) == expected


def test_wrap_writes_nothing_wider_than_the_width():
    # Test the promise the width makes, over text with no break near it
    written = wrap("- 1.1  " + " ".join(["word"] * 60) + "  ^g1")
    assert max(len(line) for line in written) <= WIDTH


@pytest.mark.parametrize(
    "document, expected",
    [
        # Test which lines are read as the rest of the line above them.  A line
        # indented further than the line above, that starts nothing of its own,
        # carries it on.  This is what wrap writes and what somebody typing a
        # paragraph under a task does by hand.
        # C1: a line broken in two, expect one line back, numbered from where
        # it started
        (
            "- [ ] 1.1.1  a task broken\n  over two lines  ^t1\n",
            [(1, "- [ ] 1.1.1  a task broken over two lines  ^t1")],
        ),
        # C2: a sub task under a task, expect two lines, since a sub task
        # starts something of its own
        (
            "- [ ] 1.1.1  a task  ^t1\n  - [ ] a sub task  ^t2\n",
            [(1, "- [ ] 1.1.1  a task  ^t1"), (2, "  - [ ] a sub task  ^t2")],
        ),
        # C3: a description under the line naming a project, expect two lines,
        # since that is what the project is about and not the rest of its name
        (
            "1. **a project**  ^p1\n   what it is about\n",
            [(1, "1. **a project**  ^p1"), (2, "   what it is about")],
        ),
        # C4: a blank line between the two, expect two lines, since a paragraph
        # somebody started is not the rest of the one before it
        (
            "   deliverable: a paper\n\n   what it is about\n",
            [(1, "   deliverable: a paper"), (2, ""), (3, "   what it is about")],
        ),
        # C5: a line indented the same as the one above, expect two lines
        (
            "   deliverable: a paper\n   with: ascopatz\n",
            [(1, "   deliverable: a paper"), (2, "   with: ascopatz")],
        ),
    ],
)
def test_logical_lines_joins_what_was_broken(document, expected):
    assert logical_lines(document) == expected


@pytest.mark.parametrize(
    "name, taken, expected_id",
    [
        # Test the id a project is given when somebody names one.  It is the
        # one id here that a person reads and types, naming the project in a
        # lister and in whatever refers to it later, so it is made from the
        # name rather than drawn at random.
        # C1: a plain name, expect it in lower case with hyphens
        ("Shock compressed WC", (), "shock-compressed-wc"),
        # C2: a name already used by another project, expect it numbered,
        # since two projects can be called the same thing
        ("Shock compressed WC", ("shock-compressed-wc",), "shock-compressed-wc-2"),
        # C3: a name used twice already, expect the next number
        (
            "Shock compressed WC",
            ("shock-compressed-wc", "shock-compressed-wc-2"),
            "shock-compressed-wc-3",
        ),
        # C4: a name of punctuation, which makes no id at all, expect a short
        # id rather than nothing
        ("!!!", (), None),
    ],
)
def test_project_id_is_made_from_the_name(name, taken, expected_id):
    made = project_id(name, taken)
    if expected_id is None:
        assert len(made) == ID_LENGTH and set(made) <= set(ID_ALPHABET)
    else:
        assert made == expected_id
