"""Builder for Proposal Reviews."""
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
    filter_presentations,
    fuzzy_retrieval
)


def subparser(subpi):
    subpi.add_argument("start_date", help="start date of the reporting period, formatted as YYYY-MM-DD",
                       default=None)
    subpi.add_argument("end_date", help="end date of the reporting period, formatted as YYYY-MM-DD")
    return subpi


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
        rc = self.rc
        # Get Dates
        start_date = rc.start_date.split("-")
        end_date = rc.end_date.split("-")
        begin_year, begin_month, begin_day = int(start_date[0]), int(start_date[1]), int(start_date[2])
        end_year, end_month, end_day = int(end_date[0]), int(end_date[1]), int(end_date[2])
        end_date = datetime.datetime(end_year, end_month, end_day)
        begin_date = datetime.datetime(begin_year, begin_month, begin_day)

        # NSF Grant _id
        grant_name = "dmref"
        # Get people linked to grant and active during reporting period
        people = [person for person in self.gtx['people']
                  if grant_name in person['grant']]
        # Get prums linked to grant and active/finished during the reporting period

        # Accomplishments

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
            individuals=individuals_data,
        )
