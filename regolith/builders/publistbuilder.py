"""Builder for publication lists."""
import os

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.tools import all_docs_from_collection
from regolith.sorters import doc_date_key, ene_date_key, position_key
from regolith.builders.basebuilder import LatexBuilderBase, latex_safe

LATEX_OPTS = ["-halt-on-error", "-file-line-error"]


class PubListBuilder(LatexBuilderBase):

    btype = "publist"

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
        rc = self.rc
        for p in self.gtx["people"]:
            names = frozenset(p.get("aka", []) + [p["name"]])
            pubs = self.filter_publications(names, reverse=True)
            bibfile = self.make_bibtex_file(
                pubs, pid=p["_id"], person_dir=self.bldir
            )
            emp = p.get("employment", [])
            emp.sort(key=ene_date_key, reverse=True)
            self.render(
                "publist.tex",
                p["_id"] + ".tex",
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
