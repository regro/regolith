"""List the mission control projects.

What ``l_projecta`` did, on the collections that replace projecta.  The
one that earns its keep is ``--orphans``: work that nobody is doing,
either because nobody was given it or because whoever had it has left
the group.  Nobody has to remember to reassign anything when somebody
goes.
"""

from collections import defaultdict

from gooey import GooeyParser

from regolith.helpers.basehelper import SoutHelperBase
from regolith.mc import CLOSED, orphaned, unled
from regolith.tools import all_docs_from_collection, collection_str, key_value_pair_filter

TARGET_COLL = "mc_projects"
HELPER_TARGET = "l-mcprojects"


def subparser(subpi):
    if isinstance(subpi, GooeyParser):
        pass
    subpi.add_argument(
        "-o",
        "--orphans",
        action="store_true",
        help="List the projects nobody is doing: the ones with no lead, and the "
        "ones led by somebody who has left the group.",
    )
    subpi.add_argument("-l", "--lead", help="List the projects led by this person, by id.")
    subpi.add_argument("-p", "--person", help="List the projects this person is on, leading them or not, by id.")
    subpi.add_argument("-g", "--grant", help="List the projects paid for by this grant, by id.")
    subpi.add_argument(
        "--all",
        action="store_true",
        help=f"Include the projects that are {' and '.join(CLOSED)}, which are left out by default.",
    )
    subpi.add_argument(
        "--grp-by-lead",
        # the underscore spelling is what l_projecta took, and is kept so that
        # nobody has to retype an alias they have used for years
        "--grp_by_lead",
        dest="grp_by_lead",
        action="store_true",
        help="Group the projects under whoever leads each one.",
    )
    subpi.add_argument("-v", "--verbose", action="store_true", help="Say more about each one.")
    subpi.add_argument(
        "-f",
        "--filter",
        nargs="+",
        help="Search the collection by giving key value pairs.",
    )
    subpi.add_argument(
        "-k",
        "--keys",
        nargs="+",
        help="The keys to print the values of, e.g. -k status project_deliverable. "
        "The id is printed whether it is asked for or not.",
    )
    return subpi


class MCProjectsListerHelper(SoutHelperBase):
    """List the mission control projects."""

    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "people"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        self.gtx[rc.coll] = list(all_docs_from_collection(rc.client, rc.coll))
        self.gtx["people"] = list(all_docs_from_collection(rc.client, "people"))

    def sout(self):
        rc = self.rc
        if rc.orphans and (rc.lead or rc.person):
            raise RuntimeError(
                "Orphans are the projects with nobody on them, so asking for a person as "
                "well asks for two different things. Please use one or the other."
            )
        projects = key_value_pair_filter(self.gtx[rc.coll], rc.filter) if rc.filter else self.gtx[rc.coll]
        people = self.gtx["people"]

        if rc.orphans:
            projects = [p for p in projects if orphaned(p, people)]
        elif not rc.all:
            projects = [p for p in projects if p.get("status") not in CLOSED]
        if rc.lead:
            projects = [p for p in projects if p.get("lead") == rc.lead]
        if rc.person:
            projects = [
                p for p in projects if p.get("lead") == rc.person or rc.person in p.get("collaborators", [])
            ]
        if rc.grant:
            projects = [p for p in projects if rc.grant in as_list(p.get("grants"))]

        projects = sorted(projects, key=lambda p: (p.get("lead") or "", p["_id"]))
        if rc.grp_by_lead:
            for line in self.by_lead(projects, rc.verbose):
                print(line)
            return
        if rc.keys:
            print(collection_str(projects, rc.keys), end="")
            return
        for project in projects:
            print(self.line(project))
            if rc.verbose:
                for line in self.more(project):
                    print(line)
        return

    @classmethod
    def by_lead(cls, projects, verbose=False):
        """Return the projects written out under whoever leads each one.

        Parameters
        ----------
        projects : list of dict
            The projects to write out.
        verbose : bool, optional
            Whether to say more about each one, as the ungrouped listing
            does.  The default is not to.

        Returns
        -------
        list of str
            The lines, a lead and then what they lead.
        """
        grouped = defaultdict(list)
        for project in projects:
            grouped["nobody" if unled(project) else project["lead"]].append(project)
        lines = []
        for lead in sorted(grouped):
            lines.append(f"{lead}:")
            for project in grouped[lead]:
                lines.append(f"    {project['_id']}  ({project.get('status', '?')})  {project.get('name', '')}")
                if verbose:
                    # what is said about a project sits under it, so it is
                    # indented one further than the ungrouped listing puts it
                    lines += [f"    {line}" for line in cls.more(project)]
        return lines

    @staticmethod
    def line(project):
        """Return the one line that says what a project is."""
        lead = "nobody" if unled(project) else project["lead"]
        return f"{project['_id']}  ({lead}, {project.get('status', '?')})  {project.get('name', '')}"

    @staticmethod
    def more(project):
        """Return the rest of what is worth knowing about a project."""
        lines = []
        for label, key in [
            ("deliverable", "project_deliverable"),
            ("description", "project_description"),
        ]:
            if project.get(key):
                lines.append(f"    {label}: {project[key]}")
        if project.get("collaborators"):
            lines.append(f"    with: {', '.join(project['collaborators'])}")
        if project.get("grants"):
            lines.append(f"    grants: {', '.join(as_list(project['grants']))}")
        return lines


def as_list(value):
    """Return a value as a list, since a grant may be one or several."""
    if not value:
        return []
    return [value] if isinstance(value, str) else list(value)
