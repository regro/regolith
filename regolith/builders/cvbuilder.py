"""Builder for CVs."""
from copy import deepcopy
from datetime import  date

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.sorters import ene_date_key, position_key
from regolith.stylers import sentencecase, month_fullnames
from regolith.tools import (
    all_docs_from_collection,
    filter_publications,
    filter_projects,
    filter_grants,
    awards_grants_honors,
    make_bibtex_file,
    filter_employment_for_advisees,
    dereference_institution,
    merge_collections_superior,
    filter_presentations, remove_duplicate_docs,
    _id_key
)


class CVBuilder(LatexBuilderBase):
    """Build CV from database entries"""

    btype = "cv"
    needed_colls = ['institutions', 'people', 'grants', 'citations', 'projects',
                  'proposals', 'presentations']

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
        gtx["presentations"] = sorted(
            all_docs_from_collection(rc.client, "presentations"), key=_id_key
        )
        gtx["institutions"] = sorted(
            all_docs_from_collection(rc.client, "institutions"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def latex(self):
        """Render latex template"""
        rc = self.rc
        for p in self.gtx["people"]:
            # so we don't modify the dbs when de-referencing
            names = frozenset(p.get("aka", []) + [p["name"]] + [p["_id"]])
            begin_period = date(1650, 1, 1)

            pubs = filter_publications(
                all_docs_from_collection(rc.client, "citations"),
                names,
                reverse=True,
            )
            bibfile = make_bibtex_file(
                pubs, pid=p["_id"], person_dir=self.bldir
            )
            emp = p.get("employment", [])

            for e in emp:
                e['position'] = e.get('position_full', e.get('position').title())
            emp.sort(key=ene_date_key, reverse=True)
            edu = p.get("education", [])
            edu.sort(key=ene_date_key, reverse=True)
            teach = p.get("teaching", [])
            for t in teach:
                t['position'] = t.get('position').title()

            projs = filter_projects(
                all_docs_from_collection(rc.client, "projects"), names
            )
            just_grants = list(all_docs_from_collection(rc.client, "grants"))
            just_proposals = list(all_docs_from_collection(rc.client, "proposals"))
            grants = merge_collections_superior(just_proposals,
                                                just_grants,
                                                "proposal_id")
            presentations = filter_presentations(self.gtx["people"],
                               self.gtx["presentations"],
                               self.gtx["institutions"],
                               p.get("_id"),
                               statuses=["accepted"])

            for grant in grants:
                for member in grant.get("team"):
                    dereference_institution(member, self.gtx["institutions"])
            pi_grants, pi_amount, _ = filter_grants(grants, names, pi=True)
            coi_grants, coi_amount, coi_sub_amount = filter_grants(
                grants, names, pi=False
            )
            aghs = awards_grants_honors(p, "honors")
            service = awards_grants_honors(p, "service", funding=False)
            # TODO: pull this out so we can use it everywhere
            for ee in [emp, edu]:
                for e in ee:
                    dereference_institution(e, self.gtx["institutions"])

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
                                                        begin_period,
                                                        "phd")
            postdocs = filter_employment_for_advisees(self.gtx["people"],
                                                      begin_period,
                                                      "postdoc")
            postdocs = remove_duplicate_docs(postdocs, "name")
            visitors = filter_employment_for_advisees(self.gtx["people"],
                                                      begin_period,
                                                      "visitor-unsupported")
            visitors = remove_duplicate_docs(visitors, "name")

            iter = deepcopy(graduateds)
            for g in iter:
                if g.get("active"):
                    graduateds.remove(g)
            iter = deepcopy(currents)
            for g in iter:
                if not g.get("active"):
                    currents.remove(g)

            self.render(
                "cv.tex",
                p["_id"] + ".tex",
                p=p,
                title=p.get("name", ""),
                aghs=aghs,
                service=service,
                undergrads=undergrads,
                masters=masters,
                currentphds=currents,
                graduatedphds=graduateds,
                postdocs=postdocs,
                visitors=visitors,
                pubs=pubs,
                names=names,
                bibfile=bibfile,
                education=edu,
                employment=emp,
                presentations=presentations,
                sentencecase=sentencecase,
                monthstyle=month_fullnames,
                projects=projs,
                pi_grants=pi_grants,
                pi_amount=pi_amount,
                coi_grants=coi_grants,
                coi_amount=coi_amount,
                coi_sub_amount=coi_sub_amount,
            )
            self.pdf(p["_id"])
