"""Helper for adding a presentation to the presentation collection."""

import time
from warnings import warn

import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.a_expensehelper import expense_constructor
from regolith.helpers.basehelper import DbHelperBase
from regolith.schemas import alloweds
from regolith.tools import (
    add_to_google_calendar,
    all_docs_from_collection,
    create_repo,
    get_pi_id,
    google_cal_auth_flow,
)

TARGET_COLL = "presentations"
EXPENSES_COLL = "expenses"

PRESENTATION_TYPES = alloweds.get("PRESENTATION_TYPES")
PRESENTATION_STATI = alloweds.get("PRESENTATION_STATI")


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument(
        "name",
        help="name of the event of the presentation. Meeting name if meeting, " "department if seminar",
    )
    subpi.add_argument(
        "place", help="the place of the presentation, Location if conference, " "institution for seminars"
    )
    subpi.add_argument("begin_date", help="Input begin date for this presentation ", **date_kwargs)
    subpi.add_argument("end_date", help="Input end date for this presentation", **date_kwargs)
    subpi.add_argument(
        "--regolith-talk-id", help="the id of the talk in your regolith talks collection, if known", default="tbd"
    )
    subpi.add_argument("-t", "--title", help="the title of the presentation, default is tbd", default="tbd")
    subpi.add_argument("-a", "--abstract", help="abstract of the presentation, defaults to tbd", default="tbd")
    subpi.add_argument(
        "-p",
        "--person",
        help="the person presenting the presentation, used for presentation name,"
        " defaults to name in user.config",
    )
    subpi.add_argument(
        "--authors",
        nargs="+",
        help="specify the authors of this presentation, " "defaults to person submitting the presentation",
    )
    subpi.add_argument(
        "-g",
        "--grants",
        nargs="+",
        help="grant, or grants (separated by spaces), that support this presentation. Defaults to tbd",
        default="tbd",
    )
    subpi.add_argument(
        "-u",
        "--presentation-url",
        help="the url to the presentation, whether it is on Google Drive, GitHub or wherever",
    )
    subpi.add_argument(
        "-n",
        "--notes",
        nargs="+",
        help="note or notes to be inserted as a list into the notes field, "
        "separate notes with spaces.  Place inside quotes if the note "
        "itself contains spaces.",
        default=[],
    )
    subpi.add_argument(
        "-s",
        "--status",
        choices=PRESENTATION_STATI,
        help=f"status, from {PRESENTATION_STATI}, default is accepted",
        default="accepted",
    )
    subpi.add_argument(
        "-y",
        "--type",
        choices=PRESENTATION_TYPES,
        help=f"types, from {PRESENTATION_TYPES}. Default is invited",
        default="invited",
    )
    subpi.add_argument("-w", "--webinar", help="Is the presentation a webinar?", action="store_true")
    subpi.add_argument("--cal", help="Add the presentation to google calendar", action="store_true")
    subpi.add_argument("--repo", help="Create a GitHub/Lab repo for the presentation", action="store_true")
    subpi.add_argument(
        "--no-expense",
        help="Do not add a template expense item to the "
        "expenses collection.  Default is to add "
        "an expense if the presentation is not a "
        "webinar.",
        action="store_true",
    )
    subpi.add_argument(
        "--database",
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
    )
    subpi.add_argument(
        "--expense-db",
        help="The database where the expense collection will be updated "
        "with the presentation-related expense data. "
        "Without a specification, by default the helper attempts to "
        "use the first database in the regolithrc.json file *but "
        "will only do so if that database is non-public*.",
    )
    subpi.add_argument(
        "--force",
        help="Force adding presentation expense data to the first DB listed in "
        "'databases' in the regolithrc.json file, *even if that database is "
        "public*. DANGER: This could reveal sensitive information to the public.",
        action="store_true",
    )
    subpi.add_argument(
        "--id",
        help="Override the default id created from the date, " "speaker and place by specifying an id here",
    )
    return subpi


class PresentationAdderHelper(DbHelperBase):
    """Helper for adding presentations"."""

    # btype must be the same as helper target in helper.py
    btype = "a_presentation"
    needed_colls = [f"{TARGET_COLL}", "groups", "people", "expenses"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]

        if rc.no_expense:
            if rc.expense_db:
                raise RuntimeError(
                    "ERROR: You specified an expense database with the --expense-db option, but also "
                    "passed --no-expense. Do you want to create an expense? Please reformulate your "
                    "helper command and rerun. "
                )
        else:
            rc.expense_db = rc.expense_db if rc.expense_db else None

            if not rc.expense_db and not rc.databases[0].get("public"):
                warn(
                    "WARNING: No expense database was provided to input the expense data "
                    "associated with this presentation. Defaulted to using the first DB "
                    "listed in your regolithrc.json, as this DB is non-public."
                )
                rc.expense_db = rc.databases[0]["name"]

            rc.expense_db = (
                rc.databases[0]["name"]
                if not rc.expense_db and rc.databases[0].get("public") and rc.force
                else rc.expense_db
            )

            if not rc.expense_db and rc.databases[0].get("public") and not rc.force:
                raise RuntimeError(
                    "ERROR: You failed to specify an expense database for the expense data "
                    "associated with this presentation. The helper defaults to entering "
                    "expenses into first database listed in your regolithrc.json file, "
                    "but it set to PUBLIC and would reveal potentially sensitive information. "
                    "Rerun by specifying the target database with --expense-db EXPENSE_DB, or "
                    "(at your own risk) pass the --force flag."
                )

            if rc.expense_db not in [database.get("name") for database in rc.databases]:
                raise RuntimeError(
                    f"ERROR: The expense database specified, {rc.expense_db}, is not listed "
                    "in your regolithrc.json file."
                )

        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc

        if rc.cal:
            event = {
                "summary": rc.name,
                "location": rc.place,
                "start": {"date": rc.begin_date},
                "end": {"date": rc.end_date},
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
        # TODO : add date format check?
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
            key = (
                f"{str(begin_date.year)[2:]}{str(begin_date.strftime('%m'))}{name_key}_"
                f"{''.join(rc.place.casefold().split()).strip()}"
            )
        else:
            key = rc.id

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError("This entry appears to already exist in the collection")
        else:
            pdoc = {}

        if not rc.authors:
            authors = [rc.person]
        else:
            authors = rc.authors

        pdoc.update(
            {
                "_id": key,
                "abstract": rc.abstract,
                "authors": authors,
                "begin_date": begin_date,
                "end_date": end_date,
                "notes": rc.notes,
            }
        )
        if rc.presentation_url:
            pdoc.update({"presentation_url": rc.presentation_url})
        if rc.webinar:
            rc.no_expense = True
            pdoc.update({"webinar": True})
        if rc.type in ["seminar", "colloquium"]:
            pdoc.update({"institution": rc.place, "department": rc.name})
        else:
            pdoc.update({"location": rc.place, "meeting_name": rc.name})
        pdoc.update(
            {
                "project": ["all"],
                "presenter": rc.person,
                "status": rc.status,
                "title": rc.title,
                "talk_id": rc.regolith_talk_id,
                "type": rc.type,
            }
        )

        rc.client.insert_one(rc.database, rc.coll, pdoc)
        print(f"{key} has been added in {TARGET_COLL}")

        if not rc.no_expense:
            rc.business = False
            rc.payee = rc.default_user_id
            rc.purpose = f"give {rc.type} presentation at {rc.name}, {rc.place}"
            rc.where = "tbd"
            rc.status = "unsubmitted"
            edoc = expense_constructor(key, begin_date, end_date, rc)
            rc.client.insert_one(rc.expense_db, EXPENSES_COLL, edoc)
            print(f"{key} has been added in {EXPENSES_COLL} in database {rc.expense_db}")

        if rc.repo:
            if not hasattr(rc, "repos"):
                rc.repos = []
            if not hasattr(rc, "tokens"):
                rc.tokens = []
            for repo in rc.repos:
                if repo.get("_id") == "talk_repo":
                    repo["params"].update({"name": key})
                    if not repo["params"].get("initialize_with_readme"):
                        repo["params"]["initialize_with_readme"] = True
                    repo["params"].update({"name": key.replace("/", "").replace(",", "")})
            msg = create_repo("talk_repo", "gitlab_private_token", rc)
            print(msg)
        return
