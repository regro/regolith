"""Builder for the plan of beamtimes. The plan contains a summary of the information for the experiments in during a
beamtime and details about how to carry out the experiments. """
from regolith.builders.basebuilder import LatexBuilderBase
from regolith.tools import all_docs_from_collection
from regolith.tools import group
import pandas as pd


class BeamPlanBuilder(LatexBuilderBase):
    """
    Build a file of experiment plans for the beamtime from database entries. The report is in .tex file. The template
    of the file is in the 'templates/beamplan.txt'. The data will be grouped according to beamtime. Each beamtime
    will generate a file of the plans. If 'beamtime' in 'rc' are not None, only plans for those beamtime will be
    generated.

    Methods
    -------
    construct_global_ctx()
        Constructs the global context.
    latex()
        Render latex template.
    """
    btype = "beamplan"
    needed_dbs = ['beamplan', "people"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["beamplan"] = all_docs_from_collection(rc.client, "beamplan")
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str

    @staticmethod
    def _gather_info(docs):
        """
        Query information from the list of documents. Return a table as the summary of the plans and a list of
        experiment plans.

        Parameters
        ----------
        docs : list
            A list of documents.

        Returns
        -------
        info : dict
        The information obtained from the database and formatted. It contains the key value pairs:
            table The latex string of table.
            plans The list of experiment plans. Each experiment plan is a list of strings.

        """
        rows = []
        plans = []
        docs = sorted(docs, key=lambda d: d.get("project_lead"))
        for n, doc in enumerate(docs):
            # gather information of the table
            row = {
                "serial id": str(n + 1),
                "project leader": doc.get("project_lead", "missing"),
                "number of samples": str(len(doc.get("samples", []))),
                "sample container": doc.get("container", "missing"),
                "sample holder": doc.get("holder", "missing"),
                "measurement": doc.get("measurement", "missing"),
                "devices": ", ".join(doc.get("devices", ["missing"])),
                "estimated time (min)": str(doc.get("time", "missing"))
            }
            rows.append(row)
            # gather information of the plan.
            plan = {
                "serial_id": n + 1,
                "samples": ', '.join(doc.get("samples", ["missing"])),
                "objective": doc.get("objective", "]missing"),
                "prep_plan": doc.get("prep_plan", ["missing"]),
                "ship_plan": doc.get("ship_plan", ["]missing"]),
                "exp_plan": doc.get("exp_plan", ["missing"]),
                "todo_list": doc.get("todo", ["missing"])
            }
            plans.append(plan)
        # make a latex tabular
        df = pd.DataFrame(rows)
        table = df.to_latex(escape=True, index=False)
        info = {"plans": plans, "table": table}
        return info

    def latex(self):
        """Render latex template."""
        gtx = self.gtx
        rc = self.rc
        db = gtx["beamplan"]
        grouped = group(db, "beamtime")
        bts = rc.beamtime if rc.beamtime else grouped.keys()
        for bt in bts:
            plans = grouped.get(bt)
            if plans:
                assert plans
                info = self._gather_info(plans)
                info["bt"] = bt
                self.render("beamplan.txt", "{}.tex".format(bt), **info)
            else:
                raise Warning("There is no beamtime {} in beamplan database".format(bt))
        return
