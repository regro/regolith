"""Base class for chaining DBs"""

from collections import ChainMap, MutableMapping


class ChainDB(ChainMap):
    """ A ChainMap who's ``_getitem__`` returns an instance of itself"""

    def __getitem__(self, key):
        res = None
        results = []
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
            return results[-1]
        return res
