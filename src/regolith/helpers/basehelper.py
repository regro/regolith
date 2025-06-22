"""Builder Base Classes."""

import os
from glob import glob
from itertools import groupby

from jinja2 import Environment, FileSystemLoader
from xonsh.api import subprocess

from regolith.sorters import category_val, date_key, doc_date_key, level_val
from regolith.tools import LATEX_OPTS, date_to_rfc822, gets, latex_safe, latex_safe_url, month_and_year, rfc822now


class HelperBase(object):
    """Base class for helpers."""

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
        """Constructs the global context."""
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
        """Render the template into a file using the kwargs and global
        context.

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
        ctx["static"] = ctx.get("static", os.path.relpath("static", os.path.dirname(fname)))
        ctx["root"] = ctx.get("root", os.path.relpath("/", os.path.dirname(fname)))
        result = template.render(ctx)
        with open(os.path.join(self.bldir, fname), "wt", encoding="utf-8") as f:
            f.write(result)

    def hlp(self):
        """Run the helper, note this runs any of the commands listed in
        ``self.cmds``"""
        for cmd in self.cmds:
            getattr(self, cmd)()


class SoutHelperBase(HelperBase):
    """Base class for builders that just print to sout."""

    def __init__(self, rc):
        super().__init__(rc)
        self.cmds = ["sout"]


class DbHelperBase(HelperBase):
    """Base class for builders that update databases."""

    def __init__(self, rc):
        super().__init__(rc)
        self.cmds = ["db_updater"]


class LatexHelperBase(HelperBase):
    """Base class for Latex builders."""

    def __init__(self, rc):
        super().__init__(rc)
        self.cmds = ["latex", "clean"]

    #        if HAVE_BIBTEX_PARSER:
    #            self.bibdb = BibDatabase()
    #            self.bibwriter = BibTexWriter()

    def construct_global_ctx(self):
        super().construct_global_ctx()
        gtx = self.gtx
        gtx["month_and_year"] = month_and_year
        gtx["latex_safe"] = latex_safe
        gtx["latex_safe_url"] = latex_safe_url

    def run(self, cmd):
        """Run command in build dir."""
        subprocess.run(cmd, cwd=self.bldir, check=True)

    def pdf(self, base):
        """Compiles latex files to PDF."""
        if self.rc.pdf:
            self.run(["latex"] + LATEX_OPTS + [base + ".tex"])
            self.run(["bibtex"] + [base + ".aux"])
            self.run(["latex"] + LATEX_OPTS + [base + ".tex"])
            if os.name == "nt":
                self.run(["pdflatex"] + LATEX_OPTS + [base + ".tex"])
            else:
                self.run(["latex"] + LATEX_OPTS + [base + ".tex"])
                self.run(["dvipdf", base])

    def clean(self):
        """Remove files created by latex."""
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
