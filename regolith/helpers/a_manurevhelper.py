"""Builder for manuscript reviews."""
import datetime as dt
import sys

import nameparser

from regolith.helpers.basehelper import DbHelperBase
from regolith.dates import month_to_str_int
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
)

ALLOWED_STATI = ["invited", "accepted", "declined", "downloaded", "inprogress",
                 "submitted", "cancelled"]


def subparser(subpi):
    subpi.add_argument("name", help="Full name, or last name, of the first author",
                       )
    subpi.add_argument("due_date", help="due date in form YYYY-MM-DD in quotes", default=''
                       )
    subpi.add_argument("journal", help="journal to be published on", default=''
                       )
    subpi.add_argument("title", help="the title of the Manuscript", default=''
                       )
    subpi.add_argument("-d", "--submitted_date", help="submitted date in ISO YYYY-MM-DD format in quotes"
                       )
    subpi.add_argument("-q", "--requester",
                       help="name, or id in contacts, of the editor requesting the review"
                       )
    subpi.add_argument("-r", "--reviewer",
                       help="name of the reviewer. Defaults to sbillinge"
                       )
    subpi.add_argument("-s", "--status",
                       help=f"status, from {ALLOWED_STATI}. default is accepted"
                       )
    subpi.add_argument("--database",
                       help="The database that will be updated. Defaults to "
                            "first database in the regolithrc.json file."
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
        if name.last == '':
            key = "{}{}_{}".format(
                str(year)[-2:], month_to_str_int(month),
                name.first.casefold().strip("."))
        else:
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
                     'freewrite': '',
                     'journal': rc.journal,
                     'recommendation': '',
                     'title': rc.title,
                     'validity_assessment': [],
                     'year': year
                     })

        if rc.reviewer:
            pdoc.update({'reviewer': rc.reviewer})
        else:
            pdoc.update({'reviewer': 'sbillinge'})
        if rc.submitted_date:
            pdoc.update({'submitted_date': rc.submitted_date})
        else:
            pdoc.update({'submitted_date': 'tbd'})
        if rc.name:
            if name.last == '':
                pdoc.update({'first_author_last_name': name.first})
            else:
                pdoc.update({'first_author_last_name': name.last})
        if rc.requester:
            pdoc.update({'requester': rc.requester})
        else:
            pdoc.update({'requester': ''})
        if rc.status:
            if rc.status not in ALLOWED_STATI:
                raise ValueError(
                    "status should be one of {}".format(ALLOWED_STATI))
            else:
                pdoc.update({'status': rc.status})
        else:
            pdoc.update({'status': 'accepted'})

        pdoc.update({"_id": key})
        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print("{} manuscript has been added/updated in manuscript reviews".format(
            rc.name))

        return
