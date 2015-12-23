"""Builder for CVs."""
import os
import shutil
from itertools import groupby

from jinja2 import Environment, FileSystemLoader
try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase
    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.tools import all_docs_from_collection, date_to_float, \
    date_to_rfc822, orfc822now, gets
from regolith import doc_date_key, ene_date_key, category_val, level_val, \
    id_key, date_key, position_key


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
        self.cv()
        # static
        #stsrc = os.path.join('templates', 'static')
        #stdst = os.path.join(self.bldir, 'static')
        #if os.path.isdir(stdst):
        #    shutil.rmtree(stdst)
        #shutil.copytree(stsrc, stdst)

    def people(self):
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
            self.render('cv.tex', p['_id'] + '.tex'), p=p,
                        title=p.get('name', ''), 
                        pubs=pubs, names=names, bibfile=bibfile, 
                        education=edu, employment=emp, projects=projs)

    def filter_publications(self, authors, reverse=False):
        rc = self.rc
        pubs = []
        for pub in all_docs_from_collection(rc.client, 'citations'):
            if len(set(pub['author']) & authors) == 0:
                continue
            pubs.append(pub)
        pubs.sort(key=doc_date_key, reverse=reverse)
        return pubs

    def make_bibtex_file(self, pubs, pid, person_dir='.'):
        if not HAVE_BIBTEX_PARSER:
            return None
        self.bibdb.entries = ents = []
        for pub in pubs:
            ent = dict(pub)
            ent['ID'] = ent.pop('_id')
            ent['ENTRYTYPE'] = ent.pop('entrytype')
            ent['author'] = ' and '.join(ent['author'])
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

