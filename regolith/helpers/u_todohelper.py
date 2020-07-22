"""Helper for updating a task in todos of people collection.
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
ALLOWED_STATUS = ["started", "finished"]


def subparser(subpi):
    subpi.add_argument("-i", "--index",
                       help="Index of the item in the enumerated list to mark as finished.",
                       type=int)
    subpi.add_argument("-d", "--description",
                       help=" Change the description of the to_do task. If the description has more than one "
                            "word, please enclose it in quotation marks."
                       )
    subpi.add_argument("-due", "--due_date",
                       help="Change the due date of the task. Either enter a date in format YYYY-MM-DD or an "
                            "integer. Integer 5 means 5 days from the begin_date. "
                       )
    subpi.add_argument("-e", "--estimated_duration",
                       help="Change the estimated duration the task will take in minutes. ",
                       type=float
                       )
    subpi.add_argument("-im", "--importance",
                       help=f"Change the importance of the task from {ALLOWED_IMPORTANCE}.",
                       type=int
                       )
    subpi.add_argument("-s", "--status",
                       help=f"Change the status of the task from {ALLOWED_STATUS}."
                       )
    subpi.add_argument("-n", "--notes", nargs="+", help="Change the notes for this task. Each note should be enclosed "
                                                        "in quotation marks.")
    subpi.add_argument("-b", "--begin_date",
                       help="Change the begin date of the task in format YYYY-MM-DD."
                       )
    subpi.add_argument("-end", "--end_date",
                       help="Change the end date of the task in format YYYY-MM-DD."
                       )
    subpi.add_argument("-a", "--assigned_to",
                       help="ID of the member to whom the task is assigned. Default id is saved in user.json. ")

    return subpi


class TodoUpdaterHelper(DbHelperBase):
    """Helper for updating a task in todos of people collection.
    """
    # btype must be the same as helper target in helper.py
    btype = "u_todo"
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
        filterid = {'_id': rc.assigned_to}
        person = rc.client.find_one(rc.database, rc.coll, filterid)
        if not person:
            raise TypeError(f"Id {rc.assigned_to} can't be found in people collection")
        todolist = person.get("todos", [])
        if len(todolist) == 0:
            print(f"{rc.assigned_to} doesn't have todos in people collection.")
            return
        index = 1
        for t in todolist:
            t["index"] = index
            index += 1
        if not rc.index:
            print("-" * 50)
            print("Please choose from one of the following to update:")

            print("    action (due date|importance|expected duration(mins)|status|begin date|end date)")

            for t in todolist:
                print(
                    f"{t.get('index'):>2}. {t.get('description')}({t.get('due_date')}|{t.get('importance')}|{str(t.get('duration'))}|{t.get('status')}|{t.get('begin_date')}|{t.get('end_date')})")
                if t.get('notes'):
                    for note in t.get('notes'):
                        print(f"     - {note}")
                del t['index']
            print("-" * 50)
            return
        else:
            match_todo = [i for i in todolist if i.get("index") == rc.index]
            if len(match_todo) == 0:
                raise RuntimeError("Please enter a valid index.")
            else:
                todo = match_todo[0]
                idx = todolist.index(todo)
                if rc.description:
                    todo["description"] = rc.description
                if rc.due_date:
                    try:
                        relative_day = int(rc.due_date)
                        due_date = todo.get("begin_date") + relativedelta(days=relative_day)
                    except ValueError:
                        due_date = date_parser.parse(rc.due_date).date()
                    todo["due_date"] = due_date
                if rc.estimated_duration:
                    todo["duration"] = rc.estimated_duration
                if rc.importance:
                    if rc.importance in ALLOWED_IMPORTANCE:
                        todo["importance"] = rc.importance
                    else:
                        raise ValueError(f"Importance should be chosen from{ALLOWED_IMPORTANCE}.")
                if rc.status:
                    if rc.status in ALLOWED_STATUS:
                        todo["status"] = rc.status
                    else:
                        raise ValueError(f"Status should be chosen from{ALLOWED_STATUS}.")
                if rc.notes:
                    todo["notes"] = rc.notes
                if rc.begin_date:
                    todo["begin_date"] = date_parser.parse(rc.begin_date).date()
                if rc.end_date:
                    todo["end_date"] = date_parser.parse(rc.end_date).date()
                todolist[idx] = todo

            for t in todolist:
                if t.get('index'):
                    del t['index']
            rc.client.update_one(rc.database, rc.coll, {'_id': rc.assigned_to}, {"todos": todolist}, upsert=True)
            print(
                f"The task for {rc.assigned_to} has been updated in {TARGET_COLL} collection.")

        return
