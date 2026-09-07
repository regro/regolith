"""Update a project in mission control from the command line.

The document is where a project is described, and for anything wordy
that is the easier place.  This is for the fields it does not show --
who is the principal investigator, which grant pays for it, when it
began -- and for the times when changing one field of one project, or
the same field of many, is quicker said than typed.

Nothing is guessed.  Only the fields given on the command line are
written, so a project can be corrected without anything else about it
being touched.
"""

from gooey import GooeyParser

from regolith.helpers.basehelper import DbHelperBase
from regolith.schemas import MC_STATI

TARGET_COLL = "mc_projects"
HELPER_TARGET = "u-mcproject"

# what the command line can set, against the field each one sets.  A list is
# replaced rather than added to, so that what is given is what is stored.
FIELDS = [
    ("name", "name"),
    ("description", "project_description"),
    ("deliverable", "project_deliverable"),
    ("lead", "lead"),
    ("collaborators", "collaborators"),
    ("grants", "grants"),
    ("pi_id", "pi_id"),
    ("status", "status"),
    ("begin_date", "begin_date"),
    ("end_date", "end_date"),
    ("urls", "urls"),
    ("notes", "notes"),
]


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument("_id", help="The id of the project to update.")
    subpi.add_argument("--name", help="What the project is called.")
    subpi.add_argument("--description", help="What the project is, for the project report.")
    subpi.add_argument("-d", "--deliverable", help="What the project produces, e.g. submit the paper.")
    subpi.add_argument("-l", "--lead", help="The id of the person leading it.")
    subpi.add_argument(
        "-w",
        "--with",
        dest="collaborators",
        nargs="+",
        help="The ids of the people on it, replacing the ones stored.",
    )
    subpi.add_argument(
        "-g",
        "--grants",
        nargs="+",
        help="The ids of the grants that pay for it, replacing the ones stored.",
    )
    subpi.add_argument("--pi", dest="pi_id", help="The id of the principal investigator.")
    subpi.add_argument("-s", "--status", help=f"The status of the project.  One of {MC_STATI}.")
    subpi.add_argument("--begin-date", help="The date the project began.", **date_kwargs)
    subpi.add_argument("--end-date", help="The date the project ended.", **date_kwargs)
    subpi.add_argument(
        "--url",
        dest="urls",
        nargs=2,
        action="append",
        # no metavar: gooey labels the field with it, and a tuple of them is
        # not something a label can be made of
        help="What a link is and the link, e.g. --url paper https://example.com/a. "
        "Give it more than once for more than one link. They replace the links "
        "stored.",
    )
    subpi.add_argument("--notes", nargs="+", help="Notes about it, replacing the ones stored.")
    return subpi


def said(value):
    """Return a value as one line, whatever shape it came in.

    Parameters
    ----------
    value : str or list
        What was written to the field.

    Returns
    -------
    str
        The value, a list written out as one line.
    """
    if not isinstance(value, list):
        return str(value)
    return ", ".join(f"{v['name']}: {v['url']}" if isinstance(v, dict) else str(v) for v in value)


class MCProjectUpdaterHelper(DbHelperBase):
    """Update a project in mission control."""

    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        self.rc.coll = f"{TARGET_COLL}"

    def db_updater(self):
        rc = self.rc
        given = {field: getattr(rc, argument) for argument, field in FIELDS if getattr(rc, argument, None)}
        if not given:
            raise ValueError(
                "Nothing was given to update. Please give at least one field to "
                "change, such as --status or --grants."
            )
        if "status" in given and given["status"] not in MC_STATI:
            raise ValueError(f"The status should be one of {MC_STATI}. Please pick one of those.")
        if "urls" in given:
            # the collection holds a link and what it is, rather than a bare link
            given["urls"] = [{"name": name, "url": url} for name, url in given["urls"]]

        dbname = self.where_it_is(rc._id)
        if dbname is None:
            raise ValueError(
                f"There is no project called {rc._id}. Please check the id, which "
                f"'regolith helper l_mcprojects' will list."
            )
        rc.client.update_one(dbname, rc.coll, {"_id": rc._id}, given)
        print(f"{rc._id} updated:")
        for field, value in given.items():
            print(f"    {field}: {said(value)}")
        return

    def where_it_is(self, _id):
        """Return the database holding a project.

        A project is updated where it is stored rather than in the first
        database that happens to be listed, since writing it anywhere
        else would leave two of it and hide the one that is real.  That
        is why ``rc.database`` is not used: the runcontrol fills it in
        with the first database before any updater runs.

        Parameters
        ----------
        _id : str
            The id of the project.

        Returns
        -------
        str or None
            The name of the database holding it, or None when nothing
            holds it.
        """
        rc = self.rc
        for database in rc.client.collection_sources(rc.coll):
            if rc.client.find_one(database["name"], rc.coll, {"_id": _id}):
                return database["name"]
        return None
