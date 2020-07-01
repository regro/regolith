"""
Helper for updating/adding  to the projecta collection.
"""
from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection, fragment_retrieval
from itertools import chain
import uuid
import datetime as dt

TARGET_COLL = "institutions"

def subparser(subpi):
    subpi.add_argument("institution_id", help="id of the institution. e.g.:columbiau")
    subpi.add_argument("--name",
                        help="Full name of the institution")
    subpi.add_argument("--city",
                       help="The city where the institution is. "
                            "Required for a new institution.")
    subpi.add_argument("--country",
                       help="The country where the institution is. "
                            "Required for a new institution")
    subpi.add_argument("--new", action="store_true",
                       help="New institution")
    subpi.add_argument("--aka",
                       nargs='+',
                       help="List of all the different names this "
                            "institution is known by.")
    # Do not delete --database arg
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file.")
    # Do not delete --date arg
    subpi.add_argument("--date",
                       help="The date when the institution was created in ISO format. "
                            "Defaults to today's date."
                       )
    return subpi

class InstitutionsUpdaterHelper(DbHelperBase):
    """
    Helper for updating/adding  to the projecta collection.
    """
    # btype must be the same as helper target in helper.py
    btype = "u_institutions"
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
        key = rc.institution_id
        filterid = {'_id': key}
        target_inst = rc.client.find_one(rc.database, rc.coll, filterid)
        now = dt.datetime.today()
        #new institution
        if rc.new:
            if target_inst:
                raise RuntimeError("This institution seems to already exist in the collection.")
            pdoc = {'name': rc.name, 'city': rc.city, 'country': rc.country, 'uuid': str(uuid.uuid4())}
            if rc.aka:
                pdoc.update({'aka':rc.aka})
            if rc.date:
                pdoc.update({'date': rc.date, 'updated':rc.date})
            else:
                pdoc.update({'date': now.date(), 'updated': now})
            rc.client.update_one(rc.database, rc.coll, {'_id': key}, pdoc)
            print(f"{key} has been added in institutions")
            return
        #not found institution
        if not target_inst:
            inst = fragment_retrieval(self.gtx["institutions"], ["_id"], rc.institution_id)
            if len(inst) == 0:
                raise RuntimeError("Please input a valid institution id."
                                   "If it is a new institution use '--new'")
            print("Institution not found. Institutions with similar id:")
            print(*(inst[i].get('_id') for i in range(len(inst))),sep='\n')
            print("Please rerun the helper specifying the complete ID. If it is a new institution use '--new'")
            return
        #updates to a existing institution
        pdoc = {}
        if rc.aka:
            current_aka = target_inst.get('aka')
            current_aka.extend(rc.aka)
            pdoc.update({'aka':current_aka})
        if rc.city:
            pdoc.update({'city': rc.city})
        if rc.country:
            pdoc.update({'country': rc.country})
        if rc.date:
            pdoc.update({'updated': rc.date})
        else:
            pdoc.update({'updated': now})
        rc.client.update_one(rc.database, rc.coll, {'_id': key}, pdoc)
        print(f"{key} has been updated in institutions")
        return
