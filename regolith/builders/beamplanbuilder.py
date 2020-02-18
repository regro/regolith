"""Builder for the plan of beamtimes. The plan contains a summary of the information for the experiments in during a
beamtime and details about how to carry out the experiments. """
from datetime import datetime

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.tools import all_docs_from_collection, group, id_key
import pandas as pd


class BeamPlanBuilder(LatexBuilderBase):
    """
    Build a file of experiment plans for the beamtime from database entries. The report is in .tex file. The template
    of the file is in the 'templates/beamplan.tex'. The data will be grouped according to beamtime. Each beamtime
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
    needed_dbs = ['beamplan', "beamtime"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["beamplan"] = all_docs_from_collection(rc.client, "beamplan")
        gtx["beamtime"] = all_docs_from_collection(rc.client, "beamtime")
        gtx["all_docs_from_collection"] = all_docs_from_collection

    @staticmethod
    def _to_readable(date):
        """Convert the string date to a human readable form."""
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        readable_date = date_obj.strftime("%d, %b %Y")
        return readable_date

    @staticmethod
    def _search(db, key):
        """Search doc in the database."""
        for doc in db:
            if id_key(doc) == key:
                return doc
        return None

    def _gather_info(self, bt, docs):
        """
        Query information from the list of documents. Return a table as the summary of the plans and a list of
        experiment plans.

        Parameters
        ----------
        bt : str
            The name of the beamtime. It should be a key in the beamtime.yml.
        docs : list
            A list of documents of the experiment plans in the beamplan database.

        Returns
        -------
        info : dict
            The information obtained from the database and formatted. It contains the key value pairs:
            table - The latex string of table.
            plans - The list of experiment plans. Each experiment plan is a list of strings.
            begin_date - The beginning date of the beamtime.
            end_date - The end date of the beamtime.
            caption - caption of the table.
        """
        # get begin_date and end_date
        beamtime = self.gtx["beamtime"]
        bt_doc = self._search(beamtime, bt)
        if bt_doc:
            begin_date = bt_doc.get("begin_date")
            end_date = bt_doc.get("end_date")
        else:
            begin_date = end_date = None
        begin_date, end_date = map(lambda d: self._to_readable(d) if d else "missing", (begin_date, end_date))
        # get data from beamplan
        rows, plans, tasks = [], [], []
        docs = sorted(docs, key=lambda d: d.get("devices"))
        for n, doc in enumerate(docs):
            # gather information of the table
            row = {
                "serial id": str(n + 1),
                "project leader": doc.get("project_lead", "missing"),
                "number of samples": str(len(doc.get("samples", []))),
                "measurement": doc.get("measurement", "missing"),
                "devices": ", ".join(doc.get("devices", ["missing"])),
                "estimated time (h)": "{:.1f}".format(doc.get("time", 0) / 60)
            }
            rows.append(row)
            # gather information of the plan.
            plan = {
                "serial_id": n + 1,
                "samples": ', '.join(doc.get("samples", ["missing"])),
                "objective": doc.get("objective", "missing"),
                "prep_plan": doc.get("prep_plan", ["missing"]),
                "ship_plan": doc.get("ship_plan", ["missing"]),
                "exp_plan": doc.get("exp_plan", ["missing"])
            }
            plans.append(plan)
            todo_list = doc.get("todo", [])
            tasks += todo_list
        # make a latex tabular
        df = pd.DataFrame(rows)
        total_time = df["estimated time (h)"].sum()
        total_sample_num = df["number of samples"].sum()
        caption = "Measurement of {} samples cost {} h in total.".format(total_sample_num, total_time)
        table = df.to_latex(escape=True, index=False)
        # make a dict
        info = {
            "plans": plans,
            "table": table,
            "tasks": tasks,
            "begin_date": begin_date,
            "end_date": end_date,
            "caption": caption
        }
        return info

    def latex(self):
        """Render latex template."""
        gtx = self.gtx
        db = gtx["beamplan"]
        grouped = group(db, "beamtime")
        for bt, plans in grouped.items():
            info = self._gather_info(bt, plans)
            info["bt"] = bt
            self.render("beamplan.tex", "{}.tex".format(bt), **info)
        return
