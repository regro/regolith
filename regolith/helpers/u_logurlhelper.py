"""Helper for updating a project's log_url

   Log_urls are the google doc links to a project's Projectum Agenda Log
"""
from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
)

TARGET_COLL = "projecta"
ALLOWED_TYPES = ["nsf", "doe", "other"]
ALLOWED_STATI = ["proposed", "started", "finished", "back_burner", "paused",
                 "cancelled"]


def subparser(subpi):
    subpi.add_argument("name", help="Projecta name to apply updates",
                       default=None)
    subpi.add_argument("log_url", help="Google Doc url link to project's Projectum Agenda Log")
    # Do not delete --database arg
    subpi.add_argument("-d", "--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file."
                       )
    return subpi


class LogUrlUpdaterHelper(DbHelperBase):
    """
    Update a project's Log_url, will add a new Log_URL if one doesn't yet exist
    """
    # btype must be the same as helper target in helper.py
    btype = "u_logurl"
    needed_dbs = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
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
        key = f"{rc.name}"
        filterid = {'_id' : key}
        current = rc.client.find_one(rc.database, rc.coll, filterid)

        if current is None:
            raise RuntimeError(
                "There does not seem to be a projecta with this name in this database"
            )
        else:
            rc.client.update_one(rc.database, rc.coll, filterid, {'log_url': rc.log_url})

        print(rc.name + " has been updated with a log_url of " + rc.log_url)
        return
