"""Helper for listing filtered data from collections in the database.
"""

from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    search_collection,
    collection_str,
)
HELPER_TARGET = "lister"

def subparser(subpi):
    subpi.add_argument(
        "coll",
        help='Collection where the lister is going to run.')
    subpi.add_argument(
        "-f","--kv_filter",
        nargs="+",
        help="Search the given collection by key-value pairs. "
             "e.g. 'regolith helper lister -f name simon' will "
             "return the id of all the people who's name contains simon.")
    subpi.add_argument(
        "-r",  "--return_fields",
        nargs="+",
        help="Specify from which keys to print values. "
             "e.g. 'regolith helper lister people -r name status title' "
             "will return the name, status, and title of all the people "
             "in the collection. If no argument is given the default is just the id.")
    subpi.add_argument(
        "-k", "--keys",
        action="store_true",
        help="List of the available keys in the collection.")
    return subpi

class GeneralListerHelper(SoutHelperBase):
    """Helper for listing filtered data from collections in the database.
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        needed_dbs = [rc.coll]
        if "groups" in needed_dbs:
            rc.pi_id = get_pi_id(rc)
        try:
            if not rc.database:
                rc.database = rc.databases[0]["name"]
        except BaseException:
            pass
        colls = [
            sorted(
                all_docs_from_collection(rc.client, collname), key=_id_key
            )
            for collname in needed_dbs
        ]
        for db, coll in zip(needed_dbs, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        coll = self.gtx[rc.coll]
        if rc.kv_filter:
            if rc.return_fields:
                print((search_collection(coll, rc.kv_filter, rc.return_fields)).strip())
                return
            else:
                print((search_collection(coll, rc.kv_filter)).strip())
                return
        if rc.return_fields:
            print(collection_str(coll, rc.return_fields).strip())
            return
        if rc.keys:
            print(sorted(set([i for k in coll for i in k.keys()])))
            return
        print(collection_str(coll).strip())
        return
