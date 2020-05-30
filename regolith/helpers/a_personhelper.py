"""Helper for adding a new person to the people collection.

"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
)

TARGET_COLL = "person"
# ALLOWED_STATI = ["undergrad", "master", "PhD"]

def subparser(subpi):
    subpi.add_argument("id", help="unique identifier for the group member (e.g. aeinstein)",
                       default=None)
    subpi.add_argument("name", help="Full, canonical name for the person",
                       default=None)
    subpi.add_argument("bio", help="short biographical text",
                       default=None)
    subpi.add_argument("degree",
                       default=None)
    subpi.add_argument("institution",
                       default=None)
    subpi.add_argument("begin_year_education", help="Begin year of education degree",
                       default=None)
    subpi.add_argument("aka", help="list of aliases (also-known-as)", nargs="+",
                       default=None)
    # subpi.add_argument("n")
    # Do not delete --database arg
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file."
                       )
    return subpi

class PersonAdderHelper(DbHelperBase):
    """Helper for adding a new person to the people collection.
    """

    btype = "a_person"
    needed_dbs = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(
            all_docs_from_collection(rc.client, rc.coll), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        # if not rc.date:
        #     now = dt.date.today()
        # else:
        #     now = date_parser.parse(rc.date).date()
        key = rc.id
        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError(
                "This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update({"_id": key})
        pdoc.update({"aka": rc.aka})
        pdoc.update({"bio": rc.bio})
        pdoc.update({"avatar": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y" })
        pdoc.update({"education":[{"begin_year": rc.begin_year_education},
                                  {"degree": rc.degree},
                                  {"institution": rc.institution}
                                ]})
        pdoc.update({"name": rc.name})
        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{rc.id} has been added in {TARGET_COLL}")

        return
