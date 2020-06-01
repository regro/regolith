"""Builder to add expenses """
import datetime as dt
import sys
import time
from argparse import RawTextHelpFormatter

import nameparser

from regolith.helpers.basehelper import SoutHelperBase, DbHelperBase
from regolith.dates import month_to_int, month_to_str_int
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    filter_grants,
    fuzzy_retrieval,
)

ALLOWED_TYPES = ["nsf", "doe", "other"]
ALLOWED_STATI = ["invited", "accepted", "declined", "downloaded", "inprogress",
                 "submitted", "cancelled"]


def subparser(subpi):
    subpi.add_argument("list_name", help="A short but unique name for the list",
                        default=None)
    subpi.add_argument("title", help="A title for the list that will be "
                                     "rendered with the list")
    subpi.add_argument("tags", help="The tags to use to build the list",
                       nargs="+")
    subpi.add_argument("-p", "--purpose",
                        help="The purpose or intended use for the reading"
                        )
    return subpi

class Expenses(DbHelperBase):
    """Build a helper"""
    btype = "a_expenses"
    needed_dbs = ['expenses']


    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        rc.coll = "expenses"

        gtx["expenses"] = sorted(
            all_docs_from_collection(rc.client, "expenses"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip


    def db_updater(self):
        rc = self.rc
        key = "{}".format("_".join(rc.list_name.split()).strip())

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            sys.exit("This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update({
            'title': rc.title,
                })
        if rc.purpose:
            pdoc.update({'purpose': rc.purpose})
        else:
            pdoc.update({'purpose': ''})
        pdoc.update({"_id": key})
        pdoc.update({'papers': {}})

        for cite in self.gtx["citations"]:
            for tag in rc.tags:
                if tag in cite.get("tags"):
                    pdoc["papers"].update({"doi": cite.get("doi"),
                                           "text": cite.get("synopsis")})
        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print("{} has been added in reading_lists".format(
            key))

        return

