"""Helper for listing the to-do tasks. Tasks are gathered from people.yml, milestones, and group meeting actions.

"""
import datetime as dt
import dateutil.parser as date_parser
import math
import sys
from dateutil.relativedelta import *

from regolith.dates import get_due_date, get_dates
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    document_by_value,
    print_task,
    key_value_pair_filter
)

TARGET_COLL = "people"
TARGET_COLL2 = "projecta"
HELPER_TARGET = "l_todo"
Importance = [0, 1, 2, -1, -2]
ALLOWED_STATI = ["started", "finished", "cancelled"]
ACTIVE_STATI = ["started", "converged", "proposed"]


def subparser(subpi):
    subpi.add_argument("-s", "--stati", nargs='+', help=f'Filter tasks with specific status from {ALLOWED_STATI}. '
                                                        f'Default is started.', default=["started"])
    subpi.add_argument("--short", nargs='?', const=30,
                       help='Filter tasks with estimated duration <= 30 mins, but if a number is specified, the duration of the filtered tasks will be less than that number of minutes.')
    subpi.add_argument("-t", "--tags", nargs='+',
                       help="Filter tasks by tags. Items are returned if they contain any of the tags listed")
    subpi.add_argument("-a", "--assigned_to",
                       help="Filter tasks that are assigned to this user id. Default id is saved in user.json. ")
    subpi.add_argument("-b", "--assigned_by", nargs='?', const="default_id",
                       help="Filter tasks that are assigned to other members by this user id. Default id is saved in user.json. ")
    subpi.add_argument("--date",
                       help="Enter a date such that the helper can calculate how many days are left from that date to the due-date. Default is today.")
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs. '-f description paper' will return tasks with description containing 'paper' ")

    return subpi


class TodoListerHelper(SoutHelperBase):
    """Helper for listing the to-do tasks. Tasks are gathered from people.yml, milestones, and group meeting actions.
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}', f'{TARGET_COLL2}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        try:
            if not rc.database:
                rc.database = rc.databases[0]["name"]
        except:
            pass
        colls = [
            sorted(
                all_docs_from_collection(rc.client, collname), key=_id_key
            )
            for collname in self.needed_dbs
        ]
        for db, coll in zip(self.needed_dbs, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        if not rc.assigned_to:
            try:
                rc.assigned_to = rc.default_user_id
            except AttributeError:
                print(
                    "Please set default_user_id in '~/.config/regolith/user.json', or you need to enter your group id "
                    "in the command line")
                return
        try:
            person = document_by_value(all_docs_from_collection(rc.client, "people"), "_id", rc.assigned_to)
            gather_todos = person.get("todos", [])
        except:
            print(
                "The id you entered can't be found in people.yml.")
            return
        if not rc.date:
            today = dt.date.today()
        else:
            today = date_parser.parse(rc.date).date()
        if rc.stati == ["started"]:
            rc.stati = ACTIVE_STATI
        for projectum in self.gtx["projecta"]:
            if projectum.get('lead') != rc.assigned_to:
                continue
            projectum["deliverable"].update({"name": "deliverable"})
            gather_miles = [projectum["kickoff"], projectum["deliverable"]]
            gather_miles.extend(projectum["milestones"])
            for ms in gather_miles:
                if projectum["status"] not in ["finished", "cancelled"]:
                    if ms.get('status') not in \
                            ["finished", "cancelled"]:
                        due_date = get_due_date(ms)
                        ms.update({
                            'id': projectum.get('_id'),
                            'due_date': due_date,
                            'assigned_by': projectum.get('pi_id')
                        })
                        ms.update({'description': f'milestone: {ms.get("name")} ({ms.get("id")})'})
                        gather_todos.append(ms)
        if rc.filter:
            gather_todos = key_value_pair_filter(gather_todos, rc.filter)
        if rc.short:
            for todo in gather_todos[::-1]:
                if todo.get('duration') is None or float(todo.get('duration')) > float(rc.short):
                    gather_todos.remove(todo)
        if rc.tags:
            for todo in gather_todos[::-1]:
                takeme = False
                for tag in rc.tags:
                    if tag in todo.get('tags'):
                        takeme = True
                if not takeme:
                    gather_todos.remove(todo)
        if rc.assigned_by:
            if rc.assigned_by == "default_id":
                rc.assigned_by = rc.default_user_id
            for todo in gather_todos[::-1]:
                if todo.get('assigned_by') != rc.assigned_by:
                    gather_todos.remove(todo)
                elif rc.assigned_to == rc.assigned_by:
                    gather_todos.remove(todo)
        len_of_started_tasks=0
        milestones = 0
        for todo in gather_todos:
            if 'milestone: ' in todo['description']:
                milestones += 1
            elif todo["status"] == 'started':
                len_of_started_tasks += 1
        len_of_tasks = len(gather_todos) - milestones
        for todo in gather_todos:
            if type(todo["due_date"]) == str:
                todo["due_date"] = date_parser.parse(todo["due_date"]).date()
            if type(todo.get("end_date")) == str:
                todo["end_date"] = date_parser.parse(todo["end_date"]).date()
            todo["days_to_due"] = (todo.get('due_date') - today).days
            todo["sort_finished"] = (todo.get("end_date", dt.date(1900, 1, 1)) - dt.date(1900, 1, 1)).days
            try:
                todo["order"] = todo.get('importance',1) + 1 / (1 + math.exp(abs(todo["days_to_due"]-0.5)))-(todo["days_to_due"] < -7)*10
            except OverflowError:
                todo["order"] = float('inf')
        gather_todos[:len_of_tasks] = sorted(gather_todos[:len_of_tasks], key=lambda k: (k['status'], k['order'], -k.get('duration', 10000)), reverse=True)
        gather_todos[len_of_started_tasks: len_of_tasks] = sorted(gather_todos[len_of_started_tasks: len_of_tasks], key=lambda k: (-k["sort_finished"]))
        gather_todos[len_of_tasks:] = sorted(gather_todos[len_of_tasks:], key=lambda k: (k['status'], k['order'], -k.get('duration', 10000)), reverse=True)
        print("If the indices are far from being in numerical order, please reorder them by running regolith helper u_todo -r")
        print("(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)")
        print("-" * 81)
        if len_of_tasks != 0:
            print("tasks from people collection:")
            print("-" * 30)
            print_task(gather_todos[:len_of_tasks], stati=rc.stati)
        if milestones != 0:
            print("-" * 42)
            print("tasks from projecta and other collections:")
            print("-" * 42)
            print_task(gather_todos[len_of_tasks:], stati=rc.stati, index=False)
        print("-" * 81)
        return
