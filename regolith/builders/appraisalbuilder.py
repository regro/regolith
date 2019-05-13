"""Builder for CVs."""
import datetime as dt
import sys
from copy import copy, deepcopy

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.chained_db import ChainDB
from regolith.dates import month_to_int
from regolith.sorters import ene_date_key, position_key, doc_date_key, date_key
from regolith.builders.cpbuilder import is_current, is_pending, has_finished, \
    has_started
from regolith.stylers import sentencecase, month_fullnames
from regolith.tools import (
    all_docs_from_collection,
    filter_publications,
    filter_projects,
    filter_grants,
    awards_grants_honors,
    make_bibtex_file,
    fuzzy_retrieval,
    dereference_institution,
    filter_employment_for_advisees,
    filter_service,
    filter_facilities,
    filter_activities,
    number_suffix, filter_presentations, awards, filter_patents,
    filter_licenses)

BEGIN_YEAR = 2018


def merge_collections(a, b, target_id):
    """
    merge two collections into a single merged collection

    for keys that are in both collections, the value in b will be kept

    Parameters
    ----------
    a  the inferior collection (will lose values of shared keys)
    b  the superior collection (will keep values of shared keys)
    target_id  str  the name of the key used in b to dereference ids in a

    Returns
    -------
    the combined collection.  Note that it returns a collection only containing
    merged items from a and b that are dereferenced in b, i.e., the merged
    intercept.  If you want the union you can update the returned collection
    with a.

    Examples
    --------
    >>>  grants = merge_collections(self.gtx["proposals"], self.gtx["grants"], "proposal_id")

    This would merge all entries in the proposals collection with entries in the
    grants collection for which "_id" in proposals has the value of
    "proposal_id" in grants.
    """
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
    return list(chained.values())


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
        gtx["presentations"] = sorted(
            all_docs_from_collection(rc.client, "presentations"), key=_id_key
        )
        gtx["patents"] = sorted(
            all_docs_from_collection(rc.client, "patents"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        begin_year = BEGIN_YEAR
        pre_begin_year = begin_year - 1
        end_year = begin_year + 1
        post_end_year = begin_year + 2
        begin_period = dt.date(begin_year, 4, 1)
        pre_begin_period = dt.date(pre_begin_year, 4, 1)
        end_period = dt.date(end_year, 3, 31)
        post_end_period = dt.date(post_end_year, 3, 31)

        rc = self.rc
        me = [p for p in self.gtx["people"] if p["_id"] == "sbillinge"][0]
        me["begin_period"] = dt.date.strftime(begin_period, "%m/%d/%Y")
        me["begin_period"] = dt.date.strftime(begin_period, "%m/%d/%Y")
        me["pre_begin_period"] = dt.date.strftime(pre_begin_period, "%m/%d/%Y")
        me["end_period"] = dt.date.strftime(end_period, "%m/%d/%Y")
        me["post_end_period"] = dt.date.strftime(post_end_period, "%m/%d/%Y")
        projs = filter_projects(
            self.gtx["projects"], set(["sbillinge"])
        )
        #########
        # current and pending
        #########
        pi = fuzzy_retrieval(
            self.gtx["people"], ["aka", "name", "_id"], "sbillinge"
        )
        #        pi['initials'] = "SJLB"

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
            if g["application_status"] == "pending"
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
        # end current and pending
        #########

        #########
        # advising
        #########
        undergrads = filter_employment_for_advisees(self.gtx["people"],
                                                    begin_period,
                                                    "undergrad")
        masters = filter_employment_for_advisees(self.gtx["people"],
                                                 begin_period,
                                                 "ms")
        currents = filter_employment_for_advisees(self.gtx["people"],
                                                  begin_period,
                                                  "phd")
        graduateds = filter_employment_for_advisees(self.gtx["people"],
                                                    begin_period.replace(
                                                        year=end_year - 5),
                                                    "phd")
        postdocs = filter_employment_for_advisees(self.gtx["people"],
                                                  begin_period,
                                                  "postdoc")
        visitors = filter_employment_for_advisees(self.gtx["people"],
                                                  begin_period,
                                                  "visitor")
        iter = deepcopy(graduateds)
        for g in iter:
            if g.get("active"):
                graduateds.remove(g)

        ######################
        # service
        #####################
        mego = deepcopy(me)
        dept_service = filter_service([mego],
                                      begin_period, "department")
        mego = deepcopy(me)
        school_service = filter_service([mego],
                                        begin_period, "school")
        mego = deepcopy(me)
        uni_service = filter_service([mego],
                                     begin_period, "university")
        uni_service.extend(school_service)
        mego = deepcopy(me)
        prof_service = filter_service([mego],
                                      begin_period, "profession")
        mego = deepcopy(me)
        outreach = filter_service([mego],
                                  begin_period, "outreach")
        mego = deepcopy(me)
        lab = filter_facilities([mego],
                                begin_period, "laboratory")
        mego = deepcopy(me)
        shared = filter_facilities([mego],
                                   begin_period, "shared")
        mego = deepcopy(me)
        fac_other = filter_facilities([mego],
                                      begin_period, "other")
        mego = deepcopy(me)
        fac_teaching = filter_facilities([mego],
                                         begin_period, "fac_teaching")
        mego = deepcopy(me)
        fac_wishlist = filter_facilities([mego],
                                         begin_period, "fac_wishlist",
                                         verbose=False)
        mego = deepcopy(me)
        tch_wishlist = filter_facilities([mego],
                                         begin_period, "tch_wishlist")
        mego = deepcopy(me)
        curric_dev = filter_activities([mego],
                                       begin_period, "teaching")
        mego = deepcopy(me)
        other_activities = filter_activities([mego],
                                             begin_period, "other")

        ##########################
        # Presentation list
        ##########################
        keypres = filter_presentations(self.gtx["people"],
                                       self.gtx["presentations"],
                                       self.gtx["institutions"],
                                       types=["award", "plenary", "keynote"],
                                       since=begin_period, before=end_period,
                                       statuses=["accepted"])
        invpres = filter_presentations(self.gtx["people"],
                                       self.gtx["presentations"],
                                       self.gtx["institutions"],
                                       types=["invited"],
                                       since=begin_period, before=end_period,
                                       statuses=["accepted"])
        sempres = filter_presentations(self.gtx["people"],
                                       self.gtx["presentations"],
                                       self.gtx["institutions"],
                                       types=["colloquium", "seminar"],
                                       since=begin_period, before=end_period,
                                       statuses=["accepted"])
        declpres = filter_presentations(self.gtx["people"],
                                        self.gtx["presentations"],
                                        self.gtx["institutions"],
                                        types=["all"],
                                        since=begin_period, before=end_period,
                                        statuses=["declined"])

        #########################
        # Awards
        #########################
        ahs = awards(me, since=begin_period)

        ########################
        # Publications
        ########################
        names = frozenset(me.get("aka", []) + [me["name"]])
        pubs = filter_publications(
            all_docs_from_collection(rc.client, "citations"),
            names,
            reverse=True,
            bold=False,
            since=begin_period
        )
        bibfile = make_bibtex_file(
            pubs, pid=me["_id"], person_dir=self.bldir
        )
        articles = [prc for prc in pubs if
                    prc.get("entrytype") in "article"]
        nonarticletypes = ["book", "inbook", "proceedings", "inproceedings",
                           "incollection", "unpublished", "phdthesis", "misc"]
        nonarticles = [prc for prc in pubs if
                       prc.get("entrytype") in nonarticletypes]
        peer_rev_conf_pubs = [prc for prc in pubs if prc.get("peer_rev_conf")]
        pubiter = deepcopy(pubs)
        for prc in pubiter:
            if prc.get("peer_rev_conf"):
                peer_rev_conf_pubs = prc
                pubs.pop(prc)

        ##############
        # TODO: add Current Projects to Research summary section
        ##############

        #############
        # IP
        #############
        patents = filter_patents(self.gtx["patents"], self.gtx["people"],
                                 "sbillinge", since=begin_period)
        licenses = filter_licenses(self.gtx["patents"], self.gtx["people"],
                                   "sbillinge", since=begin_period)
        #############
        # hindex
        #############
        hindex = sorted(me["hindex"], key=doc_date_key).pop()

        #########################
        # render
        #########################
        self.render(
            "columbia_annual_report.tex",
            "billinge-ann-report" + ".tex",
            pi=pi,
            p=me,
            projects=projs,
            pending=pending_grants,
            current=current_grants,
            undergrads=undergrads,
            masters=masters,
            currentphds=currents,
            graduatedphds=graduateds,
            postdocs=postdocs,
            visitors=visitors,
            dept_service=dept_service,
            uni_service=uni_service,
            prof_service=prof_service,
            outreach=outreach,
            lab=lab,
            shared=shared,
            facilities_other=fac_other,
            fac_teaching=fac_teaching,
            fac_wishlist=fac_wishlist,
            tch_wishlist=tch_wishlist,
            curric_dev=curric_dev,
            other_activities=other_activities,
            keypres=keypres,
            invpres=invpres,
            sempres=sempres,
            declpres=declpres,
            sentencecase=sentencecase,
            monthstyle=month_fullnames,
            ahs=ahs,
            pubs=articles,
            nonarticles=nonarticles,
            peer_rev_conf_pubs=peer_rev_conf_pubs,
            bibfile=bibfile,
            patents=patents,
            licenses=licenses,
            hindex=hindex,
        )
        self.pdf("billinge-ann-report")
