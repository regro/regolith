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
    subpi.add_argument("institution_id",
                       help="id of the institution. e.g.:columbiau")
    subpi.add_argument("-n","--name",
                        help="Full name of the institution")
    subpi.add_argument("-i","--index",
                       help="index of the item in the enumerated list chosen to update",
                       type=int)
    subpi.add_argument("--city",
                       help="The city where the institution is. "
                            "Required for a new institution.")
    subpi.add_argument("--country",
                       help="The country where the institution is. "
                            "Required for a new institution")
    subpi.add_argument("-a", "--aka",
                       nargs='+',
                       help="List of all the different names this "
                            "institution is known by.")
    subpi.add_argument("--state",
                       help="The state where the institution is.")
    subpi.add_argument("--zip",
                       help="zipcode of the institution")
    subpi.add_argument("--dept_id",
                       help="Department identificator. e.g.: physics")
    subpi.add_argument("--dept_name",
                       help="Department canonical name. e.g.: Department of Physics. "
                            "Defaults to Department id.")
    subpi.add_argument("--dept_aka",
                       nargs='+',
                       help="Department aliases. e.g.: dept. of physics")
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
        pdoc = {}
        if target_inst:
            if rc.aka:
                current_aka = target_inst.get('aka')
                current_aka.extend(rc.aka)
                pdoc.update({'aka': current_aka})
            pdoc.update({'departments': target_inst.get('departments', {})})
        else:
            inst = fragment_retrieval(self.gtx["institutions"], ["_id"], rc.institution_id)
            inst.sort(key=lambda x: x['_id'], reverse=False)
            if not rc.index:
                print("Please rerun the helper specifying '-n list-index' to update item number 'list-index':")
                print(f"1. {key} as a new institution.")
                for i in range(len(inst)):
                    print(f"{i+2}. {inst[i].get('_id')}      {inst[i].get('name')}.")
                return
            if rc.index < 1 or rc.index > len(inst)+1:
                raise RuntimeError("Sorry, you picked an invalid number.")
            if rc.index == 1:
                if not rc.name or not rc.city or not rc.country:
                    raise RuntimeError("Name, city, and country are required for a new milestone")
                pdoc.update({'name': rc.name, 'uuid': str(uuid.uuid4())})
                if rc.aka:
                    pdoc.update({'aka':rc.aka})
                if rc.date:
                    pdoc.update({'date': rc.date})
                else:
                    pdoc.update({'date': now.date()})
            else:
                chosen_inst = inst[rc.index+2]
                key = chosen_inst.get('_id')
                if rc.aka:
                    current_aka = chosen_inst.get('aka')
                    current_aka.extend(rc.aka)
                    pdoc.update({'aka': current_aka})
                pdoc.update({'departments': chosen_inst.get('departments', {})})
        if rc.city:
            pdoc.update({'city': rc.city})
        if rc.state:
            pdoc.update({'state': rc.state})
        if rc.country:
            pdoc.update({'country': rc.country})
        if rc.zip:
            pdoc.update({'zip': rc.zip})
        if rc.date:
            pdoc.update({'updated': rc.date})
        else:
            pdoc.update({'updated': now})
        # departments:
        if rc.dept_id:
            dep = {'name': f'Department of {rc.dept_id.capitalize()}'}
            if rc.dept_name:
                dep.update({'name': rc.dept_name})
            current_dep = pdoc.get('departments', {})
            if rc.dept_id not in current_dep:
                if rc.dept_aka:
                    dep.update({'aka': rc.dept_aka})
                current_dep[rc.dept_id] = dep
                pdoc.update({'departments': current_dep})
            else:
                doc = current_dep.get(rc.dept_id)
                if rc.dept_name:
                    doc.update({'name':rc.dept_name})
                current_dept_aka = doc.get('aka')
                if rc.dept_aka:
                    current_dept_aka.extend(rc.dept_aka)
                    doc.update({'aka': current_dept_aka})
                current_dep.update({rc.dept_id: doc})
        rc.client.update_one(rc.database, rc.coll, {'_id': key}, pdoc)
        print(f"{key} has been updated/added in institutions")
        return
