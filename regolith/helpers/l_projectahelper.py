"""Helper for listing upcoming (and past) projectum milestones.

   Projecta are small bite-sized project quanta that typically will result in
   one manuscript.
"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.dates import get_due_date, get_dates
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
HELPER_TARGET = "l_projecta"

ACTIVE_STATI = ["proposed", "started"]
INACTIVE_STATI = ["back_burner", "cancelled"]
FINISHED_STATI = ["finished"]


def subparser(subpi):
    subpi.add_argument("--all", action="store_true",
                       help="Lists all projecta in general")
    subpi.add_argument("-c", "--current", action="store_true",
                       help="Lists all active projecta")
    subpi.add_argument("-v", "--verbose", action="store_true",
                       help="increase verbosity of output")
    subpi.add_argument("-l", "--lead",
                       help="Filter milestones for this project lead")
    subpi.add_argument("-p", "--person",
                       help="Filter milestones for this person whether lead or not")
    subpi.add_argument("-e", "--ended", action="store_true",
                       help="Lists projecta that have ended. Use the -d and -r flags to specify up to "
                            "what date and how many days before then. The default is 7 days before today.")
    subpi.add_argument("-d", "--date",
                       help="projecta with end_date within RANGE before this date will be listed. "
                            "The default is today. Some projecta don't have an end date and won't appear in a search")
    subpi.add_argument("-r", "--range",
                       help="date range back from DATE to search over in days. "
                       "If no range is specified, search range will be 7 days")
    subpi.add_argument("-g", "--grant",
                       help="Filter projecta by a grant ID")
    subpi.add_argument("--grp_by_lead", action='store_true',
                       help="Lists all projecta by their lead")
    subpi.add_argument("-f", "--filter", nargs="+",
                       help="Search this collection by giving key element pairs")
    subpi.add_argument("-k", "--keys", nargs="+",
                       help="Specify what keys to return values from when running --filter. "
                            "If no argument is given the default is just the id.")
    return subpi


class ProjectaListerHelper(SoutHelperBase):
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
        if rc.filter:
            collection = key_value_pair_filter(self.gtx["projecta"], rc.filter)
        else:
            collection = self.gtx["projecta"]

        if (not rc.lead) and (not rc.person) and (not rc.ended) and (not rc.grant) and (not rc.verbose) and (not rc.grp_by_lead) and (not rc.filter) and (not rc.current) and (not rc.all):
            return
        if rc.date:
            desired_date = date_parser.parse(rc.date).date()
        else:
            desired_date = dt.date.today()

        if rc.range:
            num_of_days = int(rc.range)
        else:
            num_of_days = 7

        projecta, end_projecta, error_projecta = [], [], []
        grouped_projecta = {}
        if rc.lead:
            if rc.person:
                raise RuntimeError(
                    f"please specify either lead or person, not both")
            collection = [prum for prum in collection if prum.get('lead') == rc.lead]
        if rc.person:
            if isinstance(rc.person, str):
                rc.person = [rc.person]
            collection = [prum for prum in collection
                          if prum.get('lead') in rc.person
                          or bool(set(prum.get('group_members',[])).intersection(set(rc.person)))]
        if rc.current:
            collection = [prum for prum in collection if prum.get('status') in ACTIVE_STATI]

        for projectum in collection:
            if rc.all:
                projecta.append(projectum)
                continue
            if isinstance(projectum.get('group_members'), str):
                projectum['group_members'] = [projectum.get('group_members')]
            if rc.grant and rc.grant not in projectum.get('grants'):
                continue
            if rc.ended:
                if projectum.get('status') not in ACTIVE_STATI:
                    if projectum.get('status') in INACTIVE_STATI:
                        continue
                    elif projectum.get('status') not in FINISHED_STATI \
                            or not isinstance(projectum.get('end_date'), dt.date):
                        error_projecta.append(projectum)
                    else:
                        end_date = projectum.get('end_date')
                        if isinstance(end_date, str):
                            end_date = date_parser.parse(
                                end_date).date()
                        low_range = desired_date - \
                            dt.timedelta(days=num_of_days)
                        if low_range <= end_date <= desired_date:
                            end_projecta.append(projectum)
                if end_projecta != []:
                    projecta = end_projecta
                continue
            projecta.append(projectum)

        if rc.verbose:
            for p in projecta:
                grants = None
                if p.get('grants'):
                    if isinstance(p.get('grants'), list):
                        grants = ' ,'.join(p.get('grants'))
                    else:
                        grants = p.get('grants')
                print(p.get('_id'))
                print(
                    f"    status: {p.get('status')}, begin_date: {p.get('begin_date')}, due_date: {p.get('due_date')}, end_date: {p.get('end_date')}, grant: {grants}")
                print(f"    description: {p.get('description')}")
                print("    team:")
                print(f"        lead: {p.get('lead')}")
                grp_members = None
                if p.get('group_members'):
                    grp_members = ', '.join(p.get('group_members'))
                collaborators = None
                if p.get('collaborators'):
                    collaborators = ', '.join(p.get('collaborators'))
                print(f"        group_members: {grp_members}")
                print(f"        collaborators: {collaborators}")
            return

        if rc.grp_by_lead:
            for p in projecta:
                if p.get('lead') not in grouped_projecta:
                    grouped_projecta[p.get('lead')] = [p.get('_id')]
                else:
                    grouped_projecta[p.get('lead')].append(p.get('_id'))
            for key, values in grouped_projecta.items():
                print(f"{key}:")
                for v in values:
                    print(f"    {v}")
            return

        projecta.sort(key=lambda prum: prum.get("_id"))
        if rc.keys:
            results = (collection_str(projecta, rc.keys))
            print(results, end="")
            return

        if end_projecta != []:
            if desired_date == dt.date.today() and num_of_days == 7:
                print("\nProjecta finished this past week! o(*^V^*)o")
            else:
                print(
                    f"\nProjecta finished within the {num_of_days} days leading up to {desired_date}")
        elif end_projecta == [] and rc.ended:
            if desired_date == dt.date.today() and num_of_days == 7:
                print("\nNo projecta finished this week")
            else:
                print(
                    f"\nNo projecta finished within the {num_of_days} days leading up to {desired_date}")

        for i in projecta:
            print(i.get("_id"))

        if error_projecta:
            print("\nWARNING: These projecta have an issue with the end date and/or status, "
                  "please run f_prum to set status to finished and add an end date")
            for i in error_projecta:
                print(i.get("_id"))
