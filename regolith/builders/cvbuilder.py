"""Builder for CVs."""
from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.sorters import ene_date_key, position_key
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


class CVBuilder(LatexBuilderBase):
    """Build CV from database entries"""

    btype = "cv"
    needed_dbs = ['institutions', 'people', 'grants', 'citations', 'projects']

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
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def latex(self):
        """Render latex template"""
        rc = self.rc
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
            self.render(
                "cv.tex",
                p["_id"] + ".tex",
                p=p,
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
            )
            self.pdf(p["_id"])
