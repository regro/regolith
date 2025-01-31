"""Helper for marking a task as finished in todos collection."""

import datetime as dt
import math

import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import (
    all_docs_from_collection,
    document_by_value,
    get_pi_id,
    key_value_pair_filter,
    print_task,
)

TARGET_COLL = "todos"
ALLOWED_IMPORTANCE = [0, 1, 2]


def subparser(subpi):
    date_kwargs = {}
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        int_kwargs["widget"] = "IntegerField"

    subpi.add_argument(
        "-i",
        "--index",
        help="Enter the index of a certain task in the enumerated list to mark as finished.",
        type=int,
    )
    subpi.add_argument("--end-date", help="Add the end date of the task. Default is today.", **date_kwargs)
    subpi.add_argument(
        "-t",
        "--assigned-to",
        help="Filter tasks that are assigned to this user id. Default id is saved in user.json. ",
    )
    subpi.add_argument(
        "-b",
        "--assigned-by",
        nargs="?",
        const="default_id",
        help="Filter tasks that are assigned to other members by this user id. Default id is saved in user.json. ",
    )
    subpi.add_argument(
        "-f",
        "--filter",
        nargs="+",
        help="Search this collection by giving key element pairs. "
        "'-f description paper' will return tasks with description containing 'paper' ",
    )
    subpi.add_argument(
        "--date",
        help="Enter a date such that the helper can calculate how many days are left "
        "from that date to the due-date. Default is today.",
        **date_kwargs,
    )
    return subpi


class TodoFinisherHelper(DbHelperBase):
    """Helper for marking a task as finished in todos collection."""

    # btype must be the same as helper target in helper.py
    btype = "f_todo"
    needed_colls = [f"{TARGET_COLL}"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
            rc.pi_id = get_pi_id(rc)

        rc.coll = f"{TARGET_COLL}"
        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        if rc.index:
            if rc.index >= 9900:
                print(
                    "WARNING: indices >= 9900 are used for milestones which "
                    "should be finished using u_milestone and not f_todo"
                )
                return
        if not rc.assigned_to:
            try:
                rc.assigned_to = rc.default_user_id
            except AttributeError:
                print(
                    "Please set default_user_id in '~/.config/regolith/user.json', "
                    "or you need to enter your group id in the command line"
                )
                return
        person = document_by_value(all_docs_from_collection(rc.client, "todos"), "_id", rc.assigned_to)
        filterid = {"_id": rc.assigned_to}
        if not person:
            raise TypeError(f"Id {rc.assigned_to} can't be found in todos collection")
        todolist = person.get("todos", [])
        if len(todolist) == 0:
            print(f"{rc.assigned_to} doesn't have todos in todos collection.")
            return
        now = dt.date.today()
        if not rc.index:
            if not rc.date:
                today = now
            else:
                today = date_parser.parse(rc.date).date()
            if rc.filter:
                todolist = key_value_pair_filter(todolist, rc.filter)
            for todo in todolist:
                if isinstance(todo["due_date"], str):
                    todo["due_date"] = date_parser.parse(todo["due_date"]).date()
                todo["days_to_due"] = (todo.get("due_date") - today).days
                todo["order"] = 1 / (1 + math.exp(abs(todo["days_to_due"] - 0.5)))
            todolist = sorted(
                todolist, key=lambda k: (k["status"], k["importance"], k["order"], -k.get("duration", 10000))
            )
            print(
                "If the indices are far from being in numerical order, "
                "please renumber them by running regolith helper u_todo -r"
            )
            print("Please choose from one of the following to update:")
            print("(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)")
            print("-" * 80)
            print_task(todolist, stati=["started"])
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
                    if person_update:
                        todolist_update = person_update.get("todos", [])
                    else:
                        continue
                    if len(todolist_update) != 0:
                        for i, todo_u in enumerate(todolist_update):
                            if rc.index == todo_u.get("running_index"):
                                todolist_update[i] = todo
                                rc.client.update_one(
                                    db_name,
                                    rc.coll,
                                    {"_id": rc.assigned_to},
                                    {"todos": todolist_update},
                                    upsert=True,
                                )
                                print(
                                    f"The task \"({todo_u['running_index']}) {todo_u['description'].strip()}\" "
                                    f"in {db_name} for {rc.assigned_to} has been marked as finished."
                                )
                                return
        return
