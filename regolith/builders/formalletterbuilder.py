"""Builder for publication lists."""
from datetime import datetime
import string
import os
from dateutil import parser as date_parser

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase
    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.tools import all_docs_from_collection, filter_publications, make_bibtex_file
from regolith.sorters import ene_date_key, position_key
from regolith.builders.basebuilder import LatexBuilderBase

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
        try:
            rc.ranks_and_roles.update({'lc': 'Lieutenant Commander',
                       'co': 'Commanding Officer',
                       'fl': 'First Lieutenant', 'fls': '1stLt'})
        except AttributeError:
            rc.ranks_and_roles = {'lc': 'Lieutenant Commander',
                                       'co': 'Commanding Officer',
                                       'fl': 'First Lieutenant',
                                       'fls': '1stLt'}
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
            qualifiers = qualifiers + f"in the period from {from_date}"
            if self.rc.to_date:
                to_date = date_parser.parse(self.rc.to_date).date()
                filestub = filestub + "_to{}".format(to_date)
                qualifiers = qualifiers + " to {}".format(to_date)
            else:
                to_date = None
        else:
            from_date, to_date = None, None

        for letter in self.gtx["formalletters"]:
            if letter.get('date') is type(datetime.date):
                letter_date = letter.get('date')
            else:
                letter_date = date_parser.parse(letter.get('date')).date()
            letter['date'] = letter_date.strftime("%m/%e/%y").strip('0').replace(' ','')
            outfile_name_stub = f"{letter.get('_id')}"
            to = letter.get('to')
            if to.get('title') in self.rc.ranks_and_roles.keys():
                to['title'] = self.rc.ranks_and_roles.get(to.get('title'))
            nc_to = f"{to.get('title')} {to.get('name')} {to.get('postfix')}"
            fr = letter.get('from')
            if fr.get('title') in self.rc.ranks_and_roles.keys():
                fr['title'] = self.rc.ranks_and_roles.get(fr.get('title'))
            nc_fr = f"{fr.get('title')} {fr.get('name')} {fr.get('postfix')}"
            print(nc_fr)
            # The subject has to be upper case and have no trailing period, but what
            # if it wasn't entered in the DB like that...this ensures that it appears
            # this way in the final letter.
            letter["subject"] = letter["subject"].upper().strip('.')
            letter["encls"] = [f"({string.ascii_lowercase[i]}) {enc[:1].upper()+enc[1:].strip('.')}" for i, enc in
                               enumerate(letter["encls"])]
            letter["refs"] = [f"({string.ascii_lowercase[i]}) {ref[:1].upper()+ref[1:].strip('.')}" for i, ref in
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
