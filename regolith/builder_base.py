"""Builder Base Class"""
import os
from itertools import groupby

from jinja2 import Environment, FileSystemLoader

from regolith.sorters import doc_date_key, category_val, \
    level_val, date_key
from regolith.tools import date_to_rfc822, rfc822now, gets


class BuilderBase(object):
    """Base class for builders"""
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

    def construct_global_ctx(self):
        """Constructs the global context"""
        gtx = self.gtx
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

    def render(self, tname, fname, **kwargs):
        """Render the template into a file using the kwargs and global context

        Parameters
        ----------
        tname: str
            Template name
        fname: str
            Resulting file name
        kwargs: dict
            Additional kwargs to the renderer
        """
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
        """Build the thing that is being built, note this runs all commands
        listed in ``self.cmds``"""
        os.makedirs(self.bldir, exist_ok=True)
        for cmd in self.cmds:
            getattr(self, cmd)()
