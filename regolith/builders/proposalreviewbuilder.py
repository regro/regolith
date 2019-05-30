"""Builder for Proposal Reivews."""
import datetime
import time
from nameparser import HumanName

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import month_to_int
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    filter_grants,
    fuzzy_retrieval,
)


class PropRevBuilder(LatexBuilderBase):
    """Build a proposal review from database entries"""
    btype = "propreview"

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["proposalReviews"] = sorted(
            all_docs_from_collection(rc.client, "proposalReviews"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        for rev in self.gtx["proposalReviews"]:
            outname = "{}_{}".format(_id_key(rev),rev["reviewer"])
            multiauth = False
            if isinstance(rev["name"],str):
                rev["name"] = [rev["name"]]
            if len(rev["name"]) > 1:
                multiauth = True
            firstauthor = HumanName(rev["name"][0])
            firstauthorlastname = firstauthor.last
            self.render(
                "propreport_author.txt",
                outname + ".txt",
                trim_blocks=True,
                agency=agency,
                appropriateness=rev["appropriateness_of_approach"],
                title=rev["title"],
                multiauthor=multiauth,
                firstAuthorLastName=firstauthorlastname,
                journal=rev["journal"],
                didWhat=rev["did_what"],
                didHow=rev["did_how"],
                goals=rev["goals"],
                whyImportant=rev["why_important"],
                validityAssessment=rev["validity_assessment"],
                finalAssessment=rev["final_assessment"],
                recommendation=rev["recommendation"],
                freewrite=rev["freewrite"]
            )
        if len(rev["editor_eyes_only"]) > 0:
            self.render(
                "refreport_editor.txt",
                outname + "_editor.txt",
                title=title,
                firstAuthorLastName=firstAuthorLastName,
                editorEyesOnly=rev["editor_eyes_only"],
            )
