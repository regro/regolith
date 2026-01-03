"""Helper for listing upcoming (and past) projectum milestones.

Projecta are small bite-sized project quanta that typically will result
in one manuscript.
"""

from gooey import GooeyParser

from regolith.dates import get_due_date
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.schemas import (
    PROJECTUM_ACTIVE_STATI,
    PROJECTUM_CANCELLED_STATI,
    PROJECTUM_FINISHED_STATI,
    PROJECTUM_PAUSED_STATI,
    alloweds,
)
from regolith.tools import all_docs_from_collection, collection_str, get_pi_id, key_value_pair_filter, strip_str

PROJECTUM_STATI = alloweds.get("PROJECTUM_STATI")
TARGET_COLL = "projecta"
HELPER_TARGET = "l_milestones"
PROJECTUM_STATI.append("all")
INACTIVE_STATI = PROJECTUM_PAUSED_STATI + PROJECTUM_CANCELLED_STATI + PROJECTUM_FINISHED_STATI
ROLES = ["pi", "lead", "group_members", "collaborators"]


def subparser(subpi):
    listbox_kwargs = {}
    if isinstance(subpi, GooeyParser):
        listbox_kwargs["widget"] = "Listbox"

    subpi.add_argument(
        "--helper-help",
        action="store_true",
        help=f"This helper will list all ACTIVE milestones by default. To "
        f"be active the projectum itself must be active and the "
        f"milestone within the prum also active.  Active milestones "
        f"have a status from {*PROJECTUM_ACTIVE_STATI, }.\n "
        f"Please erun specifying "
        f"--lead PERSON or --person PERSON. "
        f"Rerun with --all, --current, or --finished to get "
        f"all, active or finished milestones, respectively. "
        f"filters work with AND logic so -l PERSON -c will list "
        f"the active milestones for projecta where PERSON is lead. "
        f'Note that "checklist" prums are not listed. Please use '
        f"u_milestone to see those.",
    )
    subpi.add_argument(
        "-l",
        "--lead",
        help="Filter milestones for this project lead specified as an ID, " "e.g., sbillinge",
        type=strip_str,
    )
    subpi.add_argument(
        "-p",
        "--person",
        help="Filter milestones for this person whether lead or not, specified " "by id, e.g., sbillinge",
        type=strip_str,
    )
    subpi.add_argument(
        "-c", "--current", action="store_true", help="Same behavior as default.  Here for consistency"
    )
    subpi.add_argument(
        "--finished",
        action="store_true",
        help=f"Lists all finished milestones, i.e., status is in {*PROJECTUM_FINISHED_STATI, }",
    )
    subpi.add_argument(
        "--by-prum", action="store_true", help="Valid milestones are listed in time-order but grouped by prum"
    )
    subpi.add_argument("-v", "--verbose", action="store_true", help="increase verbosity of output")
    subpi.add_argument(
        "-s",
        "--stati",
        nargs="+",
        choices=PROJECTUM_STATI,
        help=f"Filter milestones for these stati from {*PROJECTUM_STATI, }. "
        f"Default is active projecta, i.e. {*PROJECTUM_ACTIVE_STATI, }",
        default=None,
        **listbox_kwargs,
    )
    subpi.add_argument("--all", action="store_true", help="Lists all milestones in general")
    # The --filter and --keys flags should be in every lister
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs")
    subpi.add_argument(
        "-k",
        "--keys",
        nargs="+",
        help="Specify what keys to return values from when running "
        "--filter. If no argument is given the default is just the id.",
    )
    return subpi


class MilestonesListerHelper(SoutHelperBase):
    """Helper for listing upcoming (and past) projectum milestones.

    Projecta are small bite-sized project quanta that typically will
    result in one manuscript.
    """

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        colls = [
            sorted(all_docs_from_collection(rc.client, collname), key=_id_key) for collname in self.needed_colls
        ]
        for db, coll in zip(self.needed_colls, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        # This if statement should be in all listers.
        # Make sure to change self.gtx to get the database the lister needs
        if rc.filter:
            collection = key_value_pair_filter(self.gtx["projecta"], rc.filter)
        else:
            collection = self.gtx["projecta"]

        if (
            (not rc.lead)
            and (not rc.verbose)
            and (not rc.stati)
            and (not rc.current)
            and (not rc.person)
            and (not rc.all)
        ):
            return

        # fixme there must be a better way, but for now use magic to
        # to remove checklists
        # print(collection)
        collection = [
            prum for prum in collection if "checklist" not in prum.get("deliverable", {}).get("scope", [])
        ]

        if rc.lead:
            if rc.person:
                raise RuntimeError("please specify either lead or person, not both")
            collection = [prum for prum in collection if prum.get("lead") == rc.lead]
        if rc.person:
            if isinstance(rc.person, str):
                rc.person = [rc.person]
            collection = [
                prum
                for prum in collection
                if prum.get("lead") in rc.person
                or bool(set(prum.get("group_members", [])).intersection(set(rc.person)))
                or bool(set(prum.get("collaborators", [])).intersection(set(rc.person)))
            ]

        if not rc.all:
            collection = [prum for prum in collection if prum.get("status") not in INACTIVE_STATI]

        all_milestones = []
        if not rc.stati and not rc.all and not rc.finished:
            rc.stati = PROJECTUM_ACTIVE_STATI
        elif rc.finished:
            rc.stati = PROJECTUM_FINISHED_STATI
        elif rc.all:
            rc.stati = PROJECTUM_STATI
        for projectum in collection:
            projectum["deliverable"].update(
                {"name": "deliverable", "objective": "deliver", "uuid": projectum.get("_id")}
            )
            milestones = [projectum["deliverable"]]
            if projectum.get("kickoff"):
                projectum["kickoff"].update({"type": "meeting", "uuid": f"ko{projectum.get('_id')}"})
                milestones = [projectum["kickoff"], projectum["deliverable"]]
            milestones.extend(projectum["milestones"])
            milestones = [ms for ms in milestones if ms.get("status") in rc.stati]

            for ms in milestones:
                due_date = get_due_date(ms)
                ms.update(
                    {
                        "lead": projectum.get("lead"),
                        "group_members": projectum.get("group_members"),
                        "collaborators": projectum.get("collaborators"),
                        "id": projectum.get("_id"),
                        "due_date": due_date,
                        "log_url": projectum.get("log_url"),
                        "pi": projectum.get("pi_id"),
                    }
                )
            milestones.sort(key=lambda x: x["due_date"], reverse=True)
            all_milestones.extend(milestones)
        if rc.keys:
            results = collection_str(all_milestones, rc.keys)
            print(results, end="")
            return
        if not rc.by_prum:
            all_milestones.sort(key=lambda x: x["due_date"], reverse=True)
        prum = ""
        for ms in all_milestones:
            if rc.by_prum:
                if prum != ms.get("id"):
                    print("-" * 50)
                    prum = ms.get("id")
            if rc.verbose:
                print(
                    f"{ms.get('due_date')} ({(ms.get('uuid')[:6])}): lead: {ms.get('lead')}, {ms.get('id')}, "
                    f"status: {ms.get('status')}"
                )
                print(f"    Type: {ms.get('type', '')}")
                print(f"    Title: {ms.get('name')}")
                print(f"    log url: {ms.get('log_url')}")
                print(f"    Purpose: {ms.get('objective')}")
                audience = []
                for i in ms.get("audience", []):
                    if isinstance(ms.get(i, i), str):
                        audience.append(ms.get(i, i))
                    else:
                        if ms.get(i):
                            audience.extend(ms.get(i))
                out = ", ".join(audience)
                print(f"    Audience: {out}")
                if ms.get("notes"):
                    print("    Notes:")
                    for note in ms.get("notes"):
                        print(f"      - {note}")
                print(f"    uuid: {ms.get('uuid')}")
            else:
                print(
                    f"{ms.get('due_date')} ({(ms.get('uuid')[:6])}): lead: {ms.get('lead')}, {ms.get('id')}, "
                    f"{ms.get('name')}, status: {ms.get('status')}"
                )

        return
