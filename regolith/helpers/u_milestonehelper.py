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
from regolith.dates import get_due_date

TARGET_COLL = "projecta"
ALLOWED_TYPES = {"m":"meeting", "r":"release", "p":"pull request", "o":"other"}
ALLOWED_STATUS = {"p":"proposed", "s":"started", "f":"finished", "b":"back_burner","c":"converged"}

def subparser(subpi):
    subpi.add_argument("projectum_id", help="the id of the projectum")
    subpi.add_argument("-v", "--verbose", action="store_true",
                        help="gives a list of the milestones available to update.")
    subpi.add_argument("--index",
                        help="index of the item in the enumerated list to update",
                        type = int)
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
        filterid = {'_id': key}
        target_prum = rc.client.find_one(rc.database, rc.coll, filterid)
        if not target_prum:
            raise RuntimeError(f"Cannot find {key} in the projecta collection")
        milestones = target_prum.get('milestones')
        deliverable = target_prum.get('deliverable')
        kickoff = target_prum.get('kickoff')
        deliverable['identifier'] = 'deliverable'
        kickoff['identifier'] = 'kickoff'
        for item in milestones:
            item['identifier'] = 'milestones'
        all_milestones = [deliverable, kickoff]
        all_milestones.extend(milestones)
        for i in all_milestones:
            i['due_date'] = get_due_date(i)
        all_milestones.sort(key = lambda x: x['due_date'], reverse=False)
        index_list = list(range(2, (len(all_milestones)+2)))
        if rc.verbose:
            print("Please choose from one of the following to update/add:")
            print("1. new milestone")
            for i, j in zip(index_list, all_milestones):
                if j['identifier'] == 'milestones':
                    print(f"{i}. {j.get('name')}    due date: {j.get('due_date')}:\n"
                          f"     audience: {j.get('audience')}\n"
                          f"     objetive: {j.get('objective')}\n"
                          f"     status: {j.get('status')}\n"
                          f"     type: {j.get('type')}")
                else:
                    print(f"{i}. {j.get('identifier')}    due date: {j.get('due_date')}:\n"
                          f"     audience: {j.get('audience')}\n"
                          f"     status: {j.get('status')}")
                del j['identifier']
            return
        pdoc = {}
        if rc.index == 1:
            mil = {}
            if not rc.due_date or not rc.name or not rc.objective:
                raise RuntimeError("name, objective, and due date are required for a new milestone")
            mil.update({'due_date': rc.due_date})
            mil['due_date'] = get_due_date(mil)
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
        if rc.index > 1:
            doc = all_milestones[rc.index-2]
            identifier = doc['identifier']
            if rc.due_date:
                doc.update({'due_date': rc.due_date})
            if rc.status:
                doc.update({'status': ALLOWED_STATUS[rc.status]})
            if rc.type:
                doc.update({'type': ALLOWED_TYPES[rc.type]})
            doc['due_date'] = get_due_date(doc)
            if identifier == 'milestones':
                new_mil = []
                for i, j in zip(index_list, all_milestones):
                    if j['identifier'] == 'milestones' and i != rc.index:
                        new_mil.append(j)
                new_mil.append(doc)
                pdoc.update({'milestones':new_mil})
            else:
                pdoc.update({identifier:doc})
        for i in all_milestones:
            del i['identifier']
        rc.client.update_one(rc.database, rc.coll, filterid, pdoc)
        print("{} has been updated in projecta".format(key))

        return
