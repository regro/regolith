"""Tests for turning a read document into writes and drops."""

import datetime as dt

import pytest

from regolith.mc import adopt, changes, settled_status

TODAY = dt.date(2026, 9, 20)


def read(**kw):
    """Return a line as the parser hands it over."""
    base = {"_id": "g1", "project": "p1", "period": "2026Q3", "text": "a goal", "status": "active"}
    base.update(kw)
    return base


def stored(**kw):
    """Return a record as the collection holds it."""
    base = {
        "_id": "g1",
        "project": "p1",
        "period": "2026Q3",
        "first_period": "2026Q3",
        "text": "a goal",
        "status": "active",
    }
    base.update(kw)
    return base


def parsed(projects=(), goals=(), tasks=()):
    return {"person": "p", "projects": list(projects), "goals": list(goals), "tasks": list(tasks)}


def existing(projects=(), goals=(), tasks=()):
    return {
        "mc_projects": {p["_id"]: p for p in projects},
        "mc_goals": {g["_id"]: g for g in goals},
        "mc_tasks": {t["_id"]: t for t in tasks},
    }


@pytest.mark.parametrize(
    "read_status, existing_status, expected",
    [
        # Test what a status becomes after a document is read.  A document does
        # not say everything a status does, so reading one must not flatten
        # what it cannot express.
        # C1: written plainly, and it was proposed, expect it stays proposed
        ("active", "proposed", "proposed"),
        # C2: written plainly, and it was active, expect it stays active
        ("active", "active", "active"),
        # C3: written plainly, and it was held back, expect it has come back
        ("active", "backburner", "active"),
        # C4: struck through, expect finished whatever it was
        ("finished", "proposed", "finished"),
        # C5: written under a holding heading, expect it is held
        ("backburner", "active", "backburner"),
        ("wishlist", "active", "wishlist"),
        # C6: newly typed, expect the default rather than an error
        ("active", None, "active"),
    ],
)
def test_a_status_survives_being_read(read_status, existing_status, expected):
    assert settled_status(read_status, existing_status) == expected


def test_something_newly_typed_is_written():
    # Test that a line somebody typed becomes a record, which is what makes
    # the document worth typing into
    writes, drops = changes(
        parsed(goals=[read(_id="new1", text="typed in the meeting")]), "pliu", existing(), today=TODAY
    )
    assert [g["_id"] for g in writes["mc_goals"]] == ["new1"]
    assert writes["mc_goals"][0]["first_period"] == "2026Q3"
    assert drops["mc_goals"] == []


def test_a_line_taken_out_is_dropped_rather_than_deleted():
    # Test the rule that makes a wrecked document survivable: what is gone
    # from it is marked, not removed
    writes, drops = changes(parsed(), "pliu", existing(goals=[stored()]), today=TODAY)
    assert drops["mc_goals"] == ["g1"]
    assert writes["mc_goals"] == []


@pytest.mark.parametrize(
    "field, first_field, first_value",
    [
        # Test that where something started is written once and never again,
        # since that is what says how long it has been carried
        # C1: a goal keeps the period it was first set in
        ("period", "first_period", "2026Q1"),
    ],
)
def test_where_something_started_is_not_rewritten(field, first_field, first_value):
    was = stored(**{first_field: first_value})
    writes, _ = changes(parsed(goals=[read(**{field: "2026Q3"})]), "pliu", existing(goals=[was]), today=TODAY)
    assert writes["mc_goals"][0][first_field] == first_value
    assert writes["mc_goals"][0][field] == "2026Q3"


def test_finishing_something_dates_it_once():
    # Test that closing a goal records when, and that reading the document
    # again does not move the date
    was = stored(status="active")
    writes, _ = changes(parsed(goals=[read(status="finished")]), "pliu", existing(goals=[was]), today=TODAY)
    assert writes["mc_goals"][0]["end_date"] == TODAY
    already = writes["mc_goals"][0]
    writes, _ = changes(
        parsed(goals=[read(status="finished")]), "pliu", existing(goals=[already]), today=dt.date(2026, 12, 25)
    )
    assert writes["mc_goals"][0]["end_date"] == TODAY


@pytest.mark.parametrize(
    "person, expected_lead",
    [
        # Test that the lead is whoever's document a project is written in,
        # which is what makes moving a block between files an assignment
        # C1: somebody's document, expect them
        ("pliu", "pliu"),
        # C2: the unassigned document, expect no lead at all
        (None, None),
    ],
)
def test_the_lead_is_whose_document_it_is(person, expected_lead):
    project = {"_id": "p1", "name": "a project", "status": "active"}
    writes, _ = changes(parsed(projects=[project]), person, existing(), today=TODAY)
    assert writes["mc_projects"][0].get("lead") == expected_lead


def test_a_line_whose_id_was_lost_finds_its_record_again():
    # Test the likeliest damage to a document: an id gone from a line that is
    # otherwise unchanged.  It must not store a second copy and drop the first.
    was = stored(_id="realid", text="a goal")
    writes, drops = changes(
        parsed(goals=[read(_id="mintedid", text="a goal")]), "pliu", existing(goals=[was]), today=TODAY
    )
    assert [g["_id"] for g in writes["mc_goals"]] == ["realid"]
    assert drops["mc_goals"] == []


def test_two_lines_that_read_the_same_do_not_take_the_same_record():
    # Test that matching on text hands a record to one line only, so typing a
    # second line saying the same thing makes a second record
    was = stored(_id="realid", text="a goal")
    writes, _ = changes(
        parsed(goals=[read(_id="realid", text="a goal"), read(_id="other", text="a goal")]),
        "pliu",
        existing(goals=[was]),
        today=TODAY,
    )
    assert sorted(g["_id"] for g in writes["mc_goals"]) == ["other", "realid"]


def test_adopting_leaves_something_genuinely_new_alone():
    # Test that text matching does not swallow a new line that happens to be
    # near an old one
    read_line = {"_id": "minted", "text": "something else"}
    assert adopt(read_line, {"realid": {"_id": "realid", "text": "a goal"}}, set()) == {}
    assert read_line["_id"] == "minted"
