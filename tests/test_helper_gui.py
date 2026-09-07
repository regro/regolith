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
