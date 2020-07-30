"""Builder for Proposal Reviews."""
from datetime import datetime
import time
from nameparser import HumanName
import dateutil.parser as date_parser

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import (month_to_int,
                            get_dates,
                            get_due_date,
                            is_current,
                            is_after,
                            is_before)
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
    needed_dbs = ['presentations', 'projecta', 'people', 'grants', 'institutions', 'expenses']

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

        # Convert Date Strings to Datetime Objects
        rp_start_date = date_parser.parse(rc.start_date)
        rp_end_date = date_parser.parse(rc.end_date)

        # NSF Grant _id
        grant_name = "dmref"

        # Get prum associated to grant and active during reporting period
        grant_prums = []
        for prum in self.gtx['projecta']:
            if grant_name in prum['grants']:
                begin_date = get_dates(prum).get('begin_date')
                due_date = get_due_date(prum['deliverable'])
                # if projectum was finished during reporting period or is still current
                # some projectum don't have an "end date", but all projecta have a deliverable
                # due_date
                if (rp_start_date <= due_date <= rp_end_date and prum['status'] is "finished") or is_current(prum):
                    grant_prums.append(prum)
        # Get people associated with grant
        grant_people = list(set([prum['lead'] for prum in grant_prums]))

        # Accomplishments
        major_activities = []
        significant_results = []
        for prum in grant_prums:
            if prum['status'] is "finished":
                significant_results.append(prum)
            else:
                major_activities.append(prum)

        # Opportunities for Training and Professional Development
        training_and_professional_development = []
        # presentations
        for id in grant_people:
            training_and_professional_development.extend(
                filter_presentations(self.gtx["people"], self.gtx["presentations"], self.gtx["institutions"], id,
                                     types=["all"], since=rp_start_date, before=rp_end_date, statuses=["accepted"]))
        # thesis defendings
        # how do i access people.yml in rg-db-public vs the people.yml file in rg-db-group?
        for id in grant_people:
            person = self.gtx['people'][id]
            if person['']
        # How have results been disseminated

        # Plans for Next Reporting Period to Accomplish Goals

        self.render(
            "grantreport.txt",
            "billinge_grant_report.txt",
            beginYear=rp_start_date.year,
            endYear=rp_end_date.year,
            majorActivities=major_activities,
            significantResults=significant_results,
            trainingAndProfessionalDevelopment=training_and_professional_development,
        )
