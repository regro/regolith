"""Tests for the pieces the mission control tools share."""

import datetime as dt

import pytest

from regolith.mc import (
    ID_ALPHABET,
    ID_LENGTH,
    WIDTH,
    DocumentError,
    initials,
    logical_lines,
    next_period,
    period_key,
    period_of,
    project_id,
    short_id,
    struck,
    would_lose,
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


@pytest.mark.parametrize(
    "name, expected_initials",
    [
        # Test how a name is shortened for the front of a project id, which is
        # how the group has always shortened one
        # C1: a first name and a last, expect the first letter of each
        ("Adib Kabir", "ak"),
        # C2: middle names as well, expect them passed over rather than piled
        # up, so that Simon J. L. Billinge is sb
        ("Simon J. L. Billinge", "sb"),
        # C3: one name only, expect the one letter
        ("Prince", "p"),
        # C4: no name at all, expect nothing rather than an error
        ("", ""),
    ],
)
def test_initials_shorten_a_name_the_way_the_group_does(name, expected_initials):
    assert initials(name) == expected_initials


@pytest.mark.parametrize(
    "name, taken, prefix, expected_id",
    [
        # Test that a project id says whose project it is.  Group members name
        # their projects alike, so without that the second software
        # maintenance to be written down would be the first one numbered, and
        # neither id would say whose it was.
        # C1: a lead, expect their initials in front
        ("Software maintenance", (), "ak", "ak-software-maintenance"),
        # C2: nobody leading it, expect na in front, since it is nobody's
        # until somebody picks it up
        ("Software maintenance", (), "na", "na-software-maintenance"),
        # C3: the same name led by somebody else, expect no clash at all
        ("Software maintenance", ("ak-software-maintenance",), "sb", "sb-software-maintenance"),
        # C4: the same name led by the same person, expect it numbered
        (
            "Software maintenance",
            ("ak-software-maintenance",),
            "ak",
            "ak-software-maintenance-2",
        ),
        # C5: no prefix given, expect the name alone
        ("Software maintenance", (), None, "software-maintenance"),
    ],
)
def test_a_project_id_says_whose_project_it_is(name, taken, prefix, expected_id):
    assert project_id(name, taken, prefix) == expected_id


UCSB = {"fall": "10-01", "winter": "01-01", "spring": "04-01", "summer": "07-01"}


@pytest.mark.parametrize(
    "date, periods, expected_period, expected_next",
    [
        # Test which period a date falls in and which comes after it.  A group
        # says what its periods are called and when they start; the default is
        # semesters, since most universities are on them.
        # C1: the default semesters, in the autumn one
        (dt.date(2026, 9, 7), None, "2026fall", "2027spring"),
        # C2: the same date on a quarter system, where the autumn term has not
        # started yet
        (dt.date(2026, 9, 7), UCSB, "2026summer", "2026fall"),
        # C3: the last period of the year, where the next one is next year's
        (dt.date(2026, 11, 15), UCSB, "2026fall", "2027winter"),
        # C4: the first day of a period, which belongs to the period it starts
        (dt.date(2027, 1, 1), UCSB, "2027winter", "2027spring"),
        # C5: before the first period of the year begins, on a calendar whose
        # periods all start later, expect the last period of the year before
        (dt.date(2027, 2, 1), {"midyear": "06-01"}, "2026midyear", "2027midyear"),
    ],
)
def test_a_date_falls_in_the_period_a_group_says_it_does(date, periods, expected_period, expected_next):
    assert period_of(date, periods) == expected_period
    assert next_period(date, periods) == expected_next


def test_periods_sort_into_the_order_they_come_round():
    # Test that periods order by when they happen rather than by their names,
    # which do not agree: fall comes before spring in the alphabet and after
    # it in the year.  The archive and the current period both depend on this
    written = ["2026fall", "2026spring", "2026summer", "2026winter", "2027winter"]
    assert sorted(written, key=lambda p: period_key(p, UCSB)) == [
        "2026winter",
        "2026spring",
        "2026summer",
        "2026fall",
        "2027winter",
    ]


def test_a_period_written_some_other_way_still_sorts():
    # Test that a period from before a group settled its calendar does not
    # bring the ordering down, since documents already carry them
    assert period_key("2026Q3", UCSB) > period_key("2026fall", UCSB)


@pytest.mark.parametrize(
    "periods",
    [
        # Test that a calendar nobody can read says so, naming the period that
        # is wrong, rather than failing somewhere later.
        # C1: a date written the wrong way round
        {"fall": "01-40"},
        # C2: not a date at all
        {"fall": "the first of October"},
        # C3: nothing there
        {"fall": None},
    ],
)
def test_a_period_that_does_not_start_on_a_date_says_so(periods):
    with pytest.raises(DocumentError, match="not a date of the year"):
        period_of(dt.date(2026, 9, 7), periods)


BUILT = """# Mission control — Simon Billinge

## Projects

1. **a project**  ^p1

## Goals — 2026summer

- 1.1  a stored goal  ^g1

## Week of 2026-09-07

- [ ] 1.1.1  a stored task  ^t1

## On-deck

## Wishlist

## Archive
"""


@pytest.mark.parametrize(
    "typed, expected_lost",
    [
        # Test what a render would write over.  A render puts the collections
        # out over the document, so anything in the document that never
        # reached the collections is gone, and that is what this has to catch.
        # C1: nothing added, expect nothing lost
        (BUILT, []),
        # C2: a goal typed with no number, which a sync cannot store and so
        # never reaches the collections
        (
            BUILT.replace("- 1.1  a stored goal  ^g1", "- 1.1  a stored goal  ^g1\n- one I typed"),
            ["one I typed"],
        ),
        # C3: a task typed since the last sync
        (
            BUILT.replace("- [ ] 1.1.1  a stored task  ^t1", "- [ ] 1.1.1  a stored task  ^t1\n- [ ] and another"),
            ["and another"],
        ),
        # C4: a note left in the margin, which no section holds and so no
        # sync can store.  This is the one that cost Simon a morning's work
        (
            BUILT.replace("## On-deck", "remember to ask about the beamtime\n\n## On-deck"),
            ["remember to ask about the beamtime"],
        ),
        # C5: a line whose number and id changed but whose text did not, which
        # is an ordinary render and loses nothing
        (BUILT.replace("- 1.1  a stored goal  ^g1", "- 2.3  a stored goal  ^g1  (carried since 2026spring)"), []),
        # C6: a line struck through since the last sync, which says the same
        # thing and so is not lost, only unsaved
        (BUILT.replace("a stored goal", "~~a stored goal~~"), []),
    ],
)
def test_would_lose_finds_what_a_render_would_write_over(typed, expected_lost):
    assert would_lose(typed, BUILT) == expected_lost
