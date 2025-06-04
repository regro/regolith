"""Helper for listing the to-do tasks.

Tasks are gathered from people.yml, milestones, and group meeting actions."""

import datetime as dt
import math

import dateutil.parser as date_parser
from gooey import GooeyParser
from nameparser import HumanName

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.schemas import PROJECTUM_ACTIVE_STATI, alloweds
from regolith.tools import (
    all_docs_from_collection,
    document_by_value,
    get_pi_id,
    key_value_pair_filter,
    print_task,
    strip_str,
)

TARGET_COLL = "todos"
HELPER_TARGET = "l_todo"
Importance = [3, 2, 1, 0, -1, -2]  # eisenhower matrix (important|urgent) tt=3, tf=2, ft=1, ff=0
STATI = ["accepted", "downloaded", "inprep"]

TODO_STATI = alloweds.get("TODO_STATI")


def subparser(subpi):
    listbox_kwargs = {}
    date_kwargs = {}
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        listbox_kwargs["widget"] = "Listbox"
        date_kwargs["widget"] = "DateChooser"
        int_kwargs["widget"] = "IntegerField"
        int_kwargs["gooey_options"] = {"min": 0, "max": 1000}

    subpi.add_argument(
        "--short",
        nargs="?",
        const=20,
        help="Filter for tasks of short duration. "
        "All items with a duration <= # mins, will be returned "
        "if the number # is specified.",
    )
    subpi.add_argument(
        "-t",
        "--tags",
        nargs="+",
        help="Filter tasks by tags. Items are returned if they contain any of the tags listed",
        type=strip_str,
    )
    subpi.add_argument(
        "-s",
        "--stati",
        nargs="+",
        choices=TODO_STATI,
        help="Filter tasks with specific stati",
        default=["started"],
        type=strip_str,
        **listbox_kwargs,
    )
    subpi.add_argument("-o", "--outstandingreview", help="List outstanding reviews", action="store_true")
    subpi.add_argument(
        "-a",
        "--assigned-to",
        help="Filter tasks that are assigned to this user id. Default id is saved in user.json.",
        type=strip_str,
    )
    subpi.add_argument(
        "-b",
        "--assigned-by",
        nargs="?",
        const="default_id",
        help="Filter tasks that are assigned to other members by this user id. Default id is saved in user.json. ",
        type=strip_str,
    )
    subpi.add_argument(
        "--date",
        help="Enter a date such that the helper can calculate how many days are left "
        "from that date to the due-date. Default is today.",
        type=strip_str,
        **date_kwargs,
    )
    subpi.add_argument(
        "-f",
        "--filter",
        nargs="+",
        help="Search this collection by giving key element pairs. '-f description paper' will return tasks "
        "with description containing 'paper' ",
        type=strip_str,
    )

    return subpi


class TodoListerHelper(SoutHelperBase):
    """Helper for listing the to-do tasks.

    Tasks are gathered from people.yml, milestones, and group meeting actions."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "refereeReports", "proposalReviews"]

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        colls = [
            sorted(all_docs_from_collection(rc.client, collname), key=_id_key) for collname in self.needed_colls
        ]
        for db, coll in zip(self.needed_colls, colls):
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
                    "Please set default_user_id in '~/.config/regolith/user.json', "
                    "or you need to enter your group id in the command line"
                )
                return
        try:
            person = document_by_value(all_docs_from_collection(rc.client, "todos"), "_id", rc.assigned_to)
            gather_todos = person.get("todos", [])
        except Exception:
            print("The id you entered can't be found in todos.yml.")
            return
        if not rc.date:
            today = dt.date.today()
        else:
            today = date_parser.parse(rc.date).date()
        if rc.stati == ["started"]:
            rc.stati = PROJECTUM_ACTIVE_STATI
        if rc.filter:
            gather_todos = key_value_pair_filter(gather_todos, rc.filter)
        if rc.short:
            for todo in gather_todos[::-1]:
                if todo.get("duration") is None or float(todo.get("duration")) > float(rc.short):
                    gather_todos.remove(todo)
        if rc.tags:
            for todo in gather_todos[::-1]:
                takeme = False
                for tag in rc.tags:
                    if tag in todo.get("tags", []):
                        takeme = True
                if not takeme:
                    gather_todos.remove(todo)
        if rc.assigned_by:
            if rc.assigned_by == "default_id":
                rc.assigned_by = rc.default_user_id
            for todo in gather_todos[::-1]:
                if todo.get("assigned_by") != rc.assigned_by:
                    gather_todos.remove(todo)
        len_of_started_tasks = 0
        milestones = 0
        for todo in gather_todos:
            if "milestone: " in todo["description"]:
                milestones += 1
            elif todo["status"] == "started":
                len_of_started_tasks += 1
        len_of_tasks = len(gather_todos)  # - milestones
        for todo in gather_todos:
            _format_todos(todo, today)
        gather_todos[:len_of_tasks] = sorted(
            gather_todos[:len_of_tasks],
            key=lambda k: (k["status"], k["importance"], k["order"], -k.get("duration", 10000)),
        )
        gather_todos[len_of_started_tasks:len_of_tasks] = sorted(
            gather_todos[len_of_started_tasks:len_of_tasks], key=lambda k: (-k["sort_finished"])
        )
        gather_todos[len_of_tasks:] = sorted(
            gather_todos[len_of_tasks:], key=lambda k: (k["status"], k["order"], -k.get("duration", 10000))
        )
        print(
            "If the indices are far from being in numerical order, please renumber them "
            "by running regolith helper u_todo -r"
        )
        print("(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)")
        print("-" * 80)
        if len(gather_todos) != 0:
            print_task(gather_todos, stati=rc.stati)

        if rc.outstandingreview:
            prop = self.gtx["proposalReviews"]
            man = self.gtx["refereeReports"]
            outstanding_todo = []
            for manuscript in man:
                if manuscript.get("reviewer") != rc.assigned_to:
                    continue
                if manuscript.get("status") in STATI:
                    out = (
                        f"Manuscript by {manuscript.get('first_author_last_name')} in {manuscript.get('journal')} "
                        f"is due on {manuscript.get('due_date')}"
                    )
                    outstanding_todo.append((out, manuscript.get("due_date"), manuscript.get("status")))
            for proposal in prop:
                if proposal.get("reviewer") != rc.assigned_to:
                    continue
                if proposal.get("status") in STATI:
                    if isinstance(proposal.get("names"), str):
                        name = HumanName(proposal.get("names"))
                    else:
                        name = HumanName(proposal.get("names")[0])
                    out = (
                        f"Proposal by {name.last} for {proposal.get('agency')} ({proposal.get('requester')})"
                        f"is due on {proposal.get('due_date')}"
                    )
                    outstanding_todo.append((out, proposal.get("due_date"), proposal.get("status")))

            if len(outstanding_todo) != 0:
                print("-" * 30)
                print("Outstanding Reviews:")
                print("-" * 30)
            outstanding_todo = sorted(outstanding_todo, key=lambda k: str(k[1]))
            for stati in STATI:
                if stati in [output[2] for output in outstanding_todo]:
                    print(f"{stati}:")
                else:
                    continue
                for output in outstanding_todo:
                    if output[2] == stati:
                        print(output[0])

        return


def _format_todos(todo, today):
    """datify dates, set orders etc and update to-do items in place

    Parameters
    ----------
    todo: dict
      the to-do item to be munged

    Returns
    -------
    nothing

    """
    if isinstance(todo["due_date"], str):
        todo["due_date"] = date_parser.parse(todo["due_date"]).date()
    if isinstance(todo.get("end_date"), str):
        todo["end_date"] = date_parser.parse(todo["end_date"]).date()
    todo["days_to_due"] = (todo.get("due_date") - today).days
    todo["sort_finished"] = (todo.get("end_date", dt.date(1900, 1, 1)) - dt.date(1900, 1, 1)).days
    try:
        todo["order"] = 1 / (1 + math.exp(abs(todo["days_to_due"] - 0.5)))
    except OverflowError:
        todo["order"] = float("inf")
    return
