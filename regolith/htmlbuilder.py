"""Builder for websites."""
import os
import shutil

from jinja2 import Environment, FileSystemLoader

from regolith.tools import all_docs_from_collection


class HtmlBuilder(object):

    btype = 'html'

    def __init__(self, rc):
        self.rc = rc
        self.bldir = os.path.join(rc.builddir, self.btype)
        self.env = Environment(loader=FileSystemLoader([
                    'templates',
                    os.path.join(os.path.dirname(__file__), 'templates'),
                    ]))

    def render(self, tname, fname, **ctx):
        template = self.env.get_template(tname)
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
        for p in all_docs_from_collection(rc.client, 'people'):
            peeps.append(p)
        self.render('people.html', os.path.join('people', 'index.html'), people=peeps,
                    title='People')
        
