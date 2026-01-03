"""Builder for CVs."""

import datetime as dt
from copy import copy, deepcopy

from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.builders.cpbuilder import is_declined, is_pending
from regolith.dates import get_dates, is_current
from regolith.fsclient import _id_key
from regolith.sorters import doc_date_key, position_key
from regolith.stylers import month_fullnames, sentencecase
from regolith.tools import (
    all_docs_from_collection,
    awards,
    filter_activities,
    filter_committees,
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
    merge_collections_all,
)


class ActivitylogBuilder(LatexBuilderBase):
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
        "proposalReviews",
        "refereeReports",
        "recletts",
        "contacts",
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
        gtx["contacts"] = sorted(all_docs_from_collection(rc.client, "institutions"), key=_id_key)
        gtx["groups"] = sorted(all_docs_from_collection(rc.client, "groups"), key=_id_key)
        gtx["grants"] = sorted(all_docs_from_collection(rc.client, "grants"), key=_id_key)
        gtx["proposals"] = sorted(all_docs_from_collection(rc.client, "proposals"), key=_id_key)
        gtx["projects"] = sorted(all_docs_from_collection(rc.client, "projects"), key=_id_key)
        gtx["presentations"] = sorted(all_docs_from_collection(rc.client, "presentations"), key=_id_key)
        gtx["proprevs"] = sorted(all_docs_from_collection(rc.client, "proposalReviews"), key=_id_key)
        gtx["manrevs"] = sorted(all_docs_from_collection(rc.client, "refereeReports"), key=_id_key)
        gtx["recletts"] = sorted(all_docs_from_collection(rc.client, "recletts"), key=_id_key)
        gtx["patents"] = sorted(all_docs_from_collection(rc.client, "patents"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template."""
        rc = self.rc
        group = fuzzy_retrieval(self.gtx["groups"], ["_id", "aka", "name"], rc.groupname)
        if not rc.people:
            raise RuntimeError("ERROR: please rerun specifying --people name")
        if not rc.from_date:
            raise RuntimeError("ERROR: please rerun specifying --from")
        build_target = get_id_from_name(all_docs_from_collection(rc.client, "people"), rc.people[0])
        begin_year = int(rc.from_date.split("-")[0])
        begin_period = date_parser.parse(rc.from_date).date()
        pre_begin_period = begin_period - relativedelta(years=1)
        if rc.to_date:
            to_date = date_parser.parse(rc.to_date).date()
            end_period = to_date
            post_end_period = to_date + relativedelta(years=1)
        else:
            end_period = begin_period + relativedelta(years=1) - relativedelta(days=1)
            post_end_period = begin_period + relativedelta(years=2) - relativedelta(days=1)

        me = [p for p in self.gtx["people"] if p["_id"] == build_target][0]
        me["begin_period"] = dt.date.strftime(begin_period, "%m/%d/%Y")
        me["begin_period"] = dt.date.strftime(begin_period, "%m/%d/%Y")
        me["pre_begin_period"] = dt.date.strftime(pre_begin_period, "%m/%d/%Y")
        me["end_period"] = dt.date.strftime(end_period, "%m/%d/%Y")
        me["post_end_period"] = dt.date.strftime(post_end_period, "%m/%d/%Y")
        projs = filter_projects(self.gtx["projects"], set([build_target]), group=group["_id"])
        ########
        # Recommendation Letters count
        ########
        recletts = self.gtx["recletts"]
        num_recletts = len(
            [reclett["_id"] for reclett in recletts if get_dates(reclett).get("end_date") >= begin_period]
        )
        ########
        # Proposal review count
        ########
        proprevs = self.gtx["proprevs"]
        num_proprevs = len(
            [
                proprev["_id"]
                for proprev in proprevs
                if get_dates(proprev).get("end_date") >= begin_period and proprev.get("status") == "submitted"
            ]
        )
        ########
        # Manuscript review count
        ########
        manrevs = self.gtx["manrevs"]
        num_manrevs = len(
            [
                manrev["_id"]
                for manrev in manrevs
                if manrev.get("status") == "submitted"
                and get_dates(manrev, date_field_prefix="submitted").get("submitted_date", dt.date(1971, 1, 1))
                is not None
                and get_dates(manrev, date_field_prefix="submitted").get("submitted_date", dt.date(1971, 1, 1))
                >= begin_period
            ]
        )

        #########
        # current and pending
        #########
        pi = fuzzy_retrieval(self.gtx["people"], ["_id", "aka", "name"], build_target)
        pinames = pi["name"].split()
        piinitialslist = [i[0] for i in pinames]
        pi["initials"] = "".join(piinitialslist).upper()

        grants = merge_collections_all(self.gtx["proposals"], self.gtx["grants"], "proposal_id")
        for g in grants:
            g["end_date"] = get_dates(g).get("end_date")
            g["begin_date"] = get_dates(g).get("begin_date", dt.date(1900, 1, 2))
            g["award_start_date"] = "{}/{}/{}".format(
                g.get("begin_date").month,
                g.get("begin_date").day,
                g.get("begin_date").year,
            )
            g["award_end_date"] = "{}/{}/{}".format(
                g.get("end_date").month, g.get("end_date").day, g.get("end_date").year
            )

            for person in g.get("team", []):
                rperson = fuzzy_retrieval(self.gtx["people"], ["aka", "name"], person["name"])
                if rperson:
                    person["name"] = rperson["name"]
            if g.get("budget"):
                amounts = [i.get("amount") for i in g.get("budget")]
                g["subaward_amount"] = sum(amounts)

        current_grants = [dict(g) for g in grants if is_current(g)]
        current_grants, _, _ = filter_grants(current_grants, {pi["name"]}, pi=False, multi_pi=True)
        current_grants = [g for g in current_grants if g.get("status") != "declined"]
        for g in current_grants:
            if g.get("budget"):
                amounts = [i.get("amount") for i in g.get("budget")]
                g["subaward_amount"] = sum(amounts)

        pending_grants = [g for g in self.gtx["proposals"] if is_pending(g["status"])]
        for g in pending_grants:
            for person in g["team"]:
                rperson = fuzzy_retrieval(self.gtx["people"], ["aka", "name"], person["name"])
                if rperson:
                    person["name"] = rperson["name"]
        pending_grants, _, _ = filter_grants(pending_grants, {pi["name"]}, pi=False, multi_pi=True)
        badids = [i["_id"] for i in current_grants if not i.get("cpp_info").get("cppflag", "")]

        declined_proposals = [g for g in self.gtx["proposals"] if is_declined(g["status"])]
        for g in declined_proposals:
            for person in g["team"]:
                rperson = fuzzy_retrieval(self.gtx["people"], ["aka", "name"], person["name"])
                if rperson:
                    person["name"] = rperson["name"]
        declined_proposals, _, _ = filter_grants(declined_proposals, {pi["name"]}, pi=False, multi_pi=True)
        declined_proposals = [
            proposal
            for proposal in declined_proposals
            if get_dates(proposal).get("begin_date") >= begin_period
            and get_dates(proposal, date_field_prefix="submitted").get("submitted_date", end_period) <= end_period
        ]

        iter = copy(current_grants)
        for grant in iter:
            if grant["_id"] in badids:
                current_grants.remove(grant)
        #########
        # end current and pending
        #########

        #########
        # highlights
        #########
        ossoftware = False
        for proj in projs:
            if proj.get("highlights"):
                proj["current_highlights"] = False
                for highlight in proj.get("highlights"):
                    highlight_date = get_dates(highlight)
                    if highlight_date.get("end_date") >= begin_period:
                        highlight["is_current"] = True
                        proj["current_highlights"] = True
                        if proj.get("type") == "ossoftware":
                            ossoftware = True

        #########
        # advising
        #########
        undergrads = filter_employment_for_advisees(self.gtx["people"], begin_period, "undergrad", rc.people[0])
        masters = filter_employment_for_advisees(self.gtx["people"], begin_period, "ms", rc.people[0])
        currents = filter_employment_for_advisees(self.gtx["people"], begin_period, "phd", rc.people[0])
        graduateds = filter_employment_for_advisees(
            self.gtx["people"], begin_period.replace(year=begin_year - 5), "phd", rc.people[0]
        )
        postdocs = filter_employment_for_advisees(self.gtx["people"], begin_period, "postdoc", rc.people[0])
        visitors = filter_employment_for_advisees(
            self.gtx["people"], begin_period, "visitor-unsupported", rc.people[0]
        )
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
        dept_service = filter_service(mego, begin_period, "department")
        mego = deepcopy(me)
        school_service = filter_service(mego, begin_period, "school")
        mego = deepcopy(me)
        uni_service = filter_service(mego, begin_period, "university")
        uni_service.extend(school_service)
        if num_recletts > 0:
            uni_service.append({"name": f"Wrote recommendation letters for {num_recletts} " f"people this period"})
        mego = deepcopy(me)
        prof_service = filter_service(mego, begin_period, "profession")
        if num_proprevs > 0:
            prof_service.append(
                {"name": f"Reviewed {num_proprevs} funding proposals for " f"national agencies this period"}
            )
        if num_manrevs > 0:
            prof_service.append(
                {"name": f"Reviewed {num_manrevs} manuscripts for " f"peer reviewed journals this period"}
            )
        mego = deepcopy(me)
        phd_defenses = filter_committees(mego, begin_period, "phddefense")
        phd_proposals = filter_committees(mego, begin_period, "phdproposal")
        phd_orals = filter_committees(mego, begin_period, "phdoral")
        mego = deepcopy(me)
        outreach = filter_service(mego, begin_period, "outreach")
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
        # remove unpublished papers
        # unpubs = [pub for pub in pubs if len(pub.get("doi") == 0)]
        pubed = [pub for pub in pubs if len(pub.get("doi", "")) > 0]
        non_arts = [pub for pub in pubs if pub.get("entrytype") != "article"]
        pubs = pubed + non_arts
        bibfile = make_bibtex_file(pubs, pid=me["_id"], person_dir=self.bldir)
        articles = [prc for prc in pubs if prc.get("entrytype") == "article" and not prc.get("peer_rev_conf")]
        NONARTICLETYPES = [
            "book",
            "inbook",
            "proceedings",
            "inproceedings",
            "incollection",
            "unpublished",
            "phdthesis",
            "misc",
        ]
        nonarticles = [prc for prc in pubs if prc.get("entrytype") in NONARTICLETYPES]
        peer_rev_conf_pubs = [prc for prc in pubs if prc.get("peer_rev_conf")]

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
        if not me.get("miscellaneous"):
            me["miscellaneous"] = {"metrics_for_success": []}
        if me.get("hindex"):
            hindex = sorted(me["hindex"], key=doc_date_key).pop()
        #########################
        # render
        #########################
        self.render(
            "columbia_annual_report.tex",
            f"{pi['_id']}-ann-report.tex",
            pi=pi,
            p=me,
            projects=projs,
            pending=pending_grants,
            current=current_grants,
            declined=declined_proposals,
            undergrads=undergrads,
            masters=masters,
            currentphds=currents,
            graduatedphds=graduateds,
            postdocs=postdocs,
            visitors=visitors,
            ossoftware=ossoftware,
            phd_defenses=phd_defenses,
            phd_proposals=phd_proposals,
            phd_orals=phd_orals,
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
        self.pdf(f"{pi['_id']}-ann-report.tex")
