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
    subpi.add_argument("-d", "--date",
                       help="Filter grants by a date in ISO format (YYYY-MM-DD)"
                       )
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
        if rc.date:
            desired_date = date_parser.parse(rc.date).date()
        else:
            desired_date = dt.date.today()
        for grant in self.gtx["grants"]:
            try:
                if rc.current and not is_current(grant, now=desired_date):
                    continue
            except RuntimeError:
                continue
            grants.append(grant)

        grants_time_info = []
        for i in grants:
            start, end = '', ''
            if i.get('begin_year') and i.get('end_year'):
                times = get_dates(i)
                start = times['begin_date']
                end = times['end_date']
                grants_time_info.append([i, start, end, end])
            else:
                # Creating fake dates with extreme values for grants that do not have an end date for sorting
                grants_time_info.append([i, start, end, dt.date(3000, 1, 1)])

        # Sort the grants by end date in reverse chronological order
        grants_time_info.sort(key=lambda x: x[3], reverse=True)
        for g in grants_time_info:
            print("{}, awardnr: {}, acctn: {}, {} to {}".format(g[0].get('alias', ''),
                                                                (g[0].get('awardnr', '')),
                                                                (g[0].get('account', '')), (g[1]),
                                                                (g[2])))
        return
