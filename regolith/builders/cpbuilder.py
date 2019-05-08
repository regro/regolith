"""Builder for Current and Pending Reports."""
import datetime
import time
from copy import copy

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import month_to_int
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.chained_db import ChainDB
from regolith.tools import (
    all_docs_from_collection,
    filter_grants,
    fuzzy_retrieval,
    has_started,
    is_current,
)

def is_pending(status):
    return status in "pending"


def merge_collections(a, b, target_id):
    """
    merge two collections into a single merged collection

    for keys that are in both collections, the value in b will be kept

    Parameters
    ----------
    a  the inferior collection (will lose values of shared keys)
    b  the superior collection (will keep values of shared keys)

    Returns
    -------
    the combined collection
    """
    #    print(dict(b))
    adict = {}
    for k in a:
        adict[k.get("_id")] = k
    bdict = {}
    for k in b:
        bdict[k.get("_id")] = k

    b_for_a = {}
    for k in adict:
        for kk, v in bdict.items():
            if v.get(target_id, "") == k:
                b_for_a[k] = kk
    chained = {}
    for k, v in b_for_a.items():
        chained[k] = ChainDB(adict[k],
                             bdict[v])
#    chained.update(adict)
    return chained
def is_pending(sy, sm, sd):
    return not has_started(sy, sm, sd)


class CPBuilder(LatexBuilderBase):
    """Build current and pending report from database entries"""

    btype = "current-pending"
    needed_dbs = ['groups', 'people', 'grants', 'proposals']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["grants"] = sorted(
            all_docs_from_collection(rc.client, "grants"), key=_id_key
        )
        gtx["proposals"] = sorted(
            all_docs_from_collection(rc.client, "proposals"), key=_id_key
        )
        gtx["groups"] = sorted(
            all_docs_from_collection(rc.client, "groups"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        for group in self.gtx["groups"]:
            pi = fuzzy_retrieval(
                self.gtx["people"], ["aka", "name"], group["pi_name"]
            )
            pinames = pi["name"].split()
            piinitialslist = [i[0] for i in pinames]
            pi['initials'] = "".join(piinitialslist).upper()

            grants = list(
                merge_collections(self.gtx["proposals"], self.gtx["grants"],
                                  "proposal_id").values())
            for g in grants:
                for person in g["team"]:
                    rperson = fuzzy_retrieval(
                        self.gtx["people"], ["aka", "name"], person["name"]
                    )
                    if rperson:
                        person["name"] = rperson["name"]

            current_grants = [
                dict(g)
                for g in grants
                if is_current(
                    *[
                        g.get(s, 1)
                        for s in [
                            "begin_year",
                            "end_year",
                            "begin_month",
                            "begin_day",
                            "end_month",
                            "end_day",
                        ]
                    ]
                )
            ]
            current_grants, _, _ = filter_grants(
                current_grants, {pi["name"]}, pi=False, multi_pi=True
            )

            pending_grants = [
                g
                for g in self.gtx["proposals"]
                if is_pending(g["application_status"])
            ]
            for g in pending_grants:
                for person in g["team"]:
                    rperson = fuzzy_retrieval(
                        self.gtx["people"], ["aka", "name"], person["name"]
                    )
                    if rperson:
                        person["name"] = rperson["name"]
            pending_grants, _, _ = filter_grants(
                pending_grants, {pi["name"]}, pi=False, multi_pi=True
            )
            grants = pending_grants + current_grants
            for grant in grants:
                grant.update(
                    award_start_date="{2}-{1}-{0}".format(
                        grant["begin_day"],
                        month_to_int(grant["begin_month"]),
                        grant["begin_year"],
                    ),
                    award_end_date="{2}-{1}-{0}".format(
                        grant["end_day"],
                        month_to_int(grant["end_month"]),
                        grant["end_year"],
                    ),
                )
            badids = [i["_id"] for i in current_grants if not i.get('cppflag', "")]
            iter = copy(current_grants)
            for grant in iter:
                if grant["_id"] in badids:
                    current_grants.remove(grant)

            self.render(
                "current_pending.tex",
                "cpp.tex",
                pi=pi,
                #                pending=pending_grants,
                pending=pending_grants,
                current=current_grants,
                pi_upper=pi["name"].upper(),
                group=group,
            )
            self.pdf("cpp")
