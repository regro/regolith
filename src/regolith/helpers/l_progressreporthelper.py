"""Helper for listing a summary of finished prums and progress on open
prums.

Projecta are small bite-sized project quanta that typically will result
in one manuscript.
"""

import datetime

import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.schemas import PROJECTUM_ACTIVE_STATI, PROJECTUM_FINISHED_STATI, alloweds
from regolith.tools import all_docs_from_collection, get_pi_id, key_value_pair_filter, strip_str

TARGET_COLL = "projecta"
HELPER_TARGET = "l_progress"

PROJECTUM_STATI = alloweds.get("PROJECTUM_STATI")


def subparser(subpi):
    listbox_kwargs = {}
    if isinstance(subpi, GooeyParser):
        listbox_kwargs["widget"] = "Listbox"

    subpi.add_argument("lead", help="Generate report for this project lead", type=strip_str)
    subpi.add_argument("-v", "--verbose", action="store_true", help="increase verbosity of output")
    subpi.add_argument(
        "-s",
        "--stati",
        nargs="+",
        choices=PROJECTUM_STATI,
        help=f"Filter projecta for these stati."
        f" Default is {*(PROJECTUM_ACTIVE_STATI+PROJECTUM_FINISHED_STATI), }",
        default=PROJECTUM_ACTIVE_STATI + PROJECTUM_FINISHED_STATI,
        **listbox_kwargs,
    )
    # The --filter and --keys flags should be in every lister
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs")
    subpi.add_argument(
        "-k",
        "--keys",
        nargs="+",
        help="Specify what keys to return values from when running "
        "--filter. If no argument is given the default is just the id.",
    )
    subpi.add_argument("--date", help="date used in testing. Defaults to " "today's date.", type=strip_str)
    return subpi


class ProgressReportHelper(SoutHelperBase):
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

    def print_projectum(self, selected_projecta):
        rc = self.rc
        if selected_projecta == []:
            return
        selected_projecta.sort(key=lambda prum: prum.get("deliverable", {}).get("due_date"), reverse=False)
        for p in selected_projecta:
            if rc.verbose:
                print(f"{p.get('name', p.get('_id'))}")
                if p.get("deliverable"):
                    print(
                        f"  status: {p.get('status')}, begin_date: {p.get('begin_date')}, "
                        f"due_date: {p.get('deliverable').get('due_date')}"
                    )
                if p.get("status") == "finished":
                    print(f"  finished: {p.get('end_date')}")
                print(f"  {p.get('description')}")
                print(f"  log_url: {p.get('log_url')}")
                print("  team:")
                grp_members = _format_names(p.get("group_members", []))
                collaborators = _format_names(p.get("collaborators", []))
                print(f"    group_members: {grp_members}")
                print(f"    collaborators: {collaborators}")
                d = p.get("deliverable")
                print("  deliverable:")
                audience = _format_names(d.get("audience", []))
                print(f"    audience: {audience}")
                iter, title = 1, "scope:"
                for scopum in d.get("scope", ["no scope"]):
                    print(f"    {title} {str(iter)}. {scopum}")
                    iter += 1
                    title = "      "
                print(f"    platform: {d.get('platform')}")
                print("  milestones:")
                for m in p.get("milestones"):
                    print(f"    {m.get('due_date')}: {m.get('name')}")
                    print(f"      objective: {m.get('objective')}")
                    print(f"      status: {m.get('status')}")
            else:
                print(f"{p.get('name', p.get('_id'))}")
                print(_get_cline(p.get("name", ""), "="))
                print(f"  {p.get('description', 'description: None')}")
                if p.get("status") in PROJECTUM_ACTIVE_STATI:
                    if p.get("milestones"):
                        print("  milestones:")
                        print(f"  {_get_cline('milestones:  ', '-')}")
                    for m in p.get("milestones"):
                        print(
                            f"    {m.get('name')} ({m.get('uuid')[:6]}, due: {m.get('due_date')},"
                            f" {m.get('status')})"
                        )
                        print(f"      - {m.get('objective')}")
                        if m.get("progress") and m.get("status") != "finished":
                            print(f"        progress: {m.get('progress').get('text', '')}")
                print("")

    def sout(self):
        rc = self.rc
        if rc.filter:
            collection = key_value_pair_filter(self.gtx["projecta"], rc.filter)
        else:
            collection = self.gtx["projecta"]
        if not rc.date:
            now = datetime.date.today()
        else:
            now = date_parser.parse(rc.date).date()

        # remove checklist prums from the report
        collection = [
            prum for prum in collection if "checklist" not in prum.get("deliverable", {}).get("scope", [])
        ]

        title = f"\nProgress report for {rc.lead}, generated {now.isoformat()}"
        print(title)
        projecta = [valid_prum for valid_prum in collection if valid_prum.get("lead") == rc.lead]

        finishedp, proposedp, startedp, otherp = [], [], [], []
        for prum in projecta:
            if prum.get("status") == "finished":
                finishedp.append(prum)
            elif prum.get("status") == "proposed":
                proposedp.append(prum)
            elif prum.get("status") == "started":
                startedp.append(prum)
            else:
                otherp.append(prum)
        print("*************************[Orphan Projecta]*************************")
        for prum in otherp:
            print(f"{prum.get('_id')}, status: {prum.get('status')}")
        print("*************************[Finished Projecta]*************************")
        for prum in finishedp:
            print(f"{prum.get('_id')}, grant: {prum.get('grants')}")
            print(f"  {prum.get('description')}")
            print(f"  finished: {prum.get('end_date')}")
        print("*************************[Proposed Projecta]*************************")
        self.print_projectum(proposedp)
        print("*************************[In Progress Projecta]*************************")
        self.print_projectum(startedp)


def _get_cline(thing_to_underline: str, linestyle: str) -> str:
    if linestyle == "=":
        n_str = int(0.75 * len(thing_to_underline))
    else:
        n_str = len(thing_to_underline)
    return linestyle * n_str


def _format_names(namelist):
    return ", ".join(namelist)
