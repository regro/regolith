"""Builder for CVs."""

import datetime as dt
from copy import copy, deepcopy

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import get_dates, is_current, month_to_int
from regolith.fsclient import _id_key
from regolith.sorters import doc_date_key, position_key
from regolith.stylers import month_fullnames, sentencecase
from regolith.tools import (
    all_docs_from_collection,
    awards,
    filter_activities,
    filter_employment_for_advisees,
    filter_facilities,
    filter_grants,
    filter_licenses,
    filter_patents,
    filter_presentations,
    filter_projects,
    filter_publications,
    filter_service,
    fuzzy_retrieval,
    get_id_from_name,
    make_bibtex_file,
    merge_collections_superior,
)


class AppraisalBuilder(LatexBuilderBase):
    """Build CV from database entries."""

    btype = "annual-activity"
    needed_colls = [
        "groups",
        "people",
        "grants",
        "proposals",
        "institutions",
        "projects",
        "presentations",
        "patents",
        "citations",
    ]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["institutions"] = sorted(all_docs_from_collection(rc.client, "institutions"), key=_id_key)
        gtx["grants"] = sorted(all_docs_from_collection(rc.client, "grants"), key=_id_key)
        gtx["proposals"] = sorted(all_docs_from_collection(rc.client, "proposals"), key=_id_key)
        gtx["projects"] = sorted(all_docs_from_collection(rc.client, "projects"), key=_id_key)
        gtx["presentations"] = sorted(all_docs_from_collection(rc.client, "presentations"), key=_id_key)
        gtx["patents"] = sorted(all_docs_from_collection(rc.client, "patents"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template."""
        rc = self.rc
        if not rc.people:
            raise RuntimeError("ERROR: please rerun specifying --people name")
        if not rc.from_date:
            raise RuntimeError("ERROR: please rerun specifying --from")
        build_target = get_id_from_name(all_docs_from_collection(rc.client, "people"), rc.people[0])
        begin_year = int(rc.from_date.split("-")[0])
        begin_month = int(rc.from_date.split("-")[1])
        pre_begin_year = begin_year - 1
        end_year = begin_year + 1
        end_month = begin_month - 1
        post_end_year = begin_year + 2
        begin_period = dt.date(begin_year, begin_month, 1)
        pre_begin_period = dt.date(pre_begin_year, begin_month, 1)
        end_period = dt.date(end_year, end_month, 28)
        post_end_period = dt.date(post_end_year, end_month, 28)

        me = [p for p in self.gtx["people"] if p["_id"] == build_target][0]
        me["begin_period"] = dt.date.strftime(begin_period, "%m/%d/%Y")
        me["begin_period"] = dt.date.strftime(begin_period, "%m/%d/%Y")
        me["pre_begin_period"] = dt.date.strftime(pre_begin_period, "%m/%d/%Y")
        me["end_period"] = dt.date.strftime(end_period, "%m/%d/%Y")
        me["post_end_period"] = dt.date.strftime(post_end_period, "%m/%d/%Y")
        projs = filter_projects(self.gtx["projects"], set([build_target]), group="bg")
        #########
        # highlights
        #########
        for proj in projs:
            if proj.get("highlights"):
                proj["current_highlights"] = False
                for highlight in proj.get("highlights"):
                    highlight_date = dt.date(highlight.get("year"), month_to_int(highlight.get("month", 1)), 1)
                    if highlight_date > begin_period and highlight_date < end_period:
                        highlight["is_current"] = True
                        proj["current_highlights"] = True

        #########
        # current and pending
        #########
        pi = fuzzy_retrieval(self.gtx["people"], ["aka", "name", "_id"], build_target)

        grants = merge_collections_superior(self.gtx["proposals"], self.gtx["grants"], "proposal_id")
        for g in grants:
            for person in g["team"]:
                rperson = fuzzy_retrieval(self.gtx["people"], ["aka", "name"], person["name"])
                if rperson:
                    person["name"] = rperson["name"]
            if g.get("budget"):
                amounts = [i.get("amount") for i in g.get("budget")]
                g["subaward_amount"] = sum(amounts)

        current_grants = [dict(g) for g in grants if is_current(g)]

        current_grants, _, _ = filter_grants(current_grants, {pi["name"]}, pi=False, multi_pi=True)

        pending_grants = [g for g in self.gtx["proposals"] if g["status"] == "pending"]
        for g in pending_grants:
            for person in g["team"]:
                rperson = fuzzy_retrieval(self.gtx["people"], ["aka", "name"], person["name"])
                if rperson:
                    person["name"] = rperson["name"]
        pending_grants, _, _ = filter_grants(pending_grants, {pi["name"]}, pi=False, multi_pi=True)
        grants = pending_grants + current_grants
        for grant in grants:
            grant_dates = get_dates(grant)
            grant.update(
                award_start_date="{2}/{1}/{0}".format(
                    grant_dates.get("begin_day"),
                    grant_dates.get("begin_month"),
                    grant_dates.get("begin_year"),
                ),
                award_end_date="{2}/{1}/{0}".format(
                    grant_dates.get("end_day"),
                    grant_dates.get("end_month"),
                    grant_dates.get("end_year"),
                ),
            )
        badids = [i["_id"] for i in current_grants if not i["cpp_info"].get("cppflag", "")]
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
        undergrads = filter_employment_for_advisees(self.gtx["people"], begin_period, "undergrad")
        masters = filter_employment_for_advisees(self.gtx["people"], begin_period, "ms")
        currents = filter_employment_for_advisees(self.gtx["people"], begin_period, "phd")
        graduateds = filter_employment_for_advisees(
            self.gtx["people"], begin_period.replace(year=begin_year - 5), "phd"
        )
        postdocs = filter_employment_for_advisees(self.gtx["people"], begin_period, "postdoc")
        visitors = filter_employment_for_advisees(self.gtx["people"], begin_period, "visitor-unsupported")
        iter = deepcopy(graduateds)
        for g in iter:
            if g.get("active"):
                graduateds.remove(g)
        iter = deepcopy(currents)
        for g in iter:
            if not g.get("active"):
                currents.remove(g)

        ######################
        # service
        #####################
        mego = deepcopy(me)
        dept_service = filter_service([mego], begin_period, "department")
        mego = deepcopy(me)
        school_service = filter_service([mego], begin_period, "school")
        mego = deepcopy(me)
        uni_service = filter_service([mego], begin_period, "university")
        uni_service.extend(school_service)
        mego = deepcopy(me)
        prof_service = filter_service([mego], begin_period, "profession")
        mego = deepcopy(me)
        outreach = filter_service([mego], begin_period, "outreach")
        mego = deepcopy(me)
        lab = filter_facilities([mego], begin_period, "research")
        mego = deepcopy(me)
        shared = filter_facilities([mego], begin_period, "shared")
        mego = deepcopy(me)
        fac_other = filter_facilities([mego], begin_period, "other")
        mego = deepcopy(me)
        fac_teaching = filter_facilities([mego], begin_period, "teaching")
        mego = deepcopy(me)
        fac_wishlist = filter_facilities([mego], begin_period, "research_wish", verbose=False)
        mego = deepcopy(me)
        tch_wishlist = filter_facilities([mego], begin_period, "teaching_wish")
        mego = deepcopy(me)
        curric_dev = filter_activities([mego], begin_period, "teaching")
        mego = deepcopy(me)
        other_activities = filter_activities([mego], begin_period, "other")

        ##########################
        # Presentation list
        ##########################
        keypres = filter_presentations(
            self.gtx["people"],
            self.gtx["presentations"],
            self.gtx["institutions"],
            build_target,
            types=["award", "plenary", "keynote"],
            since=begin_period,
            before=end_period,
            statuses=["accepted"],
        )
        invpres = filter_presentations(
            self.gtx["people"],
            self.gtx["presentations"],
            self.gtx["institutions"],
            build_target,
            types=["invited"],
            since=begin_period,
            before=end_period,
            statuses=["accepted"],
        )
        sempres = filter_presentations(
            self.gtx["people"],
            self.gtx["presentations"],
            self.gtx["institutions"],
            build_target,
            types=["colloquium", "seminar"],
            since=begin_period,
            before=end_period,
            statuses=["accepted"],
        )
        declpres = filter_presentations(
            self.gtx["people"],
            self.gtx["presentations"],
            self.gtx["institutions"],
            build_target,
            types=["all"],
            since=begin_period,
            before=end_period,
            statuses=["declined"],
        )

        #########################
        # Awards
        #########################
        ahs = awards(me, since=begin_period)

        ########################
        # Publications
        ########################
        names = frozenset(me.get("aka", []) + [me["name"]])
        pubs = filter_publications(
            all_docs_from_collection(rc.client, "citations"), names, reverse=True, bold=False, since=begin_period
        )
        bibfile = make_bibtex_file(pubs, pid=me["_id"], person_dir=self.bldir)
        articles = [prc for prc in pubs if prc.get("entrytype") in "article"]
        nonarticletypes = [
            "book",
            "inbook",
            "proceedings",
            "inproceedings",
            "incollection",
            "unpublished",
            "phdthesis",
            "misc",
        ]
        nonarticles = [prc for prc in pubs if prc.get("entrytype") in nonarticletypes]
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
        patents = filter_patents(self.gtx["patents"], self.gtx["people"], build_target, since=begin_period)
        licenses = filter_licenses(self.gtx["patents"], self.gtx["people"], build_target, since=begin_period)
        #############
        # hindex
        #############
        if me.get("hindex"):
            hindex = sorted(me.get("hindex"), key=doc_date_key).pop()

        #########################
        # render
        #########################
        #            "C:/Users/simon/scratch/sbillinge-ann-report.tex",
        self.render(
            "columbia_annual_report.tex",
            "sbillinge-ann-report.tex",
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
