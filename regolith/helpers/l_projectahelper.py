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


def subparser(subpi):
    subpi.add_argument("--all", action="store_true",
                       help="Lists all projecta that have not ended"
                       )
    subpi.add_argument("-v", "--verbose", action="store_true", help='increase verbosity of output')
    subpi.add_argument("-l", "--lead",
                       help="Filter milestones for this project lead"
                       )
    subpi.add_argument("-p", "--person",
                       help="Filter milestones for this person whether lead or not"
                       )
    subpi.add_argument("-e", "--ended", action="store_true",
                       help="Lists projects that have ended. Use the -d and -r flags to specify"
                            "from one date and how many days"
                       )
    subpi.add_argument("-d", "--date",
                       help="projecta with end_date within RANGE before this date will be listed."
                            "Default is today"
                       )
    subpi.add_argument("-r", "--range",
                       help="date range back from DATE to search over in days. If no "
                            "range is specified, search will be 7 days"
                       )
    subpi.add_argument("-g", "--grant",
                       help="Filter projecta by a grant ID"
                       )
    subpi.add_argument("--grp_by_lead", action='store_true',
                       help="Lists all projecta by their lead")
    subpi.add_argument("-f", "--filter", nargs="+",
                       help="Search this collection by giving key element pairs"
                       )
    subpi.add_argument("-k", "--keys", nargs="+", help="Specify what keys to return values from when running "
                                                       "--filter. If no argument is given the default is just the id.")
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

        if (not rc.lead) and (not rc.person) and (not rc.ended) and (not rc.grant) and (not rc.verbose) and (not rc.grp_by_lead) and (not rc.filter) and (not rc.all):
            return
        if rc.date:
            desired_date = date_parser.parse(rc.date).date()
        else:
            desired_date = dt.date.today()

        if rc.range:
            num_of_days = int(rc.range)
        else:
            num_of_days = 7

        projecta = []
        end_projecta = []
        grouped_projecta = {}
        if rc.lead and rc.person:
            raise RuntimeError(f"please specify either lead or person, not both")
        for projectum in collection:
            if rc.all and projectum.get('status') != "finished":
                projecta.append(projectum)
                continue
            if isinstance(projectum.get('group_members'), str):
                projectum['group_members'] = [projectum.get('group_members')]
            if rc.lead and projectum.get('lead') != rc.lead:
                continue
            if rc.person:
                if isinstance(rc.person, str):
                    rc.person = [rc.person]
                good_p = []
                for i in rc.person:
                    if projectum.get('lead') == rc.person:
                        good_p.append(i)
                    if projectum.get('group_members') and i in projectum.get('group_members'):
                        good_p.append(i)
                if len(good_p) == 0:
                    continue
            if rc.grant and rc.grant not in projectum.get('grants'):
                continue
            if rc.ended and not projectum.get('end_date'):
                continue
            if rc.ended:
                end_date = projectum.get('end_date')
                if isinstance(end_date, str):
                    end_date = date_parser.parse(end_date).date()
                low_range = desired_date - dt.timedelta(days=num_of_days)
                high_range = desired_date + dt.timedelta(days=num_of_days)
                if low_range <= end_date <= high_range:
                    end_projecta.append(projectum)
                continue
            projecta.append(projectum)

        if rc.ended:
            for p in end_projecta:
                members, collaborators = None, None
                if p.get("group_members"):
                    members = ', '.join(p.get("group_members"))
                if p.get("collaborators"):
                    collaborators = ', '.join(p.get("collaborators"))
                print("{}    {}\n    Lead: {}    Members: {}    Collaborators: {}".format(p.get("_id"),
                                                                                          p.get("description"),
                                                                                          p.get("lead"), members,
                                                                                          collaborators))
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

        for i in projecta:
            print(i.get("_id"))
        return
