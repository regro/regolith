"""Helper for adding a new person to the contacts collection.

"""
import datetime as dt
from nameparser import HumanName
import dateutil.parser as date_parser
import sys
import uuid

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection


TARGET_COLL = "contacts"

def subparser(subpi):
    subpi.add_argument("name", help="first name space last name in quotes")
    subpi.add_argument("institution", help="person's institution.  Can be inf"
                                            "short form such as columbiau and will "
                                            "be retrieved from institutions collection")
    # subpi.add_argument("-e", "--email",
    #                    help="email address")
    subpi.add_argument("-a", "--aliases", nargs='+',
                        help="All the different ways that the person may "
                             "be referred to as.  As many as you like, in "
                             "quotes separated by commas")
    subpi.add_argument("-n", "--notes", nargs='+',
                        help="notes.  As many notes as you like, each one in "
                             "quotes and separated by a comma, such as where"
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
    subpi.add_argument("--update",
                       help="The date and time when the contact was updated"
                            " Defaults to the current date and time."
                       )
    subpi.add_argument("--uuid",
                       help="universally unique identifier Defaults to "
                            "a randomly generated uuid."
                       )

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

        if not rc.date:
            now = dt.date.today()
        else:
            now = date_parser.parse(rc.date).date()

        key = str(name.first[0].lower().replace(" ", "") + name.last.lower().replace(" ", ""))
        filterid = {'_id': key}
        coll = self.gtx[rc.coll]

        pdoc = {'_id': key}
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))

        if len(pdocl) > 0:
            current = rc.client.find_one(rc.database, rc.coll, filterid)
            uid = current.get('uuid', str(uuid.uuid4()))
            notes = current.get('notes', [])
            aliases = current.get('aka', [])

        else:
            pdoc.update({'day': now.day, 'month': now.month, 'year': now.year, "date": now})
            notes = []
            aliases = [rc.name]
            if not rc.uuid:
                uid = str(uuid.uuid4())
            else:
                uid = rc.uuid

        # if rc.e_email:
        #     pdoc.update({"email": rc.email})

        if rc.aliases:
            aliases.extend(rc.aliases)

        if rc.notes:
            notes.extend(rc.notes)

        if not rc.update:
            nowdt = dt.datetime.now()
        else:
            nowdt = rc.update

        pdoc.update({"aka": aliases})
        pdoc.update({"notes": notes})
        pdoc.update({'uuid': uid})
        pdoc.update({"name": name.full_name,
                    "institution": rc.institution,
                    })
        pdoc.update({'updated': nowdt})

        rc.client.update_one(rc.database, rc.coll, filterid, pdoc)
        print("{} has been added/updated in contacts".format(rc.name))

        return
