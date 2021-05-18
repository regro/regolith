"""Helper for listing upcoming (and past) projectum milestones.

   Projecta are small bite-sized project quanta that typically will result in
   one manuscript.
"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.dates import get_due_date
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    search_collection,
    key_value_pair_filter,
    collection_str
)

TARGET_COLL = "projecta"
HELPER_TARGET = "l_milestones"
ALLOWED_STATI = ["all", "proposed", "converged", "started", "finished", "back_burner",
                 "paused", "cancelled"]
ACTIVE_STATI = ["proposed", "converged", "started"]
INACTIVE_STATI = ["back_burner",
                 "paused", "cancelled"]
FINISHED_STATI = ["finished"]
ROLES = ['pi', 'lead', 'group_members', 'collaborators']


def subparser(subpi):
    subpi.add_argument('--helper_help',
                        help='This helper will list all milestones. Rerun specifying '
                             '--lead PERSON or --person PERSON to get the milestones for projecta '
                             'where PERSON is lead, or has any role, respectively. '
                             'Rerun with --all, --current, or --finished to get '
                             'all, active or finished milestones, respectively. '
                             'filters work with AND logic so -l PERSON -c will list '
                             'the active milestones for projecta where PERSON is lead'
                        )
    subpi.add_argument("-l", "--lead",
                       help="Filter milestones for this project lead"
                       )
    subpi.add_argument("-p", "--person",
                       help="Filter milestones for this person whether lead or not")
    subpi.add_argument("-s", "--stati", nargs="+",
                       help=f"Filter milestones for these stati from {ALLOWED_STATI}."
                            f" Default is active projecta, i.e. 'started'",
                       default=None
                       )
    subpi.add_argument("--all", action="store_true",
                       help="Lists all milestones in general")
    subpi.add_argument("-c", "--current", action="store_true",
                       help="Lists all active milestones")
    subpi.add_argument("--finished", action="store_true",
                       help="Lists all finished milestones")
    subpi.add_argument("-v", "--verbose", action="store_true",
                       help='increase verbosity of output')
    # The --filter and --keys flags should be in every lister
    subpi.add_argument("-f", "--filter", nargs="+",
                       help="Search this collection by giving key element pairs"
                       )
    subpi.add_argument("-k", "--keys", nargs="+", help="Specify what keys to return values from when running "
                                                       "--filter. If no argument is given the default is just the id.")
    return subpi


class MilestonesListerHelper(SoutHelperBase):
    """Helper for listing upcoming (and past) projectum milestones.

       Projecta are small bite-sized project quanta that typically will result in
       one manuscript.
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        try:
            if not rc.database:
                rc.database = rc.databases[0]["name"]
        except:
            pass
        colls = [
            sorted(
                all_docs_from_collection(rc.client, collname), key=_id_key
            )
            for collname in self.needed_dbs
        ]
        for db, coll in zip(self.needed_dbs, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        # This if statement should be in all listers. Make sure to change self.gtx to get the database the lister needs
        if rc.filter:
            collection = key_value_pair_filter(self.gtx["projecta"], rc.filter)
        else:
            collection = self.gtx["projecta"]

        if (not rc.lead) and (not rc.verbose) and (not rc.stati) and (
            not rc.current) and (not rc.person) and (not rc.all):
            return

        if rc.lead:
            if rc.person:
                raise RuntimeError(
                    f"please specify either lead or person, not both")
            collection = [prum for prum in collection if
                          prum.get('lead') == rc.lead]
        if rc.person:
            if isinstance(rc.person, str):
                rc.person = [rc.person]
            collection = [prum for prum in collection
                          if prum.get('lead') in rc.person
                          or bool(
                    set(prum.get('group_members', [])).intersection(
                        set(rc.person)))]
        if not rc.all:
            collection = [prum for prum in collection if
                          prum.get('status') not in INACTIVE_STATI
                          ]

        all_milestones = []
        if not rc.stati:
            rc.stati = ['started']
        for projectum in collection:
            if not projectum.get("deliverable"):
                projectum["deliverable"] = {"audience": []}
            if not projectum.get("kickoff"):
                projectum["kickoff"] = {"audience": []}
            if not projectum.get("milestones"):
                projectum["milestones"] = [{"audience": []}]
            projectum["deliverable"].update({"name": "deliverable",
                                             "objective": "deliver"})
            projectum["kickoff"].update({"type": "meeting"})
            milestones = [projectum["kickoff"], projectum["deliverable"]]
            milestones.extend(projectum["milestones"])
            if rc.current:
                milestones = [ms for ms in milestones if
                              ms.get('status') in ACTIVE_STATI]
            if rc.finished:
                milestones = [ms for ms in milestones if
                              ms.get('status') in FINISHED_STATI]
            if not rc.all:
                milestones = [ms for ms in milestones if
                              ms.get('status') not in INACTIVE_STATI
                              ]
            for ms in milestones:
                due_date = get_due_date(ms)
                ms.update({
                    'lead': projectum.get('lead'),
                    'group_members': projectum.get('group_members'),
                    'collaborators': projectum.get('collaborators'),
                    'id': projectum.get('_id'),
                    'due_date': due_date,
                    'log_url': projectum.get('log_url'),
                    'pi': projectum.get('pi_id')
                })
                all_milestones.append(ms)
        all_milestones.sort(key=lambda x: x['due_date'], reverse=True)
        if rc.keys:
            results = (collection_str(all_milestones, rc.keys))
            print(results, end="")
            return
        for ms in all_milestones:
            if rc.verbose:
                print(
                    f"{ms.get('due_date')}: lead: {ms.get('lead')}, {ms.get('id')}, status: {ms.get('status')}")
                print(f"    Type: {ms.get('type', '')}")
                print(f"    Title: {ms.get('name')}")
                print(f"    log url: {ms.get('log_url')}")
                print(f"    Purpose: {ms.get('objective')}")
                audience = []
                for i in ms.get('audience', []):
                    if isinstance(ms.get(i, i), str):
                        audience.append(ms.get(i, i))
                    else:
                        if ms.get(i):
                            audience.extend(ms.get(i))
                out = ", ".join(audience)
                print(f"    Audience: {out}")
                if ms.get("notes"):
                    print(f"    Notes:")
                    for note in ms.get("notes"):
                        print(f"      - {note}")
            else:
                print(
                    f"{ms.get('due_date')}: lead: {ms.get('lead')}, {ms.get('id')}, {ms.get('name')}, status: {ms.get('status')}")

        return
