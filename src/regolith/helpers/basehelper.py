"""Builder Base Classes."""

import os
import subprocess
from glob import glob
from itertools import groupby

from jinja2 import Environment, FileSystemLoader

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

    def where_stored(self, collection, _id):
        """Return the name of the database holding a record, or None.

        A record is written where it is stored rather than in the first
        database that happens to be listed, since writing it anywhere
        else would leave two of it and hide the one that is real.  When
        two databases hold it already, a chained read takes each field
        from the last of them, so that is the one written: writing the
        other would change a copy nothing shows, and a document built
        from the collections would snap back to what it said before.

        Parameters
        ----------
        collection : str
            The name of the collection.
        _id : str
            The id of the record.

        Returns
        -------
        str or None
            The name of the database holding it, or None when nothing
            does.
        """
        holding = [
            database["name"]
            for database in self.rc.client.collection_sources(collection)
            if self.rc.client.find_one(database["name"], collection, {"_id": _id})
        ]
        if len(holding) > 1:
            print(
                f"{_id} is stored in both {' and '.join(holding)}. The copy in {holding[-1]} is the one "
                f"a read shows, so it is the one written; delete the other, or they will drift apart."
            )
        return holding[-1] if holding else None

    def first_source(self, collection):
        """Return the database a new record of a collection goes to.

        The first database holding the collection, or ``rc.database``
        when nothing holds it at all.
        """
        sources = self.rc.client.collection_sources(collection)
        return sources[0]["name"] if sources else self.rc.database


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
