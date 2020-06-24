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

TARGET_COLL = "expenses"
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

    subpi.add_argument("-b", "--business", action='store_true',
                       help="expense type is business. If not specified defaults to travel"
                       )
    subpi.add_argument("-y", "--payee",
                       help="payee of the expense. defaults to sbillinge",
                       default="sbillinge"
                       )
    subpi.add_argument("-g", "--grants", nargs="+",
                       help="grant, or list of grants that cover this expense. Defaults to tbd"
                       )
    subpi.add_argument("-s", "--status",
                       help=f"status, from {ALLOWED_STATI}. Default is unsubmitted",
                       default='unsubmitted'
                       )
    subpi.add_argument("-w", "--where",
                       help="Where the expense has been submitted"
                       )
    subpi.add_argument("-n", "--notes", nargs="+",
                       help="List of notes for the expense. Defaults to empty list",
                       default= []
                       )
    subpi.add_argument("-d", "--begin_date",
                       help="Input begin date for this expense. "
                            "In YYYY-MM-DD format. Defaults to today's date",

                       )
    subpi.add_argument("-e,", "--end_date",
                       help="Input end date for this expense. "
                            "In YYYY-MM-DD format. Defaults to today's date",
                       )
    return subpi


class ExpenseAdderHelper(DbHelperBase):
    btype = "a_expense"
    needed_dbs = [f'{TARGET_COLL}', 'people', 'groups']

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
        # dates
        if rc.begin_date:
            begin_date = date_parser.parse(rc.begin_date).date()
            date_string = rc.begin_date
        else:
            begin_date = dt.date.today()
            date_string = dt.date.today().strftime('%Y-%m-%d')
        if rc.end_date:
            end_date = date_parser.parse(rc.end_date).date()
        else:
            end_date = dt.date.today()
        key = f"{str(begin_date.year)[2:]}{str(begin_date.strftime('%m'))}{rc.payee[0:2]}_{''.join(rc.name.casefold().split()).strip()}"
        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError(
                "This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update({'_id': key,
                     'begin_date': begin_date,
                     'end_date': end_date,
                     })
        # expense_type


        if rc.business:
            expense_type = 'business'
        else:
            expense_type = 'travel'
        pdoc.update({'expense_type': expense_type})

        if rc.grants:
            percentages = [100/len(rc.grants) for i in rc.grants]


        else:
            percentages = [100]
        pdoc.update({'grant_percentages':percentages,
                     'grants': rc.grants})

        if expense_type == 'travel':
            pdoc.update({'itemized_expenses': [
                {
                    'date': date_parser.parse(date_string).date(),
                    'purpose': 'registration',
                    'unsegregated_expense': 0,
                    'segregated_expense': 0
                },
                {
                    'date': date_parser.parse(date_string).date(),
                    'purpose': 'home to airport',
                    'unsegregated_expense': 0,
                    'segregated_expense': 0
                },
                {
                    'date': date_parser.parse(date_string).date(),
                    'purpose': 'flights',
                    'unsegregated_expense': 0,
                    'segregated_expense': 0
                },
                {
                    'date':date_parser.parse(date_string).date() ,
                    'purpose': 'airport to hotel',
                    'unsegregated_expense': 0,
                    'segregated_expense': 0
                },
                {
                    'date': date_parser.parse(date_string).date(),
                    'purpose': 'hotel',
                    'unsegregated_expense': 0,
                    'segregated_expense': 0
                },
                {
                    'date': date_parser.parse(date_string).date(),
                    'purpose': 'hotel to airport',
                    'unsegregated_expense': 0,
                    'segregated_expense': 0
                },
                {
                    'date': date_parser.parse(date_string).date(),
                    'purpose': 'airport to home',
                    'unsegregated_expense': 0,
                    'segregated_expense': 0
                },
                {
                    'date': date_parser.parse(date_string).date(),
                    'purpose': 'meals',
                    'unsegregated_expense': 0,
                    'segregated_expense': 0
                }
                ]
            })
        else:
            pdoc.update({'itemized_expenses': [
                {
                    'date': date_parser.parse(date_string).date(),
                    'purpose': rc.purpose,
                    'unsegregated_expense': 0,
                    'segregated_expense': 0
                }]
            })
        pdoc.update({'notes': rc.notes,
                     'overall_purpose': rc.purpose,
                     'payee': rc.payee,
                     })
        if rc.status == 'submitted':
            submission_date = dt.date.today()

        else:
            submission_date = 'tbd'

        pdoc.update({'reimbursements': [
            {
                'amount': 0,
                'date': 'tbd',
                'submission_date': submission_date,
                'where': rc.where,
            }
            ]
        })
        pdoc.update({
            'status': rc.status
        })



        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
