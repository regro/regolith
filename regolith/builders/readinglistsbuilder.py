"""Builder for Reading Lists."""

from copy import deepcopy, copy
import datetime, sys

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    fuzzy_retrieval,
    number_suffix,
)
from regolith.stylers import sentencecase, month_fullnames
from regolith.dates import month_to_int


class ReadingListsBuilder(LatexBuilderBase):
    """Build reading lists from database entries"""

    btype = "readinglists"

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["reading_lists"] = sorted(
            all_docs_from_collection(rc.client, "reading_lists"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        # just a reminder placeholder how to access these.  These
        # print statements will be removed when the builder is updated
        # to use them!
        print(self.rc.from_date)
        print(self.rc.to_date)
        print(self.rc.people)
        print(self.rc.grants)

        for rlist in self.gtx["reading_lists"]:
            listid = rlist["_id"]
            outfile_bib = listid
            for paper in rlist:
                # fixme: code here to get info from crossref
                pass
            self.render(
                "rlistbibfile.bib",
                outfile_bib + ".bib",
                rlist=rlist,
            )
"""            self.render(
                "rlist_word.docx",
                outfile_bib + ".docx",
                rlist=rlist,
            )
"""