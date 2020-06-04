"""Helper for listing group members.

"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.dates import get_due_date
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
)

TARGET_COLL = "people"
HELPER_TARGET = "l_members"
ALLOWED_STATI = ["proposed", "started", "finished", "back_burner", "paused", "cancelled"]



def subparser(subpi):
    subpi.add_argument("-v", "--verbose", action="store_true", help='increase verbosity of output')
    subpi.add_argument("-l", "--lead",
                       help="Filter milestones for this project lead"
                       )
    subpi.add_argument("-p", "--person",
                       help="Filter milestones for this person whether lead or not"
                       )
    subpi.add_argument("-s", "--stati", nargs="+",
                       help=f"List of stati for the project that you want returned,"
                            f"from {ALLOWED_STATI}.  Default is proposed and started"
                       )
    subpi.add_argument("-c", "--current", action="store_true", help='get only current group members ')

    return subpi


class MembersListerHelper(SoutHelperBase):
    """Helper for listing group members.

    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        try:
            if not rc.database:
                rc.database = rc.databases[0]["name"]
        except:
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
        bad_stati = ["finished", "cancelled", "paused", "back_burner"]
        people = []
        for person in self.gtx["people"]:
            if rc.current and not person.get('active'):
                continue
            people.append(person)
        #people.sort()
        for i in people:
            if rc.verbose:
                print("{},{}".format(i.get('name'), i.get('position')))
            else:
                print("{}".format(i.get('name')))
        return

