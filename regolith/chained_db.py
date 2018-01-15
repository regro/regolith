"""Base class for chaining DBs"""

from collections import ChainMap, MutableMapping


class ChainDB(ChainMap):
    """ A ChainMap who's ``_getitem__`` returns either a ChainDB or
    the result"""

    def __getitem__(self, key):
        res = None
        results = []
        # Try to get all the data from all the mappings
        for i, mapping in enumerate(self.maps):
            results.append(mapping.get(key, None))
        # if all the results are mapping create a ChainDB
        if all([isinstance(result, MutableMapping) for result in results]):
            for result in results:
                if res is None:
                    res = ChainDB(result)
                else:
                    res.maps.append(result)
        else:
            for result in reversed(results):
                if result is not None:
                    return result
        return res

    def __setitem__(self, key, value):
        pass
