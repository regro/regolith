"""Builder for Current and Pending Reports."""
import datetime
import time
from copy import copy
from nameparser import HumanName

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import month_to_int, is_current
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    filter_grants,
    fuzzy_retrieval,
    merge_collections,
    has_started,
)


def is_pending(status):
    return status in "pending"


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
            grp = group["_id"]
            pi = fuzzy_retrieval(
                self.gtx["people"], ["aka", "name"], group["pi_name"]
            )
            pinames = pi["name"].split()
            piinitialslist = [i[0] for i in pinames]
            pi['initials'] = "".join(piinitialslist).upper()

            grants = merge_collections(self.gtx["proposals"],
                                       self.gtx["grants"],
                                       "proposal_id")
            for g in grants:
                for person in g["team"]:
                    rperson = fuzzy_retrieval(
                        self.gtx["people"], ["aka", "name"], person["name"]
                    )
                    if rperson:
                        person["name"] = rperson["name"]
                if g.get('budget'):
                    amounts = [i.get('amount') for i in g.get('budget')]
                    g['subaward_amount'] = sum(amounts)

            current_grants = [
                dict(g)
                for g in grants
                if is_current(g)
            ]
            current_grants, _, _ = filter_grants(
                current_grants, {pi["name"]}, pi=False, multi_pi=True
            )
            for g in current_grants:
                if g.get('budget'):
                    amounts = [i.get('amount') for i in g.get('budget')]
                    g['subaward_amount'] = sum(amounts)

            pending_grants = [
                g
                for g in self.gtx["proposals"]
                if is_pending(g["status"])
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
                    award_start_date="{2}/{1}/{0}".format(
                        grant["begin_day"],
                        month_to_int(grant["begin_month"]),
                        grant["begin_year"],
                    ),
                    award_end_date="{2}/{1}/{0}".format(
                        grant["end_day"],
                        month_to_int(grant["end_month"]),
                        grant["end_year"],
                    ),
                )
            badids = [i["_id"] for i in current_grants if
                      not i.get('cpp_info').get('cppflag', "")]
            iter = copy(current_grants)
            for grant in iter:
                if grant["_id"] in badids:
                    current_grants.remove(grant)
            piname = HumanName(pi["name"])
            outfile = "current-pending-{}-{}".format(grp, piname.last.lower())

            self.render(
                "current_pending.tex",
                outfile + ".tex",
                pi=pi,
                pending=pending_grants,
                current=current_grants,
                pi_upper=pi["name"].upper(),
                group=group,
            )
            self.pdf(outfile)
