"""Helper for marking a task as finished in todos of people collection.
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
    document_by_value,
)

TARGET_COLL = "people"
ALLOWED_IMPORTANCE = [0, 1, 2]


def subparser(subpi):
    subpi.add_argument("-i", "--index",
                        help="Index of the item in the enumerated list to mark as finished.",
                        type = int)
    subpi.add_argument("-e", "--end_date",
                       help="End date of the task. Default is today.")
    subpi.add_argument("-a", "--assigned_to", help="ID of the member to whom the task is assigned. Default id is saved in user.json. ")
    return subpi


class TodoFinisherHelper(DbHelperBase):
    """Helper for marking a task as finished in todos of people collection.
    """
    # btype must be the same as helper target in helper.py
    btype = "f_todo"
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
        if not rc.assigned_to:
            try:
                rc.assigned_to = rc.default_user_id
            except AttributeError:
                print(
                    "Please set default_user_id in '~/.config/regolith/user.json', or you need to enter your group id "
                    "in the command line")
                return
        now = dt.date.today()
        if not rc.end_date:
            end_date = now
        else:
            end_date = date_parser.parse(rc.end_date).date()
        filterid = {'_id': rc.assigned_to}
        person = rc.client.find_one(rc.database, rc.coll, filterid)
        if not person:
            raise TypeError(f"Id {rc.assigned_to} can't be found in people collection")
        todolist = person.get("todos",[])
        if len(todolist) ==0:
            print(f"{rc.assigned_to} doesn't have todos in people collection.")
            return
        index = 1
        for todo in todolist:
            if todo.get('status') not in ["finished"]:
                todo["index"] = index
                index+=1

        if not rc.index:
            print("Please choose from one of the following to update:")
            for todo in todolist:
                if todo.get('status') not in ["finished"]:
                    print(f"{todo.get('index')}. {todo.get('description')}")
                    del todo['index']
            return
        else:
            match_todos = [i for i in todolist if i.get("index") == rc.index]
            if len(match_todos) ==0:
                raise RuntimeError("Please enter a valid index.")
            else:
                match_todo = match_todos[0]
                idx = todolist.index(match_todo)
                match_todo["status"] = "finished"
                match_todo["end_date"] = end_date
                todolist[idx] = match_todo

            for todo in todolist:
                if todo.get('index'):
                    del todo['index']
            rc.client.update_one(rc.database, rc.coll, {'_id': rc.assigned_to}, {"todos": todolist},upsert=True)
            print(f"The task \"{match_todo['description']}\" for {rc.assigned_to} has been marked as finished in {TARGET_COLL} collection.")

        return
