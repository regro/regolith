"""Builder for Current and Pending Reports."""
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
    subpi.add_argument("name", help="Full name of the first author",
                       )
    subpi.add_argument("due_date", help="due date in form YYYY-MM-DD in quotes", default=''
                       )
    subpi.add_argument("-c", "--recommendation",
                       help="Recommendation for this manuscript: reject, smalledits, or majoredits", default=None
                       )
    subpi.add_argument("-d", "--database",
                       help="The database that will be updated. Defaults to "
                            "first database in the regolithrc.json file."
                       )
    subpi.add_argument("-r", "--reviewer",
                       help="name of the reviewer.  Defaults to sbillinge"
                       )
    subpi.add_argument("-s", "--status",
                       help=f"status, from {ALLOWED_STATI}. default is submitted"
                       )
    subpi.add_argument("-t", "--title",
                       help="the title of the Manuscript"
                       )
    return subpi


class ManuRevAdderHelper(DbHelperBase):
    btype = "a_manurev"
    needed_dbs = ['refereeReports']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        rc.coll = "refereeReports"
        gtx["refereeReports"] = sorted(
            all_docs_from_collection(rc.client, "refereeReports"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        name = nameparser.HumanName(rc.name)
        month = dt.datetime.today().month
        year = dt.datetime.today().year
        key = "{}{}_{}_{}".format(
            str(year)[-2:], month_to_str_int(month), name.last.casefold(),
            name.first.casefold().strip("."))

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            sys.exit("This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update({'claimed_found_what': [],
                     'claimed_why_important': [],
                     'did_how': [],
                     'did_what': [],
                     'due_date': rc.due_date,
                     'editor_eyes_only': '',
                     'final_assessment': [],
                     'first_author_last_name': name.last,
                     'freewrite': '',
                     'journal': '',
                     'month': month,
                     'validity_assessment': [],
                     'year': year
                     })

        if rc.title:
            pdoc.update({'title': rc.title})
        else:
            pdoc.update({'title': ''})
        if rc.reviewer:
            pdoc.update({'reviewer': rc.reviewer})
        else:
            pdoc.update({'reviewer': 'sbillinge'})
        if rc.recommendation:
            pdoc.update({'recommendation': rc.recommendation})
        else:
            pdoc.update({'recommendation': ''})
        if rc.status:
            if rc.status not in ALLOWED_STATI:
                raise ValueError(
                    "status should be one of {}".format(ALLOWED_STATI))
            else:
                pdoc.update({'status': rc.status})
        else:
            pdoc.update({'status': 'submitted'})

        pdoc.update({"_id": key})
        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print("{} manuscript has been added/updated in manuscript reviews".format(
            rc.name))

        return
