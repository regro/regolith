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

from regolith.builders.missioncontrolbuilder import UNASSIGNED, MissionControlBuilder
from regolith.helpers.basehelper import DbHelperBase
from regolith.mc import DocumentError, changes, parse_document
from regolith.schemas import SCHEMAS, validate
from regolith.tools import all_docs_from_collection

HELPER_TARGET = "mc_sync"
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

        for person in self.people(renderer):
            path = mcdir / f"{renderer.document_name(person)}.md"
            if path.is_file():
                self.read_one(path, person)
        return

    def people(self, renderer):
        """Return everyone a document could belong to, and the
        orphans."""
        leads = {project.get("lead") or UNASSIGNED for project in self.gtx["mc_projects"]}
        return sorted(leads | {UNASSIGNED})

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
        """
        lead = None if person == UNASSIGNED else person
        projects = {project["_id"]: project for project in self.gtx["mc_projects"] if project.get("lead") == lead}
        goals = {goal["_id"]: goal for goal in self.gtx["mc_goals"] if goal.get("project") in projects}
        tasks = {task["_id"]: task for task in self.gtx["mc_tasks"] if task.get("goal") in goals}
        return {"mc_projects": projects, "mc_goals": goals, "mc_tasks": tasks}

    def read_one(self, path, person):
        """Read one document and write what it says."""
        rc = self.rc
        try:
            parsed = parse_document(path.read_text(encoding="utf-8"))
        except DocumentError as error:
            print(f"{path.name} was not read and nothing was written from it: {error}")
            print("Fix the line it names and run this again.")
            return

        existing = self.mine(person)
        writes, drops = changes(parsed, None if person == UNASSIGNED else person, existing)
        held = sum(len(records) for records in existing.values())
        dropped = sum(len(ids) for ids in drops.values())
        if held and dropped > held * DROP_SHARE and not rc.force:
            print(
                f"{path.name} no longer holds {dropped} of the {held} things it had, which "
                f"is more like damage than editing, so nothing was written from it."
            )
            print("Check the document, or run this again with --force to apply it anyway.")
            return

        for collection, records in writes.items():
            for record in records:
                valid, why = validate(collection, record, SCHEMAS)
                if not valid:
                    print(f"{path.name}: {record['_id']} does not fit {collection} and was not written.")
                    print(f"  {why}")
                    return
        if rc.dry_run:
            self.report(path, writes, drops, wrote=False)
            return
        for collection, records in writes.items():
            for record in records:
                rc.client.update_one(rc.database, collection, {"_id": record["_id"]}, record, upsert=True)
        for collection, ids in drops.items():
            for _id in ids:
                rc.client.update_field(rc.database, collection, _id, "status", "dropped")
        self.report(path, writes, drops, wrote=True)

    @staticmethod
    def report(path, writes, drops, wrote):
        """Say what was written, so a surprise is seen rather than
        found."""
        written = sum(len(records) for records in writes.values())
        dropped = sum(len(ids) for ids in drops.values())
        did = "wrote" if wrote else "would write"
        print(f"{path.name}: {did} {written}, dropped {dropped}")
