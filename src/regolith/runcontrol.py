"""Run Control object for regolith."""

from __future__ import print_function

import io
import json
import os
from collections.abc import Hashable, Iterable, Mapping
from pprint import pformat
from warnings import warn

from regolith.database import connect
from regolith.validators import DEFAULT_VALIDATORS, always_true, noop

FORBIDDEN_NAMES = frozenset(["del", "global"])


def warn_forbidden_name(forname, inname=None, rename=None):
    """Warns the user that a forbidden name has been found."""
    msg = "found forbidden name {0!r}".format(forname)
    if inname is not None:
        msg += " in {0!r}".format(inname)
    if rename is not None:
        msg += ", renaming to {0!r}".format(rename)
    warn(msg, RuntimeWarning)


def ensuredirs(f):
    """For a file path, ensure that its directory path exists."""
    d = os.path.split(f)[0]
    if not os.path.isdir(d):
        os.makedirs(d)


def touch(filename):
    """Opens a file and updates the mtime, like the posix command of the
    same name."""
    with io.open(filename, "a"):
        os.utime(filename, None)


def exec_file(filename, glb=None, loc=None):
    """A function equivalent to the Python 2.x execfile statement."""
    with io.open(filename, "r") as f:
        src = f.read()
    exec(compile(src, filename, "exec"), glb, loc)


#
# Run Control
#


class NotSpecifiedType(object):
    """A helper class singleton for run control meaning that a 'real'
    value has not been given."""

    def __repr__(self):
        return "NotSpecified"


NotSpecified = NotSpecifiedType()
"""A helper class singleton for run control meaning that a 'real' value
has not been given."""


class RunControl(object):
    """A composable configuration class.

    Unlike argparse.Namespace, this keeps the object dictionary
    (__dict__) separate from the run control attributes dictionary
    (_dict).
    """

    def __init__(self, _updaters=None, _validators=None, **kwargs):
        """Parameters
        -------------
        kwargs : optional
            Items to place into run control.

        """
        self._dict = {}
        self._updaters = _updaters or {}
        self._validators = _validators or {}
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, key):
        if key in self._dict:
            value = self._dict[key]
        elif key in self.__dict__:
            value = self.__dict__[key]
        elif key in self.__class__.__dict__:
            value = self.__class__.__dict__[key]
        else:
            msg = "RunControl object has no attribute {0!r}.".format(key)
            raise AttributeError(msg)
        if isinstance(value, property):
            value = value.fget(self)
        return value

    def __setattr__(self, key, value):
        if key.startswith("_"):
            self.__dict__[key] = value
        else:
            if value is NotSpecified and key in self:
                return
            value = self._validate(key, value)
            self._dict[key] = value

    def __delattr__(self, key):
        if key in self._dict:
            del self._dict[key]
        elif key in self.__dict__:
            del self.__dict__[key]
        elif key in self.__class__.__dict__:
            del self.__class__.__dict__[key]
        else:
            msg = "RunControl object has no attribute {0!r}.".format(key)
            raise AttributeError(msg)

    def __iter__(self):
        return iter(self._dict)

    def __repr__(self):
        keys = sorted(self._dict.keys())
        s = ", ".join(["{0!s}={1!r}".format(k, self._dict[k]) for k in keys])
        return "{0}({1})".format(self.__class__.__name__, s)

    def _get(self, key, default=None):
        try:
            val = getattr(self, key)
        except (KeyError, AttributeError):
            val = default
        return val

    def _pformat(self):
        keys = sorted(self._dict.keys())
        s = ",\n ".join(map(lambda k: "{0!s}={1}".format(k, pformat(self._dict[k], indent=2)), keys))
        return "{0}({1})".format(self.__class__.__name__, s)

    def __contains__(self, key):
        return key in self._dict or key in self.__dict__ or key in self.__class__.__dict__

    def __eq__(self, other):
        if hasattr(other, "_dict"):
            return self._dict == other._dict
        elif isinstance(other, Mapping):
            return self._dict == other
        else:
            return NotImplemented

    def __ne__(self, other):
        if hasattr(other, "_dict"):
            return self._dict != other._dict
        elif isinstance(other, Mapping):
            return self._dict != other
        else:
            return NotImplemented

    def __copy__(self):
        return type(self)(_updaters=self._updaters, _validators=self._validators, **self._dict)

    def _update(self, other):
        """Updates the rc with values from another mapping.

        If this rc has if a key is in self, other, and self._updaters,
        then the updaters value is called to perform the update.  This
        function should return a copy to be safe and not update in-
        place.
        """
        if hasattr(other, "_dict"):
            other = other._dict
        elif not hasattr(other, "items"):
            other = dict(other)
        for k, v in other.items():
            if v is NotSpecified:
                pass
            elif k in self._updaters and k in self:
                v = self._updaters[k](getattr(self, k), v)
            setattr(self, k, v)

    def _validate(self, key, value):
        """Validates - and possibly converts - a value based on its key and the current
        validators.
        """
        validators = self._validators
        if key in validators:
            validator, convertor = validators[key]
        else:
            for vld in validators:
                if isinstance(vld, str):
                    continue
                m = vld.match(key)
                if m is not None:
                    validator, convertor = validators[vld]
            else:
                validator, convertor = always_true, noop
        return value if validator(value) else convertor(value)


def flatten(iterable):
    """Generator which returns flattened version of nested sequences."""
    for el in iterable:
        if isinstance(el, str):
            yield el
        elif isinstance(el, Iterable):
            for subel in flatten(el):
                yield subel
        else:
            yield el


#
# Memoization
#


def ishashable(x):
    """Tests if a value is hashable."""
    if isinstance(x, Hashable):
        if isinstance(x, str):
            return True
        elif isinstance(x, Iterable):
            return all(map(ishashable, x))
        else:
            return True
    else:
        return False


DEFAULT_RC = RunControl(
    _validators=DEFAULT_VALIDATORS,
    builddir="_build",
    mongodbpath=property(lambda self: os.path.join(self.builddir, "_dbpath")),
    user_config=os.path.expanduser("~/.config/regolith/user.json"),
    force=False,
    database=None,
)


def load_json_rcfile(fname):
    """Loads a JSON run control file."""
    with open(fname, "r", encoding="utf-8") as f:
        rc = json.load(f)
    return rc


def load_rcfile(fname):
    """Loads a run control file."""
    base, ext = os.path.splitext(fname)
    if ext == ".json":
        rc = load_json_rcfile(fname)
    else:
        raise RuntimeError("could not determine run control file type from extension.")
    return rc


def filter_databases(rc):
    """Filters the databases list down to only the ones we need, in
    place."""
    dbs = rc.databases
    public_only = rc._get("public_only", False)
    if public_only:
        dbs = [db for db in dbs if db["public"]]
    dbname = rc._get("db")
    if dbname is not None:
        dbs = [db for db in dbs if db["name"] == dbname]
    elif len(dbs) == 1:
        rc.db = dbs[0]["name"]
    rc.databases = dbs


def connect_db(rc, colls=None):
    """Load up the db's.

    Parameters
    ----------
    rc:
        The runcontrol instance
    colls
        The list of collections that should be loaded

    Returns
    -------
    chained_db:
      The chained databases in the form of a document
    dbs:
       The databases in the form of a runcontrol client
    """
    with connect(rc, dbs=colls) as rc.client:
        dbs = rc.client.dbs
        chained_db = rc.client.chained_db
    return chained_db, dbs
