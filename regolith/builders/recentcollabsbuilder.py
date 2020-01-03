"""Builder for publication lists."""
import os
import datetime as dt
from dateutil.relativedelta import relativedelta

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.tools import all_docs_from_collection, filter_publications, \
    is_since, fuzzy_retrieval
from regolith.sorters import doc_date_key, ene_date_key, position_key
from regolith.builders.basebuilder import LatexBuilderBase, latex_safe

LATEX_OPTS = ["-halt-on-error", "-file-line-error"]


class RecentCollabsBuilder(LatexBuilderBase):
    btype = "recent-collabs"

    def construct_global_ctx(self):
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc

        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["citations"] = all_docs_from_collection(rc.client, "citations")
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def latex(self):
        rc = self.rc
        since_date = dt.date.today() - relativedelta(months=48)
        for p in self.gtx["people"]:
            if p["_id"] == "sbillinge":
                my_names = frozenset(p.get("aka", []) + [p["name"]])
                pubs = filter_publications(self.gtx["citations"], my_names,
                                           reverse=True, bold=False)
                my_collabs = []
                for pub in pubs:
                    if is_since(pub.get("year"), since_date.year, pub.get("month", 1), since_date.month):
                        if not pub.get("month"):
                            print("WARNING: {} is missing month".format(
                                pub["_id"]))
                        my_collabs.extend([collabs for collabs in
                                           [names for names in
                                            pub.get('author', [])]])
                people = []
                for collab in my_collabs:
                    people.append(fuzzy_retrieval(self.gtx["people"],
                                  ["name", "aka", "_id"], collab))
                institutions = [places[0]["institution"] for places in
                                [person["education"] for person in people if person]]
                ppl_names = [person["name"] for person in people if person]
#                print(set([person["name"] for person in people if person]))
                print(set([(person,institution) for person, institution in zip(ppl_names, institutions)]))
            emp = p.get("employment", [])
            emp.sort(key=ene_date_key, reverse=True)
            self.render(
                "recentcollabs.csv",
                p["_id"] + ".csv",
                p=p,
                title=p.get("name", ""),
                pubs=pubs,
                employment=emp,
                collabs=my_collabs
            )

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
