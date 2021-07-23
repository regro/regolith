"""Builder for Current and Pending Reports."""
import datetime as dt
from copy import copy
from nameparser import HumanName

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import is_current, get_dates
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    filter_grants,
    fuzzy_retrieval,
    merge_collections_all,
    _id_key
)


def is_pending(status):
    return status in "pending"


class CPBuilder(LatexBuilderBase):
    """Build current and pending report from database entries"""

    btype = "current-pending"
    needed_colls = ['groups', 'people', 'grants', 'proposals']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["people"] = list(sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        ))
        gtx["groups"] = list(sorted(
            all_docs_from_collection(rc.client, "groups"), key=_id_key
        ))
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        gtx = self.gtx
        rc = self.rc
        for group in self.gtx["groups"]:
            gtx["grants"] = list(sorted(
                all_docs_from_collection(rc.client, "grants"), key=_id_key
            ))
            gtx["proposals"] = list(sorted(
                all_docs_from_collection(rc.client, "proposals"), key=_id_key
            ))
            grp = group["_id"]
            pi = fuzzy_retrieval(
                self.gtx["people"], ["aka", "name"], group["pi_name"]
            )
            pinames = pi["name"].split()
            piinitialslist = [i[0] for i in pinames]
            pi['initials'] = "".join(piinitialslist).upper()

            grants = merge_collections_all(self.gtx["proposals"],
                                           self.gtx["grants"],
                                           "proposal_id")
            for g in grants:
                g['end_date'] = get_dates(g).get('end_date')
                g['begin_date'] = get_dates(g).get('begin_date',
                                                   dt.date(1900, 1, 2))
                for person in g.get("team", []):
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
            current_grants = [g for g in current_grants if
                              g.get("status") != "declined"]
            for g in current_grants:
                if g.get('budget'):
                    amounts = [i.get('amount') for i in g.get('budget')]
                    g['subaward_amount'] = sum(amounts)

            pending_grants = [
                g for g in self.gtx["proposals"]
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
            summed_grants = pending_grants + current_grants
            for grant in summed_grants:
                grant.update(
                    award_start_date="{}/{}/{}".format(
                        grant.get("begin_date").month,
                        grant.get("begin_date").day,
                        grant.get("begin_date").year,
                    ),
                    award_end_date="{}/{}/{}".format(
                        grant.get("end_date").month,
                        grant.get("end_date").day,
                        grant.get("end_date").year,
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
