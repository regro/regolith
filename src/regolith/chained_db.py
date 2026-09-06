"""Base class for chaining DBs.

ChainDBSingleton Copyright 2015-2016, the xonsh developers
"""

import itertools
from collections import ChainMap
from collections.abc import Mapping, MutableMapping


class ChainDBSingleton(object):
    """Singleton for representing when no default value is given."""

    __inst = None

    def __new__(cls):
        if ChainDBSingleton.__inst is None:
            ChainDBSingleton.__inst = object.__new__(cls)
        return ChainDBSingleton.__inst


Singleton = ChainDBSingleton()


class ChainDB(ChainMap):
    """A ChainMap who's ``_getitem__`` returns either a ChainDB or the
    result."""

    def __getitem__(self, key):
        res = None
        results = []
        # Try to get all the data from all the mappings
        for mapping in self.maps:
            results.append(mapping.get(key, Singleton))
        # if all the results are mapping create a ChainDB
        if all([isinstance(result, MutableMapping) for result in results]):
            for result in results:
                if res is None:
                    res = ChainDB(result)
                else:
                    res.maps.append(result)
        elif all([isinstance(result, list) for result in results]):
            return list(itertools.chain(*results))
        elif all([isinstance(result, (list, ChainDBSingleton)) for result in results]):
            for result in results[::-1]:
                if isinstance(result, ChainDBSingleton):
                    results.remove(result)
            if len(results) != 0:
                return list(itertools.chain(*results))
            else:
                raise KeyError("{} is none of the current mappings".format(key))
        else:
            for result in reversed(results):
                if result is not Singleton:
                    return result
            raise KeyError("{} is none of the current mappings".format(key))
        return res

    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, value)
        else:
            # Try to get all the data from all the mappings
            for mapping in reversed(self.maps):
                if key in mapping:
                    mapping[key] = value


def _convert_to_dict(cm):
    if isinstance(cm, (ChainMap, ChainDB)):
        r = {}
        for k, v in cm.items():
            r[k] = _convert_to_dict(v)
        return r
    else:
        return cm


class LazyChainedDB(Mapping):
    """The chained collections of the databases, each one built the
    first time it is asked for.

    Reading one collection must not pull in every other collection, so
    the chaining is done per collection on demand rather than for the
    whole database when it is opened.  Iterating this mapping, as
    validation does, still reaches every collection and so still loads
    them all.
    """

    def __init__(self, client):
        self._client = client
        self._chained = {}

    def __getitem__(self, collname):
        if collname not in self._chained:
            self._chained[collname] = self._client.chain_collection(collname)
        return self._chained[collname]

    def __contains__(self, collname):
        # Answer from the source map, so that testing for a collection does
        # not read it
        return collname in self._client.chained_collection_names()

    def __iter__(self):
        return iter(self._client.chained_collection_names())

    def __len__(self):
        return len(self._client.chained_collection_names())

    def materialize(self):
        """Return every chained collection as a plain dict.

        This reads every collection of every database, so use it only
        where the whole database is genuinely wanted, such as handing the
        data to a caller that outlives the connection.

        Returns
        -------
        dict
            The chained collections, keyed by collection name.
        """
        return {collname: self[collname] for collname in self}
