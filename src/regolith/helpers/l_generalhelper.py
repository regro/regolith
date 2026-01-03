"""Helper for listing filtered data from collections in the database."""

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import all_docs_from_collection, collection_str, get_pi_id, search_collection

HELPER_TARGET = "lister"


def subparser(subpi):
    subpi.add_argument("coll", help="Collection that the lister is going to list from.")
    subpi.add_argument(
        "-f",
        "--kv-filter",
        nargs="+",
        help="Search the given collection by key-value pairs. "
        "e.g. 'regolith helper lister -f name simon' will "
        "return the id of all the people who's name contains simon.",
    )
    subpi.add_argument(
        "-r",
        "--return-fields",
        nargs="+",
        help="Specify from which keys to print values. "
        "e.g. 'regolith helper lister people -r name status title' "
        "will return the name, status, and title of all the people "
        "in the collection. If no argument is given the default is just the id.",
    )
    subpi.add_argument("-k", "--keys", action="store_true", help="List of the available keys in the collection.")
    return subpi


class GeneralListerHelper(SoutHelperBase):
    """Helper for listing filtered data from collections in the
    database."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        needed_colls = [rc.coll]
        if "groups" in needed_colls:
            rc.pi_id = get_pi_id(rc)
        colls = [sorted(all_docs_from_collection(rc.client, collname), key=_id_key) for collname in needed_colls]
        for db, coll in zip(needed_colls, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        coll = self.gtx[rc.coll]
        keys = sorted(set([i for k in coll for i in k.keys()]))
        list_keys = []
        if rc.kv_filter:
            list_keys.extend([rc.kv_filter[n] for n in range(len(rc.kv_filter)) if n % 2 == 0])
            for i, item in enumerate(rc.kv_filter):
                if item.lower() == "true":
                    print(f"Warning: value {item} interpreted as a bool")
                if item.lower() == "false":
                    print(f"Warning: value {item} interpreted as a bool")
        if rc.return_fields:
            list_keys.extend(rc.return_fields)
        for i in list_keys:
            if i not in keys:
                raise ValueError(f"{i} is not a valid key. Please choose a valid key from: {keys}")
        if len(coll) == 0:
            raise RuntimeError("This collection is empty or does not exist. Please inform a valid collection.")
        if rc.kv_filter:
            filter_result = search_collection(coll, rc.kv_filter).strip()
            if filter_result == "":
                print("There are no results that match your search.")
            else:
                if rc.return_fields:
                    print(
                        "Results of your search:\n"
                        f"{(search_collection(coll, rc.kv_filter, rc.return_fields).strip())}"
                    )
                else:
                    print(f"Results of your search:\n{filter_result}")
        if rc.return_fields and not rc.kv_filter:
            print(f"Results of your search:\n{collection_str(coll, rc.return_fields).strip()}")
        if rc.keys:
            print(f"Available keys:\n{keys}")
            return
        if not rc.kv_filter and not rc.return_fields:
            print(f"Results of your search:\n{collection_str(coll).strip()}")
        return
