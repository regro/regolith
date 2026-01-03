"""Helper to add expenses."""

import datetime as dt

import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.schemas import alloweds
from regolith.tools import all_docs_from_collection, get_pi_id, strip_str

TARGET_COLL = "expenses"

EXPENSES_STATI = alloweds.get("EXPENSES_STATI")
EXPENSES_TYPES = alloweds.get("EXPENSES_TYPES")


def expense_constructor(key, begin_date, end_date, rc):
    """Constructs a document with default fields for an expense.

    Parameters
    ----------
    key str
      The key for ('_id') for this entry in the expenses collection
    begin_date datetime.date
      The date of the start of the travel/expense
    end_date datetime.date
      The date of the end of the travel/expense
    rc runcontrol object
      The runcontrol object.  Should contain:
         required:
         rc.business (bool) True if a business expense, false if a travel one.
         rc.grants (list) The list of grants that will be charged
         rc.purpose (str) The purpose of the trip/expense
         rc.payee (str) id of the payee
         rc.where (str) where submitted/reimbursed (e.g., which institution/person
            it was submitted to or which bank account it was reimbursed to
         required if rc.business:
         rc.amount (float) The amount of the expense if it is a business expense
         optional:
         rc.notes (list of strings) notes to add if there are any
         rc.status (str) the status of the expense (defaults to unsubmitted)

    Returns
    -------
    The constructed expense document
    """
    pdoc = {}
    pdoc.update(
        {
            "_id": key,
            "begin_date": begin_date,
            "end_date": end_date,
        }
    )

    if rc.business:
        expense_type = "business"
    else:
        expense_type = "travel"
    pdoc.update({"expense_type": expense_type})

    percentages = [round(100 / len(rc.grants), 2) for i in rc.grants]

    pdoc.update({"grant_percentages": percentages, "grants": rc.grants})

    if expense_type == "travel":
        pdoc.update(
            {
                "itemized_expenses": [
                    {
                        "date": begin_date,
                        "purpose": "registration",
                        "unsegregated_expense": 0,
                        "segregated_expense": 0,
                        "currency": "USD",
                        "notes": [""],
                    },
                    {
                        "date": begin_date,
                        "purpose": "home to airport",
                        "unsegregated_expense": 0,
                        "segregated_expense": 0,
                        "currency": "USD",
                        "notes": [""],
                    },
                    {
                        "date": begin_date,
                        "purpose": "flights",
                        "unsegregated_expense": 0,
                        "segregated_expense": 0,
                        "currency": "USD",
                        "notes": [""],
                    },
                    {
                        "date": begin_date,
                        "purpose": "airport to hotel",
                        "unsegregated_expense": 0,
                        "segregated_expense": 0,
                        "currency": "USD",
                        "notes": [""],
                    },
                    {
                        "date": begin_date,
                        "purpose": "hotel",
                        "unsegregated_expense": 0,
                        "segregated_expense": 0,
                        "currency": "USD",
                        "notes": [""],
                    },
                    {
                        "date": begin_date,
                        "purpose": "hotel to airport",
                        "unsegregated_expense": 0,
                        "segregated_expense": 0,
                        "currency": "USD",
                        "notes": [""],
                    },
                    {
                        "date": begin_date,
                        "purpose": "airport to home",
                        "unsegregated_expense": 0,
                        "segregated_expense": 0,
                        "currency": "USD",
                        "notes": [""],
                    },
                    {
                        "date": begin_date,
                        "purpose": "meals",
                        "unsegregated_expense": 0,
                        "segregated_expense": 0,
                        "currency": "USD",
                        "notes": [""],
                    },
                ]
            }
        )
    else:
        pdoc.update(
            {
                "itemized_expenses": [
                    {
                        "date": begin_date,
                        "purpose": rc.purpose,
                        "unsegregated_expense": float(rc.amount),
                        "segregated_expense": 0,
                        "currency": "USD",
                        "notes": [""],
                    }
                ]
            }
        )
    pdoc.update(
        {
            "notes": rc.notes,
            "overall_purpose": rc.purpose,
            "payee": rc.payee,
        }
    )
    if rc.status == "submitted":
        submission_date = dt.date.today()

    else:
        submission_date = "tbd"

    pdoc.update(
        {
            "reimbursements": [
                {
                    "amount": 0,
                    "date": "tbd",
                    "submission_date": submission_date,
                    "where": rc.where,
                }
            ]
        }
    )
    pdoc.update({"status": rc.status})
    return pdoc


def subparser(subpi):
    amount_gooey_kwargs, notes_gooey_kwargs, date_gooey_kwargs = {}, {}, {}
    if isinstance(subpi, GooeyParser):
        amount_gooey_kwargs["widget"] = "DecimalField"
        amount_gooey_kwargs["gooey_options"] = {"min": 0.00, "max": 1000000.00, "increment": 10.00, "precision": 2}
        notes_gooey_kwargs["widget"] = "Textarea"
        date_gooey_kwargs["widget"] = "DateChooser"

    subpi.add_argument("name", help="A short name for the expense", default=None, type=strip_str)
    subpi.add_argument(
        "purpose",
        help="A short description of the business " "purpose of the expense",
        default=None,
        type=strip_str,
    )

    subpi.add_argument(
        "-b",
        "--business",
        action="store_true",
        help="Is the expense type business? If not specified, defaults to travel",
    )
    subpi.add_argument(
        "-a", "--amount", help="expense amount. required if a business " "expense.", **amount_gooey_kwargs
    )
    subpi.add_argument(
        "-d",
        "--begin-date",
        help="Input begin date for this expense. " "Defaults to today's date",
        **date_gooey_kwargs,
        type=strip_str,
    )
    subpi.add_argument(
        "-e,",
        "--end-date",
        help="Input end date for this expense. " "Defaults to today's date",
        **date_gooey_kwargs,
        type=strip_str,
    )
    subpi.add_argument(
        "-g",
        "--grants",
        nargs="+",
        help="grant, or list of grants that cover this expense. Defaults to tbd",
        default="tbd",
        type=strip_str,
    )
    subpi.add_argument(
        "-s",
        "--status",
        choices=EXPENSES_STATI,
        help=f"status, from {EXPENSES_STATI}. Default is unsubmitted",
        default="unsubmitted",
    )
    subpi.add_argument("-w", "--where", help="Where the expense has been submitted.", default="", type=strip_str)
    subpi.add_argument(
        "-n",
        "--notes",
        nargs="+",
        help="List of notes for the expense. Defaults to empty list",
        default=[],
        type=strip_str**notes_gooey_kwargs,
    )
    subpi.add_argument(
        "-y", "--payee", help="payee of the expense. defaults to rc.default_user_id", type=strip_str
    )
    # Do not delete --database arg
    subpi.add_argument(
        "--database",
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
        type=strip_str,
    )
    return subpi


class ExpenseAdderHelper(DbHelperBase):
    btype = "a_expense"
    needed_colls = [f"{TARGET_COLL}", "people", "groups"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        if not rc.payee:
            if rc.default_user_id:
                rc.payee = rc.default_user_id
            else:
                raise RuntimeError(
                    " No default_user_id set.  Please specify this "
                    "either in the ~/.conf/regolith/user.json or in"
                    " regolithrc.json"
                )
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        # dates
        if rc.begin_date:
            begin_date = date_parser.parse(rc.begin_date).date()
        else:
            begin_date = dt.date.today()
        if rc.end_date:
            end_date = date_parser.parse(rc.end_date).date()
        else:
            end_date = dt.date.today()
        key = (
            f"{str(begin_date.year)[2:]}{str(begin_date.strftime('%m'))}"
            f"{rc.payee[0:2]}_{''.join(rc.name.casefold().split()).strip()}"
        )
        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError("This entry appears to already exist in the collection")
        else:
            pdoc = {}

        pdoc = expense_constructor(key, begin_date, end_date, rc)

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
