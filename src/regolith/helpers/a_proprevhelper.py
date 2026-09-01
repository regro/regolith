"""Builder for Current and Pending Reports."""

import datetime as dt
import sys

import nameparser
from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.dates import month_to_str_int
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection, strip_str

ALLOWED_TYPES = ["nsf", "doe", "other"]
ALLOWED_STATI = ["invited", "accepted", "declined", "downloaded", "inprogress", "submitted", "cancelled"]


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument("name", help="pi first name space last name in quotes", default=None, type=strip_str)
    subpi.add_argument("type", choices=ALLOWED_TYPES, help="Report type", default=None, type=strip_str)
    subpi.add_argument("due_date", help="Due date", type=strip_str, **date_kwargs)
    subpi.add_argument(
        "-d",
        "--database",
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
        type=strip_str,
    )
    subpi.add_argument("-q", "--requester", help="Name of the Program officer requesting", type=strip_str)
    subpi.add_argument("-r", "--reviewer", help="name of the reviewer.  Defaults to sbillinge", type=strip_str)
    subpi.add_argument(
        "-s", "--status", choices=ALLOWED_STATI, help="Report status", default="accepted", type=strip_str
    )
    subpi.add_argument("-t", "--title", help="the title of the proposal", type=strip_str)
    subpi.add_argument("--date", help="The date that will be used for testing.", type=strip_str, **date_kwargs)
    return subpi


class PropRevAdderHelper(DbHelperBase):
    """Build a helper."""

    btype = "a_proprev"
    needed_colls = ["proposalReviews"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        rc.coll = "proposalReviews"
        gtx["proposalReviews"] = sorted(all_docs_from_collection(rc.client, "proposalReviews"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        name = nameparser.HumanName(rc.name)
        if rc.date:
            now = date_parser.parse(rc.date).date()
        else:
            now = dt.date.today()
        month = now.month
        year = now.year
        key = "{}{}_{}_{}".format(
            str(year)[-2:], month_to_str_int(month), name.last.casefold(), name.first.casefold().strip(".")
        )

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            sys.exit("This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update(
            {
                "adequacy_of_resources": ["The resources available to the PI seem adequate"],
                "agency": rc.type,
                "competency_of_team": [
                    "For renewal applications, what is the past performance and potential of the research team? "
                    "How well qualified is the research team to carry out the proposed research? Is the lead "
                    "institution proposing to perform a greater portion of the scientific and technical work than "
                    "any other team member? Are the research environment and facilities adequate for performing "
                    "the research? Does the proposed work take advantage of unique facilities and capabilities?"
                ],
                "doe_appropriateness_of_approach": [
                    "How logical and feasible are the research approaches? Does the proposed research employ "
                    "innovative concepts or methods? Are the conceptual framework, methods, and analyses well "
                    "justified, adequately developed, and likely to lead to scientifically valid conclusions? "
                    "Does the applicant recognize significant potential problems and consider alternative "
                    "strategies? Is the proposed research aligned with the published priorities identified or "
                    "incorporated by reference in Section III of this NOFO? Does the proposed plan to recruit "
                    "and retain students and early-stage investigators provide sufficient mentorship?"
                ],
                "doe_reasonableness_of_budget": [
                    "Are the proposed budget and staffing levels adequate to carry out the proposed research? "
                    "Is the budget reasonable and appropriate for the scope?"
                ],
                "doe_relevance_to_program_mission": [],
                "doe_other": [],
                "doe_appropriateness_data_management_plan": [
                    "To what extent does the Data Management and Sharing Plan (DMSP) enable data generated in "
                    "the course of the research project to be publicly shared and preserved in a timely and "
                    "fair manner that enables validation and replication of results? How well do the selected "
                    "digital repositories enable appropriate sharing of scientific data? Does the DMSP adequately "
                    "justify any limitations of data sharing?  Are there any weaknesses in the DMSP that should "
                    "be addressed prior to the start of the project?"
                ],
                "does_how": [],
                "does_what": "",
                "due_date": rc.due_date,
                "freewrite": [],
                "goals": [],
                "importance": [],
                "institutions": [],
                "month": month,
                "names": name.full_name,
                "nsf_broader_impacts": [],
                "nsf_create_original_transformative": [],
                "nsf_plan_good": [],
                "nsf_pot_to_advance_knowledge": [],
                "nsf_pot_to_benefit_society": [],
                "status": "accepted",
                "summary": "",
                "year": year,
            }
        )

        if rc.title:
            pdoc.update({"title": rc.title})
        else:
            pdoc.update({"title": ""})
        if rc.requester:
            pdoc.update({"requester": rc.requester})
        else:
            pdoc.update({"requester": ""})
        if rc.reviewer:
            pdoc.update({"reviewer": rc.reviewer})
        else:
            pdoc.update({"reviewer": "sbillinge"})
        if rc.status:
            if rc.status not in ALLOWED_STATI:
                raise ValueError("status should be one of {}".format(ALLOWED_STATI))
            else:
                pdoc.update({"status": rc.status})
        else:
            pdoc.update({"status": "accepted"})

        pdoc.update({"_id": key})
        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print("{} proposal has been added/updated in proposal reviews".format(rc.name))

        return
