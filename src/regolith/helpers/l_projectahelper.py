"""Helper for listing upcoming (and past) projectum milestones.

Projecta are small bite-sized project quanta that typically will result
in one manuscript.
"""

import datetime as dt

import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.schemas import (
    PROJECTUM_ACTIVE_STATI,
    PROJECTUM_CANCELLED_STATI,
    PROJECTUM_FINISHED_STATI,
    PROJECTUM_PAUSED_STATI,
)
from regolith.tools import all_docs_from_collection, collection_str, get_pi_id, key_value_pair_filter, strip_str

TARGET_COLL = "projecta"
HELPER_TARGET = "l_projecta"
INACTIVE_STATI = PROJECTUM_PAUSED_STATI + PROJECTUM_CANCELLED_STATI


def subparser(subpi):
    date_kwargs = {}
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        int_kwargs["widget"] = "IntegerField"

    subpi.add_argument(
        "-l",
        "--lead",
        help="Filter milestones for this project lead, " "specified by id, e.g., sbillinge",
        type=strip_str,
    )
    subpi.add_argument(
        "-p",
        "--person",
        type=strip_str,
        help="Filter milestones for this person whether lead or " "not, specified by id, e.g., sbillinge",
    )
    subpi.add_argument("-g", "--grant", help="Filter projecta by a grant ID", type=strip_str)
    subpi.add_argument(
        "-c",
        "--current",
        action="store_true",
        help="Lists only active projecta. If not specified, will be active and paused but not cancelled",
    )
    subpi.add_argument("-v", "--verbose", action="store_true", help="increase verbosity of output")
    subpi.add_argument("--grp_by_lead", action="store_true", help="Lists all projecta by their lead")
    subpi.add_argument(
        "-o",
        "--orphans",
        action="store_true",
        help="Find all orphans: prums that are assigned to 'tbd' or have a " "non active person as lead",
    )
    subpi.add_argument(
        "--all",
        action="store_true",
        help=f"Lists all projecta including those with statuses "
        f"in {*PROJECTUM_CANCELLED_STATI, } that are excluded by default",
    )
    subpi.add_argument(
        "-e",
        "--ended",
        action="store_true",
        help="Lists projecta that have ended. Use the -r flag to specify "
        "how many days prior to today to search over for finished"
        "prums (default is 7 days). "
        "You may also use -d to change date used to search back"
        "from (mostly used for testing)",
    )
    subpi.add_argument(
        "-r",
        "--range",
        help="date range back from DATE, in days, to search over "
        "for finished prums."
        "If no range is specified, search range will be 7 days",
        type=int,
    )
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs")
    subpi.add_argument(
        "-k",
        "--keys",
        nargs="+",
        help="Specify what keys to return values from when running --filter. "
        "If no argument is given the default is just the id.",
    )
    subpi.add_argument(
        "-d",
        "--date",
        help="projecta with end_date within RANGE before this date will be listed. "
        "The default is today. Some projecta don't have an end date and won't appear in a search. "
        "mostly used for testing.",
        type=strip_str,
        **date_kwargs,
    )
    return subpi


class ProjectaListerHelper(SoutHelperBase):
    """Helper for listing upcoming (and past) projectum milestones.

    Projecta are small bite-sized project quanta that typically will
    result in one manuscript.
    """

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "people"]

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
        if rc.filter:
            collection = key_value_pair_filter(self.gtx["projecta"], rc.filter)
        else:
            collection = self.gtx["projecta"]

        if (
            (not rc.lead)
            and (not rc.person)
            and (not rc.ended)
            and (not rc.grant)
            and (not rc.verbose)
            and (not rc.grp_by_lead)
            and (not rc.filter)
            and (not rc.current)
            and (not rc.all)
            and (not rc.orphans)
        ):
            return
        if rc.date:
            now = date_parser.parse(rc.date).date()
        else:
            now = dt.date.today()
        if not rc.range:
            rc.range = 7
        since_date = now - dt.timedelta(days=int(rc.range))

        projecta, end_projecta, error_projecta = [], [], []
        grouped_projecta = {}
        if rc.grant:
            collection = [prum for prum in collection if rc.grant in prum.get("grants", [])]
        if rc.orphans:
            if rc.person or rc.lead:
                raise RuntimeError("you cannot specify lead or person with orphans")
            dead_parents = [person.get("_id") for person in self.gtx["people"] if not person.get("active")]
            collection = [
                prum
                for prum in collection
                if prum.get("lead") in dead_parents
                and prum.get("status") in PROJECTUM_ACTIVE_STATI + PROJECTUM_PAUSED_STATI
                or prum.get("lead").lower() == "tbd"
            ]
        if rc.lead:
            if rc.person or rc.orphans:
                raise RuntimeError("please specify either lead or person, not both")
            collection = [prum for prum in collection if prum.get("lead") == rc.lead]
        if rc.person:
            if rc.orphans:
                raise RuntimeError("please specify either lead or person, not both")
            if isinstance(rc.person, str):
                rc.person = [rc.person]
            collection = [
                prum
                for prum in collection
                if prum.get("lead") in rc.person
                or bool(set(prum.get("group_members", [])).intersection(set(rc.person)))
            ]
        if rc.current:
            collection = [prum for prum in collection if prum.get("status") in PROJECTUM_ACTIVE_STATI]
        elif not rc.all:
            collection = [prum for prum in collection if prum.get("status") not in PROJECTUM_CANCELLED_STATI]
        for projectum in collection:
            if rc.ended:
                if projectum.get("status") not in PROJECTUM_ACTIVE_STATI:
                    if projectum.get("status") in INACTIVE_STATI:
                        continue
                    elif projectum.get("status") not in PROJECTUM_FINISHED_STATI:
                        error_projecta.append(projectum)
                    elif not isinstance(projectum.get("end_date"), dt.date):
                        try:
                            dt.datetime(*[int(num) for num in projectum.get("end_date").split("-")])
                        except Exception:
                            error_projecta.append(projectum)
                    else:
                        end_date = projectum.get("end_date")
                        if isinstance(end_date, str):
                            end_date = date_parser.parse(end_date).date()
                        if since_date <= end_date <= now:
                            end_projecta.append(projectum)
                if end_projecta != []:
                    projecta = end_projecta
                continue
            projecta.append(projectum)

        if rc.verbose:
            for p in projecta:
                grants = None
                if p.get("grants"):
                    if isinstance(p.get("grants"), list):
                        grants = " ,".join(p.get("grants"))
                    else:
                        grants = p.get("grants")
                if p.get("status") == "finished":
                    ended = f", end_date: {p.get('end_date')}"
                else:
                    ended = ""
                print(p.get("_id"))
                print(
                    f"    status: {p.get('status')}, begin_date: {p.get('begin_date')}, "
                    f"due_date: {p.get('deliverable', {}).get('due_date')}{ended}, grant: {grants}"
                )
                print(f"    description: {p.get('description')}")
                print("    team:")
                print(f"        lead: {p.get('lead')}")
                grp_members = None
                if p.get("group_members"):
                    grp_members = ", ".join(p.get("group_members"))
                collaborators = None
                if p.get("collaborators"):
                    collaborators = ", ".join(p.get("collaborators"))
                print(f"        group_members: {grp_members}")
                print(f"        collaborators: {collaborators}")
            return

        if rc.grp_by_lead:
            for p in projecta:
                output = f"{p.get('_id')} ({p.get('status')})"
                if p.get("lead") not in grouped_projecta:
                    grouped_projecta[p.get("lead")] = [output]
                else:
                    grouped_projecta[p.get("lead")].append(output)
            for key, values in grouped_projecta.items():
                print(f"{key}:")
                for v in values:
                    print(f"    {v}")
            return

        projecta.sort(key=lambda prum: prum.get("_id"))
        if rc.keys:
            results = collection_str(projecta, rc.keys)
            print(results, end="")
            return

        if end_projecta != []:
            if now == dt.date.today() and rc.range == 7:
                print("\nProjecta finished this past week! o(*^v^*)o")
            else:
                print(f"\nProjecta finished within the {rc.range} days leading up to {now}")
        elif end_projecta == [] and rc.ended:
            if now == dt.date.today() and rc.range == 7:
                print("\nNo projecta finished this week")
            else:
                print(f"\nNo projecta finished within the {rc.range} days leading up to {now}")

        for i in projecta:
            output = f"{i.get('_id')} ({i.get('status')})"
            print(output)

        if error_projecta:
            print(
                "\nWARNING: These projecta have an issue with the end date and/or status, "
                "please run f_prum to set status to finished and add an end date"
            )
            for i in error_projecta:
                print(i.get("_id"))
