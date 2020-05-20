"""Helper for listing upcoming (and past) grants.

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

TARGET_COLL = "grants"
HELPER_TARGET = "l_grants"

def subparser(subpi):
    subpi.add_argument("-v", "--verbose", action="store_true", help='outputs the grants with more information')
    subpi.add_argument("-l", "--list",
                       help="Lists all current grants by alias"
                       )
    subpi.add_argument("-a", "--admin",
                       help="Filter grants by admin"
                       )
    return subpi


class GrantsListerHelper(SoutHelperBase):
    """Helper for listing upcoming (and past) grants.

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
        # print('rc: {}'.format(rc))
        # print('rc.lead: {}'.format(rc.list))
        # print('rc.admin: {}'.format(rc.admin))
        grants = []
        if rc.list and rc.admin:
            raise RuntimeError(f"please specify either alias or admin, not both")
        for grant in self.gtx["grants"]:
            if rc.list and rc.list != grant.get('alias'):
                continue
            if rc.admin and rc.admin != grant.get('admin'):
                continue
            grants.append(grant)

        # grants.sort()
        for i in grants:
            if rc.verbose:
                print("{:20}{:20}{:15}{:15}{:10}".format(i.get('_id'), i.get('alias'), i.get('awardnr'), str(i.get('amount')), i.get('ledger_end_date')))
            else:
                print("{:20}{:15}".format(i.get('alias'), i.get('awardnr')))
        return

