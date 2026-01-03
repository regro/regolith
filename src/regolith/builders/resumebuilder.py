"""Builder for Resumes."""

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.sorters import ene_date_key, position_key
from regolith.tools import (
    all_docs_from_collection,
    awards_grants_honors,
    filter_grants,
    filter_projects,
    filter_publications,
    fuzzy_retrieval,
    latex_safe,
    make_bibtex_file,
    merge_collections_superior,
    month_and_year,
)


class ResumeBuilder(LatexBuilderBase):
    """Build resume from database entries."""

    btype = "resume"
    needed_colls = ["institutions", "people", "grants", "citations", "projects", "proposals"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["month_and_year"] = month_and_year
        gtx["latex_safe"] = latex_safe
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def latex(self):
        """Render latex template."""
        rc = self.rc
        if rc.people:
            people = [fuzzy_retrieval(self.gtx["people"], ["aka", "_id", "name"], rc.people[0])]
        else:
            people = self.gtx["people"]

        for p in people:
            names = frozenset(p.get("aka", []) + [p["name"]])
            pubs = filter_publications(
                all_docs_from_collection(rc.client, "citations"),
                names,
                reverse=True,
            )
            bibfile = make_bibtex_file(pubs, pid=p["_id"], person_dir=self.bldir)
            emp = p.get("employment", [])
            emp = [em for em in emp if not em.get("not_in_cv", False)]
            for e in emp:
                e["position"] = e.get("position_full", e.get("position").title())
            emp.sort(key=ene_date_key, reverse=True)
            edu = p.get("education", [])
            edu.sort(key=ene_date_key, reverse=True)
            current_projects = filter_projects(all_docs_from_collection(rc.client, "projects"), names, active=True)
            past_projects = filter_projects(all_docs_from_collection(rc.client, "projects"), names, active=False)
            grants = list(all_docs_from_collection(rc.client, "grants"))
            proposals = list(all_docs_from_collection(rc.client, "proposals"))
            grants = merge_collections_superior(proposals, grants, "proposal_id")
            pi_grants, pi_amount, _ = filter_grants(grants, names, pi=True)
            coi_grants, coi_amount, coi_sub_amount = filter_grants(grants, names, pi=False)
            aghs = awards_grants_honors(p, "honors")
            self.render(
                "resume.tex",
                p["_id"] + ".tex",
                p=p,
                title=p.get("name", ""),
                aghs=aghs,
                pubs=pubs,
                names=names,
                bibfile=bibfile,
                education=edu,
                employment=emp,
                current_projects=current_projects,
                past_projects=past_projects,
                pi_grants=pi_grants,
                pi_amount=pi_amount,
                coi_grants=coi_grants,
                coi_amount=coi_amount,
                coi_sub_amount=coi_sub_amount,
            )
            self.pdf(p["_id"])
