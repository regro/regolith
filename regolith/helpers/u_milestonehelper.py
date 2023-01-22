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
from regolith.tools import all_docs_from_collection, fragment_retrieval, \
    get_uuid
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

    subpi.add_argument("-i", "--milestone_uuid",
                       help="The uuid of a milestone. "
                            "Takes a full or partial uuid. "
                            "Multiple uuids may be entered.",
                       nargs='+')
    subpi.add_argument("--projectum_id", help="The id of the projectum. If you "
                                            "opt for this the program will assume "
                                            "you are adding a new milestone "
                                            "to the specified projectum.")
    subpi.add_argument("-u", "--due-date",
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
        if rc.date:
            now = date_parser.parse(rc.date).date()
        else:
            now = dt.date.today()
        new_mil = []
        pdoc = {}
        if rc.projectum_id and rc.milestone_uuid:
            raise RuntimeError("A uuid fragment and projectum id have been entered.\n"
                                "You may enter a milestone uuid or a projectum id but not both.\n"
                                "Enter a milestone uuid to update an existing milestone, or a projectum id to add a new milestone to that projectum.\n")
        if not rc.projectum_id and not rc.milestone_uuid:
            raise RuntimeError("No milestone uuid or projectum id was entered.\n"
                                "Enter a milestone uuid to update an existing milestone, or a projectum id to add a new milestone to that projectum.\n")
        if rc.projectum_id:
            rc.projectum_id = rc.projectum_id.strip()
            target_prum = rc.client.find_one(rc.database, rc.coll, {'_id': rc.projectum_id})
            if not target_prum:
                pra = fragment_retrieval(self.gtx["projecta"], ["_id"],
                                         rc.projectum_id)
                print("Projecta not found. Projecta with similar names: ")
                for i in range(len(pra)):
                    print(f"{pra[i].get('_id')}")
                print("Please rerun the helper specifying the complete ID.\n"
                      "If your prum id looks correct, check that this id is in the collection "
                      "in the database that regolith is looking in (i.e., {rc.database}).")
                return
            milestones = deepcopy(target_prum.get('milestones'))
            all_milestones = []
            for item in milestones:
                item['identifier'] = 'milestones'
            all_milestones.extend(milestones)
            for i in all_milestones:
                i['due_date'] = get_due_date(i)
            all_milestones.sort(key=lambda x: x['due_date'], reverse=False)
            index_list = list(range(2, (len(all_milestones) + 2)))
            mil = {}
            if not rc.due_date or not rc.name or not rc.objective:
                raise RuntimeError(
                    "name, objective, and due date are required for a new milestone")
            mil.update({'due_date': rc.due_date})
            mil['due_date'] = get_due_date(mil)
            mil.update({'objective': rc.objective, 'name': rc.name, 'uuid': get_uuid()})
            if rc.audience:
                mil.update({'audience': rc.audience})
            else:
                mil.update({'audience': ['lead', 'pi', 'group_members']})
            if rc.status:
                mil.update({'status': rc.status})
            else:
                mil.update({'status': 'proposed'})
            if rc.notes:
                mil.update({'notes': rc.notes})
            if rc.type:
                if rc.type in MILESTONE_TYPES:
                    mil.update({'type': rc.type})
                else:
                    raise ValueError(
                        "ERROR: The type you have specified is not recognized. "
                        "Please rerun your command adding '--type' "
                        f"and giving a type from this list: {MILESTONE_TYPES}")
            else:
                mil.update({'type': 'meeting'})
            mil.update({'identifier': "milestones"})
            new_mil.append(mil)
            pdoc = {'milestones': mil}
            new_all = deepcopy(all_milestones)
            for i, j in zip(index_list, new_all):
                if j['identifier'] == 'milestones':
                    new_mil.append(j)
            for mile in new_mil:
                del mile['identifier']
            new_mil.sort(key=lambda x: x['due_date'], reverse=False)
            pdoc.update({'milestones': new_mil})
            rc.client.update_one(rc.database, rc.coll, {'_id': rc.projectum_id}, pdoc)
            print("{} has been updated in projecta".format(rc.projectum_id))
        else:
            for uuid in rc.milestone_uuid:
                upd_mil = []
                all_miles = []
                id = []
                target_mil = fragment_retrieval(self.gtx["projecta"], ["milestones"], uuid)
                target_del = fragment_retrieval(self.gtx["projecta"], ["_id"], uuid)
                target_ko = fragment_retrieval(self.gtx["projecta"], ["_id"], uuid[2:])
                if target_mil:
                    for prum in target_mil:
                        milestones = prum['milestones']
                        for milestone in milestones:
                            if milestone.get('uuid')[0:len(uuid)] == uuid:
                                upd_mil.append(milestone)
                            else:
                                all_miles.append(milestone)
                        if upd_mil:
                            pid = prum.get('_id')
                            id.append(pid)
                if target_del:
                    for prum in target_del:
                        if prum.get('_id')[0:len(uuid)] == uuid:
                            deliverable = prum['deliverable']
                            upd_mil.append(deliverable)
                        if upd_mil:
                            pid = prum.get('_id')
                            id.append(pid)
                if target_ko:
                    for prum in target_ko:
                        if prum.get('_id')[0:len(uuid)] == uuid[2:]:
                            kickoff = prum['kickoff']
                            upd_mil.append(kickoff)
                        if upd_mil:
                            pid = prum.get('_id')
                            id.append(pid)
                if len(upd_mil) == 1:
                    for dict in upd_mil:
                        pdoc.update(dict)
                    for i in all_miles:
                        i['due_date'] = get_due_date(i)
                    if rc.finish:
                        rc.status = "finished"
                        pdoc.update({'end_date': now})
                        notes = pdoc.get("notes", [])
                        notes_with_closed_items = [note.replace('()', '(x)', 1) for note in notes]
                        pdoc["notes"] = notes_with_closed_items
                        if target_mil or target_ko:
                            print("The milestone {} has been marked as finished in prum {}".format(
                                                        pdoc.get('name'), id[0]))
                        if target_del:
                            name = 'deliverable'
                            print("The milestone {} has been marked as finished in prum {}".format(
                                                        name, id[0]))
                    if rc.audience:
                        pdoc.update({'audience': rc.audience})
                    if rc.due_date:
                        pdoc.update({'due_date': rc.due_date})
                    if rc.name and not target_del:
                        pdoc.update({'name': rc.name})
                    if rc.objective and not target_del:
                        pdoc.update({'objective': rc.objective})
                    if rc.status:
                        pdoc.update({'status': rc.status})
                    if rc.notes:
                        pdoc.update({'notes': rc.notes})
                    if rc.type:
                        if rc.type in MILESTONE_TYPES:
                            pdoc.update({'type': rc.type})
                        else:
                            raise ValueError(
                                "ERROR: The type you have specified is not recognized. "
                                "Please rerun your command adding '--type' "
                                f"and giving a type from this list: {MILESTONE_TYPES}")
                    doc = {}
                    pdoc['due_date'] = get_due_date(pdoc)
                    all_miles.append(pdoc)
                    all_miles.sort(key=lambda x: x['due_date'], reverse=False)
                    if target_mil:
                        doc.update({'milestones': all_miles})
                    if target_del:
                        doc.update({'deliverable': pdoc})
                    if target_ko:
                        doc.update({'kickoff': pdoc})
                    rc.client.update_one(rc.database, rc.coll, {'_id': id[0]}, doc)
                    print("{} has been updated in projecta.".format(id[0]))
                else:
                    print("Multiple ids match your entry(s).\n"
                          "Rerun the helper and include more characters of each id.")
        return
