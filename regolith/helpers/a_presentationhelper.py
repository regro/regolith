"""Helper for adding a presentation to the presentation collection.
"""
import time

import dateutil.parser as date_parser
import threading

from regolith.helpers.a_expensehelper import expense_constructor
from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.schemas import PRESENTATION_TYPES, PRESENTATION_STATI
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    add_to_google_calendar,
    google_cal_auth_flow
)
from gooey import GooeyParser

TARGET_COLL = "presentations"
EXPENSES_COLL = "expenses"


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs['widget'] = 'DateChooser'

    subpi.add_argument("name", help="name of the event of the presentation. Meeting name if meeting, "
                                    "department if seminar",
                       )
    subpi.add_argument("place", help="the place of the presentation, Location if conference, "
                                     "institution for seminars"
                       )
    subpi.add_argument("begin_date",
                       help="Input begin date for this presentation ",
                       **date_kwargs
                       )
    subpi.add_argument("end_date",
                       help="Input end date for this presentation",
                       **date_kwargs
                       )
    subpi.add_argument("-t", "--title",
                       help="the title of the presentation, default is tbd",
                       default='tbd'
                       )
    subpi.add_argument("-a", "--abstract",
                       help="abstract of the presentation, defaults to tbd",
                       default='tbd'
                       )
    subpi.add_argument("-p", "--person",
                       help="the person presenting the presentation, used for presentation name,"
                            " defaults to name in user.config",
                       )
    subpi.add_argument("--authors", nargs="+",
                       help="specify the authors of this presentation, "
                            "defaults to person submitting the presentation",
                       )
    subpi.add_argument("-g", "--grants", nargs="+",
                       help="grant, or grants (separated by spaces), that support this presentation. Defaults to tbd",
                       default="tbd"
                       )
    subpi.add_argument("-u", "--presentation-url",
                       help="the url to the presentation, whether it is on Google Drive, GitHub or wherever",
                       )
    subpi.add_argument("-n", "--notes", nargs="+",
                       help="note or notes to be inserted as a list into the notes field, "
                            "separate notes with spaces.  Place inside quotes if the note "
                            "itself contains spaces.",
                       default=[]
                       )
    subpi.add_argument("-s", "--status",
                       choices=PRESENTATION_STATI,
                       help=f"status, from {PRESENTATION_STATI}, default is accepted",
                       default="accepted"
                       )
    subpi.add_argument("-y", "--type", 
                       choices=PRESENTATION_TYPES,
                       help=f"types, from {PRESENTATION_TYPES}. Default is invited",
                       default="invited"
                       )
    subpi.add_argument("-w", "--webinar", help=f"Is the presentation a webinar?",
                       action="store_true"
                       )
    subpi.add_argument("--no-expense", help=f"Do not add a template expense item to the "
                                            f"expenses collection.  Default is to add "
                                            f"an expense if the presentation is not a "
                                            f"webinar.",
                       action="store_true"
                       )
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file.",
                       )
    subpi.add_argument("--expense-db",
                       help="The database where the expense collection will be updated. "
                            "Defaults to first database in the regolithrc.json file.",
                       )
    subpi.add_argument("--id",
                       help="Override the default id created from the date, "
                            "speaker and place by specifying an id here",
                       )
    subpi.add_argument("--no_cal",
                       help=f"Do not add the presentation to google calendar",
                       action="store_true")
    subpi.add_argument("--force",
                       help=f"force adding presentation expense data to a public database, by default the first entry under 'databases` in regolithrc.json. DANGER: This could reveal sensitive information to the public.",
                       action="store_true")
    return subpi



class PresentationAdderHelper(DbHelperBase):
    """Helper for adding presentations"
    """
    # btype must be the same as helper target in helper.py
    btype = "a_presentation"
    needed_colls = [f'{TARGET_COLL}', 'groups', 'people', 'expenses']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]

        # if an expense database is specified using the --expense-db option,
        if rc.expense_db:
            # check that it's known / find it in rc.databases. Store its index number so we can access its other keys inside rc.databases
            index = 0
            db_known = False
            while index < len(rc.databases):
                if rc.databases[index]["name"] == rc.expense_db:
                    db_known = True
                    break
                index += 1
            expense_db_index = index

            # If the database is not known, exit with descriptive error message
            if not db_known:
                 raise RuntimeError(
                    f"ERROR: You specified database {rc.expense_db} for the expenses collection, "
                    "but that database was not found in your regolithrc.json file. "
                    "Please check the spelling when you ran the program and that the database is "
                    "correctly specified in regolithrc.json."
                )
            # if the specified expense database is public and the --force option wasn't passed, exit with a warning message
            if (rc.databases[expense_db_index]["public"] == True) and (not rc.force):
                raise RuntimeError(
                    "ERROR: The expense database you specified for the expenses collection, "
                    f"{rc.expense_db}, is not private. Please rerun specifying a PRIVATE database "
                    "listed in your regolithrc.json file, or, at your own risk, use the --force "
                    "option to add the presentation expense data to a public database."
                )

        # if no expense database is specified (but there is still expense data associatied with the presentation,
        # i.e., the --no-expense flag was not passed), set it as the first private database listed in rc. 
        # If no private database is found/known, exit with a warning message. If, however, the 
        # --force option was passed, the expense database is set to be the first entry under databases
        # in regolithrc.json file, even if that database is public. 
        if (not rc.expense_db) and (not rc.no_expense):
            if rc.force:
                rc.expense_db = rc.databases[0]["name"] # defaults to first entry under databases in regolithrc.json file
                if rc.databases[0]["public"]:
                    print(f"{key} has been added in {EXPENSES_COLL} in database {rc.expense_db}")
            else:
                private_dbs = [db for db in rc.databases if db["public"] != True]
                rc.expense_db = private_dbs[0]["name"] # defaults to first private database present in regolith.json

                # "Because no database for the presentation expenses was specified, the helper defaulted to the first private one listed in your regolithrc.json file, {rc.expense_db}"

                # If we still have no value for the rc.expense_db, it means we didn't find a private database after exhaustively iterating through the known databases
                # So we fail with warning "no default private db to enter expense data into"
                if not rc.expense_db:
                    raise RuntimeError(
                        "ERROR: There is no private database listed in your regolithrc.json file "
                        "to enter expense data into. Please rerun after adding a private database "
                        "to your regolithrc.json file, or, at your own risk, use the --force option "
                        "to add the presentation expense data to a public database."
                    )

        gtx[rc.coll] = sorted(
            all_docs_from_collection(rc.client, rc.coll), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        gtx = self.gtx
        rc = self.rc
        if not rc.no_cal:
            event = {
                        'summary': rc.name,
                        'location': rc.place,
                        'start': {'date': rc.begin_date},
                        'end': {'date': rc.end_date}
                    }
            cal_update_bool = add_to_google_calendar(event)
            if not cal_update_bool:
                google_cal_auth_flow()
                wait_bool, jump = 0, 0
                while not wait_bool or jump == 60:
                    time.sleep(1)
                    wait_bool = add_to_google_calendar(event)
                    jump += 1

        # dates
        begin_date = date_parser.parse(rc.begin_date).date()
        end_date = date_parser.parse(rc.end_date).date()

        # User specifies person in CL or in config.json
        if not rc.person:
            try:
                rc.person = rc.default_user_id
            except AttributeError:
                raise RuntimeError(
                    "WARNING: no person been set. please rerun specifying authors,"
                    "or add your id, e.g., sbillinge, to the config.json file in ~/.config/regolith"
                )
        split_person = rc.person.strip().split()
        if len(split_person) >= 2:
            name_key = split_person[0][0].casefold() + split_person[-1][0].casefold()
        else:
            name_key = split_person[0][:2].casefold()

        if not rc.id:
            key = f"{str(begin_date.year)[2:]}{str(begin_date.strftime('%m'))}{name_key}_{''.join(rc.place.casefold().split()).strip()}"
        else:
            key = rc.id

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError(
                "This entry appears to already exist in the collection")
        else:
            pdoc = {}


        if not rc.authors:
            authors = [rc.person]
        else:
            authors = rc.authors

        pdoc.update({'_id': key,
                     'abstract': rc.abstract,
                     'authors': authors,
                     'begin_date': begin_date,
                     'end_date': end_date,
                     'notes': rc.notes,
                     })
        if rc.presentation_url:
            pdoc.update({"presentation_url": rc.presentation_url})
        if rc.webinar:
            rc.no_expense = True
            pdoc.update({"webinar": True})
        if rc.type in ['seminar', 'colloquium']:
            pdoc.update({"institution": rc.place,
                        "department": rc.name})
        else:
            pdoc.update({"location": rc.place,
                        "meeting_name": rc.name})
        pdoc.update({"project": ['all'],
                     "status": rc.status,
                     "title": rc.title,
                     "type": rc.type,
                     })

        rc.client.insert_one(rc.database, rc.coll, pdoc)
        print(f"{key} has been added in {TARGET_COLL}")

        if not rc.no_expense:
            rc.business = False
            rc.payee = authors[0]
            rc.purpose = f"give {rc.type} presentation at {rc.name}, {rc.place}"
            rc.where = "tbd"
            rc.status = "unsubmitted"
            edoc = expense_constructor(key, begin_date, end_date, rc)
            rc.client.insert_one(rc.expense_db, EXPENSES_COLL, edoc)
            print(f"{key} has been added in {EXPENSES_COLL} in database {rc.expense_db}")

        return
