"""Read the mission control documents back into the collections.

This is the half that makes a document worth typing into.  Everything
somebody wrote in one is read back: the text, the boxes, the strikes,
the order, which section a thing sits in and which week a task is under.

Nothing is deleted.  A line somebody removed marks its record
``dropped``, so a document wrecked by accident costs nothing that a
render cannot put back, and a document that cannot be read at all is
skipped whole rather than half applied.
"""

from pathlib import Path

from gooey import GooeyParser

from regolith.builders.missioncontrolbuilder import (
    UNASSIGNED,
    UNASSIGNED_NAME,
    MissionControlBuilder,
    live,
)
from regolith.helpers.basehelper import DbHelperBase
from regolith.mc import (
    UNLED_PREFIX,
    DocumentError,
    changes,
    initials,
    led_by,
    parse_document,
    slug,
)
from regolith.schemas import SCHEMAS, validate
from regolith.tools import all_docs_from_collection

HELPER_TARGET = "mc-sync"
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
        renderer = MissionControlBuilder.__new__(MissionControlBuilder)
        renderer.gtx = self.gtx
        mcdir = Path(getattr(rc, "mission_control_dir", None) or f"{rc.builddir}/mission-control")
        if not mcdir.is_dir():
            print(f"There are no mission control documents in {mcdir}.")
            print("Run 'regolith build mission-control' to write them first.")
            return

        for path, person in self.documents(mcdir, renderer):
            self.read_one(path, person)
        return

    def documents(self, mcdir, renderer):
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
        renderer : MissionControlBuilder
            The builder, which knows what each person's document is
            called.

        Returns
        -------
        list of tuple of (pathlib.Path, str)
            Each document and the id of the person whose it is.
        """
        whose = {UNASSIGNED_NAME: UNASSIGNED}
        for person in self.gtx["people"]:
            whose.setdefault(renderer.document_name(person["_id"]), person["_id"])
        for project in self.gtx["mc_projects"]:
            lead = led_by(project)
            if lead:
                whose.setdefault(renderer.document_name(lead), lead)
        found = []
        for path in sorted(mcdir.glob("*.md")):
            if path.stem in whose:
                found.append((path, whose[path.stem]))
            else:
                print(f"{path.name} is not named for anybody, so nothing was read from it.")
                print("Name it for the person whose it is, or add them to the people collection.")
        return found

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
        goals = {goal["_id"]: goal for goal in live(self.gtx["mc_goals"]) if goal.get("project") in projects}
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

    def prefix(self, person):
        """Return what a project typed into one document is named with.

        Parameters
        ----------
        person : str
            The id of the person whose document it is, or
            ``unassigned``.

        Returns
        -------
        str
            Their initials, or ``na`` for the document of nobody.
        """
        if person == UNASSIGNED:
            return UNLED_PREFIX
        for entry in self.gtx["people"]:
            if entry["_id"] == person:
                return initials(entry.get("name") or person)
        return slug(person)

    def read_one(self, path, person):
        """Read one document and write what it says."""
        rc = self.rc
        try:
            parsed = parse_document(
                path.read_text(encoding="utf-8"), taken=self.taken(), prefix=self.prefix(person)
            )
        except DocumentError as error:
            print(f"{path.name} was not read and nothing was written from it: {error}")
            print("Fix the line it names and run this again.")
            return

        existing = self.mine(person)
        writes, drops = changes(parsed, None if person == UNASSIGNED else person, existing)
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
                where = self.where_it_goes(collection, record["_id"])
                rc.client.update_one(where, collection, {"_id": record["_id"]}, record, upsert=True)
        for collection, ids in drops.items():
            for _id in ids:
                rc.client.update_field(self.where_it_goes(collection, _id), collection, _id, "status", "dropped")
        self.report(path, writes, drops, wrote=True, new=new)

    def where_it_goes(self, collection, _id):
        """Return the database a record belongs in.

        A record already stored is written where it is stored, rather
        than in the first database that happens to be listed, since
        writing it anywhere else would leave two of it and hide the one
        that is real.  A record nothing holds yet goes where the
        collection is, or to rc.database when nothing holds it at all.

        Parameters
        ----------
        collection : str
            The name of the collection.
        _id : str
            The id of the record.

        Returns
        -------
        str
            The name of the database to write to.
        """
        rc = self.rc
        sources = rc.client.collection_sources(collection)
        for database in sources:
            if rc.client.find_one(database["name"], collection, {"_id": _id}):
                return database["name"]
        return sources[0]["name"] if sources else rc.database

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
