"""A mapping whose entries are imported only when they are used."""

from collections.abc import Mapping
from importlib import import_module


class LazyRegistry(Mapping):
    """A mapping of name to object that imports each entry on first use.

    The builders and the helpers are listed by name so that the command
    line can name the valid targets, but importing all of them costs far
    more than running one of them: between them they pull in pandas,
    matplotlib and pypdf.  Holding the import paths rather than the
    objects lets a command import only the target it was asked for, and
    lets ``regolith --version`` import none of them.

    Parameters
    ----------
    specs : dict
        The import path of each entry, keyed by name.  A path is
        ``"package.module:attribute"``, or a tuple of such paths when the
        entry is a tuple.
    """

    def __init__(self, specs):
        self._specs = dict(specs)
        self._resolved = {}

    @staticmethod
    def _resolve(spec):
        """Import and return the object a path names."""
        if isinstance(spec, tuple):
            return tuple(LazyRegistry._resolve(item) for item in spec)
        module_name, _, attribute = spec.partition(":")
        return getattr(import_module(module_name), attribute)

    def __getitem__(self, name):
        if name not in self._resolved:
            self._resolved[name] = self._resolve(self._specs[name])
        return self._resolved[name]

    def __contains__(self, name):
        # Answer from the names alone, so that testing for a target does
        # not import it
        return name in self._specs

    def __iter__(self):
        return iter(self._specs)

    def __len__(self):
        return len(self._specs)
