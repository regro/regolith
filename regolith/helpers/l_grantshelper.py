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
    search_collection,
    key_value_pair_filter,
    collection_str,
    merge_collections
)

TARGET_COLL = "grants"
HELPER_TARGET = "l_grants"
BLACKLIST = ["frap", "they_pay", "collgf", "physmatch", "ta", "chemmatch",
             "summer@seas", "startup"]

def subparser(subpi):
    subpi.add_argument("-d", "--date",
                       help="Filter grants by a date in ISO format (YYYY-MM-DD)"
                       )
    subpi.add_argument("-c", "--current", action="store_true", help='outputs only the current grants')
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs")
    subpi.add_argument("-k", "--keys", nargs="+", help="Specify what keys to return values from when when running "
                                                       "--filter. If no argument is given the default is just the id.")
    subpi.add_argument("-v", "--verbose", action="store_true",
                       help='if set, outputs also hidden grants such as TA, '
                            'matches etc.')
    return subpi


class GrantsListerHelper(SoutHelperBase):
    """Helper for listing upcoming (and past) grants.

    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}', 'proposals']

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
        gtx["grants"] = merge_collections(gtx["proposals"], gtx["grants"],
                                   "proposal_id")
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        if rc.filter:
            collection = key_value_pair_filter(self.gtx["grants"], rc.filter)
        else:
            collection = self.gtx["grants"]
        grants = []
        if rc.date:
            desired_date = date_parser.parse(rc.date).date()
        else:
            desired_date = dt.date.today()
        for grant in collection:
            # fixme maybe change this logic and change the name of "year" in proposal to "submitted_year" or sthg
            if grant.get('year'):    # year is used for prop submission but breaks get_dates
                del grant['year']
            if rc.current and not is_current(grant, now=desired_date):
                continue
            if not rc.verbose:
                if grant.get("alias") not in BLACKLIST:
                    grants.append(grant)
            else:
                grants.append(grant)

        # Sort the grants by end date in reverse chronological order
        grants.sort(key=lambda k: get_dates(k).get('end_date'), reverse=True)
        if rc.keys:
            results = (collection_str(grants, rc.keys))
            print(results, end="")
            return
        for g in grants:
            print("{}, awardnr: {}, acctn: {}, {} to {}".format(g.get('alias', ''), g.get('awardnr', ''),
                                                                g.get('account', ''), get_dates(g).get('begin_date'),
                                                                get_dates(g).get('end_date')))
        return
