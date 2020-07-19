"""Builder for Proposal Reviews."""
from datetime import datetime, date
import time
from nameparser import HumanName

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import month_to_int
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    filter_grants,
    filter_presentations,
    fuzzy_retrieval
)


class GrantReportBuilder(LatexBuilderBase):
    """Build a proposal review from database entries"""
    btype = "grantreport"
    needed_dbs = ['presentations', 'projecta', 'people', 'grants', 'institutions']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        for dbs in rc.needed_dbs:
            gtx[dbs] = sorted(
                all_docs_from_collection(rc.client, dbs), key=_id_key
            )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        # Get Dates
        today = str(date.today()).split("-")
        end_year, end_month, end_day = int(today[0]), int(today[1]), int(today[2])
        begin_year, begin_month, begin_day = int(today[0]) - 1, int(today[1]), int(today[2])
        end_date = date(end_year, end_month, end_day)
        begin_date = date(begin_year, begin_month, begin_day)

        # Get All Active Members
        current_members = [person for person in self.gtx['people'] if person['active']]

        # Major Goals

        # Accomplishments

        # Opportunities for Training and Professional Development and
        # Individuals that have worked on project
        valid_presentations = []
        individuals_data = []
        for person in current_members:
            valid_presentations.append(filter_presentations(
                self.gtx["people"], self.gtx["presentations"], self.gtx["institutions"], person["_id"],
                ["tutorial", "contributed_oral"], begin_date, end_date))
            individuals_data.append([person["_id"], person["position"]])

        # How have results been disseminated

        # Plans for Next Reporting Period to Accomplish Goals



        self.render(
            "grantreport.txt",
            "billinge_grant_report.txt",
            endYear=end_year,
            endMonth=end_month,
            endDay=end_date,
            beginYear=begin_year,
            beginMonth=begin_month,
            beginDay=begin_day,
            presentations=valid_presentations,
            individuals=individuals_data
        )
