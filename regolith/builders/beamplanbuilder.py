"""Builder for Current and Pending Reports."""
from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection


class BeamPlanBuilder(LatexBuilderBase):
    """
    Build a report of experiment plans for the beamtime from database entries. The report is in .tex file. The
    template of the file is in the 'templates/beamplan.txt'.
    """
    btype = "beamplan"
    needed_dbs = ['beamplan', "people"]

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["beamplan"] = all_docs_from_collection(rc.client, "beamplan")
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str

    def make_table(self):
        """
        Make a table as the summary of the plans. The table header contains: serial id, person name,
        number of sample, sample container, sample holder, measurement, estimated time (min). The latex string of the
        table will be returned.

        Returns
        -------
        summary : str
            The latex string of table.

        """
        gtx = self.gtx
        summary = ""
        return summary

    def make_plans(self):
        """
        Make a list of experiment plans. The plans contain objective, steps in preparation, steps in shipment and
        steps in experiment. The latex string of the paragraphs will be returned.

        Returns
        -------
        plans : list
            The list of experiment plans.

        """
        gtx = self.gtx
        plans = []
        return plans

    def latex(self):
        """Render latex template"""
        table = self.make_table()
        plans = self.make_plans()
        self.render("beamplan.txt", "beamplan_report.tex", table=table, plans=plans)
