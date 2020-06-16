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
    subpi.add_argument("-b", "--business",
                       help="expense type is business. If not specified defaults to travel"
                       )
    subpi.add_argument("-y", "--payee",
                       help="payee of the expense, defaults to sbillinge"
                       )
    subpi.add_argument("-g", "--grants", nargs="+",
                       help="list of grants that cover this expense"
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
        rc = self.rc
        if not rc.date:
            now = dt.date.today()
        else:
            now = date_parser.parse(rc.date).date()
        if not rc.due_date:
            due_date = now + relativedelta(years=1)
        else:
            due_date = date_parser.parse(rc.due_date).date()
        key = f"{str(now.year)[2:]}{rc.lead[:2]}_{''.join(rc.name.casefold().split()).strip()}"

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError(
                "This entry appears to already exist in the collection")
        else:
            pdoc = {}

        pdoc.update({
            'begin_date': now,
            'log_url': '',
            'name': rc.name,
            'pi_id': rc.pi_id,
            'lead': rc.lead,
        })
        if rc.lead is "tbd":
            pdoc.update({
                'status': 'proposed'
            })
        else:
            pdoc.update({
                'status': 'started'
            })

        if rc.description:
            pdoc.update({
                'description': rc.description,
            })
        if rc.grants:
            if isinstance(rc.grants, str):
                rc.grants = [rc.grants]
            pdoc.update({'grants': rc.grants})
        else:
            pdoc.update({'grants': ["tbd"]})
        if rc.group_members:
            if isinstance(rc.group_members, str):
                rc.group_members = [rc.group_members]
            pdoc.update({'group_members': rc.group_members})
        else:
            pdoc.update({'group_members': []})
        if rc.collaborators:
            if isinstance(rc.collaborators, str):
                rc.collaborators = [rc.collaborators]
            pdoc.update({
                'collaborators': rc.collaborators,
            })
        else:
            pdoc.update({
                'collaborators': [],
            })

        pdoc.update({"_id": key})
        pdoc.update({"deliverable": {
            "due_date": due_date,
            "audience": ["beginning grad in chemistry"],
            "success_def": "audience is happy",
            "scope": [
                "UCs that are supported or some other scope description if it software",
                "sketch of science story if it is paper"],
            "platform": "description of how and where the audience will access the deliverable.  journal if it is a paper",
            "roll_out": [
                "steps that the audience will take to access and interact with the deliverable",
                "not needed for paper submissions"],
            "status": "proposed"}
        })
        pdoc.update({"kickoff": {
            "due_date": now + relativedelta(days=7),
            "audience": ["lead", "pi", "group_members"],
            "name": "Kick off meeting",
            "objective": "introduce project to the lead",
            "status": "proposed"
        }})

        secondm = {'due_date': now + relativedelta(days=21),
                   'name': 'Project lead presentation',
                   'objective': 'to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.',
                   'audience': ['lead', 'pi', 'group_members'],
                   'status': 'proposed',
                   'type': 'meeting'
                   }
        pdoc.update({"milestones": [secondm]})

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
