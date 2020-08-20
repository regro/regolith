"""Helper for finishing prum in the projecta collection
"""
from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection, fragment_retrieval, collection_str
import datetime as dt
from dateutil import parser as date_parser

TARGET_COLL = "projecta"

def subparser(subpi):
    subpi.add_argument("projectum_id",
                       help="the ID or fragment of the ID of the projectum to be updated, e.g., 20sb")
    subpi.add_argument("--end_date",
                       help="End date of the projectum in ISO format (YYYY-MM-DD). "
                            "Defaults to today.")
    # Do not delete --database arg
    subpi.add_argument("-d", "--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file.")
    return subpi


class FinishprumUpdaterHelper(DbHelperBase):
    """
    Helper for finishing prum in the projecta collection
    """
    # btype must be the same as helper target in helper.py
    btype = "f_prum"
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
        if not found_projectum:
            pra = fragment_retrieval(self.gtx["projecta"], ["_id"], key)
            if len(pra) == 0:
                raise RuntimeError("Please input a valid projectum id or a valid fragment of a projectum id")
            print("Projectum not found. Projecta with similar names: ")
            for i in range(len(pra)):
                print(f"{pra[i].get('_id')}     status:{pra[i].get('status')}")
            print("Please rerun the helper specifying the complete ID.")
            return
        found_projectum.update({'status':'finished'})
        if rc.end_date:
            found_projectum.update({'end_date': date_parser.parse(rc.end_date).date()})
        else:
            found_projectum.update({'end_date': dt.date.today()})
        found_projectum['kickoff'].update({'status':'finished'})
        found_projectum['deliverable'].update({'status': 'finished'})
        for i in found_projectum:
            if i=='milestones':
                for field in found_projectum['milestones']:
                    field.update({'status': 'finished'})
        rc.client.update_one(rc.database, rc.coll, filterid, found_projectum)
        print(f"{rc.projectum_id} status has been updated to finished")
        return
