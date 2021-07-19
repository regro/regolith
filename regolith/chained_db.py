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

    mongo_maps = []

    def __init__(self, *maps):
        '''Initialize a ChainCollection by setting *maps* to the given mappings.
        If no mappings are provided, a single empty dictionary is used.
        '''
        map_list = list(maps)

        if all([isinstance(map, MongoCollection) for map in map_list]):
            self.mongo_maps = map_list
        elif len(map_list)==0:
            self.mongo_maps = [{}]

    def __iter__(self):
        # load all docs from each mongo map, create list of dicts, chainmap them together, get iter of the chainmap
        return iter(ChainMap(*reversed([load_mongo_col(collection) for collection in self.mongo_maps])))

    def __getitem__(self, doc_id):
        chained_collection = ChainMap(*reversed([collection.find_one({"_id": doc_id}) for collection in self.mongo_maps]))
        return chained_collection[doc_id]

    def __setitem__(self, doc_id, document):
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
