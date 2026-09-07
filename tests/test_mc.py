"""Tests for the pieces the mission control tools share."""

import pytest

from regolith.mc import ID_ALPHABET, ID_LENGTH, short_id, struck


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
