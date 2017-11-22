"""Builder Base Class"""
import os
import shutil
from copy import deepcopy
from itertools import groupby

from jinja2 import Environment, FileSystemLoader

from regolith.latex import make_bibtex_file

from regolith.tools import all_docs_from_collection, date_to_rfc822, \
    rfc822now, gets
from regolith.sorters import doc_date_key, ene_date_key, category_val, \
    level_val, id_key, date_key, position_key


class BuilderBase(object):
    def __init__(self, rc):
        self.rc = rc
        self.bldir = os.path.join(rc.builddir, self.btype)
        self.env = Environment(loader=FileSystemLoader([
            'templates',
            os.path.join(os.path.dirname(__file__), 'templates'),
        ]))
        self.gtx = {}
        self.construct_global_ctx()
        self.cmds = []

    def render(self, tname, fname, **kwargs):
        template = self.env.get_template(tname)
        ctx = dict(self.gtx)
        ctx.update(kwargs)
        ctx['rc'] = ctx.get('rc', self.rc)
        ctx['static'] = ctx.get('static',
                                os.path.relpath('static',
                                                os.path.dirname(fname)))
        ctx['root'] = ctx.get('root',
                              os.path.relpath('/', os.path.dirname(fname)))
        result = template.render(ctx)
        with open(os.path.join(self.bldir, fname), 'wt') as f:
            f.write(result)

    def build(self):
        os.makedirs(self.bldir, exist_ok=True)
        for cmd in self.cmds:
            getattr(self, cmd)()
