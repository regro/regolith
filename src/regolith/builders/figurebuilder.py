"""Builder for Figure including documents."""

import os

from jinja2 import Environment, FileSystemLoader

from regolith.broker import Broker
from regolith.builders.basebuilder import LatexBuilderBase
from regolith.tools import fuzzy_retrieval


class FigureBuilder(LatexBuilderBase):
    """Build resume from database entries."""

    btype = "figure"

    def __init__(self, rc):
        self.env = Environment(loader=FileSystemLoader(["."]))
        self.db = Broker(rc)
        super().__init__(rc)

    def construct_global_ctx(self):
        super().construct_global_ctx()
        gtx = self.gtx
        gtx["db"] = self.db.md
        gtx["get_file_path"] = self.db.get_file_path
        gtx["fuzzy_retrieval"] = fuzzy_retrieval

    def latex(self):
        """Render latex template."""
        for f in [ff for ff in os.listdir(".") if ff.endswith(".tex")]:
            fn, ext = os.path.splitext(f)
            self.render(f, fn + "_rend" + ext)
            self.pdf(fn + "_rend")
