"""Helper for adding actions from the latest group meeting to todos in people.yml

"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import *

import re
import sys
from regolith.dates import get_dates
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
    subpi.add_argument("-d", "--date",
                       help="Enter a date in format YYYY-MM-DD to add actions from the meeting held on that specifc "
                            "date. By default the helper will add tasks from the latest group meeting. ",
                       )

    return subpi


class MeetingActionsAdderHelper(DbHelperBase):
    """Helper for adding a to_do task to people.yml
    """
    # btype must be the same as helper target in helper.py
    btype = "g_todo"
    needed_dbs = [f'{TARGET_COLL}', "meetings"]

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
            rc.pi_id = get_pi_id(rc)

        rc.coll = f"{TARGET_COLL}"
        rc.database = rc.databases[0]["name"]
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





    def db_updater(self):
        rc = self.rc
        if rc.date:
            date = date_parser.parse(rc.date)
            filter_date = {'day': date.day, 'month': date.month, 'year': date.year}
            mtg = rc.client.find_one(rc.database, "meetings", filter_date)
            mtg['date']=get_dates(mtg)["date"]
            if not mtg:
                raise TypeError(f"No meeting is held on {rc.date}")
        else:
            mtgs = []
            for mtg in self.gtx["meetings"]:
                mtg['date']=get_dates(mtg)["date"]
                if len(list(mtg.get('actions'))) != 0:
                    mtgs.append(mtg)
            if len(mtgs) > 0:
                mtgs = sorted(mtgs, key=lambda x: x.get('date'), reverse=True)
                mtg = mtgs[0]

        insert_todos={}
        for person in self.gtx["people"]:
            insert_todos[person["_id"]] = person.get("todos", [])

        actions = mtg.get('actions')
        due_date = mtg.get('date') + relativedelta(weekday=TH)
        for action in actions:
            todo = {
                'description': action,
                'begin_date': mtg.get('date'),
                'due_date': due_date,
                'importance': 1,
                'status': 'started'
            }
            for person in self.gtx["people"]:
                if person["active"]:
                    id = person["_id"]
                    if "(everyone)" in action.casefold():
                        insert_todos[id].append(todo)
                        continue
                    else:
                        first_name = person["name"].split()[0].casefold()
                        if first_name in action.casefold():
                            insert_todos[id].append(todo)
                            break

        for person in self.gtx["people"]:
            if person["active"]:
                id = person["_id"]
                rc.client.update_one(rc.database, rc.coll, {'_id': person["_id"]}, {"todos": insert_todos[id]},
                                             upsert=True)
        print(f"Actions from group meeting({mtg.get('date')}) have been added to todos in people collection.")

        return
