"""Builder for publication lists."""
import os
import datetime as dt

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.tools import all_docs_from_collection, is_between
from regolith.sorters import doc_date_key, ene_date_key, position_key
from regolith.builders.basebuilder import LatexBuilderBase, latex_safe

LATEX_OPTS = ["-halt-on-error", "-file-line-error"]


class PubListBuilder(LatexBuilderBase):
    btype = "publist"
    needed_dbs = ['citations', 'people']

    def construct_global_ctx(self):
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc

        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def latex(self):
        fd = gr = False
        filestub, qualifiers = "", ""
        if self.rc.from_date:
            fd = True
            from_date = self.rc.from_date
            sy = from_date.split("-")[0]
            sm = int(from_date.split("-")[1])
            sd = int(from_date.split("-")[2])
            filestub = filestub + "_from{}".format(from_date)
            qualifiers = qualifiers + "in the period from {}".format(from_date)
            if self.rc.to_date:
                to_date = self.rc.to_date
                filestub = filestub + "_to{}".format(to_date)
                qualifiers = qualifiers + " to {}".format(to_date)
            else:
                to_date = dt.datetime.date(dt.datetime.today()).isoformat()
            by = to_date.split("-")[0]
            bm = int(to_date.split("-")[1])
            bd = int(to_date.split("-")[2])
        if self.rc.grants:
            gr = True
            grants = self.rc.grants
            if isinstance(grants, str):
                grants = [grants]
            if len(grants) > 2:
                text_grants = ", and ".join([",".join(grants[:-1]), grants[-1]])
            elif len(grants) == 2:
                text_grants = "and ".join([",".join(grants[0]), grants[1]])
            elif len(grants) == 1:
                text_grants = grants[0]
            cat_grants, all_grants = "", ""
            for g in grants:
                cat_grants = cat_grants + "_" + g
            filestub = filestub + "".format(cat_grants)
            qualifiers = qualifiers + " from grants {}".format(text_grants)

        for p in self.gtx["people"]:
            outfile = p["_id"] + filestub
            p['qualifiers'] = qualifiers
            names = frozenset(p.get("aka", []) + [p["name"]])
            pubs = self.filter_publications(names, reverse=True)

            if fd:
                dpubs = self.filter_pubs_by_date(pubs, sy, sm, sd, by, bm, bd)
                pubs = dpubs

            if gr:
                gpubs = self.filter_pubs_by_grant(pubs, grants)
                pubs = gpubs

            bibfile = self.make_bibtex_file(
                pubs, pid=p["_id"], person_dir=self.bldir
            )
            if not p.get('email'):
                p['email'] = ""
            emp = p.get("employment", [{'organization': ""}])
            emp.sort(key=ene_date_key, reverse=True)
            self.render(
                "publist.tex",
                outfile + ".tex",
                p=p,
                title=p.get("name", ""),
                pubs=pubs,
                names=names,
                bibfile=bibfile,
                employment=emp,
            )
            self.pdf(p["_id"])

    def filter_publications(self, authors, reverse=False):
        rc = self.rc
        pubs = []
        for pub in all_docs_from_collection(rc.client, "citations"):
            if len(set(pub["author"]) & authors) == 0:
                continue
            bold_self = []
            for a in pub["author"]:
                if a in authors:
                    bold_self.append("\\textbf{" + a + "}")
                else:
                    bold_self.append(a)
            pub["author"] = bold_self
            pubs.append(pub)
        pubs.sort(key=doc_date_key, reverse=reverse)
        return pubs

    def filter_pubs_by_date(self, pubs, sy, sm, sd, by, bm, bd):
        filtered_pubs = []
        for pub in pubs:
            month = pub.get("month", 1)
            day = pub.get("day", 1)
            if is_between(int(pub.get("year")), sy, by, m=month, sm=sm,
                          bm=bm,
                          d=day, sd=sd, bd=bd):
                filtered_pubs.append(pub)
        return filtered_pubs

    def filter_pubs_by_grant(self, pubs, grants):
        if isinstance(grants, str):
            grants = [grants]
        filtered_pubs = []
        for pub in pubs:
            for grant in grants:
                if grant in pub.get("grant",""):
                    filtered_pubs.append(pub)
        return filtered_pubs

    def make_bibtex_file(self, pubs, pid, person_dir="."):
        if not HAVE_BIBTEX_PARSER:
            return None
        skip_keys = set(["ID", "ENTRYTYPE", "author"])
        self.bibdb.entries = ents = []
        for pub in pubs:
            ent = dict(pub)
            ent["ID"] = ent.pop("_id")
            ent["ENTRYTYPE"] = ent.pop("entrytype")
            ent["author"] = " and ".join(ent["author"])
            for key in ent.keys():
                if key in skip_keys:
                    continue
            ents.append(ent)
        fname = os.path.join(person_dir, pid) + ".bib"
        with open(fname, "w", encoding='utf-8') as f:
            f.write(self.bibwriter.write(self.bibdb))
        return fname
