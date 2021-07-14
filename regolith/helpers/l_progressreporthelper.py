"""Helper for listing a summary of finished prums and progress on open prums.

   Projecta are small bite-sized project quanta that typically will result in
   one manuscript.
"""

from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    key_value_pair_filter,
    _id_key
)
from gooey import GooeyParser

TARGET_COLL = "projecta"
HELPER_TARGET = "l_progress"
ALLOWED_STATI = ["proposed", "started", "finished", "back_burner", "paused", "cancelled"]

def subparser(subpi):
    listbox_kwargs = {}
    if isinstance(subpi, GooeyParser):
        listbox_kwargs['widget'] = 'Listbox'

    subpi.add_argument("-v", "--verbose", action="store_true",
                       help='increase verbosity of output')
    subpi.add_argument("-l", "--lead",
                       help="Filter projecta for this project lead"
                       )
    subpi.add_argument("-s", "--stati", nargs="+",
                       choices=ALLOWED_STATI,
                       help=f"Filter projecta for these stati."
                            f" Default is all projecta",
                       default=None,
                       **listbox_kwargs
                       )
    # The --filter and --keys flags should be in every lister
    subpi.add_argument("-f", "--filter", nargs="+",
                       help="Search this collection by giving key element pairs"
                       )
    subpi.add_argument("-k", "--keys", nargs="+", help="Specify what keys to return values from when running "
                                                       "--filter. If no argument is given the default is just the id.")
    return subpi

def print_projectum(selected_projecta,rc):
    if selected_projecta == []:
        return
    selected_projecta.sort(key=lambda prum: prum.get('begin_date'), reverse=True)
    for p in selected_projecta:
        if rc.verbose:
            print(f"{p.get('_id')}")
            if p.get("deliverable"):
                print(
                    f"    status: {p.get('status')}, begin_date: {p.get('begin_date')}, due_date: {p.get('deliverable').get('due_date')}")
            else:
                print(
                    f"    status: {p.get('status')}, begin_date: {p.get('begin_date')}, due_date: {p.get('due_date')}")
            print(f"    description: {p.get('description')}")
            print(f"    log_url: {p.get('log_url')}")
            print("    team:")
            grp_members = None
            if p.get('group_members'):
                grp_members = ', '.join(p.get('group_members'))
            collaborators = None
            if p.get('collaborators'):
                collaborators = ', '.join(p.get('collaborators'))
            print(f"        group_members: {grp_members}")
            print(f"        collaborators: {collaborators}")
            d = p.get('deliverable')
            print("    deliverable:")
            audience = None
            if d.get('audience'):
                audience = ', '.join(d.get('audience'))
            print(f"        audience: {audience}")
            scope = None
            if d.get('scope'):
                scope = d.get('scope')
            if len(scope) == 1:
                print(f"        scope: {scope}")
            if len(scope) > 1:
                print(f"        scope: 1. {scope[0]}")
                for num in range(2, len(scope)+1):
                    print(f"               {str(num)}. {scope[num-1]}")
            print(f"        platform: {d.get('platform')}")
            print("    milestones:")
            for m in p.get('milestones'):
                print(f"        {m.get('due_date')}: {m.get('name')}")
                print(f"            objective: {m.get('objective')}")
                print(f"            status: {m.get('status')}")

        else:
            print(f"{p.get('_id')}")
            if p.get("deliverable"):
                print(
                    f"    status: {p.get('status')}, begin_date: {p.get('begin_date')}, due_date: {p.get('deliverable').get('due_date')}")
                print(f"    description: {p.get('description')}")
            else:
                print(
                    f"    status: {p.get('status')}, begin_date: {p.get('begin_date')}, due_date: {p.get('due_date')}")
                print(f"    description: {p.get('description')}")

class ProgressReportHelper(SoutHelperBase):
    """Helper for listing upcoming (and past) projectum milestones.

       Projecta are small bite-sized project quanta that typically will result in
       one manuscript.
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        colls = [
            sorted(
                all_docs_from_collection(rc.client, collname), key=_id_key
            )
            for collname in self.needed_colls
        ]
        for db, coll in zip(self.needed_colls, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        if rc.filter:
            collection = key_value_pair_filter(self.gtx["projecta"], rc.filter)
        else:
            collection = self.gtx["projecta"]

        projecta = []
        for projectum in collection:
            if (not rc.lead) and (not rc.stati):
                projecta.append(projectum)
                continue
            if rc.lead and projectum.get('lead') != rc.lead:
                continue
            if rc.stati and projectum.get('status') not in rc.stati:
                continue
            projecta.append(projectum)

        selected_projecta = []
        for p in projecta:
            if p.get('status') != "proposed":
                continue
            selected_projecta.append(p)
        if selected_projecta:
            print(f"*************************[Proposed Projecta]*************************")
            print_projectum(selected_projecta, rc)

        selected_projecta = []
        for p in projecta:
            if p.get('status') != "started":
                continue
            selected_projecta.append(p)
        if selected_projecta:
            print(f"*************************[Started Projecta]**************************")
            print_projectum(selected_projecta, rc)

        selected_projecta = []
        for p in projecta:
            if p.get('status') != "finished":
                continue
            selected_projecta.append(p)
        if selected_projecta:
            print(f"*************************[Finished Projecta]*************************")
            print_projectum(selected_projecta, rc)

        selected_projecta = []
        for p in projecta:
            if p.get('status') not in ["back_burner", "paused", "cancelled"]:
                continue
            selected_projecta.append(p)
        if selected_projecta:
            print(f"*************************[Others]************************************")
            print_projectum(selected_projecta, rc)
