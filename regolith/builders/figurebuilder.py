"""Builder for Figure including documents."""
import os

from jinja2 import Environment, FileSystemLoader

from regolith.broker import Broker
from regolith.builders.basebuilder import LatexBuilderBase


class FigureBuilder(LatexBuilderBase):
    """Build resume from database entries"""
    btype = 'figure'
    
    def __init__(self, rc):
        super().__init__(rc)
        self.env = Environment(
            loader=FileSystemLoader(
                # TODO: pull this from the local folder (and lower folders)
                [
                    'templates', 
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        'templates'),
                ]
            )
        )
        self.db = Broker(rc)
    
    def construct_global_ctx(self):
        super().construct_global_ctx()
        gtx = self.gtx
        gtx['db'] = self.db.md
        gtx['get_file'] = self.db.get_file 
    
    def latex(self):
        """Render latex template"""
        rc = self.rc
        # TODO: pull local files?
        for f in local_tex_files:
            fn, ext = os.path.splitext(f)
            self.render(f, fn + '_rend' + ext)
            self.pdf(fn)