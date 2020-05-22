"""Helper for listing upcoming (and past) grants.

"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.dates import get_dates, is_current
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
)

TARGET_COLL = "grants"
HELPER_TARGET = "l_grants"


def subparser(subpi):
    subpi.add_argument("-c", "--current", action="store_true", help='outputs only the current grants')
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
        grants = []
        for grant in self.gtx["grants"]:
            if rc.current and not is_current(grant):
                continue
            grants.append(grant)

        grants_time_info = []
        for i in grants:
            start = 'EMPTY'
            end = 'EMPTY'
            had_dates = False
            if i.get('begin_year') and i.get('end_year'):
                times = get_dates(i)
                start = times['begin_date']
                end = times['end_date']
                had_dates = True
            if had_dates:
                grants_time_info.append([i, start, end, start, end])
            else:
                # Creating fake dates with extreme values for grants that do not have a date for sorting
                grants_time_info.append([i, start, end, dt.date(3000, 1, 1), dt.date(3000, 1, 1)])
        grants_time_info.sort(key=lambda x: x[4], reverse=True)
        # print("{:15}{:15}{:15}{:15}{:15}".format('ALIAS', 'AWARDNR', 'ACCOUNT', 'BEGIN', 'END'))
        for g in grants_time_info:
            print("{:15}{:15}{:15}{:15}{:15}".format(g[0].get('alias', 'EMPTY'), g[0].get('awardnr', 'EMPTY'),
                                                     str(g[0].get('account', 'EMPTY')), str(g[1]), str(g[2])))
        return
