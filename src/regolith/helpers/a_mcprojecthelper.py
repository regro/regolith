"""Add a project to mission control.

Typing a project into a document creates it just as well, and for
anything wordy that is the easier way.  This is for the moment in a
conversation when a project is mentioned and writing it down should cost
nothing: name it, say who leads it if anybody does yet, and carry on.

Creating cannot conflict with a document, because a new project is in no
document until the next render puts it in one.  Everything the document
carries is read back from it, so it stays the place to say what a
project is called or who is on it; this is the place to record what the
document never shows, such as which grant pays for it.
"""

import datetime as dt

from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.mc import UNLED_PREFIX, initials, project_id, slug, unled
from regolith.schemas import MC_STATI
from regolith.tools import all_docs_from_collection

TARGET_COLL = "mc_projects"
# a stub is written down so that it is not forgotten, and what is not known
# yet says so rather than being left out
TBD = "tbd"
HELPER_TARGET = "a_mcproject"


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument("name", help="A name for the project.")
    subpi.add_argument(
        "-l",
        "--lead",
        default=TBD,
        help=f"The id of the person leading it.  Default is {TBD}, which leaves "
        f"the project unassigned and writes it to the unassigned document until "
        f"somebody moves it into theirs.",
    )
    subpi.add_argument(
        "-w",
        "--with",
        dest="collaborators",
        nargs="+",
        help="The ids of the people on it, group members and others alike.",
    )
    subpi.add_argument(
        "-g",
        "--grants",
        nargs="+",
        default=[TBD],
        help=f"The ids of the grants that pay for it.  Default is {TBD}.",
    )
    subpi.add_argument("--pi", dest="pi_id", help="The id of the principal investigator.")
    subpi.add_argument(
        "-d",
        "--deliverable",
        default=TBD,
        help=f"What the project produces, e.g. submit the paper.  Default is {TBD}.",
    )
    subpi.add_argument(
        "--description",
        default=TBD,
        help=f"What the project is, for the project report.  Default is {TBD}.",
    )
    subpi.add_argument(
        "-s",
        "--status",
        default="proposed",
        help=f"The status of the project.  One of {MC_STATI}.  Default is proposed.",
    )
    subpi.add_argument(
        "--begin-date",
        help="The date the project began.  Default is today.",
        **date_kwargs,
    )
    subpi.add_argument(
        "--id",
        dest="_id",
        help="An id for it.  Default is made from the name.  Either way it is put "
        "in lower case with hyphens, since ids no longer carry underscores.",
    )
    subpi.add_argument("--database", help="The database to write to.")
    return subpi


class MCProjectAdderHelper(DbHelperBase):
    """Add a project to mission control."""

    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "people"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        self.gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        self.gtx["people"] = list(all_docs_from_collection(rc.client, "people"))

    def prefix(self):
        """Return the initials a project of this lead's is named
        with."""
        rc = self.rc
        # tbd is a placeholder rather than a person, so it names the project
        # the way no lead at all does
        if unled({"lead": rc.lead}):
            return UNLED_PREFIX
        for entry in self.gtx["people"]:
            if entry["_id"] == rc.lead:
                return initials(entry.get("name") or rc.lead)
        return slug(rc.lead)

    def db_updater(self):
        rc = self.rc
        taken = {project["_id"] for project in self.gtx[rc.coll]}
        # an id given by hand goes through the same slug, so an underscore
        # cannot get in that way either
        _id = slug(rc._id) if rc._id else project_id(rc.name, prefix=self.prefix())
        if _id in taken:
            raise ValueError(
                f"There is already a project called {_id}. Give it another name, or "
                f"pass --id with an id of your own."
            )
        if rc.status not in MC_STATI:
            raise ValueError(f"The status should be one of {MC_STATI}. Please pick one of those.")

        project = {
            "_id": _id,
            "name": rc.name,
            "status": rc.status,
            "begin_date": rc.begin_date or dt.date.today(),
        }
        for key, value in [
            ("lead", rc.lead),
            ("collaborators", rc.collaborators),
            ("grants", rc.grants),
            ("pi_id", rc.pi_id),
            ("project_deliverable", rc.deliverable),
            ("project_description", rc.description),
        ]:
            if value:
                project[key] = value
        rc.client.insert_one(rc.database, rc.coll, project)

        whose = "unassigned" if unled(project) else f"to {rc.lead}"
        print(f'The project "{rc.name}" has been added {whose} as {_id}.')
        return
