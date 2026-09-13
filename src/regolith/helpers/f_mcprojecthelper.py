"""Finish a project in mission control, and everything under it.

Finishing a project by hand means striking through its goals in the
document, and the tasks under those, and then the project.  This does
all of it at once, the way f_prum does for a projectum: the project is
finished, and every goal of it and task of those goals that was still
open is finished with it.

There is no finisher for a goal or a task on their own.  Those are
struck through in the document, which is where somebody is looking when
they finish one.
"""

import datetime as dt

from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection, fragment_retrieval, strip_str

TARGET_COLL = "mc_projects"
HELPER_TARGET = "f-mcproject"
COLLECTIONS = (TARGET_COLL, "mc_goals", "mc_tasks")
# what is over already, and is not finished again
CLOSED = ("finished", "dropped")


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument(
        "project_id",
        type=strip_str,
        help="The id of the project to finish, or enough of it to name one.",
    )
    subpi.add_argument(
        "--end-date",
        type=strip_str,
        help="The day it finished.  Default is today.",
        **date_kwargs,
    )
    subpi.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Say what would be finished without finishing it.",
    )
    return subpi


class MCProjectFinisherHelper(DbHelperBase):
    """Finish a project in mission control, and everything under it."""

    btype = HELPER_TARGET
    needed_colls = list(COLLECTIONS)

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        rc = self.rc
        rc.coll = TARGET_COLL
        for collection in COLLECTIONS:
            self.gtx[collection] = list(all_docs_from_collection(rc.client, collection))

    def db_updater(self):
        rc = self.rc
        project = self.the_project(rc.project_id)
        if project is None:
            return
        end_date = date_parser.parse(rc.end_date).date() if rc.end_date else dt.date.today()

        goals = [g for g in self.gtx["mc_goals"] if g.get("project") == project["_id"]]
        of_those = {g["_id"] for g in goals}
        tasks = [t for t in self.gtx["mc_tasks"] if t.get("goal") in of_those]
        finishing = [(TARGET_COLL, project)] + [("mc_goals", g) for g in goals] + [("mc_tasks", t) for t in tasks]
        # what is dropped stays dropped, and what was finished keeps the day it
        # was finished on rather than being moved to today
        open_now = [(coll, record) for coll, record in finishing if record.get("status") not in CLOSED]

        for collection, record in open_now:
            record["status"] = "finished"
            record.setdefault("end_date", end_date)
        if rc.dry_run:
            self.report(project, open_now, finishing, wrote=False)
            return
        for collection, record in open_now:
            rc.client.update_one(
                self.where_it_lives(collection, record["_id"]), collection, {"_id": record["_id"]}, record
            )
        self.report(project, open_now, finishing, wrote=True)
        return

    def the_project(self, _id):
        """Return the project an id names, saying so when it names none.

        Parameters
        ----------
        _id : str
            The id, or enough of it to name one project.

        Returns
        -------
        dict or None
            The project, or None when the id named none or several.
        """
        projects = {p["_id"]: p for p in self.gtx[TARGET_COLL]}
        if _id in projects:
            return projects[_id]
        near = fragment_retrieval(self.gtx[TARGET_COLL], ["_id"], _id)
        if not near:
            raise ValueError(
                f"There is no project called {_id}. Please check the id, which "
                f"'regolith helper l-mcprojects' will list."
            )
        if len(near) == 1:
            return near[0]
        print(f"{_id} names more than one project:")
        for project in near:
            print(f"    {project['_id']}  ({project.get('status', '?')})  {project.get('name', '')}")
        print("Please run this again with the whole id of the one you mean.")
        return None

    def where_it_lives(self, collection, _id):
        """Return the database holding a record.

        A record is written where it is stored rather than in the first
        database that happens to be listed, since writing it anywhere
        else would leave two of it and hide the one that is real.

        Parameters
        ----------
        collection : str
            The name of the collection.
        _id : str
            The id of the record.

        Returns
        -------
        str
            The name of the database to write to.
        """
        rc = self.rc
        sources = rc.client.collection_sources(collection)
        for database in sources:
            if rc.client.find_one(database["name"], collection, {"_id": _id}):
                return database["name"]
        return sources[0]["name"] if sources else rc.database

    @staticmethod
    def report(project, finished, all_of_it, wrote):
        """Say what was finished, and what was over already."""
        did = "finished" if wrote else "would finish"
        goals = sum(1 for collection, _ in finished if collection == "mc_goals")
        tasks = sum(1 for collection, _ in finished if collection == "mc_tasks")
        already = len(all_of_it) - len(finished)
        print(f"{did} {project['_id']}, with {goals} goal(s) and {tasks} task(s) under it.")
        if already:
            print(f"    {already} more were finished or dropped already, and were left as they were.")
