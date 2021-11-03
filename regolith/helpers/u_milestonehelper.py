"""Helper for updating milestones to the projecta collection.
    It can update the status, type, and due date of a projectum.
    It can add a new milestone to the projecta collection.
"""
from copy import deepcopy
from itertools import chain
import datetime as dt
import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection, fragment_retrieval
from regolith.dates import get_due_date
from regolith.schemas import PROJECTUM_ACTIVE_STATI, \
    MILESTONE_TYPES, PROJECTUM_STATI


TARGET_COLL = "projecta"
MILESTONE_TYPES = MILESTONE_TYPES
PROJECTUM_STATI = PROJECTUM_STATI


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs['widget'] = 'DateChooser'

    subpi.add_argument("projectum_id", help="The id of the projectum.  If you just "
                                            "specify this the program will return a "
                                            "numbered list of milestones to select for "
                                            "updating. #1 in the list is always used "
                                            "to add a new milestone.")
    subpi.add_argument("-c", "--current", action="store_true",
                       help="only list current (unfinished, unpaused) milestones",
                       )
    subpi.add_argument("-i", "--index",
                       help="Index of the item in the enumerated list to update. "
                            "To update multiple milestones with the same edits "
                            "(often used for finishing checklist items), "
                            "please enter in the "
                            "format of 2,5,7 or 3-7 for multiple indices.",
                       type=str)
    subpi.add_argument("-v", "--verbose", action="store_true",
                       help="Increases the verbosity of the output.")
    subpi.add_argument("-u", "--due_date",
                       help="New due date of the milestone. "
                            "Required for a new milestone.",
                       **date_kwargs)
    subpi.add_argument("-n", "--name",
                       help="Name of the milestone. "
                            "Required for a new milestone.")
    subpi.add_argument("-o", "--objective",
                       help="Objective of the milestone. "
                            "Required for a new milestone.")
    subpi.add_argument("-s", "--status",
                       help="Status of the milestone/deliverable: "
                            f"{*PROJECTUM_STATI,}. "
                            "Defaults to proposed for a new milestone.")
    subpi.add_argument("-t", "--type",
                       help="Type of the milestone: "
                            f"{*MILESTONE_TYPES,} "
                            "Defaults to meeting for a new milestone.")
    subpi.add_argument("-a", "--audience",
                       nargs='+',
                       help="Audience of the milestone. "
                            "Defaults to ['lead', 'pi', 'group_members'] for a new milestone.",
                       )
    subpi.add_argument("--notes",
                       nargs='+',
                       help="Any notes you want to add to the milestone."
                       )
    subpi.add_argument("-f", "--finish", action="store_true",
                       help="Finish milestone. "
                       )
    # Do not delete --database arg
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file.")
    subpi.add_argument("--date",
                       help="The date that will be used for testing.",
                       **date_kwargs
                       )
    return subpi


class MilestoneUpdaterHelper(DbHelperBase):
    """Helper for updating milestones to the projecta collection.
    """
    # btype must be the same as helper target in helper.py
    btype = "u_milestone"
    needed_colls = [f'{TARGET_COLL}']

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
        if rc.date:
            now = date_parser.parse(rc.date).date()
        else:
            now = dt.date.today()
        filterid = {'_id': key}
        target_prum = rc.client.find_one(rc.database, rc.coll, filterid)
        if not target_prum:
            pra = fragment_retrieval(self.gtx["projecta"], ["_id"],
                                     rc.projectum_id)
            if len(pra) == 0:
                raise RuntimeError(
                    "Please input a valid projectum id or a valid fragment of a projectum id")
            print("Projecta not found. Projecta with similar names: ")
            for i in range(len(pra)):
                print(f"{pra[i].get('_id')}")
            print("Please rerun the helper specifying the complete ID.")
            return
        milestones = deepcopy(target_prum.get('milestones'))
        deliverable = deepcopy(target_prum.get('deliverable'))
        kickoff = deepcopy(target_prum.get('kickoff'))
        deliverable['identifier'] = 'deliverable'
        kickoff['identifier'] = 'kickoff'
        for item in milestones:
            item['identifier'] = 'milestones'
        all_milestones = [deliverable, kickoff]
        all_milestones.extend(milestones)
        for i in all_milestones:
            i['due_date'] = get_due_date(i)
        all_milestones.sort(key=lambda x: x['due_date'], reverse=False)
        index_list = list(range(2, (len(all_milestones) + 2)))
        if not rc.index:
            deliverable['name'] = 'deliverable'
            print("Please choose from one of the following to update/add:")
            print("1. new milestone")
            for i, j in zip(index_list, all_milestones):
                if rc.current:
                    if j.get("status") not in PROJECTUM_ACTIVE_STATI:
                        continue
                print(
                    f"{i}. {j.get('name')}    due date: {j.get('due_date')}"
                    f"    status: {j.get('status')}")
                if rc.verbose:
                    if j.get("audience"):
                        print(f"     audience: {j.get('audience')}")
                    if j.get("objective"):
                        print(f"     objective: {j.get('objective')}")
                    if j.get("type"):
                        print(f"     type: {j.get('type')}")
                    if j.get('notes'):
                        print(f"     notes:")
                        for note in j.get('notes', []):
                            print(f"       - {note}")
                if j.get('identifier') == 'deliverable':
                    del j['name']
            return
        rc.index = rc.index.replace(" ", "")
        if "-" in rc.index:
            idx_parsed = [i for i in range(int(rc.index.split('-')[0]),
                                           int(rc.index.split('-')[1]) + 1)]
        elif "," in rc.index:
            idx_parsed = [int(i) for i in rc.index.split(',')]
        else:
            idx_parsed = [int(rc.index)]
        new_mil = []
        for idx in idx_parsed:
            pdoc = {}
            if idx == 1:
                mil = {}
                if not rc.due_date or not rc.name or not rc.objective:
                    raise RuntimeError(
                        "name, objective, and due date are required for a new milestone")
                mil.update({'due_date': rc.due_date})
                mil['due_date'] = get_due_date(mil)
                mil.update({'objective': rc.objective, 'name': rc.name})
                if rc.audience:
                    mil.update({'audience': rc.audience})
                else:
                    mil.update({'audience': ['lead', 'pi', 'group_members']})
                if rc.type:
                    mil.update({'type': rc.type})
                else:
                    mil.update({'type': 'meeting'})
                if rc.status:
                    mil.update({'status': rc.status})
                else:
                    mil.update({'status': 'proposed'})
                if rc.notes:
                    mil.update({'notes': rc.notes})
                mil.update({'identifier': "milestones"})
                new_mil.append(mil)
                pdoc = {'milestones': mil}
            if idx > 1:
                doc = deepcopy(all_milestones[idx - 2])
                identifier = doc['identifier']
                if not doc.get(
                        'type') and not rc.type and identifier == 'milestones':
                    raise RuntimeError(
                        "ERROR: This milestone does not have a type set and this is required. "
                        "Please rerun your command adding '--type' "
                        f"and typing a type from this list: {MILESTONE_TYPES}")
                if rc.type:
                    if rc.type in MILESTONE_TYPES:
                        doc.update({'type': rc.type})
                    else:
                        raise ValueError(
                            "ERROR: The type you have specified is not recognized. "
                            "Please rerun your command adding '--type' "
                            f"and giving a type from this list: {MILESTONE_TYPES}")
                if rc.finish:
                    rc.status = "finished"
                    doc.update({'end_date': now})
                    if identifier == 'deliverable':
                        name = 'deliverable'
                    else:
                        name = doc['name']
                    print(
                        "The milestone {} has been marked as finished in prum {}".format(
                            name, key))
                if rc.status:
                    doc.update({'status': rc.status})
                if rc.audience:
                    doc.update({'audience': rc.audience})
                if rc.due_date:
                    doc.update({'due_date': rc.due_date})
                doc['due_date'] = get_due_date(doc)
                if rc.objective:
                    doc.update({'objective': rc.objective})
                if rc.notes:
                    notes = doc.get("notes", [])
                    notes.extend(rc.notes)
                    doc["notes"] = notes
                if identifier == 'milestones':
                    if rc.name:
                        doc.update({'name': rc.name})
                    new_mil.append(doc)
                else:
                    del doc['identifier']
                    pdoc.update({identifier: doc})
        new_all = deepcopy(all_milestones)
        for i, j in zip(index_list, new_all):
            if j['identifier'] == 'milestones' and i not in idx_parsed:
                new_mil.append(j)
        for mile in new_mil:
            del mile['identifier']
        new_mil.sort(key=lambda x: x['due_date'], reverse=False)
        pdoc.update({'milestones': new_mil})
        rc.client.update_one(rc.database, rc.coll, filterid, pdoc)
        print("{} has been updated in projecta".format(key))

        return
