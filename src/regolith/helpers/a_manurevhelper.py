"""Builder for manuscript reviews."""

import sys

import nameparser
from dateutil import parser as dateparser
from gooey import GooeyParser

from regolith.dates import month_to_str_int
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection, strip_str

ALLOWED_STATI = ["invited", "accepted", "declined", "downloaded", "inprogress", "submitted", "cancelled"]


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument(
        "name",
        type=strip_str,
        help="Full name, or last name, of the first author",
    )
    subpi.add_argument("due_date", type=strip_str, help="Due date", default="", **date_kwargs)
    subpi.add_argument("journal", type=strip_str, help="journal to be published in", default="")
    subpi.add_argument("title", type=strip_str, help="the title of the Manuscript", default="")
    subpi.add_argument(
        "-q", "--requester", type=strip_str, help="name, or id in contacts, of the editor requesting the review"
    )
    subpi.add_argument(
        "-s", "--status", type=strip_str, choices=ALLOWED_STATI, help="Manuscript status", default="accepted"
    )
    subpi.add_argument(
        "-d", "--submitted-date", type=strip_str, help="Submitted date. Defaults " "to tbd", **date_kwargs
    )
    subpi.add_argument(
        "-r", "--reviewer", type=strip_str, help="name of the reviewer. Defaults to the one saved in user.json. "
    )
    subpi.add_argument(
        "-t",
        "--database",
        type=strip_str,
        help="The database that will be updated. Defaults to " "first database in the regolithrc.json file.",
    )
    return subpi


class ManuRevAdderHelper(DbHelperBase):
    btype = "a_manurev"
    needed_colls = ["refereeReports"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        rc.coll = "refereeReports"
        gtx["refereeReports"] = sorted(all_docs_from_collection(rc.client, "refereeReports"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        name = nameparser.HumanName(rc.name)
        due_date = dateparser.parse(rc.due_date).date()
        if name.last == "":
            key = "{}{}_{}".format(
                str(due_date.year)[-2:], month_to_str_int(due_date.month), name.first.casefold().strip(".")
            )
        else:
            key = "{}{}_{}_{}".format(
                str(due_date.year)[-2:],
                month_to_str_int(due_date.month),
                name.last.casefold(),
                name.first.casefold().strip("."),
            )
        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            sys.exit("This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update(
            {
                "claimed_found_what": [],
                "claimed_why_important": [],
                "did_how": [],
                "did_what": [],
                "due_date": due_date,
                "editor_eyes_only": "",
                "final_assessment": [],
                "freewrite": "",
                "journal": rc.journal,
                "recommendation": "",
                "title": rc.title,
                "validity_assessment": [],
                "year": due_date.year,
            }
        )

        if rc.reviewer:
            pdoc.update({"reviewer": rc.reviewer})
        else:
            try:
                rc.reviewer = rc.default_user_id
                pdoc.update({"reviewer": rc.reviewer})
            except AttributeError:
                print(
                    "Please set default_user_id in '~/.config/regolith/user.json', "
                    "or you need to enter your group id in the command line"
                )
                return
        if rc.submitted_date:
            pdoc.update({"submitted_date": rc.submitted_date})
        else:
            pdoc.update({"submitted_date": "tbd"})
        if rc.name:
            if name.last == "":
                pdoc.update({"first_author_last_name": name.first})
            else:
                pdoc.update({"first_author_last_name": name.last})
        if rc.requester:
            pdoc.update({"requester": rc.requester})
        else:
            pdoc.update({"requester": ""})
        if rc.status:
            if rc.status not in ALLOWED_STATI:
                raise ValueError("status should be one of {}".format(ALLOWED_STATI))
            else:
                pdoc.update({"status": rc.status})
        else:
            pdoc.update({"status": "accepted"})

        pdoc.update({"_id": key})
        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print("{} manuscript has been added/updated in manuscript reviews".format(rc.name))

        return
