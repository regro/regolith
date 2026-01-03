"""Helper for listing upcoming (and past) grants."""

import datetime as dt

import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.dates import get_dates, is_current
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import (
    all_docs_from_collection,
    collection_str,
    get_pi_id,
    key_value_pair_filter,
    merge_collections_superior,
)

TARGET_COLL = "grants"
HELPER_TARGET = "l_grants"
BLACKLIST = ["they_pay", "collgf", "physmatch", "ta", "chemmatch", "summer@seas"]


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument("-c", "--current", action="store_true", help="outputs only the current grants")
    subpi.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="if set, additional information will be printed about each grant",
    )
    subpi.add_argument(
        "-r",
        "--reveal-hidden",
        action="store_true",
        help="if set, outputs also hidden grants such as TA, " "matches etc.",
    )
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs")
    subpi.add_argument(
        "-k",
        "--keys",
        nargs="+",
        help="Specify what keys to return values from when when running "
        "--filter. If no argument is given the default is just the id.",
    )
    subpi.add_argument("-d", "--date", help="Filter grants by a date.  Mostly used for testing.", **date_kwargs)
    return subpi


class GrantsListerHelper(SoutHelperBase):
    """Helper for listing upcoming (and past) grants."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "proposals"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        colls = [
            sorted(all_docs_from_collection(rc.client, collname), key=_id_key) for collname in self.needed_colls
        ]
        for db, coll in zip(self.needed_colls, colls):
            gtx[db] = coll
        gtx["grants"] = merge_collections_superior(gtx["proposals"], gtx["grants"], "proposal_id")
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
            if rc.current and not is_current(grant, now=desired_date):
                continue
            if not rc.reveal_hidden:
                if grant.get("alias") not in BLACKLIST:
                    grants.append(grant)
            else:
                grants.append(grant)

        if rc.keys:
            results = collection_str(grants, rc.keys)
            print(results, end="")
            return
        for g in grants:
            if g.get("admin") is None:
                g["admin"] = "missing"
            g["admin"] = g.get("admin").casefold()
        grants.sort(key=lambda x: x["admin"])
        admins = list(set([g.get("admin") for g in grants]))
        for admin in admins:
            print(f"\nAdministered by: {admin}")
            sub_grants = [grant for grant in grants if grant.get("admin").strip() == admin.strip()]
            sub_grants.sort(key=lambda k: get_dates(k).get("end_date"), reverse=True)
            for g in sub_grants:
                print(
                    f"  {g.get('alias', '').ljust(15)}\t awardnr: {g.get('awardnr', '').ljust(15)}\t "
                    f"acctn: {g.get('account', 'n/a').ljust(20)}\t {get_dates(g).get('begin_date')} "
                    f"to {get_dates(g).get('end_date')}"
                )
                if rc.verbose:
                    funds_entries = g.get("funds_available")
                    if funds_entries:
                        funds_entries.sort(
                            key=lambda k: get_dates(k).get("date", get_dates(k).get("end_date")), reverse=True
                        )
                        if funds_entries[0].get("funds_available"):
                            print(
                                f"      funds available: ${funds_entries[0].get('funds_available'):,.0f} on "
                                f"{get_dates(funds_entries[0]).get('date').isoformat()}"
                            )
        return
