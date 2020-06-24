"""Helper for adding a projectum to the projecta collection.

   Projecta are small bite-sized project quanta that typically will result in
   one manuscript.
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

TARGET_COLL = "todolist"
Importance = [0, 1, 2]


def subparser(subpi):
    subpi.add_argument("description", help="the description of the to_do task",
                       default=None)
    subpi.add_argument("due_date",
                       help="Proposed due date for the to_do task. Please enter a number. 5 means 5 days from the "
                            "begin_date. "
                       )
    subpi.add_argument("-b", "--begin_date",
                       help="Begin date of the task. Default is today."
                       )
    subpi.add_argument("-i", "--id", help="ID of the to_do list's owner. The default id is saved in user.json. ")
    subpi.add_argument("-p", "--importance",
                       help=f"The importance of this task from {Importance}. Default is 1.",
                       default=1
                       )
    subpi.add_argument("-d", "--duration",
                       help="The estimated duration that the task will take. The unit is minute. Default is 60 ",
                       default=60
                       )
    return subpi


class TodoAdderHelper(DbHelperBase):
    """Helper for adding a projectum to the projecta collection.

       Projecta are small bite-sized project quanta that typically will result in
       one manuscript.
    """
    # btype must be the same as helper target in helper.py
    btype = "a_todo"
    needed_dbs = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
            rc.pi_id = get_pi_id(rc)

        rc.coll = f"{TARGET_COLL}"
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
        if not rc.id:
            try:
                rc.id = rc.default_user_id
            except AttributeError:
                raise RuntimeError(
                    "Please set default_user_id and user_first_name in '~/.config/regolith/user.json',\
                     or you need to input your id in the command line")

        now = dt.date.today()
        if not rc.begin_date:
            begin_date = now
        else:
            begin_date = date_parser.parse(rc.begin_date).date()
        due_date = begin_date + relativedelta(days=int(rc.due_date))

        key = f"{rc.id}"
        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            for member in coll:
                if key == member["_id"]:
                    todo_update = []
                    mark = 0
                    for todo_item in member["todos"]:
                        todo_item['mark'] = mark
                        todo_update.append(todo_item)
                        mark += 1
                    todo_update.append({
                        'description': rc.description,
                        'due_date': due_date,
                        'begin_date': begin_date,
                        'duration': float(rc.duration),
                        'importance': int(rc.importance),
                        'status': "started",
                        'mark': mark})
                    rc.client.update_one(rc.database, rc.coll, {'id': rc.id}, {"todos": todo_update},
                                         upsert=True)
                    break
        else:
            member = {}
            member.update({
                "_id": rc.id,
                "id": rc.id
            })
            member.update({"todos": [{
                'description': rc.description,
                'due_date': due_date,
                'begin_date': begin_date,
                'duration': float(rc.duration),
                'importance': int(rc.importance),
                'status': "started",
                'mark': 0}]
            })
            rc.client.insert_one(rc.database, rc.coll, member)

        print(f"The task has been added in {TARGET_COLL}.")

        return
