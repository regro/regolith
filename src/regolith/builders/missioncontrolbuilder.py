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
from regolith.mc import (
    KEEP_FINISHED_DAYS,
    DocumentError,
    in_the_group,
    led_by,
    parse_document,
    period_key,
    period_of,
    retired,
    struck,
    unassigned,
    week_of,
    would_lose,
    wrap,
)
from regolith.tools import all_docs_from_collection, fuzzy_retrieval

UNASSIGNED = "unassigned"
# how many of the things a document would lose to name before saying how many
# more there are
SHOWN_WHEN_REFUSING = 10
UNASSIGNED_NAME = "unassigned"
HELD_STATI = ("on-deck", "wishlist")
ID_IN_DOCUMENT = re.compile(r"\^([\w.-]+)")


def live(records):
    """Return the records a document should still show.

    Deleting a line is how somebody deletes a thing, and the sync marks
    what they deleted ``dropped`` rather than removing it, so that an
    accident can be undone.  The document is what they deleted it from,
    so it is the one place a dropped record does not come back.

    Parameters
    ----------
    records : iterable of dict
        The records to sift.

    Returns
    -------
    list of dict
        The records that are not dropped.
    """
    return [record for record in records if record.get("status") != "dropped"]


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


def one_blank_between(lines):
    """Return the lines with no more than one blank line in a row.

    A section writes a blank line after itself and another before what
    comes next, which used to be hidden by the sections with nothing in
    them not being written at all.

    Parameters
    ----------
    lines : list of str
        The lines of the document.

    Returns
    -------
    list of str
        The lines, with runs of blank lines collapsed into one.
    """
    tidied = []
    for line in lines:
        if line.strip() or (tidied and tidied[-1].strip()):
            tidied.append(line)
    return tidied


def label(item):
    """Return what a record is called, which is how a document names it
    when it carries no id."""
    return item.get("name") or item.get("text")


def keys_in_document(text):
    """Return what a document names, in the order it names them.

    A line carries an id once a render has put one there, but a document
    somebody typed carries none at all, and the order they typed is
    still the order they chose.  So each thing is listed by its id and
    by its text, and a render finds it either way.

    Parameters
    ----------
    text : str
        The document to read.

    Returns
    -------
    list of str
        The ids and the texts, in the order they appear, each once.
    """
    try:
        read = parse_document(text)
    except DocumentError:
        # a document that cannot be read at all still has its ids
        return ids_in_document(text)
    keys = []
    for record in read["projects"] + read["goals"] + read["tasks"]:
        for key in (record["_id"], label(record)):
            if key and key not in keys:
                keys.append(key)
    return keys


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
        What the document names, in order: an id where a line carries
        one and the text of the line where it does not.
    fallback_key : callable
        The sort key for items the document does not mention.

    Returns
    -------
    list of dict
        The items, ordered.
    """
    position = {key: n for n, key in enumerate(order)}

    def where(item):
        """Return where the document put an item, or None for one it
        does not name."""
        found = position.get(item["_id"])
        return position.get(label(item)) if found is None else found

    known = sorted((i for i in items if where(i) is not None), key=where)
    unknown = sorted((i for i in items if where(i) is None), key=fallback_key)
    return known + unknown


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
    # what the periods of the year are called and when they start, which a
    # group says in regolithrc.json.  It decides the period a new goal belongs
    # to and the order the archive reads in.  None is the semesters that
    # mc.DEFAULT_PERIODS gives, and stands for a builder made without a
    # runcontrol, as the sync helper makes one to name documents with.
    periods = None
    # whose documents to write.  None is everybody in the group, which is the
    # point: a group of any age has more people who have left than people in
    # it, and nobody wants to read through the documents of both.
    only_people = None
    build_all = False
    # how long a project stays in the document after it is finished
    keep_finished_days = KEEP_FINISHED_DAYS

    def __init__(self, rc):
        super().__init__(rc)
        self.cmds = ["render"]
        # The documents are edited where people can reach them, which is not
        # the build directory.  rc.mission_control_dir says where; without it
        # they go under the build directory like any other built thing.
        self.mcdir = Path(getattr(rc, "mission_control_dir", None) or self.bldir)
        # what the periods of the year are called and when they start, which a
        # group says in regolithrc.json and which decides both the period a new
        # goal belongs to and the order the archive reads in
        self.periods = getattr(rc, "mission_control_periods", None)
        self.only_people = getattr(rc, "people", None)
        self.build_all = bool(getattr(rc, "build_all", False))
        self.keep_finished_days = getattr(rc, "mission_control_keep_finished_days", KEEP_FINISHED_DAYS)

    @staticmethod
    def owner(person):
        """Return the id a goal of no project carries, or None for the
        unassigned document."""
        return None if person == UNASSIGNED else person

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
        """Write a document for each person, and one for the orphans.

        A render writes the collections out over the document, so a
        document is only written when everything in it is in the
        collections already.  Anything else is work that has not been
        read back yet, and writing over it would be the end of it.
        """
        self.mcdir.mkdir(parents=True, exist_ok=True)
        self.left_out = {}
        wanted = self.whose_documents()
        left_out = 0
        for person, lines in sorted(self.documents(self.existing_orders()).items()):
            if person not in wanted:
                left_out += 1
                continue
            path = self.mcdir / f"{self.document_name(person)}.md"
            written = "\n".join(lines) + "\n"
            if path.is_file():
                existing = path.read_text(encoding="utf-8")
                lost = would_lose(existing, written, self.left_out.get(person, ()))
                if lost:
                    self.refuse(path, lost)
                    continue
                self.keep_a_copy(path, existing)
            path.write_text(written, encoding="utf-8")
        if left_out:
            print(
                f"{left_out} documents were not built, of people who are not in the group. "
                f"Use --all for all of them, or --people to name one."
            )

    def whose_documents(self):
        """Return whose documents this build is for.

        Everybody in the group, and the unassigned document, unless the
        command line said otherwise.  A group of any age has more people
        who have left than people in it, and their documents are answered
        by ``l-mcprojects --orphans`` rather than by reading them.

        Returns
        -------
        set of str
            The ids of the people to write for, and ``unassigned``.
        """
        everybody = set(self.documents_by_person())
        if self.only_people:
            named = {self.person_id(name) for name in self.only_people}
            return {person for person in everybody if person in named}
        if self.build_all:
            return everybody
        return {p for p in everybody if p == UNASSIGNED or in_the_group(p, self.gtx.get("people", []))}

    def documents_by_person(self):
        """Return the projects of each person, keyed by whose they
        are."""
        by_person = defaultdict(list)
        for project in live(self.gtx["mc_projects"]):
            by_person[led_by(project) or UNASSIGNED].append(project)
        return by_person

    def person_id(self, name):
        """Return the id of somebody named by id, by name or by an aka.

        Parameters
        ----------
        name : str
            What the command line called them.

        Returns
        -------
        str
            Their id, or what was given when the people collection does
            not know them.
        """
        found = fuzzy_retrieval(self.gtx.get("people", []), ["_id", "name", "aka"], name, case_sensitive=False)
        return found["_id"] if found else name

    @staticmethod
    def refuse(path, lost):
        """Say why a document was left as it is."""
        print(f"{path.name} was left alone: it says things the collections do not have.")
        for said in lost[:SHOWN_WHEN_REFUSING]:
            print(f"    {said}")
        if len(lost) > SHOWN_WHEN_REFUSING:
            print(f"    ... and {len(lost) - SHOWN_WHEN_REFUSING} more")
        print("Run 'regolith helper mc_sync' to read them in, then build again.")
        print(
            "A line still named after a sync is one the collections cannot hold as "
            "it is: put it under a goal or a project, or take it out."
        )

    def keep_a_copy(self, path, existing):
        """Keep the document as it was before writing over it.

        The copy goes under the build directory rather than beside the
        document, so that it is out of the way of whatever syncs the
        documents themselves.
        """
        previous = Path(self.bldir) / "mission-control-previous"
        previous.mkdir(parents=True, exist_ok=True)
        (previous / path.name).write_text(existing, encoding="utf-8")

    def existing_orders(self):
        """Return what each document already in the build dir names, in
        order."""
        by_name = {}
        for path in self.mcdir.glob("*.md"):
            by_name[path.stem] = keys_in_document(path.read_text(encoding="utf-8"))
        people = {led_by(p) or UNASSIGNED for p in self.gtx["mc_projects"]}
        return {person: by_name.get(self.document_name(person), []) for person in people}

    left_out = {}

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
        by_person = self.documents_by_person()
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
        # a project finished long ago stays in the collections and leaves the
        # document, along with everything under it
        old = (
            [] if self.build_all else [p for p in projects if retired(p, dt.date.today(), self.keep_finished_days)]
        )
        projects = [p for p in projects if p not in old]
        self.left_out[person] = [p.get("name", "") for p in old]
        number_of = {project["_id"]: n for n, project in enumerate(projects, start=1)}
        # a goal of a project belongs to whoever leads the project; a goal of
        # no project says whose it is itself, and is held on deck or on the
        # wishlist until somebody gives it a project
        mine = [
            g
            for g in live(self.gtx["mc_goals"])
            if g["project"] in number_of or (unassigned(g) and g.get("lead") == self.owner(person))
        ]
        goals = in_document_order(mine, order, lambda g: g["_id"])
        goal_number = self.number_goals(goals, number_of)
        tasks = [t for t in live(self.gtx["mc_tasks"]) if t["goal"] in goal_number]
        self.left_out[person] = self.not_written(person, {p["_id"] for p in projects}, goal_number, tasks)

        lines = [f"# Mission control — {self.display_name(person)}", ""]
        lines += self.render_projects(projects)
        lines += self.render_goals(goals, goal_number)
        lines += self.render_weeks(tasks, goal_number, order)
        lines += self.render_bucket("On-deck", goals, goal_number, "on-deck")
        lines += self.render_bucket("Wishlist", goals, goal_number, "wishlist")
        lines += self.render_archive(goals, goal_number)
        return [written for line in one_blank_between(lines) for written in wrap(line)]

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
        # a goal of no project has no number: the number says which project it
        # is of, and that is the thing nobody has decided yet.  Nor does a
        # piece of another goal, which is of whatever its goal is
        of_a_project = [goal for goal in goals if goal["project"] in number_of and not goal.get("parent")]
        for goal in sorted(of_a_project, key=lambda g: number_of[g["project"]]):
            counts[goal["project"]] += 1
            numbers[goal["_id"]] = f"{number_of[goal['project']]}.{counts[goal['project']]}"
        return numbers

    @staticmethod
    def render_projects(projects):
        """Return the lines of the projects section.

        What is written under a project is separated by blank lines.
        Markdown reads lines that run together as one paragraph, which
        would show a project as a single block of text wherever the
        document is read as markdown rather than as a file.
        """
        lines = ["## Projects", ""]
        for n, project in enumerate(projects, start=1):
            lines.append(f"{n}. **{project['name']}**  ^{project['_id']}")
            if project.get("project_deliverable"):
                lines += ["", f"   deliverable: {project['project_deliverable']}"]
            if project.get("collaborators"):
                lines += ["", f"   with: {', '.join(project['collaborators'])}"]
            if project.get("project_description"):
                lines += ["", f"   {project['project_description']}"]
            lines.append("")
        return lines

    def render_goals(self, goals, goal_number):
        """Return the lines of the goals section, for the current
        period."""
        current = self.current_period(goals)
        lines = [f"## Goals — {current}", ""]
        for goal in self.in_order(goals, goal_number):
            if goal["period"] != current or goal["status"] in HELD_STATI:
                continue
            if goal["_id"] not in goal_number:
                # of no project, so it belongs in a holding section rather
                # than among the goals of the period
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
        shown = {task["_id"] for task in tasks}
        children = defaultdict(list)
        for task in tasks:
            # a sub task whose task has gone is shown in its own right, rather
            # than hanging off something that is no longer there
            parent = task.get("parent")
            children[parent if parent in shown else None].append(task)
        by_week = defaultdict(list)
        for task in children[None]:
            due = as_date(task.get("due_date"))
            if due is not None:
                by_week[week_of(due)].append(task)
        lines = []
        by_week.setdefault(week_of(dt.date.today()), [])
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
        """Return the lines of the on-deck or wishlist section.

        The heading is written whether or not there is anything under
        it, so that a document has somewhere to move a goal to.
        """
        ordered = self.in_order(goals, goal_number)
        held = [g for g in ordered if g["status"] == status]
        # a piece of a held goal is written under it whatever it says itself:
        # ticking one off does not take it out of the list it is a piece of
        theirs = {g["_id"] for g in held}
        for goal in ordered:
            parent = goal.get("parent")
            while parent and parent not in theirs and parent in {g["_id"] for g in ordered}:
                parent = next((g.get("parent") for g in ordered if g["_id"] == parent), None)
            if parent in theirs and goal["_id"] not in theirs:
                held.append(goal)
                theirs.add(goal["_id"])
        held = [g for g in ordered if g["_id"] in theirs]
        under = defaultdict(list)
        for goal in held:
            under[goal.get("parent")].append(goal)
        shown = {goal["_id"] for goal in held}
        lines = [f"## {heading}", ""]
        for goal in held:
            # a piece of a goal is written under it rather than in its own
            # right, and one whose goal has gone is written in its own right
            # rather than not at all
            if goal.get("parent") in shown:
                continue
            lines += self.render_held(goal, goal_number, under, depth=0)
        lines.append("")
        return lines

    def render_held(self, goal, goal_number, under, depth):
        """Return the lines of a held goal and the breakdown under it.

        Parameters
        ----------
        goal : dict
            The goal to write.
        goal_number : dict
            The number of each goal that has one, keyed by id.
        under : dict
            The goals under each goal, keyed by parent id.
        depth : int
            How far under a goal of its own it sits.

        Returns
        -------
        list of str
            The lines, indented by depth.
        """
        # only a goal of its own is numbered: the number says which project it
        # is of, and a piece of a goal is of whatever its goal is
        number = f"{goal_number[goal['_id']]}  " if not depth and goal["_id"] in goal_number else ""
        indent = "  " * depth
        box = "[x] " if goal["status"] == "finished" and depth else "[ ] " if depth else ""
        lines = [f"{indent}- {box}{number}{struck(goal['text'], goal['status'])}  ^{goal['_id']}"]
        for piece in under.get(goal["_id"], []):
            lines += self.render_held(piece, goal_number, under, depth + 1)
        return lines

    def render_archive(self, goals, goal_number):
        """Return the lines of the archive, one section per past period.

        A goal that has moved on from a period is still shown under it,
        marked with where it went, so the record of what was agreed then
        stays truthful without a second document.
        """
        current = self.current_period(goals)
        seen = {g["first_period"] for g in goals} | {g["period"] for g in goals}
        periods = sorted(seen, key=self.period_key, reverse=True)
        past = [p for p in periods if self.period_key(p) < self.period_key(current)]
        lines = ["## Archive", ""]
        for period in past:
            shown = [
                g
                for g in self.in_order(goals, goal_number)
                if g["_id"] in goal_number
                and self.period_key(g["first_period"]) <= self.period_key(period) <= self.period_key(g["period"])
            ]
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
        """Return the goals in the order their numbers read.

        A goal with no number is of no project yet, and goes after the
        ones that are, in the order the document already had them.
        """
        numbered = [g for g in goals if g["_id"] in goal_number]
        unnumbered = [g for g in goals if g["_id"] not in goal_number]
        in_number_order = sorted(numbered, key=lambda g: [int(n) for n in goal_number[g["_id"]].split(".")])
        return in_number_order + unnumbered

    def not_written(self, person, shown, goal_number, tasks):
        """Return what the collections hold for somebody and the
        document does not say.

        A document is not written with everything: a project finished
        long ago is left out, and so is anything dropped.  None of it is
        lost, because the collections still hold it, so a document that
        still names it is not a document holding the only copy.

        Parameters
        ----------
        person : str
            The id of the person, or ``unassigned``.
        shown : set of str
            The ids of the projects the document is written with.
        goal_number : dict
            The goals the document is written with, keyed by id.
        tasks : list of dict
            The tasks the document is written with.

        Returns
        -------
        list of str
            What each of them says, for a render to account for.
        """
        owner = self.owner(person)
        mine = [p for p in self.gtx["mc_projects"] if (led_by(p) or UNASSIGNED) == (owner or UNASSIGNED)]
        theirs = {p["_id"] for p in mine}
        goals = [
            g
            for g in self.gtx["mc_goals"]
            if g.get("project") in theirs or (unassigned(g) and g.get("lead") == owner)
        ]
        written = {t["_id"] for t in tasks}
        return (
            [p.get("name", "") for p in mine if p["_id"] not in shown]
            + [g.get("text", "") for g in goals if g["_id"] not in goal_number]
            + [
                t.get("text", "")
                for t in self.gtx["mc_tasks"]
                if t.get("goal") in {g["_id"] for g in goals} and t["_id"] not in written
            ]
        )

    def period_key(self, period):
        """Return a key putting periods in the order they came round."""
        return period_key(period, self.periods)

    def current_period(self, goals):
        """Return the latest period any goal is in.

        A person with no goals yet is in the period everybody else is,
        so that their document has a goals section to type into.  The
        names of the periods do not sort into the order they happen, so
        the latest is found by when it came round rather than by its
        text.
        """
        periods = [g["period"] for g in goals]
        return max(periods, key=self.period_key) if periods else period_of(dt.date.today(), self.periods)

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
        return ""
