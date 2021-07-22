"""Base class for chaining DBs

ChainDBSingleton
Copyright 2015-2016, the xonsh developers
"""

import itertools

from collections import ChainMap
from collections.abc import MutableMapping
from itertools import chain

from pymongo.collection import Collection as MongoCollection

from regolith.mongoclient import load_mongo_col


class ChainDBSingleton(object):
    """Singleton for representing when no default value is given."""

    __inst = None

    def __new__(cls):
        if ChainDBSingleton.__inst is None:
            ChainDBSingleton.__inst = object.__new__(cls)
        return ChainDBSingleton.__inst


Singleton = ChainDBSingleton()


class ChainCollection:
    """
    The chained database has been used as a reference up until the transition to remote mongo, rather than an edit-able
    object. When using only remote mongo databases, the chained database will become a fully functional chained mongo
    collection rather than a reference of what all of the databases look like mashed together. Checking to see if the
    object's fs_map dictionary is empty is a good indicator of whether or not mongo methods can/should be used directly.

    e.g.
        if rc.client.chained_db[collection_name].fs_map == {}:
            rc.client.chained_db[collection_name].find_one_and_update({"keyName": "Value"},{"$set": {UpdateDict}})
    """

    def __init__(self, *maps):
        '''
        Initialize a ChainCollection by setting *maps* to the given mappings.
        '''

        self.mongo_maps = []
        self.fs_map = {}

        map_list = list(maps)

        if map_list and all([isinstance(map, MongoCollection) for map in map_list]):
            self.mongo_maps = map_list
        elif len(map_list) == 1 and isinstance(map_list[0], dict):
            # There is only ever one collection for the filesystem,
            # as it is chained at the document level, not collection
            self.fs_map = map_list[0]

    def __iter__(self):
        # load all docs from each mongo map, create list of dicts, chainmap them together, get iter of the chainmap
        mongo_chain = ChainMap(*reversed([load_mongo_col(collection) for collection in self.mongo_maps]))
        fs_chain = self.fs_map
        return iter(ChainMap(*[mongo_chain, fs_chain]))

    def __getitem__(self, doc_id):
        chained_mongo_docs = ChainMap(*reversed([collection.find_one({"_id": doc_id}) for collection in self.mongo_maps]))
        chained_fs_docs = self.fs_map.get(doc_id, {})
        return ChainMap(*[chained_mongo_docs, chained_fs_docs])

    def __setitem__(self, doc_id, document):
        if isinstance(document, ChainDocument):
            self.fs_map[doc_id] = document
        elif self.mongo_maps:
            # reached if mongo maps is not empty and the document is not chained
            for db_coll in self.mongo_maps:
                db_coll.find_one_and_update({"_id": doc_id}, {"$set": document})

    def __getattr__(self, method):
        if hasattr(MongoCollection, method):
            results = []
            for db_coll in self.mongo_maps:
                results.append(getattr(db_coll, method))

            # This is a closure that forces the evaluation of the mongo method on every collection w/ the same name.
            def multi_call(args):
                mongo_results = []
                for result in results:
                    mongo_results.extend(result(args))
                return mongo_results

            return multi_call
        else:
            raise AttributeError

    def keys(self):
        if self.fs_map:
            key_list = self.mongo_maps + [self.fs_map]
        else:
            key_list = self.mongo_maps
        return ChainMap(*reversed(key_list)).keys()

    def values(self):
        if self.fs_map:
            full_coll = [load_mongo_col(collection) for collection in self.mongo_maps] + [self.fs_map]
        else:
            full_coll = [load_mongo_col(collection) for collection in self.mongo_maps]
        return ChainMap(*reversed(full_coll)).values()

    def items(self):
        return zip(self.keys(), self.items())


class ChainDocument(ChainMap):
    """ A ChainMap who's ``_getitem__`` returns either a ChainDocument or
    the result"""

    def __getitem__(self, key):
        res = None
        results = []
        # Try to get all the data from all the mappings
        for mapping in self.maps:
            results.append(mapping.get(key, Singleton))
        # if all the results are mapping create a ChainDocument
        if all([isinstance(result, MutableMapping) for result in results]):
            for result in results:
                if res is None:
                    res = ChainDocument(result)
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
    if isinstance(cm, (ChainMap, ChainDocument)):
        r = {}
        for k, v in cm.items():
            r[k] = _convert_to_dict(v)
        return r
    else:
        return cm
