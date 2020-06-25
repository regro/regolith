"""Helper for finding people's information in the people collection
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
        help='collection where the lister is going to run.')
    subpi.add_argument(
        "--kv_filter",
        nargs="+",
        help='search the given collection by key element pairs')
    subpi.add_argument(
        "-r",
        nargs="+",
        help='the name of the fields to return from the search')
    subpi.add_argument(
        "-k", "--keys",
        action="store_true",
        help='list of the available keys and their description')
    return subpi

class GeneralListerHelper(SoutHelperBase):
    """Helper for finding and listing contacts from the contacts.yml file
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = ["abstracts", "assignments","beamplan", "beamtime",
                  "beam_time", "beam_proposals","blog","citations",
                  "contacts", "courses", "expenses", "grades", "grants",
                  "groups","institutions", "jobs", "meetings", "news",
                  "patents","people", "presentations", "pronouns",
                  "proposals", "proposalReviews", "projecta", "projects",
                  "reading_lists", "refereeReports","students"]

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
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
            for collname in self.needed_dbs
        ]
        for db, coll in zip(self.needed_dbs, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        coll = self.gtx[rc.coll]
        if rc.kv_filter:
            if rc.r:
                print((search_collection(coll, rc.kv_filter, rc.r)).strip())
                return
            else:
                print((search_collection(coll, rc.kv_filter)).strip())
                return
        if rc.keys:
            print(sorted(set([i for k in coll for i in k.keys()])))
            return
        print(collection_str(coll).strip())
        return
