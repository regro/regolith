"""Builder for CVs."""
import datetime as dt

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.dates import month_to_int
from regolith.sorters import ene_date_key, position_key
from regolith.builders.cpbuilder import is_current, is_pending, has_finished, has_started
from regolith.tools import (
    all_docs_from_collection,
    filter_publications,
    filter_projects,
    filter_grants,
    awards_grants_honors,
    make_bibtex_file,
    fuzzy_retrieval,
    dereference_institution,

)

BEGIN_YEAR = 2018

class AppraisalBuilder(LatexBuilderBase):
    """Build CV from database entries"""

    btype = "ann-appraisal"

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
        gtx["institutions"] = sorted(
            all_docs_from_collection(rc.client, "institutions"), key=_id_key
        )
        gtx["grants"] = sorted(
            all_docs_from_collection(rc.client, "grants"), key=_id_key
        )
        gtx["proposals"] = sorted(
            all_docs_from_collection(rc.client, "proposals"), key=_id_key
        )
        gtx["projects"] = sorted(
            all_docs_from_collection(rc.client, "projects"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def latex(self):
        """Render latex template"""
        begin_year = BEGIN_YEAR
        pre_begin_year = begin_year - 1
        end_year = begin_year + 1
        post_end_year = begin_year + 2
        begin_period = dt.date(begin_year,4,1)
        pre_begin_period = dt.date(pre_begin_year,4,1)
        end_period = dt.date(end_year,3,31)
        post_end_period = dt.date(post_end_year,3,31)

        rc = self.rc
        me = [p for p in self.gtx["people"] if p["_id"] == "sbillinge"][0]
        me["begin_period"] = dt.date.strftime(begin_period,"%m/%d/%Y")
        me["begin_period"] = dt.date.strftime(begin_period,"%m/%d/%Y")
        me["pre_begin_period"] = dt.date.strftime(pre_begin_period,"%m/%d/%Y")
        me["end_period"] = dt.date.strftime(end_period,"%m/%d/%Y")
        me["post_end_period"] = dt.date.strftime(end_period,"%m/%d/%Y")
        projs = filter_projects(
            self.gtx["projects"], set(["sbillinge"])
        )
        #########
        # current and pending
        #########
        pi = fuzzy_retrieval(
            self.gtx["people"], ["aka", "name"], "sbillinge"
        )
        pi['initials'] = "SJLB"

        grants = merge_collections(self.gtx["proposals"], self.gtx["grants"],
                                   "proposal_id")
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
                        "begin_day",
                        "begin_month",
                        "begin_year",
                        "end_day",
                        "end_month",
                        "end_year",
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
        badids = [i["_id"] for i in current_grants if not i.get('cppflag', "")]
        iter = copy(current_grants)
        for grant in iter:
            if grant["_id"] in badids:
                current_grants.remove(grant)
        #########
        # current and pending
        #########

        self.render(
            "columbia_annual_report.tex",
            "billinge-ann-report" + ".tex",
            p=me,
            projects=projs,
            pending = pending_grants,
            current = current_grants,
        )
        self.pdf("billinge-ann-report")

        """
        for p in self.gtx["people"]:
            # so we don't modify the dbs when de-referencing
            names = frozenset(p.get("aka", []) + [p["name"]])
            pubs = filter_publications(
                all_docs_from_collection(rc.client, "citations"),
                names,
                reverse=True,
            )
            bibfile = make_bibtex_file(
                pubs, pid=p["_id"], person_dir=self.bldir
            )
            emp = p.get("employment", [])
            emp.sort(key=ene_date_key, reverse=True)
            edu = p.get("education", [])
            edu.sort(key=ene_date_key, reverse=True)

            grants = list(all_docs_from_collection(rc.client, "grants"))
            pi_grants, pi_amount, _ = filter_grants(grants, names, pi=True)
            coi_grants, coi_amount, coi_sub_amount = filter_grants(
                grants, names, pi=False
            )
            aghs = awards_grants_honors(p)
            # TODO: pull this out so we can use it everywhere
            for ee in [emp, edu]:
                for e in ee:
                    dereference_institution(e, self.gtx["institutions"])
        """

        """
                title=p.get("name", ""),
                aghs=aghs,
                pubs=pubs,
                names=names,
                bibfile=bibfile,
                education=edu,
                employment=emp,
                projects=projs,
                pi_grants=pi_grants,
                pi_amount=pi_amount,
                coi_grants=coi_grants,
                coi_amount=coi_amount,
                coi_sub_amount=coi_sub_amount,
        """
