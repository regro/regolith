"""Helper for setting a task as finished by entering the mark of a certain task. The mark can be found by regolith helper l_todo -v.
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
)

TARGET_COLL = "todolist"
Importance = [0, 1, 2, 3, 4, 5]


def subparser(subpi):
    subpi.add_argument("mark",
                       help="the mark of the to_do task you want to set as finished, can be found by regolith helper l_todo -v ",
                       default=None)
    subpi.add_argument("-i", "--id", help="ID of the to_do list's owner. The default id is saved in user.json. ")
    subpi.add_argument("-e", "--end_date", help="End date of the task. Default is today. ")

    return subpi


class TodoFinisherHelper(DbHelperBase):
    """Helper for adding a projectum to the projecta collection.

       Projecta are small bite-sized project quanta that typically will result in
       one manuscript.
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
        if not rc.id:
            try:
                rc.id = rc.default_user_id
            except AttributeError:
                raise RuntimeError(
                    "Please set default_user_id in '~/.config/regolith/user.json',\
                     or you need to input your id in the command line")

        key = f"{rc.id}"
        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) == 0:
            print(f"{rc.id} doesn't have to-do list.")
        else:
            now = dt.date.today()
            if not rc.end_date:
                end_date = now
            else:
                end_date = date_parser.parse(rc.end_date).date()
            for member in coll:
                if key == member["_id"]:
                    todo_update = []
                    for todo_item in member["todos"]:
                        if todo_item['mark'] == int(rc.mark):
                            todo_item['status'] = "finished"
                            todo_item['end_date'] = end_date
                            task_name = todo_item['description']
                        todo_update.append(todo_item)
                    rc.client.update_one(rc.database, rc.coll, {'id': rc.id}, {"todos": todo_update},
                                         upsert=True)
                    print(f"The task ({task_name}) is set as finished.")
                    break

        return