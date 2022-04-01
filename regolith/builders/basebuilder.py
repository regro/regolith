"""Builder Base Classes"""
import os
from xonsh.lib import subprocess
from glob import glob
from itertools import groupby

from jinja2 import Environment, FileSystemLoader

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.sorters import doc_date_key, category_val, level_val, date_key
from regolith.tools import (
    date_to_rfc822,
    rfc822now,
    gets,
    LATEX_OPTS,
    month_and_year,
    latex_safe,
    latex_safe_url)


class BuilderBase(object):
    """Base class for builders"""

    def __init__(self, rc):
        self.rc = rc
        self.bldir = os.path.join(rc.builddir, self.btype)
        # allow subclasses to override
        if not hasattr(self, "env"):
            self.env = Environment(
                loader=FileSystemLoader(
                    [
                        "templates",
                        os.path.join(
                            os.path.dirname(os.path.dirname(__file__)),
                            "templates",
                        ),
                    ]
                )
            )
        self.gtx = {}
        self.construct_global_ctx()
        self.cmds = []

    def construct_global_ctx(self):
        """Constructs the global context"""
        gtx = self.gtx
        gtx["len"] = len
        gtx["True"] = True
        gtx["False"] = False
        gtx["None"] = None
        gtx["sorted"] = sorted
        gtx["groupby"] = groupby
        gtx["gets"] = gets
        gtx["date_key"] = date_key
        gtx["doc_date_key"] = doc_date_key
        gtx["level_val"] = level_val
        gtx["category_val"] = category_val
        gtx["rfc822now"] = rfc822now
        gtx["date_to_rfc822"] = date_to_rfc822

    def render(self, tname, fname, **kwargs):
        """Render the template into a file using the kwargs and global context

        Parameters
        ----------
        tname : str
            Template name
        fname : str
            Resulting file name
        kwargs : dict
            Additional kwargs to the renderer
        """
        template = self.env.get_template(tname)
        ctx = dict(self.gtx)
        ctx.update(kwargs)
        ctx["rc"] = ctx.get("rc", self.rc)
        ctx["static"] = ctx.get(
            "static", os.path.relpath("static", os.path.dirname(fname))
        )
        ctx["root"] = ctx.get(
            "root", os.path.relpath("/", os.path.dirname(fname))
        )
        result = template.render(ctx)
        with open(os.path.join(self.bldir, fname), "wt", encoding='utf-8'
                  ) as f:
            f.write(result)

    def build(self):
        """Build the thing that is being built, note this runs all commands
        listed in ``self.cmds``"""
        os.makedirs(self.bldir, exist_ok=True)
        for cmd in self.cmds:
            getattr(self, cmd)()


class LatexBuilderBase(BuilderBase):
    """Base class for Latex builders"""

    def __init__(self, rc):
        super().__init__(rc)
        self.cmds = ["latex", "clean"]
        if HAVE_BIBTEX_PARSER:
            self.bibdb = BibDatabase()
            self.bibwriter = BibTexWriter()

    def construct_global_ctx(self):
        super().construct_global_ctx()
        gtx = self.gtx
        gtx["month_and_year"] = month_and_year
        gtx["latex_safe"] = latex_safe
        gtx["latex_safe_url"] = latex_safe_url

    def run(self, cmd):
        """Run command in build dir"""
        subprocess.run(cmd, cwd=self.bldir, check=True)

    def pdf(self, base):
        """Compiles latex files to PDF"""
        if self.rc.pdf:
            if os.name == 'nt':
                self.run(["pdflatex"] + LATEX_OPTS + [base + ".tex"])
            else:
                self.run(["latex"] + LATEX_OPTS + [base + ".tex"])
                self.run(["dvipdf", base])

    def clean(self):
        """Remove files created by latex"""
        postfixes = [
            "*.dvi",
            "*.toc",
            "*.aux",
            "*.out",
            "*.log",
            "*.bbl",
            "*.blg",
            "*.log",
            "*.spl",
            "*~",
            "*.spl",
            "*.run.xml",
            "*-blx.bib",
        ]
        to_rm = []
        for pst in postfixes:
            to_rm += glob(os.path.join(self.bldir, pst))
        for f in set(to_rm):
            os.remove(f)
