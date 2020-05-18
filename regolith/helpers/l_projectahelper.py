"""Helper for listing upcoming (and past) projectum milestones.

   Projecta are small bite-sized project quanta that typically will result in
   one manuscript.
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

TARGET_COLL = "projecta"
HELPER_TARGET = "l_projecta"
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
    return subpi


class ProjectaListerHelper(SoutHelperBase):
    """Helper for listing upcoming (and past) projectum milestones.

       Projecta are small bite-sized project quanta that typically will result in
       one manuscript.
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
        projecta = []
        if rc.lead and rc.person:
            raise RuntimeError(f"please specify either lead or person, not both")
        for projectum in self.gtx["projecta"]:
            if rc.lead and projectum.get('lead') != rc.lead:
                continue
            if rc.person:
                if isinstance(rc.person, str):
                    rc.person = [rc.person]
                good_p = []
                for i in rc.person:
                    if not projectum.get('group_members'):
                        continue
                    if projectum.get('group_members') and i not in projectum.get('group_members'):
                        continue
                    else:
                        good_p.append(i)
                if len(good_p) == 0:
                    continue
            if not rc.stati and projectum.get('status') in bad_stati:
                continue
            if rc.stati and projectum.get('status') not in rc.stati:
                continue
            projecta.append(projectum["_id"])

        projecta.sort()
        for i in projecta:
            print(i)
        return

