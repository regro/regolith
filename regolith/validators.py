"""Validators and convertors for regolith input."""
import re

def noop(x):
    """Does nothing, just returns the input."""
    return x


def is_int(x):
    """Tests if something is an integer"""
    return isinstance(x, int)


def always_true(x):
    """Returns True"""
    return True


def always_false(x):
    """Returns False"""
    return False


def is_bool(x):
    """Tests if something is a boolean"""
    return isinstance(x, bool)


_FALSES = frozenset(['', '0', 'n', 'f', 'no', 'none', 'false'])


def to_bool(x):
    """"Converts to a boolean in a semantically meaningful way."""
    if isinstance(x, bool):
        return x
    elif isinstance(x, string_types):
        return False if x.lower() in _FALSES else True
    else:
        return bool(x)


def ensure_string(x):
    """Returns a string if x is not a string, and x if it already is."""
    if isinstance(x, string_types):
        return x
    else:
        return str(x)


DEFAULT_VALIDATORS = {
    }