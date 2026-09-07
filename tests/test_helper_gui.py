"""Tests for what the helpers promise the graphical front end.

helper_gui builds a page of fields from each helper's arguments, and it
cannot be run here: it needs a display, and wxPython is not installed on
every machine the suite runs on.  So what it needs of an argument is
checked directly, which is what these do.
"""

import argparse

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
        # C3: a target still listed with underscores, typed as it is listed
        ("l_todo", "l_todo"),
        # C4: that one typed with hyphens
        ("l-todo", "l_todo"),
        # C5: a name that is no target at all, expect it handed back so that
        # whoever asked can say so
        ("no-such-helper", "no-such-helper"),
    ],
)
def test_a_target_is_found_however_it_is_spelled(typed, expected_target):
    assert HELPERS.canonical(typed) == expected_target
    assert (typed in HELPERS) == (expected_target in HELPERS)
