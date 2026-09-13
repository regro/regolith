"""Tests for what the helpers promise the graphical front end.

helper_gui builds a page of fields from each helper's arguments, and it
cannot be run here: it needs a display, and wxPython is not installed on
every machine the suite runs on.  So what it needs of an argument is
checked directly, which is what these do.
"""

import argparse
import pathlib
import tomllib

import pytest

from regolith.helper import HELPERS


def parser_for(target):
    """Return a plain parser carrying one helper's arguments.

    Parameters
    ----------
    target : str
        The name of the helper, as the command line takes it.

    Returns
    -------
    argparse.ArgumentParser
        A parser the helper has added its arguments to.
    """
    parser = argparse.ArgumentParser(prog=target)
    # the registry resolves the import when it is asked for the helper
    HELPERS[target][1](parser)
    return parser


def test_every_script_the_package_installs_is_there():
    # Test that script-files names files that exist.  setuptools installs what
    # it is given without checking, so a script renamed on one line and not
    # the other goes missing from the install rather than failing to build
    root = pathlib.Path(__file__).resolve().parent.parent
    listed = tomllib.loads((root / "pyproject.toml").read_text())["tool"]["setuptools"]["script-files"]
    missing = [name for name in listed if not (root / name).is_file()]
    assert missing == []


def test_the_old_helper_gui_name_still_runs():
    # Test that helper_gui keeps working while people move to helper-gui.  It
    # is what anybody who has used regolith has in their fingers, and a
    # command that stops existing is a worse way to learn of a rename than a
    # line of output
    root = pathlib.Path(__file__).resolve().parent.parent
    old = (root / "scripts" / "helper_gui").read_text()
    assert "helper-gui" in old
    assert "from regolith.helper_gui_main import main" in old


def test_the_targets_are_listed_in_the_order_they_are_read_in():
    # Test the order the helper GUI shows, which is the order of the registry.
    # It is a list somebody reads down to find the helper they want, so it is
    # grouped by what the helpers do and sorted within each group.  Adding one
    # in the wrong place is how it stopped being either
    listed = list(HELPERS)
    groups = {"l-": [], "a-": [], "f-": [], "u-": []}
    unprefixed = []
    for name in listed:
        for prefix in groups:
            if name.startswith(prefix):
                groups[prefix].append(name)
                break
        else:
            unprefixed.append(name)
    for prefix, names in groups.items():
        assert names == sorted(names), f"the {prefix} helpers are not in order"
        # each group is together rather than scattered through the list
        where = [listed.index(name) for name in names]
        assert where == list(range(where[0], where[0] + len(where))), f"the {prefix} helpers are not together"
    # and the groups come in the order somebody works in: find it, add it,
    # finish it, change it
    assert [listed.index(groups[p][0]) for p in ("l-", "a-", "f-", "u-")] == sorted(
        listed.index(groups[p][0]) for p in ("l-", "a-", "f-", "u-")
    )


def test_every_target_is_spelled_with_hyphens():
    # Test that no target has an underscore in it.  argparse has spelled a
    # user-facing name with hyphens since forever, and regolith followed it
    # for arguments and not for the targets beside them
    assert [name for name in HELPERS if "_" in name] == []


@pytest.mark.parametrize("target", sorted(HELPERS))
def test_no_argument_is_labelled_with_a_tuple(target):
    # Test that no argument gives gooey a metavar it cannot make a label out
    # of.  Gooey labels each field with "action.metavar or action.dest", and
    # hands that to wx.StaticText, which takes a string: a tuple metavar, which
    # argparse allows for an argument taking several values, brings the whole
    # window down before it opens with a TypeError naming neither the helper
    # nor the argument
    for action in parser_for(target)._actions:
        assert not isinstance(action.metavar, tuple), (
            f"{target} labels {action.dest} with a tuple. Give it no metavar, or "
            f"one string, so that the helper GUI can label the field."
        )


@pytest.mark.parametrize(
    "typed, expected_target",
    [
        # Test that a target is found however it is spelled.  Targets face the
        # user with hyphens now, the way argparse has always spelled an
        # argument, and the underscored spelling keeps working so that nobody
        # has to retype an alias.
        # C1: the name as it is listed
        ("mc-sync", "mc-sync"),
        # C2: the same target with underscores
        ("mc_sync", "mc-sync"),
        # C3: another target, typed the way it is listed
        ("l-todo", "l-todo"),
        # C4: that one typed the way it used to be spelled
        ("l_todo", "l-todo"),
        # C5: a name that is no target at all, expect it handed back so that
        # whoever asked can say so
        ("no-such-helper", "no-such-helper"),
    ],
)
def test_a_target_is_found_however_it_is_spelled(typed, expected_target):
    assert HELPERS.canonical(typed) == expected_target
    assert (typed in HELPERS) == (expected_target in HELPERS)
