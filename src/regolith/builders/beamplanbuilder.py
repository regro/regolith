"""Builder for the planning of beamtimes.

The plan contains a summary of the information for the experiments in
during a beamtime and details about how to carry out the experiments.
"""

from datetime import datetime

import pandas as pd

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.tools import all_docs_from_collection, group, id_key


class BeamPlanBuilder(LatexBuilderBase):
    """Build a file of experiment plans for the beamtime from database
    entries.

    The report is in the '.tex' file. The template of the file is in the
    'templates/beamplan.tex'. The data will be grouped
    according to beamtime. Each beamtime will generate a file of the plans.
    If 'beamtime' in 'rc' are not None, only plans for those beamtime will be generated.

    Methods
    -------
    construct_global_ctx()
        Constructs the global context.
    latex()
        Render latex template.
    """

    btype = "beamplan"
    needed_colls = ["beamplan", "beamtime"]

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
        if date is None:
            return "missing"
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        readable_date = date_obj.strftime("%b %d, %Y")
        return readable_date

    @staticmethod
    def _search(db, key):
        """Search doc in the database."""
        for doc in db:
            if id_key(doc) == key:
                return doc
        return None

    def _gather_info(self, bt, docs):
        """Query information from the list of documents. Return a table
        as the summary of the plans and a list of experiment plans.

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
            table - The latex string of table (used in tex file).
            table_str - The string of the table (used in txt file).
            tasks - The combination of todos in the plans.
            plans - The list of experiment plans. Each item in a plan is a list of strings.
            begin_date - The beginning date of the beamtime.
            end_date - The end date of the beamtime.
            caption - caption of the table.
        """
        # get begin_date and end_date
        beamtime = self.gtx["beamtime"]
        bt_doc = self._search(beamtime, bt)
        if bt_doc:
            begin_date = self._to_readable(bt_doc.get("begin_date"))
            end_date = self._to_readable(bt_doc.get("end_date"))
            begin_time = bt_doc.get("begin_time", "missing")
            end_time = bt_doc.get("end_time", "missing")
        else:
            begin_time = end_time = begin_date = end_date = "no doc"
        # get data from beamplan
        rows, plans, tasks = [], [], []
        docs = sorted(docs, key=lambda d: d.get("devices"))
        for n, doc in enumerate(docs):
            # gather information of the table
            serial_id = str(n + 1)
            row = {
                "serial id": serial_id,
                "project leader": doc.get("project_lead", ""),
                "number of samples": str(len(doc.get("samples", []))),
                "measurement": doc.get("measurement", ""),
                "devices": ", ".join(doc.get("devices", [])),
                "estimated time (h)": "{:.1f}".format(doc.get("time", 0) / 60),
            }
            rows.append(row)
            # gather information of the plan.
            plan = {
                "serial_id": serial_id,
                "samples": doc.get("samples", []),
                "objective": doc.get("objective", ""),
                "prep_plan": doc.get("prep_plan", []),
                "ship_plan": doc.get("ship_plan", []),
                "exp_plan": doc.get("exp_plan", []),
                "scanplan": doc.get("scanplan", []),
            }
            plans.append(plan)
            # gather info of the task
            todo_list = ["(Exp. {}) {}".format(serial_id, todo) for todo in doc.get("todo", [])]
            tasks += todo_list
        # make a pandas dataframe and calculate time and samples
        df = pd.DataFrame(rows)
        total_time = "{:.1f}".format(df["estimated time (h)"].astype(float).sum())
        total_sample_num = "{:d}".format(df["number of samples"].astype(int).sum())
        # convert to the string form
        table_latex = df.to_latex(escape=True, index=False)
        table_str = df.to_string()
        # make a dict
        info = {
            "bt": bt,  # str
            "plans": plans,  # List[dict]
            "table": table_latex,  # str
            "table_for_txt": table_str,  # str
            "tasks": tasks,  # List[str]
            "begin_date": begin_date,  # str
            "end_date": end_date,  # str
            "begin_time": begin_time,  # str
            "end_time": end_time,  # str
            "total_time": total_time,  # str
            "total_sample_num": total_sample_num,  # str
        }
        return info

    def latex(self):
        """Render latex template."""
        gtx = self.gtx
        db = gtx["beamplan"]
        grouped = group(db, "beamtime")
        for bt, plans in grouped.items():
            info = self._gather_info(bt, plans)
            self.render("beamplan.tex", "{}.tex".format(bt), **info)
            self.render("beamplan.txt", "{}.txt".format(bt), **info)
            self.pdf(bt)
        return
