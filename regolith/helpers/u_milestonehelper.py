"""Helper for updating milestones to the projecta collection.
    It can update the status and due date of a projectum.
    It can add a new milestone to the projecta collection.
"""
import datetime as dt
import sys
from dateutil import parser
from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection


TARGET_COLL = "projecta"
ALLOWED_TYPES = {"m":"meeting", "r":"release", "p":"pull request", "o":"other"}
ALLOWED_STATUS = {"p":"proposed", "s":"started", "f":"finished", "b":"back_burner","c":"converged"}

def subparser(subpi):
    subpi.add_argument("projectum_id", help="the id of the projectum")
    subpi.add_argument("--number",
                        help="number of the milestone to update from numbered list")
    subpi.add_argument("--due_date",
                       help="new due date of the milestone in ISO format (YYYY-MM-DD) "
                            "required to add a new milestone")
    subpi.add_argument("--name",
                       help="name of the new milestone. "
                            "required to add a new milestone")
    subpi.add_argument("-o", "--objective",
                       help="objective of the new milestone. "
                            "required to add a new milestone")
    subpi.add_argument("-s", "--status",
                       help="initial of the status of the milestone/deliverable: "
                            f"{ALLOWED_STATUS}")
    subpi.add_argument("-t", "--type",
                       help="initial of type of the new milestone "
                            f"{ALLOWED_TYPES}")
    # Do not delete --database arg
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file.")
    return subpi

class MilestoneUpdaterHelper(DbHelperBase):
    """Helper for updating milestones to the projecta collection.
    """
    # btype must be the same as helper target in helper.py
    btype = "u_milestone"
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
        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) == 0:
            raise RuntimeError(
                "This entry appears to not exist in the collection")
        filterid = {'_id': key}
        current = rc.client.find_one(rc.database, rc.coll, filterid)
        milestones = current.get('milestones')
        deliverable = current.get('deliverable')
        kickoff = current.get('kickoff')
        deliverable['identifier'] = 'deliverable'
        kickoff['identifier'] = 'kickoff'
        for item in milestones:
            item['identifier'] = 'milestones'
        all_milestones = [deliverable, kickoff]
        all_milestones.extend(milestones)
        for i in all_milestones:
            if isinstance(i['due_date'], str):
                i['due_date'] = dt.date.fromisoformat(i['due_date'])
        all_milestones.sort(key=lambda x: x['due_date'], reverse=False)
        index = 2
        numbered_milestones = {}
        for item in all_milestones:
            numbered_milestones[str(index)] = item
            index += 1
        if not rc.number:
            print("Please choose from one of the following to update/add:")
            print("1. new milestone")
            for i in numbered_milestones:
                current_mil = numbered_milestones[i]
                if 'name' in current_mil:
                    print("{}. {}    due date: {}    {}".format(i, current_mil["name"],
                                                    current_mil["due_date"], current_mil["status"]))
                else:
                    print("{}. {}    due date: {}    {}".format(i, current_mil['identifier'],
                                                                current_mil["due_date"], current_mil["status"]))
                del current_mil['identifier']
            return
        pdoc = {}
        if int(rc.number) == 1:
            mil = {}
            if not rc.due_date or not rc.name or not rc.objective:
                for i in numbered_milestones:
                    current_mil = numbered_milestones[i]
                    del current_mil['identifier']
                raise RuntimeError("name, objective, and due date are required for a new milestone")
            if isinstance(rc.due_date, str):
                mil.update({'due_date': dt.date.fromisoformat(rc.due_date)})
            else:
                mil.update({'due_date': rc.due_date})
            mil.update({'objective': rc.objective, 'name': rc.name})
            mil.update({'audience': ['lead', 'pi', 'group_members']})
            if rc.status:
                mil.update({'status': ALLOWED_STATUS[rc.status]})
            else:
                mil.update({'status': 'proposed'})
            if rc.type:
                mil.update({'type': ALLOWED_TYPES[rc.type]})
            else:
                mil.update({'type': 'meeting'})
            milestones.append(mil)
            pdoc = {'milestones':milestones}
        if int(rc.number) > 1:
            doc = numbered_milestones[rc.number]
            identifier = doc['identifier']
            if rc.due_date:
                if isinstance(rc.due_date, str):
                    doc.update({'due_date': dt.date.fromisoformat(rc.due_date)})
                else:
                    doc.update({'due_date': rc.due_date})
            if rc.status:
                doc.update({'status': ALLOWED_STATUS[rc.status]})
            if identifier == 'milestones':
                new_mil = []
                for i in numbered_milestones:
                    if numbered_milestones[i]['identifier'] =='milestones' and i!= rc.number:
                        new_mil.append(numbered_milestones[i])
                new_mil.append(doc)
                pdoc.update({'milestones':new_mil})
            else:
                pdoc.update({identifier:doc})
        for i in numbered_milestones:
            current_mil = numbered_milestones[i]
            del current_mil['identifier']

        rc.client.update_one(rc.database, rc.coll, filterid, pdoc)
        print("{} has been updated in projecta".format(key))

        return
