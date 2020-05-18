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
)

TARGET_COLL = "projecta"
HELPER_TARGET = "l_milestones"
ALLOWED_STATI = ["all", "proposed", "started", "finished", "back_burner",
                 "paused", "cancelled"]
ROLES = ['pi',  'lead', 'group_members', 'collaborators']


def subparser(subpi):
    subpi.add_argument("-v", "--verbose", action="store_true",
                       help='increase verbosity of output')
    subpi.add_argument("-l", "--lead",
                       help="Filter milestones for this project lead"
                       )
    subpi.add_argument("-s", "--stati", nargs="+",
                       help=f"Filter milestones for these stati from {ALLOWED_STATI}."
                            f" Default is active projecta, i.e. 'started'",
                       default=None
                       )
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
        all_milestones = []
        if not rc.stati:
            rc.stati = ['started']
        for projectum in self.gtx["projecta"]:
            if rc.lead and projectum.get('lead') != rc.lead:
                continue
            projectum["deliverable"].update({"name": "deliverable",
                                             "objective": "deliver"})
            gather_miles = [projectum["kickoff"], projectum["deliverable"]]
            gather_miles.extend(projectum["milestones"])
            for ms in gather_miles:
                if projectum["status"] in rc.stati or \
                        'all' in rc.stati:
                    if ms.get('status') not in \
                            ["finished", "cancelled"]:
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
        for ms in all_milestones:
            if rc.verbose:
                print(
                    f"{ms.get('due_date')}: lead: {ms.get('lead')}, {ms.get('id')}, status: {ms.get('status')}")
                print(f"    Title: {ms.get('name')}")
                print(f"    log url: {ms.get('log_url')}")
                print(f"    Purpose: {ms.get('objective')}")
                audience = []
                for i in ms.get('audience'):
                    if isinstance(ms.get(i,i), str):
                        audience.append(ms.get(i,i))
                    else:
                        if ms.get(i):
                            audience.extend(ms.get(i))
                out = ", ".join(audience)
                print(f"    Audience: {out}")
            else:
                print(
                    f"{ms.get('due_date')}: lead: {ms.get('lead')}, {ms.get('id')}, {ms.get('name')}, status: {ms.get('status')}")

        return

    def db_updater(self):
        rc = self.rc
        if not rc.date:
            now = dt.date.today()
        else:
            now = date_parser.parse(rc.date).date()
        key = f"{str(now.year)[2:]}{rc.lead[:2]}_{''.join(rc.name.casefold().split()).strip()}"

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            sys.exit("This entry appears to already exist in the collection")
        else:
            pdoc = {}

        pdoc.update({
            'begin_date': now.isoformat(),
        })
        pdoc.update({
            'name': rc.name,
        })
        pdoc.update({
            'pi_id': rc.pi_id,
        })
        pdoc.update({
            'lead': rc.lead,
        })
        if rc.description:
            pdoc.update({
                'description': rc.description,
            })
        if rc.grants:
            if isinstance(rc.grants, str):
                rc.grants = [rc.grants]
            pdoc.update({'grants': rc.grants})
        else:
            pdoc.update({'grants': ["tbd"]})
        if rc.group_members:
            if isinstance(rc.group_members, str):
                rc.group_members = [rc.group_members]
            pdoc.update({'group_members': rc.group_members})
        else:
            pdoc.update({'group_members': []})
        if rc.collaborators:
            if isinstance(rc.collaborators, str):
                rc.collaborators = [rc.collaborators]
            pdoc.update({
                'collaborators': rc.collaborators,
            })
        pdoc.update({"_id": key})

        firstm = {'due_date': now + relativedelta(days=7),
                  'name': 'Kick off meeting',
                  'objective': 'roll out of project to team',
                  'audience': ['pi', 'lead', 'group members',
                               'collaborators'],
                  'status': 'proposed'
                  }
        secondm = {'due_date': now + relativedelta(days=21),
                   'name': 'Project lead presentation',
                   'objective': 'lead presents background reading and '
                                'initial project plan',
                   'audience': ['pi', 'lead', 'group members'],
                   'status': 'proposed'
                   }
        thirdm = {'due_date': now + relativedelta(days=28),
                  'name': 'planning meeting',
                  'objective': 'develop a detailed plan with dates',
                  'audience': ['pi', 'lead', 'group members'],
                  'status': 'proposed'
                  }
        fourthm = {'due_date': now + relativedelta(years=1),
                   'name': 'final submission',
                   'objective': 'submit paper, make release, whatever',
                   'audience': ['pi', 'lead', 'group members', 'collaborators'],
                   'status': 'proposed'
                   }
        pdoc.update({"milestones": [firstm, secondm, thirdm, fourthm]})

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
