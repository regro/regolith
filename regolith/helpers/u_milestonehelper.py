"""Helper for updating milestones to the projecta collection.
    It can update the status and due date of a projectum.
    It can add a new milestone to the projecta collection.
"""
import datetime as dt
from nameparser import HumanName
import dateutil.parser as date_parser
import sys
import uuid

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection


TARGET_COLL = "projecta"

def subparser(subpi):
    subpi.add_argument("projectum_id", help="the id of the projectum")
    subpi.add_argument("--number",
                        help="number of the milestone to update from numbered list")
    subpi.add_argument("--due_date",
                       help="new due date of the milestone"
                            "required to add a new milestone")
    subpi.add_argument("-s", "--status",
                       help="status of the milestone/deliverable:"
                            "proposed, started, finished, back_burner"
                            "paused, cancelled")
    subpi.add_argument("--name",
                       help="name of the new milestone."
                            "required to add a new milestone.")
    subpi.add_argument("-o", "--objective",
                       help="objective of the new milestone."
                            "required to add a new milestone")
    subpi.add_argument("-t", "--type",
                       help="type of the new milestone")
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
        milestones = current.get('milestones', {})
        deliverable = current.get('deliverable', {})
        kickoff = current.get('kickoff', {})
        lmil = {}
        nmil = len(milestones)
        for i in range(nmil):
            lmil[str(i + 4)] = milestones[i]
        #if list number was not informed, print a numbered list
        if not rc.number:
            print('Please choose from one of the following to update/add:')
            print('1. name: deliverable     due date:{}'.format(deliverable['due_date']))
            print('2. name: kick off    due date:{}'.format(kickoff['due_date']))
            print('3. name: new milestone')
            for key in lmil:
                current_mil = lmil[key]
                print("{}. name: {}      due date:{}".format(key, current_mil['name'], current_mil['due_date']))
            return

        lmil['1'] = deliverable
        lmil['2'] = kickoff
        pdoc = {}
        if rc.number == '1':
            if rc.due_date:
                deliverable.update({'due_date':rc.due_date})
            if rc.status:
                deliverable.update({'status': rc.status})
            pdoc.update({'deliverable':deliverable})
        if rc.number == '2':
            if rc.due_date:
                kickoff.update({'due_date':rc.due_date})
            if rc.status:
                kickoff.update({'status': rc.status})
            pdoc.update({'kickoff': kickoff})
        if int(rc.number) == 3:
            mil = {}
            if not rc.due_date or not rc.name or not rc.objective:
                print('Please inform name, objective, and due date to add a new milestone')
                return
            mil.update({'due_date': rc.due_date, 'objective': rc.objective, 'name': rc.name})
            mil.update({'audience': ['lead', 'pi', 'group_members']})
            if rc.status:
                mil.update({'status': rc.status})
            else:
                mil.update({'status': 'proposed'})
            if rc.type:
                mil.update({'type': rc.type})
            else:
                mil.update({'type': 'meeting'})
            milestones.append(mil)
        if int(rc.number) > 3:
            mil = lmil[rc.number]
            if rc.due_date:
                mil.update({'due_date':rc.due_date})
            if rc.status:
                mil.update({'status': rc.status})
            num = int(rc.number) - 4
            milestones[num] = mil

        rc.client.update_one(rc.database, rc.coll, filterid, pdoc)
        print("{} has been updated in projecta".format(rc.projectum_id))

        return
