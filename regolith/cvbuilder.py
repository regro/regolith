"""Builder for CVs."""
import os
import shutil
import subprocess
from glob import glob
from copy import deepcopy
from itertools import groupby

from jinja2 import Environment, FileSystemLoader
try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase
    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.tools import all_docs_from_collection, date_to_float, \
    date_to_rfc822, rfc822now, gets, month_and_year
from regolith.sorters import doc_date_key, ene_date_key, category_val, \
    level_val, id_key, date_key, position_key

LATEX_OPTS = ['-halt-on-error', '-file-line-error']

def latex_safe(s):
    return s.replace('&', '\&').replace('$', '\$').replace('#', '\#')

class CVBuilder(object):

    btype = 'cv'

    def __init__(self, rc):
        self.rc = rc
        self.bldir = os.path.join(rc.builddir, self.btype)
        self.env = Environment(loader=FileSystemLoader([
                    'templates',
                    os.path.join(os.path.dirname(__file__), 'templates'),
                    ]))
        self.construct_global_ctx()
        if HAVE_BIBTEX_PARSER:
            self.bibdb = BibDatabase()
            self.bibwriter = BibTexWriter()

    def construct_global_ctx(self):
        self.gtx = gtx = {}
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

    def render(self, tname, fname, **kwargs):
        template = self.env.get_template(tname)
        ctx = dict(self.gtx)
        ctx.update(kwargs)
        ctx['rc'] = ctx.get('rc', self.rc)
        ctx['static'] = ctx.get('static',
                               os.path.relpath('static', os.path.dirname(fname)))
        ctx['root'] = ctx.get('root', os.path.relpath('/', os.path.dirname(fname)))
        result = template.render(ctx)
        with open(os.path.join(self.bldir, fname), 'wt') as f:
            f.write(result)

    def build(self):
        os.makedirs(self.bldir, exist_ok=True)
        self.latex()
        self.pdf()
        self.clean()

    def latex(self):
        rc = self.rc
        for p in self.gtx['people']:
            names = frozenset(p.get('aka', []) + [p['name']])
            pubs = self.filter_publications(names, reverse=True)
            bibfile = self.make_bibtex_file(pubs, pid=p['_id'],
                                            person_dir=self.bldir)
            emp = p.get('employment', [])
            emp.sort(key=ene_date_key, reverse=True)
            edu = p.get('education', [])
            edu.sort(key=ene_date_key, reverse=True)
            projs = self.filter_projects(names)
            pi_grants, pi_amount, _ = self.filter_grants(names, pi=True)
            coi_grants, coi_amount, coi_sub_amount = self.filter_grants(names, pi=False)
            aghs = self.awards_grants_honors(p)
            self.render('cv.tex', p['_id'] + '.tex', p=p,
                        title=p.get('name', ''), aghs=aghs,
                        pubs=pubs, names=names, bibfile=bibfile,
                        education=edu, employment=emp, projects=projs,
                        pi_grants=pi_grants, pi_amount=pi_amount,
                        coi_grants=coi_grants, coi_amount=coi_amount,
                        coi_sub_amount=coi_sub_amount,
                        )

    def filter_publications(self, authors, reverse=False):
        rc = self.rc
        pubs = []
        for pub in all_docs_from_collection(rc.client, 'citations'):
            if len(set(pub['author']) & authors) == 0:
                continue
            pub = deepcopy(pub)
            bold_self = []
            for a in pub['author']:
                if a in authors:
                    bold_self.append('\\textbf{' + a + '}')
                else:
                    bold_self.append(a)
            pub['author'] = bold_self
            pubs.append(pub)
        pubs.sort(key=doc_date_key, reverse=reverse)
        return pubs

    def make_bibtex_file(self, pubs, pid, person_dir='.'):
        if not HAVE_BIBTEX_PARSER:
            return None
        skip_keys = set(['ID', 'ENTRYTYPE', 'author'])
        self.bibdb.entries = ents = []
        for pub in pubs:
            ent = dict(pub)
            ent['ID'] = ent.pop('_id')
            ent['ENTRYTYPE'] = ent.pop('entrytype')
            ent['author'] = ' and '.join(ent['author'])
            for key in ent.keys():
                if key in skip_keys:
                    continue
                ent[key] = latex_safe(ent[key])
            ents.append(ent)
        fname = os.path.join(person_dir, pid) + '.bib'
        with open(fname, 'w') as f:
            f.write(self.bibwriter.write(self.bibdb))
        return fname

    def filter_projects(self, authors, reverse=False):
        rc = self.rc
        projs = []
        for proj in all_docs_from_collection(rc.client, 'projects'):
            team_names = set(gets(proj['team'], 'name'))
            if len(team_names & authors) == 0:
                continue
            proj = dict(proj)
            proj['team'] = [x for x in proj['team'] if x['name'] in authors]
            projs.append(proj)
        projs.sort(key=id_key, reverse=reverse)
        return projs

    def filter_grants(self, names, pi=True, reverse=True):
        rc = self.rc
        grants = []
        total_amount = 0.0
        subaward_amount = 0.0
        for grant in all_docs_from_collection(rc.client, 'grants'):
            team_names = set(gets(grant['team'], 'name'))
            if len(team_names & names) == 0:
                continue
            grant = deepcopy(grant)
            person = [x for x in grant['team'] if x['name'] in names][0]
            if pi:
                if person['position'].lower() == 'pi':
                    total_amount += grant['amount']
                else:
                    continue
            else:
                if person['position'].lower() == 'pi':
                    continue
                else:
                    total_amount += grant['amount']
                    subaward_amount += person.get('subaward_amount', 0.0)
            grants.append(grant)
        grants.sort(key=ene_date_key, reverse=reverse)
        return grants, total_amount, subaward_amount

    def awards_grants_honors(self, p):
        """Make sorted awards grants and honrs list."""
        aghs = []
        for x in p.get('funding', ()):
            d = {'description': '{0} ({1}{2:,})'.format(latex_safe(x['name']),
                    x.get('currency', '$').replace('$', '\$'), x['value']),
                 'year': x['year'],
                 '_key': date_to_float(x['year'], x.get('month', 0)),
                 }
            aghs.append(d)
        for x in p.get('service', []) + p.get('honors', []):
            d = {'description': latex_safe(x['name']),
                 'year': x['year'],
                 '_key': date_to_float(x['year'], x.get('month', 0)),
                 }
            aghs.append(d)
        aghs.sort(key=(lambda x: x.get('_key', 0.0)), reverse=True)
        return aghs

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
