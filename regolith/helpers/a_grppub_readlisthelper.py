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

class GrpPubReadListAdderHelper(DbHelperBase):
    """Build a helper"""
    btype = "a_grppub_readlist"
    needed_dbs = ['citations', "reading_lists"]

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.database = None
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        rc.coll = "reading_lists"
        gtx["citations"] = sorted(
            all_docs_from_collection(rc.client, "citations"), key=_id_key
        )
        gtx["reading_lists"] = sorted(
            all_docs_from_collection(rc.client, "reading_lists"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip


    def sout(self):
        person = self.rc.person
        return print(f"hello {person}")

    def db_updater(self):
        rc = self.rc
        name = nameparser.HumanName(rc.name)
        month = dt.datetime.today().month
        year = dt.datetime.today().year
        key = "{}".format("_".join(rc.list_name.split()).strip())

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            sys.exit("This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update({
            ''
            
            
            'adequacy_of_resources': [
            'The resources available to the PI seem adequate'],
                'agency': rc.type,
                'competency_of_team': [],
                'doe_appropriateness_of_approach': [],
                'doe_reasonableness_of_budget': [],
                'doe_relevance_to_program_mission': [],
                'does_how': [],
                'does_what': '',
                'due_date': rc.due_date,
                'freewrite': [],
                'goals': [],
                'importance': [],
                'institutions': [],
                'month': 'tbd',
                'names': name.full_name,
                'nsf_broader_impacts': [],
                'nsf_create_original_transformative': [],
                'nsf_plan_good': [],
                'nsf_pot_to_advance_knowledge': [],
                'nsf_pot_to_benefit_society': [],
                'status': 'accepted',
                'summary': '',
                'year': 2020
                })

        if rc.title:
            pdoc.update({'title': rc.title})
        else:
            pdoc.update({'title': ''})
        if rc.requester:
            pdoc.update({'requester': rc.requester})
        else:
            pdoc.update({'requester': ''})
        if rc.reviewer:
            pdoc.update({'reviewer': rc.reviewer})
        else:
            pdoc.update({'reviewer': 'sbillinge'})
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

        print("{} proposal has been added/updated in proposal reviews".format(
            rc.name))

        return

