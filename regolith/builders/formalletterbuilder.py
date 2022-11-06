"""Builder for publication lists."""
import os

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.tools import all_docs_from_collection, filter_publications, make_bibtex_file
from regolith.sorters import ene_date_key, position_key
from regolith.builders.basebuilder import LatexBuilderBase
from dateutil import parser as date_parser

LATEX_OPTS = ["-halt-on-error", "-file-line-error"]


class FormalLetterBuilder(LatexBuilderBase):
    btype = "formalletter"
    needed_colls = ['formalletters']

    def construct_global_ctx(self):
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if not rc.people:
            rc.people = ['all']
        if isinstance(rc.people, str):
            rc.people = [rc.people]

        gtx["formalletters"] = sorted(
            all_docs_from_collection(rc.client, "formalletters"),
            key=position_key,
            reverse=True,
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def latex(self):
        fd = gr = False
        filestub, qualifiers = "", ""
        if self.rc.from_date:
            from_date = date_parser.parse(self.rc.from_date).date()
            filestub = filestub + "_from{}".format(from_date)
            qualifiers = qualifiers + "in the period from {}".format(from_date)
            if self.rc.to_date:
                to_date = date_parser.parse(self.rc.to_date).date()
                filestub = filestub + "_to{}".format(to_date)
                qualifiers = qualifiers + " to {}".format(to_date)
            else:
                to_date = None
        else:
            from_date, to_date = None, None

        for letter in self.gtx["formalletters"]:
            if p.get("_id") in self.rc.people or self.rc.people == ['all']:
                # if self.rc.people[0] != 'all':
                #     if p.get("_id") != self.rc.people[0]:
                #         continue
                outfile = p["_id"] + filestub
                p['qualifiers'] = qualifiers
                names = frozenset(p.get("aka", []) + [p["name"]])
                citations = list(self.gtx["citations"])
                grants = self.rc.grants

                pubs_nobold = filter_publications(citations, names, reverse=True, bold=False,
                                                  ackno=False, since=from_date,
                                                  before=to_date, grants=grants)
                pubs_ackno = filter_publications(citations, names, reverse=True,
                                                 bold=False, ackno=True,
                                                 since=from_date,
                                                 before=to_date, grants=grants)
                pubs = filter_publications(citations, names, reverse=True, ackno=False,
                                           bold=True, since=from_date,
                                           before=to_date, grants=grants)

                bibfile = make_bibtex_file(
                    pubs, pid=p["_id"], person_dir=self.bldir
                )
                bibfile_nobold = make_bibtex_file(
                    pubs_nobold, pid=f"{p['_id']}_nobold", person_dir=self.bldir
                )
                bibfile_ackno = make_bibtex_file(
                    pubs_ackno, pid=f"{p['_id']}_ackno", person_dir=self.bldir
                )
                if not p.get('email'):
                    p['email'] = ""
                emp = p.get("employment", [{'organization': ""}])
                emp.sort(key=ene_date_key, reverse=True)
                self.render(
                    "naval_correspondence.tex",
                    outfile + "_nc.tex",
                    p=p,
                    title=p.get("name", ""),
                    pubs=pubs,
                    names=names,
                    bibfile=bibfile,
                    employment=emp,
                )

    def filter_pubs_by_grant(self, pubs, grants):
        if isinstance(grants, str):
            grants = [grants]
        filtered_pubs = []
        for pub in pubs:
            for grant in grants:
                if grant in pub.get("grant",""):
                    filtered_pubs.append(pub)
        return filtered_pubs
