"""Helper for adding a proposal to the proposals.yml collection."""

import datetime as dt
from math import floor

import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection, get_pi_id

TARGET_COLL = "proposals"


def subparser(subpi):
    amount_kwargs = {}
    notes_kwargs = {}
    date_kwargs = {}
    dropdown_kwargs = {}
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        amount_kwargs["widget"] = "DecimalField"
        amount_kwargs["gooey_options"] = {"min": 0.00, "max": 1000000.00, "increment": 10.00, "precision": 2}
        notes_kwargs["widget"] = "Textarea"
        date_kwargs["widget"] = "DateChooser"
        dropdown_kwargs["widget"] = "Dropdown"
        dropdown_kwargs["choices"] = [True, False]
        int_kwargs["widget"] = "IntegerField"

    # Do not delete --database arg
    subpi.add_argument(
        "name",
        help="A short but unique name for the proposal",
    )
    subpi.add_argument(
        "amount",
        help="value of award",
    )
    subpi.add_argument("title", help="Actual title of the proposal")
    subpi.add_argument("--begin-date", help="The begin date for the proposed grant ", **date_kwargs)
    subpi.add_argument(
        "--duration",
        help="The duration for the proposed grant in months. " "Please enter either an end date or a duration. ",
        **int_kwargs,
    )
    subpi.add_argument(
        "--end-date",
        help="The end date for the proposed grant." " Please enter either an " "end date or a duration",
        **date_kwargs,
    )
    subpi.add_argument("--due-date", help="The due date for the proposal", **date_kwargs)
    subpi.add_argument("-a", "--authors", nargs="+", help="Other investigator names", default=[])
    subpi.add_argument(
        "--not-cpp",
        action="store_true",
        help="Check if the proposal should not appear in the " "current and pending support form",
    )
    subpi.add_argument(
        "--other-agencies",
        help="Other agencies to which the proposal has been " "submitted. Defaults to None",
        default="None",
    )
    subpi.add_argument(
        "-i", "--institution", help="The institution where the work will primarily " "be carried out", default=""
    )
    subpi.add_argument(
        "-p", "--pi", help="ID of principal investigator. Defaults to " "group pi id in regolithrc.json"
    )
    subpi.add_argument(
        "--months-academic",
        help="Number of working months in the academic year "
        "to be stated on the current and pending form. "
        "Defaults to 0",
        default=0,
        **int_kwargs,
    )
    subpi.add_argument(
        "--months-summer",
        help="Number of working months in the summer to be "
        "stated on the current and pending form. "
        "Defaults to 0",
        default=0,
        **int_kwargs,
    )
    subpi.add_argument(
        "-s",
        "--scope",
        help="Scope of project and statement of any overlaps " "with other current and pending grants",
        default="",
    )
    subpi.add_argument("-f", "--funder", help="Agency where the proposal is being submitted", default="")
    subpi.add_argument("-n", "--notes", nargs="+", help="Anything to note", default=[], **notes_kwargs)
    subpi.add_argument(
        "-c", "--currency", help="Currency in which amount is specified. Defaults to USD", default="USD"
    )
    subpi.add_argument(
        "--database",
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
    )
    subpi.add_argument("--date", help="The date that will be used for testing.", **date_kwargs)
    return subpi


class ProposalAdderHelper(DbHelperBase):
    """Helper for adding a proposal to the proposals collection.

    A proposal is a dictionary object describing a research or  project
    proposal submitted by the group.
    """

    # btype must be the same as helper target in helper.py
    btype = "a_proposal"
    needed_colls = [f"{TARGET_COLL}", "people", "groups"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        if rc.date:
            now = date_parser.parse(rc.date).date()
        else:
            now = dt.date.today()
        key = f"{str(now.year)[2:]}_{''.join(rc.name.casefold().split()).strip()}"

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError("This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update({"_id": key, "amount": float(rc.amount)})
        pdoc.update({"authors": rc.authors})
        if rc.begin_date:
            begin_date = date_parser.parse(rc.begin_date).date()
            if rc.end_date:
                end_date = date_parser.parse(rc.end_date).date()
                if begin_date > end_date:
                    raise ValueError("begin_date can not be after end_date")
                if rc.duration:
                    expected_duration = relativedelta(end_date, begin_date)
                    input_duration = float(rc.duration)
                    input_years = floor(input_duration / 12)
                    input_months = floor(input_duration) % 12
                    input_days = (input_duration % 1) * 30.5
                    # we take 30.5 as an average of 30 and 31 day months
                    if (
                        expected_duration.years != input_years
                        or expected_duration.months != input_months
                        or abs(expected_duration.days - input_days) > 3.05
                    ):
                        # assuming that the user inputs the correct duration up to 1 decimal place
                        # so the maximum allowed difference is 0.1*30.5
                        raise ValueError("ERROR: please rerun specifying a duration OR an end-date but not both")
            pdoc.update({"begin_date": begin_date})
        else:
            pdoc.update({"begin_date": "tbd"})
        cpp_info = {}
        if rc.not_cpp:
            cpp_info["cppflag"] = False
        else:
            cpp_info["cppflag"] = True
        cpp_info["other_agencies_submitted"] = rc.other_agencies
        cpp_info["institution"] = rc.institution
        cpp_info["person_months_academic"] = float(rc.months_academic)
        cpp_info["person_months_summer"] = float(rc.months_summer)
        cpp_info["project_scope"] = rc.scope
        pdoc.update({"cpp_info": cpp_info})
        pdoc.update({"currency": rc.currency})
        if rc.due_date:
            pdoc.update({"due_date": date_parser.parse(rc.due_date).date()})
        else:
            pdoc.update({"due_date": "tbd"})
        if rc.end_date:
            pdoc.update({"end_date": date_parser.parse(rc.end_date).date()})
        elif rc.begin_date and rc.duration and not rc.end_date:
            begin_date = date_parser.parse(rc.begin_date).date()
            pdoc.update({"end_date": begin_date + relativedelta(days=30.5 * float(rc.duration))})
        else:
            pdoc.update({"end_date": "tbd"})
        pdoc.update({"funder": rc.funder})
        pdoc.update({"notes": rc.notes})
        if rc.pi:
            pdoc.update({"pi": rc.pi})
        else:
            pdoc.update({"pi": rc.pi_id})
        pdoc.update({"status": "inprep"})
        sample_team = {"name": "", "subaward_amount": 0}
        pdoc.update({"team": [sample_team]})
        pdoc.update({"title": rc.title})

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
