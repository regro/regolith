"""Tests for adding a project to mission control from the command
line."""

import copy
import os

import pytest

from regolith.database import connect
from regolith.main import main
from regolith.mc import slug
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile


@pytest.mark.parametrize(
    "name, expected_id",
    [
        # Test the id a project name is given, since it is what gets typed and
        # read aloud when referring to the project
        # C1: words, expect them joined by hyphens
        ("shock compressed WC", "shock-compressed-wc"),
        # C2: punctuation somebody typed, expect it gone
        ("WC/diamond: texture!", "wc-diamond-texture"),
        # C3: hyphens already there, expect them kept and not doubled
        ("wc-diamond  texture", "wc-diamond-texture"),
        # C4: nothing usable, expect nothing, so a made up id is used instead
        ("!!!", ""),
    ],
)
def test_a_project_name_becomes_an_id_worth_typing(name, expected_id):
    assert slug(name) == expected_id


@pytest.mark.parametrize(
    "args, expected_in_output",
    [
        # Test adding a project, which is the moment in a conversation when
        # writing one down should cost nothing
        # C1: a project nobody leads yet, expect it called unassigned
        (["helper", "a_mcproject", "a new idea"], "unassigned"),
        # C2: a project with a lead, expect it assigned to them
        (["helper", "a_mcproject", "a led idea", "-l", "sbillinge"], "to sbillinge"),
    ],
)
def test_adding_a_project_says_whose_it_is(args, expected_in_output, make_db, capsys):
    os.chdir(make_db)
    main(args)
    assert expected_in_output in capsys.readouterr().out


def test_a_project_is_stored_with_what_was_given(make_db):
    # Test that what the command line carries reaches the collection, and that
    # what it does not carry is left out rather than stored empty
    os.chdir(make_db)
    main(
        [
            "helper",
            "a_mcproject",
            "grain boundaries",
            "-l",
            "sbillinge",
            "-w",
            "ascopatz",
            "afriend",
            "-g",
            "dmref15",
            "--pi",
            "sbillinge",
            "-d",
            "a short paper",
            "--begin-date",
            "2026-09-01",
        ]
    )
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        project = rc.client.get("mc_projects", "grain-boundaries")
    assert project["lead"] == "sbillinge"
    assert project["collaborators"] == ["ascopatz", "afriend"]
    assert project["grants"] == ["dmref15"]
    assert project["project_deliverable"] == "a short paper"
    assert project["status"] == "proposed"
    assert "project_description" not in project


def test_adding_a_project_that_is_already_there_says_how_to_pick_another(make_db):
    # Test that a clashing id is reported with what to do about it, rather
    # than overwriting the project that is already there
    os.chdir(make_db)
    main(["helper", "a_mcproject", "clash test project"])
    with pytest.raises(ValueError, match="already a project"):
        main(["helper", "a_mcproject", "clash test project"])


def test_a_status_that_is_not_one_of_them_lists_the_ones_that_are(make_db):
    # Test that a status outside the vocabulary says which are allowed
    os.chdir(make_db)
    with pytest.raises(ValueError, match="should be one of"):
        main(["helper", "a_mcproject", "bad status project", "-s", "nonsense"])


@pytest.mark.parametrize(
    "given_id, expected_id",
    [
        # Test that an id given by hand is put in the form ids now take, since
        # underscores in them are being retired
        # C1: underscores, expect hyphens
        ("sg_shock_compressed_wc", "sg-shock-compressed-wc"),
        # C2: upper case, expect lower
        ("AB-Upper-Case", "ab-upper-case"),
        # C3: already in the right form, expect it unchanged
        ("cd-already-fine", "cd-already-fine"),
    ],
)
def test_an_id_given_by_hand_is_put_in_the_form_ids_take(given_id, expected_id, make_db):
    os.chdir(make_db)
    main(["helper", "a_mcproject", f"project for {given_id}", "--id", given_id])
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        assert rc.client.get("mc_projects", expected_id) is not None
