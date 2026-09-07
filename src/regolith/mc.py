"""Pieces shared by the mission control tools.

Kept apart from ``regolith.tools`` so that reading or writing a mission
control document does not import the rest of it.
"""

import datetime as dt
import re
import secrets
import textwrap

# Lowercase base32 without the characters that are read for one another, so
# an id can be said aloud in a meeting and typed back correctly
# No underscore: ids are written with hyphens.  The patterns below still read
# one, so a document written before that stays readable.
ID_ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"
ID_LENGTH = 6


def short_id(taken=(), length=ID_LENGTH):
    """Return a short id that nothing has taken yet.

    The id appears beside every line of a mission control document, so it
    is as short as it can be while staying unique.  Six characters of this
    alphabet is about nine hundred million ids, and clashes are not left
    to chance: an id already taken is thrown away and another drawn.

    Parameters
    ----------
    taken : iterable of str, optional
        The ids already in use.
    length : int, optional
        How many characters to draw.  The default is six.

    Returns
    -------
    str
        The new id.
    """
    taken = set(taken)
    while True:
        candidate = "".join(secrets.choice(ID_ALPHABET) for _ in range(length))
        if candidate not in taken:
            return candidate


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


# When the periods of the year begin, for a group that has not said.  Most
# universities are on semesters, so those are the default; a group on quarters,
# or on nothing much, says so in regolithrc.json under mission_control_periods,
# as {name: MM-DD} saying what each period is called and the day it starts.
DEFAULT_PERIODS = {"spring": "01-01", "summer": "06-01", "fall": "09-01"}


def period_starts(periods=None):
    """Return when each period of the year starts, earliest first.

    Parameters
    ----------
    periods : dict, optional
        The periods as ``{name: "MM-DD"}``.  The default is semesters.

    Returns
    -------
    list of tuple of (int, int, str)
        The month, the day and the name of each, in the order they come
        round.

    Raises
    ------
    DocumentError
        When a start is not written as MM-DD, naming the one that is not.
    """
    starts = []
    for name, start in (periods or DEFAULT_PERIODS).items():
        try:
            month, day = (int(part) for part in str(start).split("-"))
            dt.date(2000, month, day)
        except (TypeError, ValueError):
            raise DocumentError(
                f"The period {name} starts on {start!r}, which is not a date of the "
                f"year. Please write it as MM-DD, such as 09-01, in "
                f"mission_control_periods in regolithrc.json."
            )
        starts.append((month, day, str(name)))
    return sorted(starts)


def period_of(date, periods=None):
    """Return the period a date falls in, as the documents write one.

    The year goes in front of the name, so a period reads as the whole
    of when it was: ``2026fall``.

    Parameters
    ----------
    date : datetime.date
        The date to place.
    periods : dict, optional
        The periods as ``{name: "MM-DD"}``.  The default is semesters.

    Returns
    -------
    str
        The period, e.g. ``2026fall``.
    """
    starts = period_starts(periods)
    begun = [(month, day, name) for month, day, name in starts if (month, day) <= (date.month, date.day)]
    if begun:
        return f"{date.year}{begun[-1][2]}"
    # the year has not reached its first period yet, so we are still in the
    # last one of the year before
    return f"{date.year - 1}{starts[-1][2]}"


def next_period(date, periods=None):
    """Return the period after the one a date falls in.

    Preparing for the period to come is ordinary work, and it happens
    while the one before it is still running.

    Parameters
    ----------
    date : datetime.date
        The date to start from.
    periods : dict, optional
        The periods as ``{name: "MM-DD"}``.  The default is semesters.

    Returns
    -------
    str
        The period after this one.
    """
    starts = period_starts(periods)
    year, name = split_period(period_of(date, periods), periods)
    nth = [start[2] for start in starts].index(name) + 1
    if nth == len(starts):
        return f"{int(year) + 1}{starts[0][2]}"
    return f"{year}{starts[nth][2]}"


def split_period(period, periods=None):
    """Return a period as its year and its name.

    Parameters
    ----------
    period : str
        The period, e.g. ``2026fall``.
    periods : dict, optional
        The periods as ``{name: "MM-DD"}``.  The default is semesters.

    Returns
    -------
    tuple of (str, str) or None
        The year and the name, or None for a period written some other
        way.
    """
    for _, _, name in period_starts(periods):
        if period.endswith(name) and period[: -len(name)]:
            return period[: -len(name)], name
    return None


def period_key(period, periods=None):
    """Return a key that puts periods in the order they came round.

    The names of the periods do not sort into the order they happen --
    fall comes before spring in the alphabet and after it in the year --
    so anything ordering periods sorts on this rather than on the text.

    Parameters
    ----------
    period : str
        The period, e.g. ``2026fall``.
    periods : dict, optional
        The periods as ``{name: "MM-DD"}``.  The default is semesters.

    Returns
    -------
    tuple of (str, int)
        The year, and where in the year the period comes.  A period
        written some other way sorts after the ones of its own text.
    """
    starts = period_starts(periods)
    split = split_period(period, periods)
    if split is None:
        return (period, len(starts))
    year, name = split
    return (year, [start[2] for start in starts].index(name))


def slug(text):
    """Return a name as an id someone would be willing to type.

    Parameters
    ----------
    text : str
        The name of the project.

    Returns
    -------
    str
        The name in lower case with anything but letters, numbers and
        hyphens replaced by a hyphen.
    """
    # an underscore becomes a hyphen along with everything else that is not a
    # letter or a number: underscores in ids are being retired
    kept = [c if (c.isalnum() or c == "-") else "-" for c in text.lower()]
    return "-".join(part for part in "".join(kept).split("-") if part)


UNLED_PREFIX = "na"


def initials(name):
    """Return the initials a project of somebody's is named with.

    Parameters
    ----------
    name : str
        The name of the person, as the people collection has it.

    Returns
    -------
    str
        The first letter of their first name and of their last, in lower
        case, which is how the group has always shortened a name.  A
        middle name is passed over, so that Simon J. L. Billinge is sb
        rather than sjlb.
    """
    parts = name.split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0][0].lower()
    return f"{parts[0][0]}{parts[-1][0]}".lower()


def project_id(name, taken=(), prefix=None):
    """Return the id to give a project somebody has just named.

    A project id is the one id here that a person reads and types: it
    names the project in a lister, in a grant, and in whatever refers to
    it later.  So it is made from the name rather than drawn at random,
    the way the adder helper makes one, and a name that two projects
    share is numbered rather than made unreadable.

    Whose project it is comes first, as the initials of the person
    leading it.  Group members name their projects alike -- there is a
    software maintenance in most of them -- so without that the second
    one to be written down would be the first one numbered, and neither
    id would say whose it was.

    Parameters
    ----------
    name : str
        The name of the project.
    taken : iterable of str, optional
        The ids already in use.
    prefix : str, optional
        What to put in front, which is the initials of whoever leads it,
        or ``na`` for a project nobody leads.

    Returns
    -------
    str
        The id, or a short one when the name makes no id at all.
    """
    taken = set(taken)
    stem = slug(name)
    if stem and prefix:
        stem = f"{slug(prefix)}-{stem}"
    if not stem:
        return short_id(taken)
    if stem not in taken:
        return stem
    nth = 2
    while f"{stem}-{nth}" in taken:
        nth += 1
    return f"{stem}-{nth}"


def struck(text, status):
    """Return the text struck through when the thing is finished.

    Striking a line through is how the group has always marked something
    off, so a rendered document does it too, and reading one back takes a
    struck line as finished whether or not its box was ticked.

    Parameters
    ----------
    text : str
        The text of the goal or task.
    status : str
        Its status.

    Returns
    -------
    str
        The text, struck through when it is finished.
    """
    return f"~~{text}~~" if status == "finished" else text


class DocumentError(ValueError):
    """Raised when a mission control document cannot be read.

    Carries the line it gave up on, so a person can be told where to
    look rather than that their file is bad.
    """


HEADING = re.compile(r"^(#+)\s+(.*?)\s*$")
PROJECT_LINE = re.compile(r"^(\d+)\.\s+\*\*(?P<text>.*?)\*\*\s*(?:\^(?P<id>[\w.-]+))?\s*$")
DELIVERABLE_LINE = re.compile(r"^\s+deliverable:\s*(?P<text>.*?)\s*$")
WITH_LINE = re.compile(r"^\s+with:\s*(?P<people>.*?)\s*$")
DESCRIPTION_LINE = re.compile(r"^\s+description:\s*(?P<text>.*?)\s*$")
# anything else written under a project is what the project is about
PROSE_LINE = re.compile(r"^\s+(?P<text>\S.*?)\s*$")
GOAL_LINE = re.compile(
    r"^-\s+(?P<number>[\d.]+)?\s*(?P<text>.*?)\s*(?:\^(?P<id>[\w.-]+))?\s*(?:\((?P<note>.*)\))?\s*$"
)
TASK_LINE = re.compile(
    r"^(?P<indent>\s*)-\s+\[(?P<box>[ xX])\]\s+(?P<number>[\d.]+)?\s*"
    r"(?P<text>.*?)\s*(?:\^(?P<id>[\w.-]+))?\s*$"
)
STRUCK = re.compile(r"^~~(?P<text>.*)~~$")
# what starts something rather than carrying on the line above: a heading, a
# bullet, a task box or a numbered project
MARKER = re.compile(r"^\s*(?:#+\s+|-\s+(?:\[[ xX]\]\s+)?|\d+\.\s+)")
WIDTH = 79
GOALS_HEADING = re.compile(r"^Goals\s+—\s+(?P<period>\S+)$")
# what a section holding a goal back is called.  Backburner is what the
# heading used to say, and is still read so that a document written before the
# rename keeps working.
HELD_HEADINGS = {"on-deck": "on-deck", "backburner": "on-deck", "wishlist": "wishlist"}
# what a goal says instead of a project when it is not of one yet
UNASSIGNED_PROJECT = "tbd"
WEEK_HEADING = re.compile(r"^Week of\s+(?P<monday>\d{4}-\d{2}-\d{2})$")


def read_text(raw):
    """Return the text of a line and what its marks say about its
    status.

    A finished line is struck through, and a task is also ticked.  When
    the two disagree the strike is believed: the box is what gets
    forgotten.

    Parameters
    ----------
    raw : str
        The text as written, possibly struck through.

    Returns
    -------
    tuple of (str, bool)
        The text without its marks, and whether it is struck.
    """
    struck_out = STRUCK.match(raw)
    return (struck_out.group("text").strip(), True) if struck_out else (raw.strip(), False)


def indent_of(line):
    """Return how far a line is indented, counting a tab as four."""
    return len(line[: len(line) - len(line.lstrip())].expandtabs(4))


def wrap(line, width=WIDTH):
    """Return a rendered line broken to fit a plain text editor.

    A goal or a task can run to a paragraph, and a document is read in an
    editor that does not fold, where finding the end of a long line is a
    chore.  So a written line is broken, and what carries on from it is
    indented two further than the line it belongs to: enough for
    ``join_wrapped`` to know it for a continuation, and few enough that
    markdown still reads it as the same paragraph rather than as a code
    block.

    A heading and the line naming a project are left alone.  Neither can
    be joined back up, the first because it must stay one line to be a
    heading and the second because the indented lines under a project are
    what the project is about.

    Parameters
    ----------
    line : str
        The line as rendered.
    width : int, optional
        The longest line to write.  The default is 79.

    Returns
    -------
    list of str
        The line, broken into as many as it needs.
    """
    if len(line) <= width or HEADING.match(line) or PROJECT_LINE.match(line):
        return [line]
    return textwrap.wrap(
        line,
        width=width,
        subsequent_indent=" " * (indent_of(line) + 2),
        break_long_words=False,
        break_on_hyphens=False,
    ) or [line]


def logical_lines(text):
    """Return the document's lines with every broken one joined back up.

    A line that is indented further than the line above it and does not
    start something of its own is the rest of that line.  That is the
    shape ``wrap`` writes, and it is also what somebody typing a
    paragraph under a task does by hand, so both read the same way.

    A line under the line naming a project is left alone, since that is
    the project's description and not the rest of its name.

    Parameters
    ----------
    text : str
        The document as written.

    Returns
    -------
    list of tuple of (int, str)
        One line per thing the document says, each with the line of the
        file it started on, so that an error names a line the writer can
        find.
    """
    joined = []
    for number, line in enumerate(text.splitlines(), start=1):
        carries_on = (
            joined
            and line.strip()
            and joined[-1][1].strip()
            and not MARKER.match(line)
            and indent_of(line) > indent_of(joined[-1][1])
            and not PROJECT_LINE.match(joined[-1][1])
        )
        if carries_on:
            joined[-1] = (joined[-1][0], f"{joined[-1][1].rstrip()} {line.strip()}")
        else:
            joined.append((number, line))
    return joined


HEADING_LINE = re.compile(r"^\s*#+\s")
# what a render may add to or take off a line without the line having changed
LEADING = re.compile(r"^\s*(?:[-*]\s+(?:\[[ xX]\]\s+)?)?(?:\d+(?:\.\d+)*\.?\s+)?")
NOTE = re.compile(r"\((?:carried since|finished|dropped|→ rolled to)[^)]*\)")
MARKS = re.compile(r"\^[\w.-]+|~~|\*\*")


def said_in(line):
    """Return what a line says, without the marks a render may change.

    The number in front of a goal is positional, the id after it is
    written by the render, and the note at the end says what became of
    it.  None of them is what somebody typed, so none of them counts
    when asking whether a line is still there.

    Parameters
    ----------
    line : str
        The line, as the document has it.

    Returns
    -------
    str
        What it says.
    """
    text = NOTE.sub("", LEADING.sub("", line.strip(), count=1))
    return " ".join(MARKS.sub("", text).split())


def would_lose(existing, written, also_kept=()):
    """Return what a document says that a new one would not.

    A render writes the collections out over the document, so anything
    in the document that never reached the collections is gone.  That is
    every line typed since the last sync, and every line a sync could
    not store: a goal under no project, a task under no goal, a note
    somebody left in the margin.

    Headings are not compared.  They are the shape of the document
    rather than anything somebody typed, and a week with nothing left in
    it is meant to go.

    Parameters
    ----------
    existing : str
        The document as it stands.
    written : str
        The document as the render would write it.
    also_kept : iterable of str, optional
        What the render left out on purpose, which the collections still
        hold and so is not lost.  A project finished years ago is left
        out this way.

    Returns
    -------
    list of str
        What the document says and the render does not, in the order it
        says it.  Empty when nothing would be lost.
    """
    kept = {said_in(line) for _, line in logical_lines(written) if not HEADING_LINE.match(line)}
    kept |= {said_in(text) for text in also_kept}
    lost = []
    for _, line in logical_lines(existing):
        if not line.strip() or HEADING_LINE.match(line):
            continue
        said = said_in(line)
        if said and said not in kept and said not in lost:
            lost.append(said)
    return lost


def parse_document(text, taken=(), prefix=None):
    """Return the projects, goals and tasks a mission control document
    describes.

    The document is what people type into, so it is read forgivingly: a
    line that is not one of the shapes below is left alone rather than
    treated as an error.  What it does insist on is that the shapes it
    does recognise make sense, since a task under no goal, or a goal
    under no project, cannot be stored.

    A line with no ``^id`` is something somebody typed, and is given one.
    Ids are the only thing here that is not the person's to write, so
    they are minted rather than demanded.  A project is given an id made
    from its name, since that is the one id anybody reads or types; a
    goal or a task is given a short one.

    Parameters
    ----------
    text : str
        The document.
    taken : iterable of str, optional
        Ids in use elsewhere, so a newly minted one does not collide with
        another person's document.
    prefix : str, optional
        What to put in front of the id of a project typed in here, which
        is the initials of whoever the document belongs to.

    Returns
    -------
    dict
        ``person``, and ``projects``, ``goals`` and ``tasks`` as lists of
        records in the order the document put them, plus ``mentioned``,
        the ids the document showed without saying anything to store.

    Raises
    ------
    DocumentError
        When a recognised line cannot be placed, naming the line.
    """
    ids = set(taken) | set(re.findall(r"\^([\w.-]+)", text))
    state = _Reader(ids, prefix)
    for number, line in logical_lines(text):
        state.read(line, number)
    return state.result()


class _Reader:
    """Reads a document a line at a time, holding where it has got
    to."""

    def __init__(self, ids, prefix=None):
        self.ids = set(ids)
        self.prefix = prefix
        self.person = None
        self.projects = []
        self.goals = []
        self.tasks = []
        self.section = None
        self.period = None
        self.monday = None
        self.by_number = {}
        self.stack = []
        self.mentioned = []

    def mint(self):
        _id = short_id(self.ids)
        self.ids.add(_id)
        return _id

    def mint_project(self, name):
        """Return an id made from a project's name, as the adder makes
        one."""
        _id = project_id(name, self.ids, self.prefix)
        self.ids.add(_id)
        return _id

    def read(self, line, number):
        """Take one line of the document."""
        heading = HEADING.match(line)
        if heading:
            self.enter(heading.group(1), heading.group(2))
            return
        if not line.strip():
            return
        if self.section == "projects" and self.project(line):
            return
        if self.section in ("goals", "on-deck", "wishlist", "archive") and self.goal(line, number):
            return
        if self.section == "week" and self.task(line, number):
            return

    def enter(self, hashes, title):
        """Note which section of the document we have reached."""
        if len(hashes) == 1:
            self.person = title.split("—")[-1].strip()
            return
        self.stack = []
        goals = GOALS_HEADING.match(title)
        week = WEEK_HEADING.match(title)
        if title == "Projects":
            self.section = "projects"
        elif goals:
            # a goals heading inside the archive is a period that has passed
            self.section = "archive" if self.section == "archive" else "goals"
            self.period = goals.group("period")
        elif week:
            self.section = "week"
            self.monday = dt.date.fromisoformat(week.group("monday"))
        elif title.lower() in HELD_HEADINGS:
            self.section = HELD_HEADINGS[title.lower()]
        elif title == "Archive":
            self.section = "archive"
        else:
            self.section = None

    def project(self, line):
        """Read a line of the projects section."""
        deliverable = DELIVERABLE_LINE.match(line)
        if deliverable and self.projects:
            self.projects[-1]["project_deliverable"] = deliverable.group("text")
            return True
        with_line = WITH_LINE.match(line)
        if with_line and self.projects:
            people = [who.strip() for who in with_line.group("people").split(",")]
            self.projects[-1]["collaborators"] = [who for who in people if who]
            return True
        described = DESCRIPTION_LINE.match(line)
        if described and self.projects:
            self.describe(described.group("text"))
            return True
        found = PROJECT_LINE.match(line)
        if not found:
            # prose under a project is what the project is about, whether or
            # not anybody wrote "description:" in front of it
            prose = PROSE_LINE.match(line)
            if prose and self.projects:
                self.describe(prose.group("text"))
                return True
            return False
        text, struck_out = read_text(found.group("text"))
        project = {
            "_id": found.group("id") or self.mint_project(text),
            "name": text,
            "status": "finished" if struck_out else "active",
        }
        self.projects.append(project)
        self.by_number[found.group(1)] = project["_id"]
        return True

    def describe(self, text):
        """Add a line of prose to what the last project is about.

        Somebody writing a paragraph will wrap it over several lines, so
        they are joined rather than the last one winning.
        """
        project = self.projects[-1]
        described = project.get("project_description")
        project["project_description"] = f"{described} {text}".strip() if described else text

    def goal(self, line, number):
        """Read a line of a goals, on-deck, wishlist or archive
        section."""
        found = GOAL_LINE.match(line)
        if not found or found.group("text") is None:
            return False
        text, struck_out = read_text(found.group("text"))
        if not text:
            return False
        goal_number = found.group("number")
        if goal_number is None:
            if self.section not in HELD:
                raise DocumentError(f"line {number}: a goal needs a number saying which project it is of")
            # a thing held on deck or on the wishlist is an idea that has not
            # been made anybody's work yet, so it does not have to say which
            # project it is of.  It says so when somebody gives it a number
            project = UNASSIGNED_PROJECT
        else:
            project_number = goal_number.split(".")[0]
            if project_number not in self.by_number:
                raise DocumentError(f"line {number}: there is no project {project_number}")
            project = self.by_number[project_number]
        # the archive says what a period was; the current sections say what is
        _id = found.group("id") or self.mint()
        if self.section == "archive":
            # nothing in the archive is written back, but a line that is there
            # is a line nobody deleted, so it must not read as one
            self.mentioned.append(_id)
            return True
        goal = {
            "_id": _id,
            "project": project,
            "period": self.period,
            "text": text,
            "status": self.goal_status(struck_out),
        }
        self.goals.append(goal)
        if goal_number is not None:
            self.by_number[goal_number] = _id
        return True

    def goal_status(self, struck_out):
        """Return the status a goal's section and marks give it."""
        if struck_out:
            return "finished"
        return self.section if self.section in HELD else "active"

    def task(self, line, number):
        """Read a line of a week section."""
        found = TASK_LINE.match(line)
        if not found:
            return False
        text, struck_out = read_text(found.group("text"))
        # any indent at all puts a task under the one above it.  People do not
        # count spaces, so what matters is deeper or not, never how much
        indent = len(found.group("indent").expandtabs(4))
        ticked = found.group("box").lower() == "x"
        task = {
            "_id": found.group("id") or self.mint(),
            # a strike is believed over a box, since the box is what gets forgotten
            "status": "finished" if (struck_out or ticked) else "active",
            "text": text,
            "due_date": self.monday,
        }
        while self.stack and self.stack[-1][0] >= indent:
            self.stack.pop()
        if self.stack:
            parent = self.stack[-1][1]
            task["parent"] = parent["_id"]
            task["goal"] = parent["goal"]
        else:
            task_number = found.group("number")
            if task_number is None:
                raise DocumentError(
                    f"line {number}: this task is not under another one, so it needs a "
                    f"number saying which goal it belongs to, such as 1.1.1"
                )
            goal_number = ".".join(task_number.split(".")[:-1])
            if goal_number not in self.by_number:
                raise DocumentError(f"line {number}: there is no goal {goal_number}")
            task["goal"] = self.by_number[goal_number]
        self.stack.append((indent, task))
        self.tasks.append(task)
        return True

    def result(self):
        """Return what was read."""
        return {
            "person": self.person,
            "projects": self.projects,
            "goals": self.goals,
            "tasks": self.tasks,
            "mentioned": self.mentioned,
        }


HELD = ("on-deck", "wishlist")
OPEN = ("proposed", "active")


def settled_status(read_status, existing_status, default="active"):
    """Return the status a record should have after its document was
    read.

    A document does not say everything a status does.  Everything in the
    goals section reads back as ``active``, so a goal that was
    ``proposed`` would lose that on the first read for no reason anybody
    intended.  What a document does say is when something is finished,
    when it is held on deck or on the wishlist, and when it has
    come back from either.

    Parameters
    ----------
    read_status : str
        What the document said.
    existing_status : str or None
        What the record said, or None for something newly typed.
    default : str, optional
        The status for something newly typed that the document does not
        pin down.  The default is ``active``.

    Returns
    -------
    str
        The status to store.
    """
    if read_status in ("finished",) + HELD:
        return read_status
    if existing_status is None:
        return default
    # it is in the ordinary sections, so it is not held and not finished
    return existing_status if existing_status in OPEN else "active"


def adopt(read, existing, claimed):
    """Return the record a read line belongs to, matching on text if
    need be.

    The likeliest damage to a document is a lost id: a paste, an
    autocorrect, somebody retyping a line.  Left alone that would store a
    second copy of something that is already there and drop the first.
    So a line whose id is not known is offered to a record with the same
    text that nothing else has claimed.

    Parameters
    ----------
    read : dict
        The line as read, carrying an id the parser may have just minted.
    existing : dict
        The records already stored, keyed by id.
    claimed : set
        The ids already taken by other lines of this document.

    Returns
    -------
    dict
        The record it belongs to, empty for something genuinely new.
    """
    if read["_id"] in existing:
        return existing[read["_id"]]
    for _id, record in existing.items():
        same = record.get("text") == read.get("text") and record.get("name") == read.get("name")
        if _id not in claimed and same:
            read["_id"] = _id
            return record
    return {}


def changes(parsed, person, existing, today=None):
    """Return the records a document says to write, and the ids to drop.

    Nothing is deleted.  A line somebody removed sets the record's status
    to ``dropped``, so a document wrecked by accident costs nothing that
    a render cannot put back.

    Parameters
    ----------
    parsed : dict
        What ``parse_document`` read.
    person : str or None
        The id of the person whose document it is, which is what makes
        them the lead of the projects in it, and what makes a project
        newly typed into it active rather than proposed.  None for the
        unassigned document.
    existing : dict
        The records already stored for that person, as
        ``{collection: {id: record}}``.
    today : datetime.date, optional
        The date to close things on.  The default is today.

    Returns
    -------
    tuple of (dict, dict)
        The records to write and the ids to drop, both as
        ``{collection: [...]}``.
    """
    today = today or dt.date.today()
    writes = {"mc_projects": [], "mc_goals": [], "mc_tasks": []}
    seen = {"mc_projects": set(), "mc_goals": set(), "mc_tasks": set()}
    # what a line was given while reading, against what it turned out to be.
    # A goal says which project it is of by the id the reader gave that
    # project, so when the project turns out to be one already stored, every
    # reference to it has to follow it
    adopted = {}

    for read in parsed["projects"]:
        given = read["_id"]
        was = adopt(read, existing["mc_projects"], seen["mc_projects"])
        if read["_id"] != given:
            adopted[given] = read["_id"]
        record = dict(was)
        record.update({k: v for k, v in read.items() if k != "status"})
        # a project written into somebody's document is one that somebody is
        # doing.  One in the unassigned document is one nobody has picked up
        # yet, which is what the adder helper makes as well
        record["status"] = settled_status(
            read["status"], was.get("status"), default="active" if person else "proposed"
        )
        record["lead"] = person if person else None
        if record["lead"] is None:
            record.pop("lead", None)
        record.setdefault("begin_date", today)
        _close(record, was, today)
        writes["mc_projects"].append(record)
        seen["mc_projects"].add(record["_id"])

    for read in parsed["goals"]:
        given = read["_id"]
        read["project"] = adopted.get(read["project"], read["project"])
        was = adopt(read, existing["mc_goals"], seen["mc_goals"])
        if read["_id"] != given:
            adopted[given] = read["_id"]
        record = dict(was)
        record.update({k: v for k, v in read.items() if k != "status"})
        record["status"] = settled_status(read["status"], was.get("status"))
        # written once, so how long a goal has been carried is knowable
        record.setdefault("first_period", read["period"])
        # a goal of no project has no project to say whose it is, so it says
        # so itself: it belongs to whoever's document it was written in
        if unassigned(record):
            record["lead"] = person
            if person is None:
                record.pop("lead", None)
        else:
            record.pop("lead", None)
        _close(record, was, today)
        writes["mc_goals"].append(record)
        seen["mc_goals"].add(record["_id"])

    for read in parsed["tasks"]:
        given = read["_id"]
        read["goal"] = adopted.get(read["goal"], read["goal"])
        if read.get("parent"):
            read["parent"] = adopted.get(read["parent"], read["parent"])
        was = adopt(read, existing["mc_tasks"], seen["mc_tasks"])
        if read["_id"] != given:
            adopted[given] = read["_id"]
        record = dict(was)
        record.update({k: v for k, v in read.items() if k != "status"})
        record["status"] = settled_status(read["status"], was.get("status"))
        record.setdefault("first_due_date", read["due_date"])
        _close(record, was, today)
        writes["mc_tasks"].append(record)
        seen["mc_tasks"].add(record["_id"])

    # the archive shows a goal without saying anything to store about it, so
    # what it shows is neither written nor taken for deleted
    seen["mc_goals"].update(parsed.get("mentioned", ()))
    drops = {collection: sorted(set(records) - seen[collection]) for collection, records in existing.items()}
    return writes, drops


def _close(record, was, today):
    """Date a record that has just been finished, and only just."""
    if record["status"] == "finished" and was.get("status") != "finished":
        record.setdefault("end_date", today)


# what a lead is called when nobody is leading it.  Old projecta wrote "na" or
# "tbd" by default; a mission control project simply has no lead
NOBODY = ("", "na", "tbd", "none")
# a project in one of these is done with, so it cannot be an orphan
CLOSED = ("finished", "dropped")


# how long a finished project stays in the document, when nothing says
KEEP_FINISHED_DAYS = 365


def retired(project, today, days=KEEP_FINISHED_DAYS):
    """Return True if a project finished long enough ago to leave the
    document.

    Seeing what has just been finished is worth the room it takes; a
    project finished years ago is not, and a person who has been in the
    group a while has many.  It stays in the collections either way, and
    a build asked for everything writes it out as before.

    The date it finished is its end date, or the date it began when
    nothing recorded an end.  A finished project with neither stays,
    since there is nothing to say it is old.

    Parameters
    ----------
    project : dict
        The project.
    today : datetime.date
        The day to count back from.
    days : int, optional
        How long a finished project is kept.  The default is a year.

    Returns
    -------
    bool
        Whether it has been finished long enough to go.
    """
    if project.get("status") != "finished":
        return False
    when = as_a_date(project.get("end_date")) or as_a_date(project.get("begin_date"))
    return bool(when) and (today - when).days > days


def as_a_date(value):
    """Return a date from a date or from what a collection wrote one as.

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
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def unassigned(goal):
    """Return True if a goal is not of any project yet.

    Something held on deck or on the wishlist is an idea somebody wrote
    down, not work anybody has taken on, so it need not say which
    project it belongs to.  It says so when they give it a number.

    Parameters
    ----------
    goal : dict
        The goal.

    Returns
    -------
    bool
        Whether it belongs to a project.
    """
    project = goal.get("project")
    return not project or str(project).strip().lower() in NOBODY


def unled(project):
    """Return True if nobody is leading a project.

    Parameters
    ----------
    project : dict
        The project.

    Returns
    -------
    bool
        Whether it has a lead worth the name.
    """
    lead = project.get("lead")
    return not lead or str(lead).strip().lower() in NOBODY


def led_by(project):
    """Return who leads a project, or None when nobody does.

    A lead written as ``tbd`` or ``na`` is a placeholder rather than a
    person, so it reads the same as no lead at all: the project belongs
    in the unassigned document until somebody picks it up.

    Parameters
    ----------
    project : dict
        The project.

    Returns
    -------
    str or None
        The id of whoever leads it, or None.
    """
    return None if unled(project) else project["lead"]


def in_the_group(person_id, people):
    """Return True if somebody is in the group at the moment.

    Somebody who has left is not, which is what makes their unfinished
    work show up as orphaned without anybody having to reassign it by
    hand.

    Parameters
    ----------
    person_id : str
        The id to look for.
    people : iterable of dict
        The people collection.

    Returns
    -------
    bool
        Whether the people collection has them, and has not marked them
        inactive.  Somebody with no mark either way is in the group: the
        people schema says active defaults to true, and a record written
        without it is somebody nobody has had to think about.
    """
    for person in people:
        if person.get("_id") == person_id:
            return bool(person.get("active", True))
    return False


def orphaned(project, people):
    """Return True if a project has nobody to do it.

    A project is orphaned when it is not finished or dropped, and either
    nobody leads it or whoever does has left the group.  The second half
    is what makes somebody's unfinished work reappear when they go,
    rather than sitting under a name that is no longer around.

    Parameters
    ----------
    project : dict
        The project.
    people : iterable of dict
        The people collection.

    Returns
    -------
    bool
        Whether it needs somebody.
    """
    if project.get("status") in CLOSED:
        return False
    return unled(project) or not in_the_group(project["lead"], people)
