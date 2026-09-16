"""Read the mission control documents back into the collections.

This is the half that makes a document worth typing into.  Everything
somebody wrote in one is read back: the text, the boxes, the strikes,
the order, which section a thing sits in and which week a task is under.

Nothing is deleted.  A line somebody removed marks its record
``dropped``, so a document wrecked by accident costs nothing that a
render cannot put back, and a document that cannot be read at all is
skipped whole rather than half applied.
"""

import datetime as dt
from pathlib import Path

from gooey import GooeyParser

from regolith.builders.missioncontrolbuilder import live
from regolith.helpers.basehelper import DbHelperBase
from regolith.mc import (
    KEEP_FINISHED_DAYS,
    UNASSIGNED,
    DocumentError,
    changes,
    document_name,
    in_the_group,
    led_by,
    parse_document,
    period_of,
    project_prefix,
    retired,
    unassigned,
)
from regolith.schemas import SCHEMAS, validate
from regolith.tools import all_docs_from_collection

HELPER_TARGET = "u-mcsync"
COLLECTIONS = ("mc_projects", "mc_goals", "mc_tasks")
# a document that has lost more than this share of what it held is more
# likely to be damaged than edited
DROP_SHARE = 1 / 3


def subparser(subpi):
    if isinstance(subpi, GooeyParser):
        pass
    subpi.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Apply a document even when most of what it held has gone from it.",
    )
    subpi.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Say what would be written without writing it.",
    )
    subpi.add_argument("--database", help="The database to write to.")
    return subpi


class MCSyncHelper(DbHelperBase):
    """Read every mission control document back into the collections."""

    btype = HELPER_TARGET
    needed_colls = list(COLLECTIONS) + ["people"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        rc = self.rc
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        for collection in COLLECTIONS:
            self.gtx[collection] = list(all_docs_from_collection(rc.client, collection))
        self.gtx["people"] = list(all_docs_from_collection(rc.client, "people"))

    def db_updater(self):
        rc = self.rc
        mcdir = Path(getattr(rc, "mission_control_dir", None) or f"{rc.builddir}/mission-control")
        if not mcdir.is_dir():
            print(f"There are no mission control documents in {mcdir}.")
            print("Run 'regolith build mission-control' to write them first.")
            return

        found = self.documents(mcdir)
        for path, person in found:
            self.read_one(path, person)
        self.say_who_is_missing(mcdir, {person for _, person in found})

    def say_who_is_missing(self, mcdir, read):
        """Say who has work stored and no document to read it from.

        A sync reads documents; it does not write them.  Somebody whose
        first project has just been stored has nothing on disk yet, so a
        sync passes over them in silence and they look forgotten.

        Parameters
        ----------
        mcdir : pathlib.Path
            The directory the documents are in.
        read : set of str
            The people whose documents were read.
        """
        days = getattr(self.rc, "mission_control_keep_finished_days", KEEP_FINISHED_DAYS)
        today = dt.date.today()
        people = self.gtx["people"]
        waiting = {
            lead
            for project in live(self.gtx["mc_projects"])
            for lead in [led_by(project)]
            if lead and lead not in read and in_the_group(lead, people) and not retired(project, today, days)
        }
        for person in sorted(waiting):
            name = document_name(person, people)
            print(f"{person} has work stored and no document: {mcdir / (name + '.md')} is not there.")
        if waiting:
            print("Run 'regolith build mission-control' to write it, then edit that rather than a new file.")

    def documents(self, mcdir):
        """Return each document in the directory, with whose it is.

        The documents are what there is to read, so they are what is
        read.  Working the list out from the projects in the collections
        instead would pass over the document of somebody who has no
        project in them, and that is exactly the person whose document
        is asking for one to be made.

        Parameters
        ----------
        mcdir : pathlib.Path
            The directory the documents are in.

        Returns
        -------
        list of tuple of (pathlib.Path, str)
            Each document and the id of the person whose it is.
        """
        people = self.gtx["people"]
        whose = {UNASSIGNED: UNASSIGNED}
        for person in people:
            whose.setdefault(document_name(person["_id"], people), person["_id"])
        for project in self.gtx["mc_projects"]:
            lead = led_by(project)
            if lead:
                whose.setdefault(document_name(lead, people), lead)
        found = []
        for path in sorted(mcdir.glob("*.md")):
            if path.stem in whose:
                found.append((path, whose[path.stem]))
            else:
                print(f"{path.name} is not named for anybody, so nothing was read from it.")
                print("Name it for the person whose it is, or add them to the people collection.")
        return found

    def everything(self):
        """Return every record of every collection, keyed by id.

        A document may name something that is stored and is not the
        person's, which is what a project whose lead was changed looks
        like from the document it used to be in.  Read against this it
        is recognised rather than made again.

        Returns
        -------
        dict
            ``{collection: {id: record}}`` for everything stored.
        """
        return {
            collection: {record["_id"]: record for record in self.gtx[collection]} for collection in COLLECTIONS
        }

    def mine(self, person):
        """Return the records already stored for one person.

        Parameters
        ----------
        person : str
            The id of the person, or ``unassigned``.

        Returns
        -------
        dict
            ``{collection: {id: record}}`` for what is theirs.

        Notes
        -----
        What was dropped is left out.  It is not in their document, so
        counting it would have every sync drop it again and read as a
        document losing more than it holds.
        """
        lead = None if person == UNASSIGNED else person
        projects = {
            project["_id"]: project for project in live(self.gtx["mc_projects"]) if led_by(project) == lead
        }
        goals = {
            goal["_id"]: goal
            for goal in live(self.gtx["mc_goals"])
            # a goal of no project is not reached through a project, so it is
            # found by whose it is, or it would read as deleted every sync
            if goal.get("project") in projects or (unassigned(goal) and goal.get("lead") == lead)
        }
        tasks = {task["_id"]: task for task in live(self.gtx["mc_tasks"]) if task.get("goal") in goals}
        return {"mc_projects": projects, "mc_goals": goals, "mc_tasks": tasks}

    def taken(self):
        """Return every id mission control holds.

        A project is given an id made from its name, so unlike a drawn
        id it can be one somebody else's document already has.

        Returns
        -------
        set of str
            The ids in use across the mission control collections.
        """
        return {record["_id"] for collection in COLLECTIONS for record in self.gtx[collection]}

    @staticmethod
    def copies_are_settled(path, parsed):
        """Say what became of lines that shared an id, and whether to go
        on.

        Somebody who copies a line to make a new one often leaves the id
        on it.  Where one of the two says what is stored under that id,
        that one is the original and keeps it, and the other is stored as
        new: that is said, and the sync goes on.  Where neither does, or
        both do, there is nothing to tell them apart by, and nothing is
        written from the document, so that a guess cannot reach a build.

        Parameters
        ----------
        path : pathlib.Path
            The document that was read.
        parsed : dict
            What was read from it, after ``changes`` has settled the ids.

        Returns
        -------
        bool
            Whether the sync may write what the document says.
        """
        settled = True
        for copy in parsed.get("copied", ()):
            kind = copy["collection"].replace("mc_", "")[:-1]
            if copy["sure"]:
                print(
                    f"{path.name}: two lines carried the id {copy['id']}. "
                    f'"{copy["kept"]}" keeps it, being what was stored under it, and '
                    f'"{copy["new"]}" is stored as a new {kind}. The next build writes '
                    f"its new id into the document."
                )
                continue
            settled = False
            print(
                f"{path.name}: two lines carry the id {copy['id']}, and there is no telling "
                f'which is the {kind} already stored: "{copy["kept"]}" or "{copy["new"]}". '
                f"Nothing was written from {path.name}."
            )
            print(f"Take ^{copy['id']} off the line that is new, then sync again.")
        return settled

    def left_out_of_documents(self, existing):
        """Return the ids a document is not written with.

        A project finished longer ago than the runcontrol keeps them is
        left out of the document by the builder, and so are its goals
        and their tasks.

        Parameters
        ----------
        existing : dict
            The records stored, as ``{collection: {id: record}}``.

        Returns
        -------
        list of str
            The ids the document is not expected to hold.
        """
        days = getattr(self.rc, "mission_control_keep_finished_days", KEEP_FINISHED_DAYS)
        today = dt.date.today()
        # a project finished long ago is not written at all, and one finished
        # at any time is written as a line in the archive without its goals
        gone = {
            _id
            for _id, project in existing["mc_projects"].items()
            if retired(project, today, days) or project.get("status") == "finished"
        }
        # what hangs under something finished goes with it
        goals = {
            _id
            for _id, goal in existing["mc_goals"].items()
            if goal.get("project") in gone or goal.get("status") == "finished"
        }
        tasks = set()
        for _id, task in existing["mc_tasks"].items():
            if task.get("goal") in goals or task.get("status") == "finished":
                tasks.add(_id)
        # and a sub task of one that has gone goes too, however deep
        changing = True
        while changing:
            changing = False
            for _id, task in existing["mc_tasks"].items():
                if _id not in tasks and task.get("parent") in tasks:
                    tasks.add(_id)
                    changing = True
        return sorted(gone) + sorted(goals) + sorted(tasks)

    def read_one(self, path, person):
        """Read one document and write what it says."""
        rc = self.rc
        lead = None if person == UNASSIGNED else person
        try:
            parsed = parse_document(
                path.read_text(encoding="utf-8"),
                taken=self.taken(),
                prefix=project_prefix(lead, self.gtx["people"]),
                period=period_of(dt.date.today(), getattr(rc, "mission_control_periods", None)),
            )
        except DocumentError as error:
            print(f"{path.name} was not read and nothing was written from it: {error}")
            print("Fix the line it names and run this again.")
            return

        existing = self.mine(person)
        # a document is not written with everything the collections hold, so
        # what it leaves out on purpose must not read as a line somebody
        # deleted.  The record is neither written nor dropped: the document
        # says nothing about it either way
        parsed["mentioned"] = list(parsed.get("mentioned", ())) + self.left_out_of_documents(existing)
        writes, drops = changes(parsed, lead, existing, elsewhere=self.everything())
        if not self.copies_are_settled(path, parsed):
            return
        held = sum(len(records) for records in existing.values())
        dropped = sum(len(ids) for ids in drops.values())
        read = sum(len(parsed[kind]) for kind in ("projects", "goals", "tasks"))
        if held and not read:
            # nothing in it was recognised at all.  That is not somebody
            # deleting their work, it is a file that has stopped being a
            # mission control document, and --force does not apply to it:
            # there is nothing in it to apply
            print(f"{path.name} has nothing in it that a mission control document has.")
            print("Its headings and its bullets have gone, which is what an editor does to a")
            print("file when it saves it as plain text rather than as markdown.")
            self.name_what_is_at_risk(existing, drops)
            print("Nothing was written from it, with or without --force.")
            print(f"Put the document back from your file history, or from {self.copies()}.")
            return
        if held and dropped > held * DROP_SHARE and not rc.force:
            print(
                f"{path.name} no longer holds {dropped} of the {held} things it had, which "
                f"is more like damage than editing, so nothing was written from it."
            )
            self.name_what_is_at_risk(existing, drops)
            print("Check the document, or run this again with --force to apply it anyway.")
            return

        for collection, records in writes.items():
            for record in records:
                valid, why = validate(collection, record, SCHEMAS)
                if not valid:
                    print(f"{path.name}: {record['_id']} does not fit {collection} and was not written.")
                    print(f"  {why}")
                    return
        new = sum(
            1 for collection, records in writes.items() for r in records if r["_id"] not in existing[collection]
        )
        if rc.dry_run:
            self.report(path, writes, drops, wrote=False, new=new)
            return
        for collection, records in writes.items():
            for record in records:
                where = self.where_stored(collection, record["_id"]) or self.first_source(collection)
                rc.client.update_one(where, collection, {"_id": record["_id"]}, record, upsert=True)
        for collection, ids in drops.items():
            for _id in ids:
                where = self.where_stored(collection, _id) or self.first_source(collection)
                rc.client.update_field(where, collection, _id, "status", "dropped")
        self.report(path, writes, drops, wrote=True, new=new)

    def copies(self):
        """Return where a render keeps the copy it took."""
        return f"{self.rc.builddir}/mission-control-previous"

    @staticmethod
    def name_what_is_at_risk(existing, drops):
        """Say which things a document no longer holds.

        A count says how much is at stake and not what, and what is what
        somebody needs in order to tell whether the document is right.

        Parameters
        ----------
        existing : dict
            The records stored, as ``{collection: {id: record}}``.
        drops : dict
            The ids no longer in the document, by collection.
        """
        for collection, ids in drops.items():
            for _id in ids:
                record = existing[collection].get(_id, {})
                said = record.get("name") or record.get("text") or ""
                print(f"    {_id}  {said}")

    @staticmethod
    def report(path, writes, drops, wrote, new=0):
        """Say what was written, so a surprise is seen rather than
        found.

        Parameters
        ----------
        path : pathlib.Path
            The document that was read.
        writes : dict
            The records written, by collection.
        drops : dict
            The ids dropped, by collection.
        wrote : bool
            Whether anything was actually written.
        new : int, optional
            How many of the records nothing held before, which is what
            somebody typing into the document wants to see.
        """
        written = sum(len(records) for records in writes.values())
        dropped = sum(len(ids) for ids in drops.values())
        did = "wrote" if wrote else "would write"
        of_which = f", {new} of them new" if new else ""
        print(f"{path.name}: {did} {written}{of_which}, dropped {dropped}")
