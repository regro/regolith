"""Helper for updating a task in todos of todos collection."""

import datetime as dt
import math

import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.schemas import PROJECTUM_ACTIVE_STATI, alloweds
from regolith.tools import (
    all_docs_from_collection,
    document_by_value,
    get_pi_id,
    key_value_pair_filter,
    print_task,
)

TARGET_COLL = "todos"
ALLOWED_IMPORTANCE = [3, 2, 1, 0]

TODO_STATI = alloweds.get("TODO_STATI")


def subparser(subpi):
    deci_kwargs = {}
    notes_kwargs = {}
    date_kwargs = {}
    int_kwargs = {}
    listbox_kwargs = {}
    if isinstance(subpi, GooeyParser):
        deci_kwargs["widget"] = "DecimalField"
        deci_kwargs["gooey_options"] = {"min": 0.0, "max": 10000.0, "increment": 1, "precision": 1}
        notes_kwargs["widget"] = "Textarea"
        date_kwargs["widget"] = "DateChooser"
        int_kwargs["widget"] = "IntegerField"
        listbox_kwargs["widget"] = "Listbox"
        listbox_kwargs["choices"] = TODO_STATI

    subpi.add_argument(
        "-i",
        "--index",
        help="Enter the index of a certain task in the enumerated list to update that task.",
        type=int,
        **int_kwargs,
    )
    subpi.add_argument(
        "-s",
        "--stati",
        nargs="+",
        help='Update tasks with specific stati"',
        default=["started"],
        **listbox_kwargs,
    )
    subpi.add_argument(
        "-f",
        "--filter",
        nargs="+",
        help="Search this collection by giving key element pairs. "
        "'-f description paper' will return tasks with description containing 'paper' ",
    )
    subpi.add_argument("-r", "--renumber", action="store_true", help="Renumber the indices.")
    subpi.add_argument(
        "-d",
        "--description",
        help=" Change the description of the to_do task. If the description has more than one "
        "word, please enclose it in quotation marks.",
    )
    subpi.add_argument("-u", "--due-date", help="Change the due date of the task.", **date_kwargs)
    subpi.add_argument(
        "-e",
        "--estimated-duration",
        help="Change the estimated duration the task will take in minutes. ",
        type=float,
        **deci_kwargs,
    )
    subpi.add_argument(
        "--deadline", help="give value 't' if due_date is a hard deadline, else 'f' if not", choices=["t", "f"]
    )
    subpi.add_argument(
        "-m", "--importance", choices=ALLOWED_IMPORTANCE, help="Change the importance of the task.", type=int
    )
    subpi.add_argument("--status", choices=TODO_STATI, help="Change the status of the task.")
    subpi.add_argument(
        "-n",
        "--notes",
        nargs="+",
        help="The new notes for this task. Each note should be enclosed " "in quotation marks.",
        **notes_kwargs,
    )
    subpi.add_argument("-t", "--tags", nargs="+", help="The new tags to add for this task.")
    subpi.add_argument("--begin-date", help="Change the begin date of the task.", **date_kwargs)
    subpi.add_argument("--end-date", help="Change the end date of the task.", **date_kwargs)
    subpi.add_argument(
        "-a",
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
        "--date",
        help="Enter a date such that the helper can calculate how many days are left "
        "from that date to the due date. Default is today.",
        **date_kwargs,
    )

    return subpi


class TodoUpdaterHelper(DbHelperBase):
    """Helper for updating a task in todos of todos collection."""

    # btype must be the same as helper target in helper.py
    btype = "u_todo"
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
                    "should be updated using u_milestone and not u_todo"
                )
                return
        if not rc.assigned_to:
            try:
                rc.assigned_to = rc.default_user_id
            except AttributeError:
                print(
                    "Please set default_user_id in '~/.config/regolith/user.json', or you need to enter "
                    "your group id in the command line"
                )
                return
        filterid = {"_id": rc.assigned_to}
        person = document_by_value(all_docs_from_collection(rc.client, "todos"), "_id", rc.assigned_to)
        if not person:
            raise TypeError(f"Id {rc.assigned_to} can't be found in todos collection")
        todolist = person.get("todos", [])
        if len(todolist) == 0:
            print(f"{rc.assigned_to} doesn't have todos in todos collection.")
            return
        if not rc.date:
            today = dt.date.today()
        else:
            today = date_parser.parse(rc.date).date()
        if not rc.index:
            finished_todo = 0
            for todo in todolist:
                if todo["status"] == "finished":
                    finished_todo += 1
                if isinstance(todo.get("due_date"), str):
                    todo["due_date"] = date_parser.parse(todo["due_date"]).date()
                if isinstance(todo.get("end_date"), str):
                    todo["end_date"] = date_parser.parse(todo["end_date"]).date()
                todo["days_to_due"] = (todo.get("due_date") - today).days
                todo["sort_finished"] = (todo.get("end_date", dt.date(1900, 1, 1)) - dt.date(1900, 1, 1)).days
                todo["order"] = 1 / (1 + math.exp(abs(todo["days_to_due"] - 0.5)))
            todolist = sorted(
                todolist, key=lambda k: (k["status"], k["importance"], k["order"], -k.get("duration", 10000))
            )
            todolist[:finished_todo] = sorted(todolist[:finished_todo], key=lambda k: (-k["sort_finished"]))
            index_match = {}
            if rc.renumber:
                new_index_started = 1
                new_index_finished = -1
                for todo in reversed(todolist[finished_todo:]):
                    index_match[todo["running_index"]] = new_index_started
                    new_index_started += 1
                for todo in reversed(todolist[:finished_todo]):
                    index_match[todo["running_index"]] = new_index_finished
                    new_index_finished += -1
                for i in range(0, len(rc.databases)):
                    db_name = rc.databases[i]["name"]
                    person_idx = rc.client.find_one(db_name, rc.coll, filterid)
                    if isinstance(person_idx, dict):
                        todolist_idx = person_idx.get("todos", [])
                    else:
                        continue
                    if len(todolist_idx) != 0:
                        for todo in todolist_idx:
                            index = index_match[todo["running_index"]]
                            todo["running_index"] = index
                        rc.client.update_one(
                            db_name, rc.coll, {"_id": rc.assigned_to}, {"todos": todolist_idx}, upsert=True
                        )
                        print(f"Indices in {db_name} for {rc.assigned_to} have been updated.")
                return
            if rc.assigned_by:
                if rc.assigned_by == "default_id":
                    rc.assigned_by = rc.default_user_id
                for todo in todolist[::-1]:
                    if todo.get("assigned_by") != rc.assigned_by:
                        print(todo.get("assigned_by"))
                        todolist.remove(todo)
            if rc.filter:
                todolist = key_value_pair_filter(todolist, rc.filter)
            if rc.stati == ["started"]:
                rc.stati = PROJECTUM_ACTIVE_STATI
            print(
                "If the indices are far from being in numerical order, please renumber them by running "
                "regolith helper u_todo -r"
            )
            print("Please choose from one of the following to update:")
            print("(index) action (days to due date|importance|expected duration (mins)|assigned by)")
            print("-" * 80)
            print_task(todolist, stati=rc.stati)
        else:
            match_todo = [i for i in todolist if i.get("running_index") == rc.index]
            if len(match_todo) == 0:
                raise RuntimeError("Please enter a valid index.")
            else:
                todo = match_todo[0]
                if rc.description:
                    todo["description"] = rc.description
                if rc.due_date:
                    try:
                        relative_day = int(rc.due_date)
                        due_date = today + relativedelta(days=relative_day)
                    except ValueError:
                        due_date = date_parser.parse(rc.due_date).date()
                    todo["due_date"] = due_date
                if rc.deadline:
                    if rc.deadline.lower() != "t":
                        if rc.deadline.lower() != "f":
                            raise RuntimeError("ERROR: allowed values for deadline are t or f")
                        else:
                            todo["deadline"] = False
                    else:
                        todo["deadline"] = True
                if rc.estimated_duration:
                    todo["duration"] = rc.estimated_duration
                if rc.importance or rc.importance == 0:
                    if rc.importance in ALLOWED_IMPORTANCE:
                        todo["importance"] = rc.importance
                    else:
                        raise ValueError(f"Importance should be chosen from{ALLOWED_IMPORTANCE}.")
                if rc.status:
                    if rc.status in TODO_STATI:
                        todo["status"] = rc.status
                    else:
                        raise ValueError(f"Status should be chosen from {TODO_STATI}.")
                if rc.notes:
                    try:
                        todo["notes"].extend(rc.notes)
                    except KeyError:
                        todo["notes"] = []
                        todo["notes"].extend(rc.notes)
                if rc.tags:
                    try:
                        todo["tags"].extend(rc.tags)
                    except KeyError:
                        todo["tags"] = []
                        todo["tags"].extend(rc.tags)
                if rc.begin_date:
                    todo["begin_date"] = date_parser.parse(rc.begin_date).date()
                if rc.end_date:
                    todo["end_date"] = date_parser.parse(rc.end_date).date()

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
                                    f"The task \"({todo_u['running_index']}) {todo_u['description'].strip()}\" in "
                                    f"{db_name} for {rc.assigned_to} has been updated."
                                )
                                return
        return
