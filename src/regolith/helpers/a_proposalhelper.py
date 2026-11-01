"""Helper for adding a proposal to the proposals.yml collection."""

import datetime as dt
from math import floor

import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.schemas import alloweds
from regolith.tools import all_docs_from_collection, fuzzy_retrieval, get_pi_id, strip_str

TARGET_COLL = "proposals"
AVERAGE_DAYS_PER_MONTH = 30.5


def subparser(subpi):
    amount_kwargs = {}
    notes_kwargs = {}
    date_kwargs = {}
    dropdown_kwargs = {}
    int_kwargs = {}
    status_kwargs = {"choices": alloweds["PROPOSAL_STATI"]}
    if isinstance(subpi, GooeyParser):
        amount_kwargs["widget"] = "DecimalField"
        amount_kwargs["gooey_options"] = {"min": 0.00, "max": 1000000.00, "increment": 10.00, "precision": 2}
        notes_kwargs["widget"] = "Textarea"
        date_kwargs["widget"] = "DateChooser"
        dropdown_kwargs["widget"] = "Dropdown"
        dropdown_kwargs["choices"] = [True, False]
        int_kwargs["widget"] = "IntegerField"
        status_kwargs["widget"] = "Dropdown"

    # Do not delete --database arg
    subpi.add_argument("name", help="A short but unique name for the proposal", type=strip_str)
    subpi.add_argument("amount", help="value of award", type=strip_str)
    subpi.add_argument("title", help="Actual title of the proposal", type=strip_str)
    subpi.add_argument(
        "--begin-date", help="The begin date for the proposed grant ", type=strip_str, **date_kwargs
    )
    subpi.add_argument(
        "--duration",
        help="The duration for the proposed grant in months. " "Please enter either an end date or a duration. ",
        **int_kwargs,
    )
    subpi.add_argument(
        "--end-date",
        help="The end date for the proposed grant." " Please enter either an " "end date or a duration",
        type=strip_str,
        **date_kwargs,
    )
    subpi.add_argument("--due-date", help="The due date for the proposal", type=strip_str, **date_kwargs)
    subpi.add_argument(
        "--submitted-date", help="The date the proposal was submitted", type=strip_str, **date_kwargs
    )
    subpi.add_argument(
        "--status",
        help="The status of the proposal. Defaults to inprep. Use pending once it is submitted "
        "and awaiting a decision, so that it appears in the current and pending form.",
        default="inprep",
        **status_kwargs,
    )
    subpi.add_argument(
        "--call-for-proposals", help="The URL of the solicitation or call for proposals", type=strip_str
    )
    subpi.add_argument(
        "-a",
        "--authors",
        nargs="+",
        help="Other investigator names or ids. They are added to the team as co-PIs.",
        default=[],
        type=strip_str,
    )
    subpi.add_argument(
        "--not-cpp",
        action="store_true",
        help="Check if the proposal should not appear in the " "current and pending support form",
    )
    subpi.add_argument(
        "--other-agencies",
        help="Other agencies to which the proposal has been " "submitted. Defaults to None",
        default="None",
        type=strip_str,
    )
    subpi.add_argument(
        "-i",
        "--institution",
        help="The institution where the work will primarily " "be carried out",
        default="",
        type=strip_str,
    )
    subpi.add_argument(
        "-p",
        "--pi",
        help="ID of principal investigator. Defaults to " "group pi id in regolithrc.json",
        type=strip_str,
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
        type=strip_str,
    )
    subpi.add_argument(
        "-f", "--funder", help="Agency where the proposal is being submitted", default="", type=strip_str
    )
    subpi.add_argument(
        "-n", "--notes", nargs="+", help="Anything to note", default=[], type=strip_str, **notes_kwargs
    )
    subpi.add_argument(
        "-c",
        "--currency",
        help="Currency in which amount is specified. Defaults to USD",
        default="USD",
        type=strip_str,
    )
    subpi.add_argument(
        "--database",
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
        type=strip_str,
    )
    subpi.add_argument("--date", help="The date that will be used for testing.", type=strip_str, **date_kwargs)
    return subpi


def _parse_date(value):
    return date_parser.parse(value).date()


def _end_date_from_duration(begin_date, duration_months):
    whole_months = floor(duration_months)
    extra_days = round((duration_months - whole_months) * AVERAGE_DAYS_PER_MONTH)
    return begin_date + relativedelta(months=whole_months, days=extra_days) - relativedelta(days=1)


def _check_duration_matches(begin_date, end_date, duration_months):
    expected_duration = relativedelta(end_date, begin_date)
    input_years = floor(duration_months / 12)
    input_months = floor(duration_months) % 12
    input_days = (duration_months % 1) * AVERAGE_DAYS_PER_MONTH
    # Allow a tenth of a month, since durations are entered to one decimal place
    if (
        expected_duration.years != input_years
        or expected_duration.months != input_months
        or abs(expected_duration.days - input_days) > 0.1 * AVERAGE_DAYS_PER_MONTH
    ):
        raise ValueError(
            f"The duration of {duration_months} months does not match the begin date {begin_date} "
            f"and end date {end_date}. Please re-run giving either --duration or --end-date, not both."
        )


def _team_member(person, position, people, institution=None):
    found = fuzzy_retrieval(people, ["_id", "aka", "name"], person, case_sensitive=False)
    member = {"name": found["name"] if found else person, "position": position}
    if institution:
        member["institution"] = institution
    return member


class ProposalAdderHelper(DbHelperBase):
    """Helper for adding a proposal to the proposals collection.

    A proposal is a dictionary object describing a research or  project
    proposal submitted by the group.
    """

    # btype must be the same as helper target in helper.py
    btype = "a-proposal"
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
        gtx["people"] = sorted(all_docs_from_collection(rc.client, "people"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        if rc.date:
            now = _parse_date(rc.date)
        else:
            now = dt.date.today()
        key = f"{str(now.year)[2:]}_{''.join(rc.name.casefold().split()).strip()}"

        coll = self.gtx[rc.coll]
        if any(doc["_id"] == key for doc in coll):
            raise RuntimeError(
                f"A proposal with the id {key} is already in the {TARGET_COLL} collection. "
                "Please re-run with a different name, or edit the existing proposal."
            )

        begin_date = _parse_date(rc.begin_date) if rc.begin_date else None
        end_date = _parse_date(rc.end_date) if rc.end_date else None
        duration_months = float(rc.duration) if rc.duration else None
        if begin_date and end_date:
            if begin_date > end_date:
                raise ValueError(
                    f"The begin date {begin_date} is after the end date {end_date}. "
                    "Please re-run with a begin date that is before the end date."
                )
            if duration_months:
                _check_duration_matches(begin_date, end_date, duration_months)
        if begin_date and duration_months and not end_date:
            end_date = _end_date_from_duration(begin_date, duration_months)

        pi = rc.pi if rc.pi else rc.pi_id
        people = self.gtx["people"]
        team = [_team_member(pi, "pi", people, institution=rc.institution)]
        team.extend(_team_member(author, "copi", people) for author in rc.authors)

        pdoc = {"_id": key, "amount": float(rc.amount), "authors": rc.authors}
        if begin_date:
            pdoc["begin_date"] = begin_date
        if rc.call_for_proposals:
            pdoc["call_for_proposals"] = rc.call_for_proposals
        pdoc["cpp_info"] = {
            "cppflag": not rc.not_cpp,
            "other_agencies_submitted": rc.other_agencies,
            "institution": rc.institution,
            "person_months_academic": float(rc.months_academic),
            "person_months_summer": float(rc.months_summer),
            "project_scope": rc.scope,
        }
        pdoc["currency"] = rc.currency
        if rc.due_date:
            pdoc["due_date"] = _parse_date(rc.due_date)
        if end_date:
            pdoc["end_date"] = end_date
        pdoc["funder"] = rc.funder
        pdoc["notes"] = rc.notes
        pdoc["pi"] = pi
        pdoc["status"] = rc.status
        if rc.submitted_date:
            pdoc["submitted_date"] = _parse_date(rc.submitted_date)
        pdoc["team"] = team
        pdoc["title"] = rc.title

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
