"""Base class for chaining DBs"""

from collections import ChainMap


class ChainDB(ChainMap):
    """ A ChainMap who's ``_getitem__`` returns an instance of itself"""

    def __getitem__(self, key):
        res = None
        for mapping in self.maps:
            if key in mapping:
                if res is None:
                    res = ChainDB(mapping[key])
                else:
                    res.maps.append(mapping[key])
        return res
