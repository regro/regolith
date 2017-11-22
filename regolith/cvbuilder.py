"""Builder for CVs."""
import os
import subprocess
from glob import glob
from itertools import groupby

from regolith.builder_base import BuilderBase

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.tools import all_docs_from_collection, date_to_rfc822, rfc822now, gets, month_and_year, \
    filter_publications, \
    filter_projects, filter_grants, awards_grants_honors, latex_safe, LATEX_OPTS, make_bibtex_file
from regolith.sorters import doc_date_key, ene_date_key, category_val, \
    level_val, date_key, position_key


class CVBuilder(BuilderBase):
    btype = 'cv'

    def __init__(self, rc):
        super().__init__(rc)
        self.cmds = ['latex', 'pdf', 'clean']

    def construct_global_ctx(self):
        gtx = self.gtx
        rc = self.rc
        gtx['len'] = len
        gtx['True'] = True
        gtx['False'] = False
        gtx['None'] = None
        gtx['sorted'] = sorted
        gtx['groupby'] = groupby
        gtx['gets'] = gets
        gtx['date_key'] = date_key
        gtx['doc_date_key'] = doc_date_key
        gtx['level_val'] = level_val
        gtx['category_val'] = category_val
        gtx['rfc822now'] = rfc822now
        gtx['date_to_rfc822'] = date_to_rfc822
        gtx['month_and_year'] = month_and_year
        gtx['latex_safe'] = latex_safe
        gtx['people'] = sorted(all_docs_from_collection(rc.client, 'people'),
                               key=position_key, reverse=True)
        gtx['all_docs_from_collection'] = all_docs_from_collection

    def latex(self):
        rc = self.rc
        for p in self.gtx['people']:
            names = frozenset(p.get('aka', []) + [p['name']])
            pubs = filter_publications(
                all_docs_from_collection(rc.client, 'citations'),
                names, reverse=True)
            bibfile = make_bibtex_file(pubs, pid=p['_id'],
                                       person_dir=self.bldir)
            emp = p.get('employment', [])
            emp.sort(key=ene_date_key, reverse=True)
            edu = p.get('education', [])
            edu.sort(key=ene_date_key, reverse=True)
            projs = filter_projects(
                all_docs_from_collection(rc.client, 'projects'), names)
            pi_grants, pi_amount, _ = filter_grants(names, pi=True)
            coi_grants, coi_amount, coi_sub_amount = filter_grants(
                all_docs_from_collection(rc.client, 'grants'), names, pi=False)
            aghs = awards_grants_honors(p)
            self.render('cv.tex', p['_id'] + '.tex', p=p,
                        title=p.get('name', ''), aghs=aghs,
                        pubs=pubs, names=names, bibfile=bibfile,
                        education=edu, employment=emp, projects=projs,
                        pi_grants=pi_grants, pi_amount=pi_amount,
                        coi_grants=coi_grants, coi_amount=coi_amount,
                        coi_sub_amount=coi_sub_amount,
                        )

    def pdf(self):
        """Compiles latex files to PDF"""
        for p in self.gtx['people']:
            base = p['_id']
            self.run(['latex'] + LATEX_OPTS + [base + '.tex'])
            self.run(['bibtex'] + [base + '.aux'])
            self.run(['latex'] + LATEX_OPTS + [base + '.tex'])
            self.run(['latex'] + LATEX_OPTS + [base + '.tex'])
            self.run(['dvipdf', base])

    def run(self, cmd):
        subprocess.run(cmd, cwd=self.bldir, check=True)

    def clean(self):
        postfixes = ['*.dvi', '*.toc', '*.aux', '*.out', '*.log', '*.bbl',
                     '*.blg', '*.log', '*.spl', '*~', '*.spl', '*.run.xml',
                     '*-blx.bib']
        to_rm = []
        for pst in postfixes:
            to_rm += glob(os.path.join(self.bldir, pst))
        for f in set(to_rm):
            os.remove(f)
