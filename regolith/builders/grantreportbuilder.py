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
        gtx["projecta"] = sorted(
            all_docs_from_collection(rc.client, "projecta"), key=_id_key
        )
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"), key=_id_key
        )
        gtx["presentations"] = sorted(
            all_docs_from_collection(rc.client, "presentations"), key=_id_key
        )
        gtx["grants"] = sorted(
            all_docs_from_collection(rc.client, "grants"), key=_id_key
        )
        gtx["institutions"] = sorted(
            all_docs_from_collection(rc.client, "institutions"), key=_id_key
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
        begin_year, begin_month, begin_day = int(today[0])-1, int(today[1]), int(today[2])
        end_date = date(end_year, end_month, end_day)
        begin_date = date(begin_year, begin_month, begin_day)
        # Major Goals

        # Accomplishments

        # Opportunities for Training and Professional Development
        valid_presentations = []
        for p in self.gtx["people"]:
            if p["active"] and p["_id"] is not "sbillinge":
                valid_presentations.append(filter_presentations(
                    self.gtx["people"], self.gtx["presentations"], self.gtx["institutions"], p["_id"],
                    ["tutorial", "contributed_oral"], begin_date, end_date))

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
            presentations=valid_presentations
        )
