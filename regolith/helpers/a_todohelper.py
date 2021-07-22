"""Helper for adding a to_do task to todos.yml

"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta

from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    _id_key
)
from gooey import GooeyParser

TARGET_COLL = "todos"
ALLOWED_IMPORTANCE = [3, 2, 1, 0]


def subparser(subpi):
    date_kwargs = {}
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs['widget'] = 'DateChooser'
        int_kwargs['widget'] = 'IntegerField'
        int_kwargs['gooey_options'] = {'min': 0, 'max': 10000}
    subpi.add_argument("description",
                       help="the description of the to_do task. If the description has more than one "
                            "word, please enclose it in quotation marks.",
                       default=None)
    subpi.add_argument("due_date",
                       help="Due date of the task, in days from today (integer), or "
                            "as a date in iso format (yyyy-mm-dd)",
                       )
    subpi.add_argument("duration",
                       help="The estimated duration the task will take in minutes (integer) "
                            "e.g., 60 would be a duration of 1 hour."
                       )
    subpi.add_argument("-d", "--deadline", action="store_true",
                       help=f"specify if the due date (above) has a hard deadline",
                       )
    subpi.add_argument("-m", "--importance",
                       choices=ALLOWED_IMPORTANCE,
                       type=int,
                       help=f"The importance of the task. "
                            f"Corresponds roughly to (3) tt, (2) tf, (1) ft, (0) ff in the Eisenhower matrix of "
                            f"importance vs. urgency.  An important and urgent task would be 3.",
                       default=1
                       )
    subpi.add_argument("-t", "--tags", nargs="+",
                       help="Tags to be associated with this task.  Enter as single words separated by spaces. "
                            "The todo list can be filtered by these tags")
    subpi.add_argument("-n", "--notes", nargs="+",
                       help="Additional notes for this task. Each note should be enclosed "
                            "in quotation marks and different notes separated by spaces")
    subpi.add_argument("-a", "--assigned_to",
                       help="ID of the group member to whom the task is assigned. Default is the id saved in user.json. ")
    subpi.add_argument("-b", "--assigned_by",
                       help="ID of the member that is assigning the task. Default is the id saved in user.json. ")
    subpi.add_argument("--begin_date",
                       help="Begin date of the task. Default is today.",
                       **date_kwargs
                       )
    subpi.add_argument("--database",
                       help="The database in which the collection will be updated. "
                            "Defaults to the first database in regolithrc.json if not "
                            "specified.")
    subpi.add_argument("--date",
                       help="Enter a date such that the helper can calculate how many days are left from that date to the deadline. Default is today.",
                       **date_kwargs)

    return subpi


class TodoAdderHelper(DbHelperBase):
    """Helper for adding a todo task to todos.yml
    """
    # btype must be the same as helper target in helper.py
    btype = "a_todo"
    needed_colls = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
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
            raise TypeError(
                f"The id {rc.assigned_to} can't be found in the todos collection")
        if not rc.assigned_by:
            rc.assigned_by = rc.default_user_id
        find_person = rc.client.find_one(rc.database, rc.coll,
                                         {'_id': rc.assigned_by})
        if not find_person:
            raise TypeError(
                f"The id {rc.assigned_by} can't be found in the todos collection")
        now = dt.date.today()
        if not rc.begin_date:
            begin_date = now
        else:
            begin_date = date_parser.parse(rc.begin_date).date()
        if not rc.date:
            today = now
        else:
            today = date_parser.parse(rc.date).date()
        try:
            relative_day = int(rc.due_date)
            due_date = today + relativedelta(days=relative_day)
        except ValueError:
            due_date = date_parser.parse(rc.due_date).date()
        if begin_date > due_date:
            raise ValueError("begin_date can not be after due_date")
        if rc.importance not in ALLOWED_IMPORTANCE:
            raise ValueError(
                f"importance should be chosen from {ALLOWED_IMPORTANCE}")
        else:
            importance = int(rc.importance)

        todolist = person.get("todos", [])
        if not rc.deadline:
            rc.deadline = False
        todolist.append({
            'description': rc.description,
            'due_date': due_date,
            'begin_date': begin_date,
            'deadline': rc.deadline,
            'duration': float(rc.duration),
            'importance': importance,
            'status': "started",
            'assigned_by': rc.assigned_by})
        if rc.notes:
            todolist[-1]['notes'] = rc.notes
        if rc.tags:
            todolist[-1]['tags'] = rc.tags
        indices = [todo.get("running_index", 0) for todo in todolist]
        todolist[-1]['running_index'] = max(indices) + 1
        rc.client.update_one(rc.database, rc.coll, {'_id': rc.assigned_to},
                             {"todos": todolist},
                             upsert=True)
        print(
            f"The task \"{rc.description}\" for {rc.assigned_to} has been added in {TARGET_COLL} collection.")

        return
