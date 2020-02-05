"""Builder for Current and Pending Reports."""
from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection
import pandas as pd


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

    def gather_info(self):
        """
        Make a table as the summary of the plans and a list of experiment plans. The table header contains: serial
        id, person name, number of sample, sample container, sample holder, measurement, estimated time (min). The
        latex string of the table will be returned. The plans contain objective, steps in preparation,
        steps in shipment, steps in experiment and a to do list. The latex string of the paragraphs will be returned.

        Returns
        -------
        table : str
            The latex string of table.
        plans : list
            The list of experiment plans.

        """
        gtx = self.gtx
        rows = []
        plans = []
        for n, doc in enumerate(gtx["beamplan"]):
            # gather information of the table
            row = {
                "serial_id": str(n + 1),
                "project leader": doc["project_lead"],
                "number of samples": str(len(doc["samples"])),
                "sample container": doc["container"],
                "sample holder": doc["holder"],
                "measurement": doc["measurement"],
                "estimated time (min)": str(doc["time"])
            }
            rows.append(row)
            # gather information of the plan.
            plan = {
                "serial_id": str(n + 1),
                "objective": doc["objective"],
                "prep_plan": doc["prep_plan"],
                "ship_plan": doc["ship_plan"],
                "expr_plan": doc["expr_plan"],
                "todo_list": doc["todo"]
            }
            plans.append(plan)
        # make a latex tabular
        table = pd.DataFrame(rows).to_latex(escape=True, index=False)
        return table, plans

    def latex(self):
        """Render latex template."""
        table, plans = self.gather_info()
        self.render("beamplan.txt", "beamplan_report.tex", table=table, plans=plans)
