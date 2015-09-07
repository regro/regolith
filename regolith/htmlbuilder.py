"""Builder for websites."""
import os
import shutil

from jinja2 import Environment, FileSystemLoader

from regolith.tools import all_docs_from_collection, year_month_to_float


pub_date_key = lambda pub: year_month_to_float(pub.get('year', 1970), 
                                               pub.get('month', 'jan'))


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

    def construct_global_ctx(self):
        self.gtx = gtx = {}
        rc = self.rc
        gtx['people'] = list(all_docs_from_collection(rc.client, 'people'))
        gtx['len'] = len

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
            self.render('person.html', os.path.join('people', p['_id'] + '.html'), p=p,
                        title=p.get('name', ''), pubs=pubs, names=names)
        self.render('people.html', os.path.join('people', 'index.html'), title='People')

    def filter_publications(self, authors, reverse=False):
        rc = self.rc
        pubs = []
        for pub in all_docs_from_collection(rc.client, 'citations'):
            if len(set(pub['author']) & authors) == 0:
                continue
            pubs.append(pub)
        pubs.sort(key=pub_date_key, reverse=reverse)
        return pubs
        
