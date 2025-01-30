"""Builder for Current and Pending Reports."""

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection


class PostdocadBuilder(LatexBuilderBase):
    """Build current and pending report from database entries."""

    btype = "postdocads"
    needed_colls = ["postdocads"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["postdocads"] = sorted(all_docs_from_collection(rc.client, "postdocads"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template."""
        for ads in self.gtx["postdocads"]:
            goals = ads["projectGoals"]
            positionOn = ads["positionOn"]
            projectTasks = ads["projectTasks"]
            requiredExperience = ads["requiredExperience"]
            additionalDesiredExperience = ads["additionalDesiredExperience"]
            startDate = ads["startDate"]
            thirdYear = ads["thirdyear"]
            k = ads["_id"]
            applicationDeadline = ads["applicationDeadline"]
            outname = "{}".format(k)
            self.render(
                "postdocad.tex",
                outname + ".tex",
                projectGoals=goals,
                positionOn=positionOn,
                projectTasks=projectTasks,
                requiredExperience=requiredExperience,
                additionalDesiredExperience=additionalDesiredExperience,
                startDate=startDate,
                thirdYear=thirdYear,
                k=k,
                applicationDeadline=applicationDeadline,
            )
            self.pdf("test")
