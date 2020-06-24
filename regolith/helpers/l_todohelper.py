"""Helper for listing the to-do tasks. Tasks are gathered from todolist.yml, milestones, and group meeting actions.

"""
import datetime as dt
import dateutil.parser as date_parser
import sys
from dateutil.relativedelta import *

from regolith.dates import get_due_date
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
)

TARGET_COLL = "todolist"
TARGET_COLL2 = "projecta"
TARGET_COLL3 = "meetings"
HELPER_TARGET = "l_todo"
Importance = [0, 1, 2]
ALLOWED_STATI = ["started", "finished"]


def subparser(subpi):
    subpi.add_argument("-v", "--verbose", action="store_true",
                       help='increase verbosity of output')
    subpi.add_argument("-i", "--id",
                       help=f"Filter to-do tasks for this user id. Default is saved in user.json."
                       )
    subpi.add_argument("-f", "--firstname",
                       help='Filter to-do tasks for this first name. Default is saved in user.json.')
    subpi.add_argument("-d", "--duration",
                       help='Filter to-do tasks whose estimated duration is less than the input value.')
    return subpi


class TodoListerHelper(SoutHelperBase):
    """Helper for listing the to-do tasks. Tasks are gathered from todolist.yml, milestones, and group meeting actions.
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}', f'{TARGET_COLL2}', f'{TARGET_COLL3}']

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
        if not rc.id:
            try:
                rc.id = rc.default_user_id
            except AttributeError:
                raise RuntimeError(
                    "Please set default_user_id and user_first_name in '~/.config/regolith/user.json',\
                     or you need to input your id and first name in the command line")
        if not rc.firstname:
            try:
                rc.firstname = rc.user_first_name
            except AttributeError:
                raise RuntimeError(
                    "Please set default_user_id and user_first_name in '~/.config/regolith/user.json',\
                     or you need to input your id and first name in the command line")
        gather_todos = []
        # gather to-do tasks in todolist.yml
        for member in self.gtx["todolist"]:
            if member.get('id') == rc.id:
                for todo in member["todos"]:
                    if type(todo["due_date"]) == str:
                        todo["due_date"] = date_parser.parse(todo["due_date"]).date()
                gather_todos = member["todos"]
                break

        # gather to-do tasks in projecta.yml
        for projectum in self.gtx["projecta"]:
            if projectum.get('lead') != rc.id:
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
                        })
                        ms.update({'description': f'{ms.get("id")}, {ms.get("name")}', 'mark': 'no mark'})

                        gather_todos.append(ms)

        mtgs = []
        for mtg in self.gtx["meetings"]:
            mtg['date'] = dt.date(mtg.get("year"), mtg.get("month"),
                                  mtg.get("day"))
            if len(list(mtg.get('actions'))) != 0:
                mtgs.append(mtg)
        if len(mtgs) > 0:
            mtgs = sorted(mtgs, key=lambda x: x.get('date'), reverse=True)
            actions = mtgs[0].get('actions')

            due_date = mtgs[0].get('date') + relativedelta(weekday=TH)
            for a in actions:
                ac = a.casefold()
                if "everyone" in ac or "all" in ac or rc.firstname.casefold() in ac:
                    gather_todos.append({
                        'description': a,
                        'due_date': due_date,
                        'mark': 'no mark',
                        'status': 'started'
                    })

        num = 0

        for item in gather_todos:
            if item.get('importance') is None:
                item['importance'] = 1

        gather_todos = sorted(gather_todos, key=lambda k: (k['due_date'], -k['importance']))

        if rc.verbose:
            for t in gather_todos:
                if t.get('status') not in ["finished", "cancelled"]:
                    print(
                        f"{num + 1}. {t.get('description')}")
                    print(f"     --({t.get('mark')}, due: {t.get('due_date')}, {t.get('duration')} min, importance:"
                          f"{t.get('importance')}, start date: {t.get('begin_date')})")
                    num += 1
        elif rc.duration:
            for t in gather_todos:
                if t.get('status') not in ["finished", "cancelled"]:
                    if t.get('duration') and float(t.get('duration')) <= float(rc.duration):
                        print(f"{num + 1}. {t.get('description')}")
                        num += 1
        else:
            for t in gather_todos:
                if t.get('status') not in ["finished", "cancelled"]:
                    print(f"{num + 1}. {t.get('description')}")
                    num += 1

        return
