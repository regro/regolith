"""Helper for adding a new person to the contacts collection.

"""
import datetime as dt
from nameparser import HumanName
import dateutil.parser as date_parser
import uuid

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection, fragment_retrieval


TARGET_COLL = "contacts"

def subparser(subpi):
    subpi.add_argument("name", help="name, name fragment (single argument only) or id "
                                    "used to find an existing contact. "
                                    "please, inform full name if this is a new contact")
    subpi.add_argument("-d", "--id", help="id of the person, e.g., first letter first name "
                                            "plus last name, but unique")
    subpi.add_argument("--number", help="number in the numbered list")
    subpi.add_argument("-i", "--institution", help="person's institution. It can be "
                                                   "institution id or anything in the "
                                                   "aka or name from institutions collection. "
                                                   "it is required to create a new contact")
    subpi.add_argument("-a", "--aliases", nargs='+',
                        help="All the different ways that the person may "
                             "be referred to as.  As many as you like, in "
                             "quotes separated by a space")
    subpi.add_argument("--notes", nargs='+',
                        help="notes.  As many notes as you like, each one in "
                             "quotes and separated by a space, such as where"
                             "and when met, what discussed.")
    # Do not delete --database arg
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file.")
    # Do not delete --date arg
    subpi.add_argument("--date",
                       help="The date when the contact was created in ISO format"
                            " Defaults to today's date."
                       )
    #FIXME
    # subpi.add_argument("-e", "--email",
    #                    help="email address")

    return subpi

class ContactUpdaterHelper(DbHelperBase):
    """Helper for adding a new person to the contacts collection.
    """
    # btype must be the same as helper target in helper.py
    btype = "u_contact"
    needed_dbs = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(
            all_docs_from_collection(rc.client, rc.coll), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        name = HumanName(rc.name)
        sorted_ids = sorted(set(i.get('_id') for i in fragment_retrieval(self.gtx['contacts'],
                                            ["_id", "aka", "name"], rc.name)))
        index = list(range(len(sorted_ids)))
        if not rc.number:
            print("Please choose from one of the following to update/add:")
            print(f"{0}. {rc.name} as a new contact")
            print(*[f"{i+1}. {rc.client.find_one(rc.database, rc.coll, {'_id': j})['name']}    id: {j}\n"
                                                                    for i, j, in zip(index, sorted_ids)])
            return
        pdoc = {}
        if rc.number == 0:
            if not rc.institution:
                raise RuntimeError("institution is required to create a new contact")
            if not rc.d:
                key = str(name.first[0].lower().replace(" ", "") + name.last.lower().replace(" ", ""))
            else:
                key = rc.d
            pdoc.update({"name": name.full_name})
            pdoc.update({"date": dt.date.today()})
            pdoc.update({"institution": rc.institution})
            notes = []
            aliases = []
            uniqueidentifier = str(uuid.uuid4())
            pdoc.update({'uuid': uniqueidentifier})
        else:
            key = sorted_ids[int(rc.number)-1]
            current = rc.client.find_one(rc.database, rc.coll, {'_id': key})
            notes = current.get('notes', [])
            aliases = current.get('aka', [])
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
        pdoc.update({"aka": aliases})
        pdoc.update({"notes": notes})
        pdoc.update({'updated': now})
        rc.client.update_one(rc.database, rc.coll, {'_id': key}, pdoc)
        print("{} has been added/updated in contacts".format(rc.name))

        return
