"""Builder for Current and Pending Reports."""

import datetime as dt
import sys

import nameparser
from gooey import GooeyParser

from regolith.dates import month_to_str_int
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection

ALLOWED_TYPES = ["nsf", "doe", "other"]
ALLOWED_STATI = ["invited", "accepted", "declined", "downloaded", "inprogress", "submitted", "cancelled"]


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument("name", help="pi first name space last name in quotes", default=None)
    subpi.add_argument("type", choices=ALLOWED_TYPES, help="Report type", default=None)
    subpi.add_argument("due_date", help="Due date", **date_kwargs)
    subpi.add_argument(
        "-d",
        "--database",
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
    )
    subpi.add_argument("-q", "--requester", help="Name of the Program officer requesting")
    subpi.add_argument("-r", "--reviewer", help="name of the reviewer.  Defaults to sbillinge")
    subpi.add_argument("-s", "--status", choices=ALLOWED_STATI, help="Report status", default="accepted")
    subpi.add_argument("-t", "--title", help="the title of the proposal")
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
        month = dt.datetime.today().month
        year = dt.datetime.today().year
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
                "competency_of_team": [],
                "doe_appropriateness_of_approach": [],
                "doe_reasonableness_of_budget": [],
                "doe_relevance_to_program_mission": [],
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
