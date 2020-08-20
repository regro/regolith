"""Helper for marking a task as finished in todos of people collection.
"""

import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys
import math

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    document_by_value,
    print_task,
    key_value_pair_filter
)

TARGET_COLL = "people"
ALLOWED_IMPORTANCE = [0, 1, 2]


def subparser(subpi):
    subpi.add_argument("-i", "--index",
                       help="Enter the index of a certain task in the enumerated list to mark as finished.",
                       type=int)
    subpi.add_argument("--end_date",
                       help="Add the end date of the task. Default is today.")
    subpi.add_argument("-t", "--assigned_to",
                       help="Filter tasks that are assigned to this user id. Default id is saved in user.json. ")
    subpi.add_argument("-b", "--assigned_by", nargs='?', const="default_id",
                       help="Filter tasks that are assigned to other members by this user id. Default id is saved in user.json. ")
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs. '-f description paper' will return tasks with description containing 'paper' ")
    subpi.add_argument("-c", "--certain_date",
                       help="Enter a certain date so that the helper can calculate how many days are left from that date to the deadline. Default is today.")
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
        person = document_by_value(all_docs_from_collection(rc.client, "people"), "_id", rc.assigned_to)
        filterid = {'_id': rc.assigned_to}
        if not person:
            raise TypeError(f"Id {rc.assigned_to} can't be found in people collection")
        todolist = person.get("todos", [])
        if len(todolist) == 0:
            print(f"{rc.assigned_to} doesn't have todos in people collection.")
            return
        now = dt.date.today()
        if not rc.index:
            if not rc.certain_date:
                today = now
            else:
                today = date_parser.parse(rc.certain_date).date()
            if rc.filter:
                todolist = key_value_pair_filter(todolist, rc.filter)
            for todo in todolist:
                if not todo.get('importance'):
                    todo['importance'] = 1
                if type(todo["due_date"]) == str:
                    todo["due_date"] = date_parser.parse(todo["due_date"]).date()
                todo["days_to_due"] = (todo.get('due_date') - today).days
                todo["order"] = todo['importance'] + 1 / (1 + math.exp(abs(todo["days_to_due"]-0.5)))-(todo["days_to_due"] < -7)*10
            todolist = sorted(todolist, key=lambda k: (k['status'], k['order'], -k.get('duration', 10000)), reverse=True)
            print("If the indices are far from being in numerical order, please reorder them by running regolith helper u_todo -r")
            print("Please choose from one of the following to update:")
            print("(index) action (days to due date|importance|expected duration (mins)|assigned by)")
            print("-" * 81)
            print_task(todolist, stati=['started'])
            print("-" * 81)
        else:
            match_todo = [i for i in todolist if i.get("running_index") == rc.index]
            if len(match_todo) == 0:
                raise RuntimeError("Please enter a valid index.")
            else:
                todo = match_todo[0]
                todo["status"] = "finished"
                if not rc.end_date:
                    end_date = now
                else:
                    end_date = date_parser.parse(rc.end_date).date()
                todo["end_date"] = end_date
                for i in range(0, len(rc.databases)):
                    db_name = rc.databases[i]["name"]
                    person_update = rc.client.find_one(db_name, rc.coll, filterid)
                    todolist_update = person_update.get("todos", [])
                    if len(todolist_update) != 0:
                        for i, todo_u in enumerate(todolist_update):
                            if rc.index == todo_u.get("running_index"):
                                todolist_update[i]= todo
                                rc.client.update_one(db_name, rc.coll, {'_id': rc.assigned_to}, {"todos": todolist_update}, upsert=True)
                                print(f"The task \"({todo_u['running_index']}) {todo_u['description'].strip()}\" in {db_name} for {rc.assigned_to} has been marked as finished.")
                                return
        return
