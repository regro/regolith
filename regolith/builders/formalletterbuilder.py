"""Builder for publication lists."""
from datetime import datetime

import string

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
RANKS_AND_ROLES = {'lc': 'Lieutenant Commander',
                   'co': 'Commanding Officer',
                   'fl': 'First Lieutenant', 'fls': '1stLt'}


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
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

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
            letter_date = date_parser.parse(letter.get('date')).date()
            letter['date'] = letter_date.strftime("%m/%e/%y").strip('0').replace(' ','')
            outfile_name_stub = f"{letter.get('_id')}"
            to = letter.get('to')
            if to.get('title') in RANKS_AND_ROLES.keys():
                to['title'] = RANKS_AND_ROLES.get(to.get('title'))
            nc_to = f"{to.get('title')} {to.get('name')} {to.get('postfix')}"
            fr = letter.get('from')
            if fr.get('title') in RANKS_AND_ROLES.keys():
                fr['title'] = RANKS_AND_ROLES.get(fr.get('title'))
            nc_fr = f"{fr.get('title')} {fr.get('name')} {fr.get('postfix')}"
            print(nc_fr)
            # The subject has to be upper case and have no trailing period, but what
            # if it wasn't entered in the DB like that...this ensures that it appears
            # this way in the final letter.
            letter["subject"] = letter["subject"].upper().strip('.')
            letter["encls"] = [f"({string.ascii_lowercase[i]}) {enc.strip('.').capitalize()}" for i, enc in
                               enumerate(letter["encls"])]
            letter["refs"] = [f"({string.ascii_lowercase[i]}) {ref.strip('.').capitalize()}" for i, ref in
                               enumerate(letter["refs"])]
            # ensure that all paras end in a (single) period
            letter['paras'] = [f"{para.strip('.').capitalize()}." for para in letter.get('paras', '')]
            self.render(
                "naval_correspondence.tex",
                outfile_name_stub + "_nc.tex",
                contents=letter,
                to=nc_to,
                fr=nc_fr
            )

            # Izzy, add more things here as you need them

            # everything above was collecting and cleaning the database info. Now
            # below we just send the things to be rendered into the template by
            # Jinja2
            # loaded_template = open(tmpl_file, 'r').read()
            # doc = Template(loaded_template)
            # print(contents)
            # with open(outfile, 'w') as o:
            #     o.write(doc.render(contents=letter,
            #                        to=to_field,
            #                        fr=fr_field,
            #                        )
            #             )

            # if p.get("_id") in self.rc.people or self.rc.people == ['all']:
            #     # if self.rc.people[0] != 'all':
            #     #     if p.get("_id") != self.rc.people[0]:
            #     #         continue
            #     outfile = p["_id"] + filestub
            #     p['qualifiers'] = qualifiers
            #     names = frozenset(p.get("aka", []) + [p["name"]])
            #     citations = list(self.gtx["citations"])
            #     grants = self.rc.grants
            #
            #     pubs_nobold = filter_publications(citations, names, reverse=True, bold=False,
            #                                       ackno=False, since=from_date,
            #                                       before=to_date, grants=grants)
            #     pubs_ackno = filter_publications(citations, names, reverse=True,
            #                                      bold=False, ackno=True,
            #                                      since=from_date,
            #                                      before=to_date, grants=grants)
            #     pubs = filter_publications(citations, names, reverse=True, ackno=False,
            #                                bold=True, since=from_date,
            #                                before=to_date, grants=grants)
            #
            #     bibfile = make_bibtex_file(
            #         pubs, pid=p["_id"], person_dir=self.bldir
            #     )
            #     bibfile_nobold = make_bibtex_file(
            #         pubs_nobold, pid=f"{p['_id']}_nobold", person_dir=self.bldir
            #     )
            #     bibfile_ackno = make_bibtex_file(
            #         pubs_ackno, pid=f"{p['_id']}_ackno", person_dir=self.bldir
            #     )
            #     if not p.get('email'):
            #         p['email'] = ""
            #     emp = p.get("employment", [{'organization': ""}])
            #     emp.sort(key=ene_date_key, reverse=True)

    def filter_pubs_by_grant(self, pubs, grants):
        if isinstance(grants, str):
            grants = [grants]
        filtered_pubs = []
        for pub in pubs:
            for grant in grants:
                if grant in pub.get("grant",""):
                    filtered_pubs.append(pub)
        return filtered_pubs
