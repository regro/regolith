"""Builder for websites."""
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

from regolith.tools import all_docs_from_collection, year_month_to_float


doc_date_key = lambda x: year_month_to_float(x.get('year', 1970), 
                                             x.get('month', 'jan'))
ene_date_key = lambda x: year_month_to_float(x.get('end_year', 1970), 
                                             x.get('end_month', 'jan'))
category_val = lambda x: x.get('category', '<uncategorized>')
level_val = lambda x: x.get('level', '<no-level>')
id_key = lambda x: x.get('_id', '')

def date_key(x):
    if 'end_year' in x:
        v = year_month_to_float(x['end_year'], x.get('end_month', 'jan'))
    elif 'year' in x:
        v = year_month_to_float(x['year'], x.get('month', 'jan'))
    elif 'begin_year' in x:
        v = year_month_to_float(x['begin_year'], x.get('begin_month', 'jan'))
    else:
        raise KeyError('could not find year in ' + str(x))
    return v


def gets(seq, key, default=None):
    """Gets a key from every element of a sequence if possible."""
    for x in seq:
        yield x.get(key, default)


class HtmlBuilder(object):

    btype = 'html'

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
        gtx['people'] = list(all_docs_from_collection(rc.client, 'people'))

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
        rc = self.rc
        os.makedirs(self.bldir, exist_ok=True)
        self.people()
        # static
        stsrc = os.path.join('templates', 'static')
        stdst = os.path.join(self.bldir, 'static')
        if os.path.isdir(stdst):
            shutil.rmtree(stdst)
        shutil.copytree(stsrc, stdst)

    def people(self):
        rc = self.rc
        peeps_dir = os.path.join(self.bldir, 'people')
        os.makedirs(peeps_dir, exist_ok=True)
        peeps = []
        for p in self.gtx['people']:
            names = frozenset(p.get('aka', []) + [p['name']])
            pubs = self.filter_publications(names, reverse=True)
            bibfile = self.make_bibtex_file(pubs, pid=p['_id'], person_dir=peeps_dir)
            ene = p.get('employment', []) + p.get('education', [])
            ene.sort(key=ene_date_key, reverse=True)
            projs = self.filter_projects(names)
            self.render('person.html', os.path.join('people', p['_id'] + '.html'), p=p,
                        title=p.get('name', ''), pubs=pubs, names=names, bibfile=bibfile, 
                        education_and_employment=ene, projects=projs)
        self.render('people.html', os.path.join('people', 'index.html'), title='People')

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
