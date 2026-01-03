"""Builder for Current and Pending Reports."""

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection


class ManRevBuilder(LatexBuilderBase):
    """Build a manuscript review from database entries."""

    btype = "review-man"
    needed_colls = ["refereeReports"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["refereeReports"] = sorted(all_docs_from_collection(rc.client, "refereeReports"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template."""
        for rev in self.gtx["refereeReports"]:
            outname = "{}_{}".format(_id_key(rev), rev["reviewer"])
            self.render(
                "refreport_author.txt",
                outname + "_author.txt",
                trim_blocks=True,
                title=rev["title"],
                firstAuthorLastName=rev["first_author_last_name"],
                journal=rev["journal"],
                didWhat=rev["did_what"],
                didHow=rev["did_how"],
                foundWhat=rev["claimed_found_what"],
                whyImportant=rev["claimed_why_important"],
                validityAssessment=rev["validity_assessment"],
                finalAssessment=rev["final_assessment"],
                recommendation=rev["recommendation"],
                freewrite=rev["freewrite"],
            )
            if len(rev["editor_eyes_only"]) > 0:
                self.render(
                    "refreport_editor.txt",
                    outname + "_editor.txt",
                    title=rev["title"],
                    newline="\n",
                    firstAuthorLastName=rev["first_author_last_name"],
                    editorEyesOnly=rev["editor_eyes_only"],
                )
