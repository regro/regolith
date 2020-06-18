"""
Helper to add expenses.
"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
)

TARGET_COLL = "projecta"
ALLOWED_TYPES = ["business", "travel"] # need to check all expense types.
ALLOWED_STATI = ["submitted", "unsubmitted", "reimbursed"]


def subparser(subpi):
    subpi.add_argument("amount", help="expense amount",
                       )
    subpi.add_argument("name", help="A short name for the expense",
                       default=None
                       )
    subpi.add_argument("purpose", help="A short description of expense purpose",
                       default=None)
    subpi.add_argument("reimbur")
    subpi.add_argument("-b", "--business", action='store_true',
                       help="expense type is business. If not specified defaults to travel"
                       )
    subpi.add_argument("-y", "--payee",
                       help="payee of the expense, defaults to sbillinge"
                       )
    subpi.add_argument("-g", "--grants", nargs="+",
                       help="grant, or list of grants that cover this expense. Defaults to tbd"
                       )
    subpi.add_argument("-s", "--status",
                       help=f"status, from {ALLOWED_STATI}. Default is unsubmitted"
                       )
    subpi.add_argument("-z", "--segregated",
                       help="Amount for any segregated expense. Defaults to 0"
                       )
    subpi.add_argument("-w", "--where",
                       help="Where the expense has been submitted"
                       )
    subpi.add_argument("-n", "--notes", nargs="+",
                       help="List of notes for the expense. Defaults to empty list"
                       )
    subpi.add_argument("-d", "--begin_date",
                       help="Input begin date for this expense. "
                            "In YYYY-MM-DD format. Defaults to today's date"
                       )
    subpi.add_argument("-e,", "--end_date",
                       help="Input end date for this expense. "
                            "In YYYY-MM-DD format. Defaults to today's date"
                       )
    return subpi


class ExpenseAdderHelper(DbHelperBase):
    """
    Helper to add expenses


    """
    # btype must be the same as helper target in helper.py
    btype = "a_expense"
    needed_dbs = ['expenses']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(
            all_docs_from_collection(rc.client, rc.coll), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        gtx = self.gtx

        rc = self.rc

        if not rc.begin_date:
            begin_date = dt.date.today() # string with date time format
            begin_date = begin_date.strftime('%Y-%m-%d')
        else:
            begin_date = rc.begin_date() # need to raise exception for wrongly formatted user input
        if not rc.end_date:
            end_date = dt.date.today()
            end_date = end_date.strftime('%Y-%m-%d')
        else:
            end_date = rc.end_date

        # defaults to sbillinge
        if rc.payee:
            key = f"{str(begin_date.year)[2:]}{rc.payee[:2]}_{''.join(rc.name.casefold().split()).strip()}"
        else:
            key = f"{str(begin_date.year)[2:]}{'sb'}_{''.join(rc.name.casefold().split()).strip()}"



        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError(
                "This entry appears to already exist in the collection")
        else:
            pdoc = {}


        pdoc.update({
            "begin_year": int(begin_date.split('-')[0]),
             "begin_month": int(begin_date.split('-')[1]),
             "begin_day": int(begin_date.split('-')[2]),
             "end_year": int(end_date.split('-')[0]),
             "end_month": int(end_date.split('-')[1]),
             "end_day": int(end_date.split('-')[2])
             })
        if rc.business:
            pdoc.update({'expense_type': "business"
                         })
        else:
            pdoc.update({"expense_type":"travel"
                         })
    # Updates the grants, assumes equal percentage for each grant
        if rc.grants:
            if isinstance(rc.grants, str):
                rc.grants = [rc.grants]
            percentages = [100 / len(rc.grants) for i in rc.grants]
        else:
            rc.grants = 'tbd'
            percentages = 0 #No grant => no percentage?

        # segregated expense
        if not rc.segregated:
            rc.segregated = "0"



        pdoc.update({"grant_percentages": percentages,
                     "grants": rc.grants,
                     "itemized_expenses":{
                         [{"day": int(begin_date.split('-')[2]),
                           "month": int(begin_date.split('-')[1]),
                           "purpose": rc.purpose,
                           "segregated_expense" : int(rc.segregated),
                           "unsegregated_expense": int(rc.amount) - int(rc.segregated)
                         }]
                     }
                     })
        # Notes
        if rc.notes:
            if isinstance(rc.notes, str)
            notes = [rc.notes]
        else:
            notes = []
        pdoc.update({
            "notes": notes,
            "overall_purpose": rc.purpose,
            "payee": rc.payee

        })



        print(f"{key} has been added in {TARGET_COLL}")

        return
