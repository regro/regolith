"""Builder for the mission control documents.

One document per person, plus one for the projects nobody leads.  The
document is a view of the ``mc_projects``, ``mc_goals`` and ``mc_tasks``
collections, laid out to follow a meeting: what are your projects, what
did we agree for this period, what did you plan for this past week.

The numbers in it are positional and are rewritten every time it is
built.  The ``^id`` after each line is the stable identity, and is what
a reader of the document will match a line back to.  Nobody types
either.

See ~/dev/regolith-notes/plan-mission-control.md for the design.
"""

import datetime as dt
import re
from collections import defaultdict
from pathlib import Path

from regolith.builders.basebuilder import BuilderBase
from regolith.dates import get_dates
from regolith.mc import struck
from regolith.tools import all_docs_from_collection

UNASSIGNED = "unassigned"
UNASSIGNED_NAME = "unassigned"
HELD_STATI = ("backburner", "wishlist")
ID_IN_DOCUMENT = re.compile(r"\^([\w.-]+)")


def ids_in_document(text):
    """Return the ids a document carries, in the order they appear.

    The order of a mission control document is meaningful: things are put
    in the order they matter, in conversation.  Reading the ids back is
    how a render keeps an order somebody chose.

    Parameters
    ----------
    text : str
        The document to read.

    Returns
    -------
    list of str
        The ids, in the order they appear, each once.
    """
    seen = []
    for _id in ID_IN_DOCUMENT.findall(text):
        if _id not in seen:
            seen.append(_id)
    return seen


def in_document_order(items, order, fallback_key):
    """Return items in the order a document put them in.

    Anything the document does not mention goes after everything it does,
    in whatever order ``fallback_key`` gives, since nobody has said where
    it belongs yet.

    Parameters
    ----------
    items : list of dict
        The items to order.
    order : list of str
        The ids the document carries, in order.
    fallback_key : callable
        The sort key for items the document does not mention.

    Returns
    -------
    list of dict
        The items, ordered.
    """
    position = {_id: n for n, _id in enumerate(order)}
    known = sorted((i for i in items if i["_id"] in position), key=lambda i: position[i["_id"]])
    unknown = sorted((i for i in items if i["_id"] not in position), key=fallback_key)
    return known + unknown


def week_of(date):
    """Return the Monday of the week a date falls in.

    Parameters
    ----------
    date : datetime.date
        The date to place.

    Returns
    -------
    datetime.date
        The Monday of that week.
    """
    return date - dt.timedelta(days=date.weekday())


def as_date(value):
    """Return a date from either a date or an iso string.

    A collection can be backed by mongo, which stores dates as iso
    strings, or by the filesystem, which stores them as dates.

    Parameters
    ----------
    value : datetime.date or str or None
        The value to read.

    Returns
    -------
    datetime.date or None
        The date, or None when there was nothing to read.
    """
    if value is None or isinstance(value, dt.date):
        return value
    return get_dates({"date": value}).get("date")


class MissionControlBuilder(BuilderBase):
    """Render the mission control document of every person."""

    btype = "mission-control"
    needed_colls = ["mc_projects", "mc_goals", "mc_tasks", "people"]

    def __init__(self, rc):
        super().__init__(rc)
        self.cmds = ["render"]
        # The documents are edited where people can reach them, which is not
        # the build directory.  rc.mission_control_dir says where; without it
        # they go under the build directory like any other built thing.
        self.mcdir = Path(getattr(rc, "mission_control_dir", None) or self.bldir)

    def display_name(self, person):
        """Return the name to head a person's document with."""
        for entry in self.gtx.get("people", []):
            if entry["_id"] == person:
                return entry.get("name") or person
        return person

    def document_name(self, person):
        """Return the file name to write a person's document to.

        A person is known to the database by an id, but the document is
        for them to open, so it is named for them.  Their first name if
        the people collection knows it, and their id if it does not.

        Parameters
        ----------
        person : str
            The id of the person, or ``unassigned``.

        Returns
        -------
        str
            The file name, without a suffix.
        """
        if person == UNASSIGNED:
            return UNASSIGNED_NAME
        for entry in self.gtx.get("people", []):
            if entry["_id"] == person:
                first = str(entry.get("name", "")).split()[0:1]
                if first:
                    return first[0].lower().replace(" ", "-")
        return person

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["mc_projects"] = list(all_docs_from_collection(rc.client, "mc_projects"))
        gtx["mc_goals"] = list(all_docs_from_collection(rc.client, "mc_goals"))
        gtx["mc_tasks"] = list(all_docs_from_collection(rc.client, "mc_tasks"))
        gtx["people"] = list(all_docs_from_collection(rc.client, "people"))
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def render(self):
        """Write a document for each person, and one for the orphans."""
        self.mcdir.mkdir(parents=True, exist_ok=True)
        for person, lines in sorted(self.documents(self.existing_orders()).items()):
            path = self.mcdir / f"{self.document_name(person)}.md"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def existing_orders(self):
        """Return the id order of each document already in the build
        dir."""
        by_name = {}
        for path in self.mcdir.glob("*.md"):
            by_name[path.stem] = ids_in_document(path.read_text(encoding="utf-8"))
        people = {p.get("lead") or UNASSIGNED for p in self.gtx["mc_projects"]}
        return {person: by_name.get(self.document_name(person), []) for person in people}

    def documents(self, orders=None):
        """Return the lines of every document, keyed by the person it is
        for.

        Returns
        -------
        dict
            The lines of each document, keyed by person id.  A project
            with no lead goes to the unassigned document.
        """
        orders = orders or {}
        by_person = defaultdict(list)
        for project in self.gtx["mc_projects"]:
            by_person[project.get("lead") or UNASSIGNED].append(project)
        return {
            person: self.render_person(person, projects, orders.get(person, []))
            for person, projects in by_person.items()
        }

    def render_person(self, person, projects, order=()):
        """Return the lines of one person's document.

        Parameters
        ----------
        person : str
            The id of the person, or ``unassigned``.
        projects : list of dict
            Their projects.

        Returns
        -------
        list of str
            The lines of the document.
        """
        projects = in_document_order(projects, order, lambda p: p["_id"])
        number_of = {project["_id"]: n for n, project in enumerate(projects, start=1)}
        goals = in_document_order(
            [g for g in self.gtx["mc_goals"] if g["project"] in number_of], order, lambda g: g["_id"]
        )
        goal_number = self.number_goals(goals, number_of)
        tasks = [t for t in self.gtx["mc_tasks"] if t["goal"] in goal_number]

        lines = [f"# Mission control — {self.display_name(person)}", ""]
        lines += self.render_projects(projects)
        lines += self.render_goals(goals, goal_number)
        lines += self.render_weeks(tasks, goal_number, order)
        lines += self.render_bucket("Backburner", goals, goal_number, "backburner")
        lines += self.render_bucket("Wishlist", goals, goal_number, "wishlist")
        lines += self.render_archive(goals, goal_number)
        return lines

    @staticmethod
    def number_goals(goals, number_of):
        """Return the number to print against each goal, e.g. ``1.2``.

        Parameters
        ----------
        goals : list of dict
            The goals to number.
        number_of : dict
            The number of each project, keyed by project id.

        Returns
        -------
        dict
            The number of each goal, keyed by goal id.
        """
        numbers = {}
        counts = defaultdict(int)
        for goal in sorted(goals, key=lambda g: number_of[g["project"]]):
            counts[goal["project"]] += 1
            numbers[goal["_id"]] = f"{number_of[goal['project']]}.{counts[goal['project']]}"
        return numbers

    @staticmethod
    def render_projects(projects):
        """Return the lines of the projects section."""
        lines = ["## Projects", ""]
        for n, project in enumerate(projects, start=1):
            lines.append(f"{n}. **{project['name']}**  ^{project['_id']}")
            if project.get("project_deliverable"):
                lines.append(f"   deliverable: {project['project_deliverable']}")
        lines.append("")
        return lines

    def render_goals(self, goals, goal_number):
        """Return the lines of the goals section, for the current
        period."""
        current = self.current_period(goals)
        if current is None:
            return []
        lines = [f"## Goals — {current}", ""]
        for goal in self.in_order(goals, goal_number):
            if goal["period"] != current or goal["status"] in HELD_STATI:
                continue
            lines.append(
                f"- {goal_number[goal['_id']]}  {struck(goal['text'], goal['status'])}  "
                f"^{goal['_id']}{self.carried(goal)}{self.outcome(goal, current)}"
            )
        lines.append("")
        return lines

    def render_weeks(self, tasks, goal_number, order=()):
        """Return the lines of one section per week that has tasks.

        A task with no parent is one of the week's tasks and the rest
        hang under it, indented, as deep as they were written.  A week
        is chosen by the due date of the task at the top, so a sub task
        stays with the one it belongs to.
        """
        children = defaultdict(list)
        for task in tasks:
            children[task.get("parent")].append(task)
        by_week = defaultdict(list)
        for task in children[None]:
            due = as_date(task.get("due_date"))
            if due is not None:
                by_week[week_of(due)].append(task)
        lines = []
        for monday in sorted(by_week, reverse=True):
            lines += [f"## Week of {monday.isoformat()}", ""]
            counts = defaultdict(int)
            roots = in_document_order(by_week[monday], order, lambda t: t["_id"])
            for task in sorted(roots, key=lambda t: goal_number[t["goal"]]):
                counts[task["goal"]] += 1
                number = f"{goal_number[task['goal']]}.{counts[task['goal']]}"
                lines += self.render_task(task, number, children, order, depth=0)
            lines.append("")
        return lines

    def render_task(self, task, number, children, order, depth):
        """Return the lines of a task and everything under it.

        Parameters
        ----------
        task : dict
            The task to render.
        number : str
            The number to print against it, empty for a sub task.
        children : dict
            The tasks under each task, keyed by parent id.
        order : list of str
            The ids the document carries, in order.
        depth : int
            How far under a top level task it sits.

        Returns
        -------
        list of str
            The lines, indented by depth.
        """
        box = "x" if task["status"] == "finished" else " "
        indent = "  " * depth
        # Only a task of the week is numbered.  A number says which goal and
        # which of its tasks, and a sub task is a breakdown of one of them
        # rather than something anybody points at by number.
        label = f"{number}  " if number else ""
        lines = [f"{indent}- [{box}] {label}{struck(task['text'], task['status'])}  ^{task['_id']}"]
        under = in_document_order(children.get(task["_id"], []), order, lambda t: t["_id"])
        for child in under:
            lines += self.render_task(child, "", children, order, depth + 1)
        return lines

    def render_bucket(self, heading, goals, goal_number, status):
        """Return the lines of the backburner or wishlist section."""
        held = [g for g in self.in_order(goals, goal_number) if g["status"] == status]
        if not held:
            return []
        lines = [f"## {heading}", ""]
        for goal in held:
            lines.append(f"- {goal_number[goal['_id']]}  {struck(goal['text'], goal['status'])}  ^{goal['_id']}")
        lines.append("")
        return lines

    def render_archive(self, goals, goal_number):
        """Return the lines of the archive, one section per past period.

        A goal that has moved on from a period is still shown under it,
        marked with where it went, so the record of what was agreed then
        stays truthful without a second document.
        """
        current = self.current_period(goals)
        periods = sorted({g["first_period"] for g in goals} | {g["period"] for g in goals}, reverse=True)
        past = [p for p in periods if current is None or p < current]
        if not past:
            return []
        lines = ["## Archive", ""]
        for period in past:
            shown = [g for g in self.in_order(goals, goal_number) if g["first_period"] <= period <= g["period"]]
            if not shown:
                continue
            lines += [f"### Goals — {period}", ""]
            for goal in shown:
                lines.append(
                    f"- {goal_number[goal['_id']]}  {self.archived_text(goal, period)}  "
                    f"^{goal['_id']}{self.outcome(goal, period)}"
                )
            lines.append("")
        return lines

    @staticmethod
    def in_order(goals, goal_number):
        """Return the goals in the order their numbers read."""
        return sorted(goals, key=lambda g: [int(n) for n in goal_number[g["_id"]].split(".")])

    @staticmethod
    def current_period(goals):
        """Return the latest period any goal is in, or None."""
        periods = [g["period"] for g in goals]
        return max(periods) if periods else None

    @staticmethod
    def carried(goal):
        """Return a note saying since when a goal has been carried."""
        if goal["first_period"] != goal["period"]:
            return f"  (carried since {goal['first_period']})"
        return ""

    @staticmethod
    def archived_text(goal, period):
        """Return a goal's text as the archive should show it.

        A period is over, so anything that left it is struck through:
        what finished in it, and what rolled out of it, both being done
        with as far as that period is concerned.
        """
        done = goal["status"] == "finished" or goal["period"] != period
        return struck(goal["text"], "finished" if done else goal["status"])

    @staticmethod
    def outcome(goal, period):
        """Return what became of a goal in a period it is shown
        under."""
        if goal["period"] != period:
            return f"  (→ rolled to {goal['period']})"
        if goal["status"] == "finished":
            end = as_date(goal.get("end_date"))
            return f"  (finished {end.isoformat()})" if end else "  (finished)"
        if goal["status"] == "dropped":
            return "  (dropped)"
        return ""
