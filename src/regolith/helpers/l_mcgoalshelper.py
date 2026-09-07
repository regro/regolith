"""List the mission control goals.

What ``l_milestones`` did, on the collections that replace projecta.
Goals are what milestones were, so this is the view that answers what
somebody agreed to get done this period and how far along it is.
"""

from gooey import GooeyParser

from regolith.helpers.basehelper import SoutHelperBase
from regolith.mc import CLOSED, HELD, unassigned
from regolith.tools import all_docs_from_collection, key_value_pair_filter

TARGET_COLL = "mc_goals"
HELPER_TARGET = "l-mcgoals"


def subparser(subpi):
    if isinstance(subpi, GooeyParser):
        pass
    subpi.add_argument("-l", "--lead", help="List the goals of the projects this person leads, by id.")
    subpi.add_argument("-p", "--person", help="List the goals of the projects this person is on, by id.")
    subpi.add_argument("--period", help="List the goals of this period, e.g. 2026Q3.")
    subpi.add_argument(
        "--carried",
        action="store_true",
        help="List only the goals that have been carried from an earlier period, and say "
        "which one they started in.",
    )
    subpi.add_argument(
        "--held",
        action="store_true",
        help=f"List the goals on the {' and '.join(HELD)} instead of the ones being worked on.",
    )
    subpi.add_argument(
        "--all",
        action="store_true",
        help=f"Include the goals that are {' and '.join(CLOSED)}, and every period.",
    )
    subpi.add_argument("-v", "--verbose", action="store_true", help="Say more about each one.")
    subpi.add_argument("-f", "--filter", nargs="+", help="Search the collection by giving key value pairs.")
    return subpi


class MCGoalsListerHelper(SoutHelperBase):
    """List the mission control goals."""

    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "mc_projects"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        self.gtx[rc.coll] = list(all_docs_from_collection(rc.client, rc.coll))
        self.gtx["mc_projects"] = list(all_docs_from_collection(rc.client, "mc_projects"))

    def sout(self):
        rc = self.rc
        goals = key_value_pair_filter(self.gtx[rc.coll], rc.filter) if rc.filter else self.gtx[rc.coll]
        projects = {project["_id"]: project for project in self.gtx["mc_projects"]}

        # a goal of a project belongs to whoever leads the project; one held
        # on deck or on the wishlist may be of no project yet, and says whose
        # it is itself
        if rc.lead:
            goals = [g for g in goals if self.whose(g, projects) == rc.lead]
        if rc.person:
            goals = [
                g
                for g in goals
                if self.is_on(projects.get(g["project"], {}), rc.person) or self.whose(g, projects) == rc.person
            ]
        if rc.held:
            goals = [g for g in goals if g.get("status") in HELD]
        elif not rc.all:
            goals = [g for g in goals if g.get("status") not in CLOSED + HELD]
        if rc.carried:
            goals = [g for g in goals if g.get("first_period") != g.get("period")]
        period = rc.period or (None if rc.all else self.latest(goals))
        if period:
            goals = [g for g in goals if g.get("period") == period]

        for project_id, its_goals in self.by_project(goals):
            if project_id not in projects:
                print(f"{project_id}  (of no project yet)")
            else:
                project = projects[project_id]
                print(f"{project_id}  ({project.get('lead', 'nobody')})  {project.get('name', '')}")
            for goal in its_goals:
                print(f"    {self.line(goal)}")
                if rc.verbose and goal.get("notes"):
                    for note in goal["notes"]:
                        print(f"        {note}")
        return

    @staticmethod
    def whose(goal, projects):
        """Return whose goal it is, by its project or by itself.

        Parameters
        ----------
        goal : dict
            The goal.
        projects : dict
            The projects, keyed by id.

        Returns
        -------
        str or None
            The id of the person whose goal it is.
        """
        if unassigned(goal):
            return goal.get("lead")
        return projects.get(goal["project"], {}).get("lead")

    @staticmethod
    def is_on(project, person):
        """Return True if somebody leads a project or is on it."""
        return project.get("lead") == person or person in project.get("collaborators", [])

    @staticmethod
    def latest(goals):
        """Return the most recent period any of these goals is in."""
        periods = [g.get("period") for g in goals if g.get("period")]
        return max(periods) if periods else None

    @staticmethod
    def by_project(goals):
        """Return the goals grouped under the project they belong to."""
        grouped = {}
        for goal in goals:
            grouped.setdefault(goal["project"], []).append(goal)
        return sorted((k, sorted(v, key=lambda g: g["_id"])) for k, v in grouped.items())

    @staticmethod
    def line(goal):
        """Return the one line that says what a goal is."""
        carried = ""
        if goal.get("first_period") and goal["first_period"] != goal.get("period"):
            carried = f"  (carried since {goal['first_period']})"
        return f"{goal['_id']}  ({goal.get('status', '?')})  {goal.get('text', '')}{carried}"
