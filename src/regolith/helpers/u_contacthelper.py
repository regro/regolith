"""Helper for adding a new person to the contacts collection."""

import datetime as dt
import uuid

import dateutil.parser as date_parser
from gooey import GooeyParser
from nameparser import HumanName

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection, fragment_retrieval, strip_str

TARGET_COLL = "contacts"


def subparser(subpi):
    date_kwargs = {}
    notes_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        notes_kwargs["widget"] = "Textarea"

    subpi.add_argument(
        "fragmentname", type=strip_str, help="Fragment of name, id, or aliases to search for contacts."
    )
    subpi.add_argument(
        "-i", "--index", help="Index of the item in the enumerated list chosen to update.", type=int
    )
    subpi.add_argument("-n", "--name", type=strip_str, help="Full name. Required if new contact.")
    subpi.add_argument(
        "-o",
        "--institution",
        type=strip_str,
        help="Person's institution. It can be "
        "institution id or anything in the "
        "aka or name from institutions collection. "
        "It is required to create a new contact.",
    )
    subpi.add_argument(
        "-t",
        "--notes",
        type=strip_str,
        nargs="+",
        help="Notes.  As many notes as you like, each one in "
        "quotes and separated by a space, such as where "
        "and when met, what discussed.",
        **notes_kwargs,
    )
    subpi.add_argument("-d", "--department", type=strip_str, help="Department at the institution.")
    subpi.add_argument(
        "--id",
        type=strip_str,
        help="id of the person, e.g., first letter first name " "plus last name, but unique.",
    )
    subpi.add_argument(
        "--aliases",
        type=strip_str,
        nargs="+",
        help="All the different ways that the person may "
        "be referred to as.  As many as you like, in "
        "quotes separated by a space",
    )
    # Do not delete --date arg
    subpi.add_argument(
        "--date",
        type=strip_str,
        help="The date when the contact was created. " "Defaults to today's date.",
        **date_kwargs,
    )
    # Do not delete --database arg
    subpi.add_argument(
        "--database",
        type=strip_str,
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
    )
    # FIXME
    # subpi.add_argument("-e", "--email",
    #                    help="email address")

    return subpi


class ContactUpdaterHelper(DbHelperBase):
    """Helper for adding a new person to the contacts collection."""

    # btype must be the same as helper target in helper.py
    btype = "u_contact"
    needed_colls = [f"{TARGET_COLL}"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        found_contacts = fragment_retrieval(self.gtx["contacts"], ["_id", "aka", "name"], rc.fragmentname)
        found_contacts.sort(key=lambda x: x["_id"], reverse=False)
        index_list = list(range(2, (len(found_contacts) + 2)))
        if not rc.index:
            print(
                "Please rerun the helper by hitting up arrow and adding '-i list-index' "
                "to update the list item 'list-index', e.g., 'regolith helper eins -i 2'. "
                "For new contacts --name (-n) and --institution (-o) are required:"
            )
            print(f"{1}. {rc.fragmentname} as a new contact")
            for i, j in zip(index_list, found_contacts):
                print(
                    f"{i}. {j.get('name')}\n"
                    f"   id: {j.get('_id')}\n"
                    f"   email: {j.get('email')}\n"
                    f"   institution: {j.get('institution')}\n"
                    f"   department: {j.get('department')}\n"
                    f"   notes: {j.get('notes')}\n"
                    f"   aliases: {j.get('aka')}"
                )
            return
        pdoc = {}
        if int(rc.index) == 1:
            if not rc.institution or not rc.name:
                raise RuntimeError("Institution and name are required to create a new contact")
            name = HumanName(rc.name)
            if not rc.id:
                key = str(name.first[0].lower().replace(" ", "") + name.last.lower().replace(" ", ""))
            else:
                key = rc.id
            pdoc.update({"name": name.full_name})
            pdoc.update({"date": dt.date.today()})
            pdoc.update({"institution": rc.institution})
            notes = []
            aliases = []
            uniqueidentifier = str(uuid.uuid4())
            pdoc.update({"uuid": uniqueidentifier})
        else:
            current = found_contacts[rc.index - 2]
            key = current.get("_id")
            notes = current.get("notes", [])
            aliases = current.get("aka", [])
        if not rc.date:
            now = dt.datetime.now()
        else:
            now = date_parser.parse(rc.date).date()
        if rc.aliases:
            aliases.extend(rc.aliases)
        if rc.notes:
            if isinstance(rc.notes, str):
                rc.notes.list()
            notes.extend(rc.notes)
        if rc.department:
            pdoc.update({"department": rc.department})
        pdoc.update({"aka": aliases})
        pdoc.update({"notes": notes})
        pdoc.update({"updated": now})
        rc.client.update_one(rc.database, rc.coll, {"_id": key}, pdoc)
        print("{} has been added/updated in contacts".format(key))

        return
