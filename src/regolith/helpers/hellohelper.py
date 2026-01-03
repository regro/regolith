"""Builder for Current and Pending Reports."""

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import all_docs_from_collection


def subparser(subpi):
    subpi.add_argument("--person", help="pi first name space last name in quotes", default=None)
    return subpi


class HelloHelper(SoutHelperBase):
    """Build a helper."""

    btype = "hello"
    needed_colls = ["test"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["test"] = sorted(all_docs_from_collection(rc.client, "test"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        person = self.rc.person
        return print(f"hello {person}")

    def latex(self):
        """Render latex template."""
        for rev in self.gtx["refereeReports"]:
            outname = "{}_{}".format(_id_key(rev), rev["reviewer"])
            self.render(
                "mt.txt",
                outname + ".txt",
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
                    firstAuthorLastName=rev["first_author_last_name"],
                    editorEyesOnly=rev["editor_eyes_only"],
                )
