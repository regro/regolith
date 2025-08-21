"""Helper for updating milestones to the projecta collection.

It can update the status, type, and due date of a projectum. It can add
a new milestone to the projecta collection.
"""

import datetime as dt
from copy import deepcopy

import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.dates import get_due_date
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.schemas import SCHEMAS, alloweds
from regolith.tools import all_docs_from_collection, fragment_retrieval, get_uuid

TARGET_COLL = "projecta"
MILESTONE_TYPES = alloweds.get("MILESTONE_TYPES")
PROJECTUM_STATI = alloweds.get("PROJECTUM_STATI")


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    # subpi.add_argument("-i", "--uuid", help="The universally unique id for the task so it
    #   can be referenced elsewhere. " "Takes a full or partial uuid.")
    subpi.add_argument(
        "-p",
        "--projectum_id",
        help="The id of the projectum. If you "
        "opt for this the program will assume "
        "you are adding a new milestone "
        "to the specified projectum.",
    )
    # subpi.add_argument(
    #     "-u", "--due-date", help="New due date of the milestone. " "Required for a new milestone.", **date_kwargs
    # )
    # Do not delete --database arg
    subpi.add_argument(
        "--database",
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
    )
    subpi.add_argument("-f", "--finish", action="store_true", help="Finish milestone. ")
    # subpi.add_argument("-n", "--name", help="Name of the milestone. " "Required for a new milestone.")
    # subpi.add_argument("-o", "--objective", help="Objective of the milestone. " "Required for a new milestone.")
    # # subpi.add_argument(
    # #     "-s",
    # #     "--status",
    # #     help="Status of the milestone/deliverable: "
    # #     f"{*PROJECTUM_STATI, }. "
    # #     "Defaults to proposed for a new milestone.",
    # # )
    # subpi.add_argument(
    #     "-t",
    #     "--type",
    #     help="Type of the milestone: " f"{*MILESTONE_TYPES, } " "Defaults to meeting for a new milestone.",
    # )
    # subpi.add_argument(
    #     "-a",
    #     "--audience",
    #     nargs="+",
    #     help="Audience of the milestone. " "Defaults to ['lead', 'pi', 'group_members'] for a new milestone.",
    # )
    # subpi.add_argument("--notes", nargs="+", help="Any notes you want to add to the milestone.")
    subpi.add_argument("--date", help="The date that will be used for testing.", **date_kwargs)

    milestone_keys = [key for key in SCHEMAS.get("projecta").get("milestones").get("schema").get("schema")]
    milestone_helps = milestone_keys
    milestone_helps = [
        help[1].get("description")
        for help in SCHEMAS.get("projecta").get("milestones").get("schema").get("schema").items()
    ]

    for key, help in zip(milestone_keys, milestone_helps):
        subpi.add_argument(f"--{key}", help=f"{help}")

    return subpi


class MilestoneUpdaterHelper(DbHelperBase):
    """Helper for updating milestones to the projecta collection."""

    # btype must be the same as helper target in helper.py
    btype = "u_milestone"
    needed_colls = [f"{TARGET_COLL}"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        updated, zero, multiple = [], [], []
        if rc.date:
            now = date_parser.parse(rc.date).date()
        else:
            now = dt.date.today()
        new_mil = []
        pdoc = {}
        if rc.projectum_id and rc.uuid:
            raise RuntimeError(
                "Detected both a uuid fragment and projectum id.\n"
                "You may enter either a milestone uuid or a projectum id but not both.\n"
                "Enter a milestone uuid to update an existing milestone, "
                "or a projectum id to add a new milestone to that projectum.\n"
            )
        if not rc.projectum_id and not rc.uuid:
            raise RuntimeError(
                "No milestone uuid or projectum id was entered.\n"
                "Enter a milestone uuid to update an existing milestone, "
                "or a projectum id to add a new milestone to that projectum.\n"
            )
        if rc.projectum_id:
            rc.projectum_id = rc.projectum_id.strip()
            target_prum = rc.client.find_one(rc.database, rc.coll, {"_id": rc.projectum_id})
            if not target_prum:
                pra = fragment_retrieval(self.gtx["projecta"], ["_id"], rc.projectum_id)
                print("Projectum not found. Projecta with similar names: ")
                for i in range(len(pra)):
                    print(f"{pra[i].get('_id')}")
                print(
                    f"Please rerun the helper specifying the complete ID.\n"
                    f"If your prum id looks correct, check that this id is in the collection "
                    f"in the database {rc.database}.\n"
                    f"If this is not the case, rerun with --database set to "
                    f"the database where the item is located."
                )
                return
            milestones = deepcopy(target_prum.get("milestones"))
            all_milestones = []
            for item in milestones:
                item["identifier"] = "milestones"
            all_milestones.extend(milestones)
            for i in all_milestones:
                i["due_date"] = get_due_date(i)
            all_milestones.sort(key=lambda x: x["due_date"], reverse=False)
            index_list = list(range(2, (len(all_milestones) + 2)))
            mil = {}
            if not rc.due_date or not rc.name or not rc.objective:
                raise RuntimeError("name, objective, and due date are required for a new milestone")
            mil.update({"due_date": rc.due_date})
            mil["due_date"] = get_due_date(mil)
            mil.update({"objective": rc.objective, "name": rc.name, "uuid": get_uuid()})
            if rc.audience:
                mil.update({"audience": rc.audience})
            else:
                mil.update({"audience": ["lead", "pi", "group_members"]})
            if rc.status:
                mil.update({"status": rc.status})
            else:
                mil.update({"status": "proposed"})
            if rc.notes:
                mil.update({"notes": rc.notes})
            if rc.type:
                if rc.type in MILESTONE_TYPES:
                    mil.update({"type": rc.type})
                else:
                    raise ValueError(
                        "The type you have specified is not recognized. \n"
                        "Please rerun your command adding '--type' \n"
                        f"and giving a type from this list:\n{MILESTONE_TYPES}\n"
                    )
            else:
                mil.update({"type": "meeting"})
            mil.update({"identifier": "milestones"})
            mil.update({"progress": {"text": ""}})
            new_mil.append(mil)
            pdoc = {"milestones": mil}
            new_all = deepcopy(all_milestones)
            for i, j in zip(index_list, new_all):
                if j["identifier"] == "milestones":
                    new_mil.append(j)
            for mile in new_mil:
                del mile["identifier"]
            new_mil.sort(key=lambda x: x["due_date"], reverse=False)
            pdoc.update({"milestones": new_mil})
            rc.client.update_one(rc.database, rc.coll, {"_id": rc.projectum_id}, pdoc)
            updated.append(f"{rc.projectum_id} has been updated in projecta")
        else:
            pdoc, upd_mil, all_miles, id = {}, [], [], []
            target_mil = fragment_retrieval(self.gtx["projecta"], ["milestones"], rc.uuid)
            target_del = fragment_retrieval(self.gtx["projecta"], ["_id"], rc.uuid)
            target_ko = fragment_retrieval(self.gtx["projecta"], ["_id"], rc.uuid[2:])
            if target_mil and not target_del and not target_ko:
                for prum in target_mil:
                    milestones = prum["milestones"]
                    for milestone in milestones:
                        if milestone.get("uuid")[0 : len(rc.uuid)] == rc.uuid:
                            upd_mil.append(milestone)
                        else:
                            all_miles.append(milestone)
                    if upd_mil:
                        pid = prum.get("_id")
                        id.append(pid)
            if target_del:
                for prum in target_del:
                    if prum.get("_id")[0 : len(rc.uuid)] == rc.uuid:
                        deliverable = prum["deliverable"]
                        upd_mil.append(deliverable)
                    if upd_mil:
                        pid = prum.get("_id")
                        id.append(pid)
            if target_ko and rc.uuid[:2] == "ko":
                for prum in target_ko:
                    if prum.get("_id")[0 : len(rc.uuid) - 2] == rc.uuid[2:]:
                        kickoff = prum["kickoff"]
                        upd_mil.append(kickoff)
                    if upd_mil:
                        pid = prum.get("_id")
                        id.append(pid)
            if len(upd_mil) == 0:
                zero.append(rc.uuid)
            elif len(upd_mil) == 1:
                for dict in upd_mil:
                    pdoc.update(dict)
                if not pdoc.get("type") and not rc.type and not target_del and not target_ko:
                    raise ValueError(
                        f"Milestone ({rc.uuid}) does not have a type set and this is required.\n"
                        "Specify '--type' and rerun the helper to update this milestone.\n"
                    )
                if rc.type:
                    if rc.type in MILESTONE_TYPES:
                        pdoc.update({"type": rc.type})
                    else:
                        raise ValueError(
                            "The type you have specified is not recognized. \n"
                            "Please rerun your command adding '--type' \n"
                            f"and giving a type from this list:\n{MILESTONE_TYPES}\n"
                        )
                for i in all_miles:
                    i["due_date"] = get_due_date(i)
                if rc.finish:
                    rc.status = "finished"
                    pdoc.update({"end_date": now})
                    if pdoc.get("notes"):
                        notes = pdoc.get("notes", [])
                        notes_with_closed_items = [note.replace("()", "(x)", 1) for note in notes]
                        pdoc["notes"] = notes_with_closed_items
                    if pdoc.get("name"):
                        updated.append(
                            f"The milestone '{pdoc.get('name')}' has been marked as finished in prum {id[0]}."
                        )
                    else:
                        name = "deliverable"
                        updated.append(f"The milestone '{name}' has been marked as finished in prum {id[0]}.")
                if rc.audience:
                    pdoc.update({"audience": rc.audience})
                if rc.due_date:
                    pdoc.update({"due_date": rc.due_date})
                if rc.name and pdoc.get("name"):
                    pdoc.update({"name": rc.name})
                elif rc.name and not pdoc.get("name"):
                    print(f"Ignoring 'name' assignment for deliverable uuid ({rc.uuid})")
                if rc.objective and pdoc.get("name"):
                    pdoc.update({"objective": rc.objective})
                elif rc.objective and not pdoc.get("name"):
                    print(f"Ignoring 'objective' assignment for deliverable uuid ({rc.uuid})")
                if rc.status:
                    pdoc.update({"status": rc.status})
                if rc.notes:
                    pdoc.update({"notes": rc.notes})
                doc = {}
                pdoc["due_date"] = get_due_date(pdoc)
                all_miles.append(pdoc)
                all_miles.sort(key=lambda x: x["due_date"], reverse=False)
                if target_mil and not target_del and not target_ko:
                    doc.update({"milestones": all_miles})
                if target_del:
                    doc.update({"deliverable": pdoc})
                if target_ko and rc.uuid[:2] == "ko":
                    doc.update({"kickoff": pdoc})
                rc.client.update_one(rc.database, rc.coll, {"_id": id[0]}, doc)
                if not rc.finish:
                    updated.append(f"The milestone uuid {rc.uuid} in {id[0]} has been updated in projecta.")
            else:
                multiple.append(rc.uuid)
        if updated:
            for msg in updated:
                print(msg)
        else:
            print("Failed to update projecta.")
        if zero:
            print(
                f"No ids were found that match your uuid entry ({zero[0]}).\n"
                "Make sure you have entered the correct uuid or uuid fragment and rerun the helper.\n"
            )
        if multiple:
            print(
                f"Multiple ids match your uuid entry ({multiple[0]}).\n"
                "Try entering more characters of the uuid and rerun the helper.\n"
            )
        return
