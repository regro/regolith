"""Helper for updating a projectum's log_url
   Log_urls are the google doc links to a projectum's Projectum Agenda Log
"""
from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection, fragment_retrieval

TARGET_COLL = "projecta"


def subparser(subpi):
    subpi.add_argument("projectum_id", help="the ID or fragment of the ID of the Projectum to be updated, e.g., 20vl",
                       default=None)
    subpi.add_argument("log_url", help="Google Doc url link to project's Projectum Agenda Log")
    subpi.add_argument("-n", "--number", help="The id you would like to choose from the listed projectum ids")
    # Do not delete --database arg
    subpi.add_argument("-d", "--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file."
                       )
    return subpi


class LogUrlUpdaterHelper(DbHelperBase):
    """
    Update a projectum's Log_url, will add a new Log_URL if one doesn't yet exist
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
        key = rc.projectum_id
        filterid = {'_id': key}
        found_projectum = rc.client.find_one(rc.database, rc.coll, filterid)

        # id exists
        if found_projectum is not None:
            rc.client.update_one(rc.database, rc.coll, filterid, {'log_url': rc.log_url})
            print(f"{rc.projectum_id} has been updated with a log_url of {rc.log_url}")
        else:
            # find all similar projectum ids
            pra = fragment_retrieval(self.gtx["projecta"], ["_id"], rc.projectum_id)

            # no matches to id fragment and id does not exist
            if len(pra) == 0:
                raise RuntimeError("Please input a valid projectum id or a valid fragment of a projectum id")

            # id fragment and no inputted number
            elif not rc.number:
                print("There does not seem to be a projectum with this exact name in this database.")
                print("However, there are projecta with similar names: ")
                for i in range(len(pra)):
                    print(f"{i + 1}. {pra[i].get('_id')}     current url: {pra[i].get('log_url')}")
                print("Please rerun the u_logurl helper with the same name as previously inputted, "
                      "but with the addition of -n followed by a number corresponding to one of the above listed "
                      "projectum ids that you would like to update.")

            # id fragment and inputted number
            else:
                if int(rc.number) < 1 or int(rc.number) > len(pra):
                    raise RuntimeError("Sorry, you picked an invalid number.")
                else:
                    filterid = {'_id': pra[int(rc.number) - 1].get('_id')}
                    rc.client.update_one(rc.database, rc.coll, filterid, {'log_url': rc.log_url})
                    print(f"{pra[int(rc.number) - 1].get('_id')} has been updated with a log_url of {rc.log_url}")

        return
