"""Helper for adding a service entry to a person in the people
collection."""

from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.person_records import PEOPLE_COLL, find_person, person_parts, validate_field, write_field
from regolith.schemas import alloweds
from regolith.tools import all_docs_from_collection, get_uuid, public_and_private_databases, strip_str


def subparser(subpi):
    date_kwargs = {}
    notes_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        notes_kwargs["widget"] = "Textarea"
    subpi.add_argument(
        "name", type=strip_str, help="What the service is, e.g. Program committee, ACA annual meeting 2027"
    )
    subpi.add_argument(
        "--person",
        type=strip_str,
        help="The id, name or aka of the person who served. Defaults to default_user_id in your user config.",
    )
    subpi.add_argument(
        "--type",
        default="profession",
        choices=alloweds["SERVICE_TYPES"],
        help="The kind of service. Defaults to profession.",
    )
    subpi.add_argument("--role", type=strip_str, help="The role played, e.g. chair")
    subpi.add_argument("--date", type=strip_str, help="The date of a one-off service", **date_kwargs)
    subpi.add_argument("--begin-date", type=strip_str, help="The date the service began", **date_kwargs)
    subpi.add_argument("--end-date", type=strip_str, help="The date the service ended", **date_kwargs)
    subpi.add_argument("--description", type=strip_str, help="A sentence or two on what it involved")
    subpi.add_argument("-n", "--notes", nargs="+", type=strip_str, help="Notes about it", **notes_kwargs)
    subpi.add_argument(
        "--private",
        action="store_true",
        help="Keep it in the private database, e.g. for an ad hoc promotion committee. By default it goes in "
        "the public one.",
    )
    return subpi


def _dates(entry):
    return tuple(str(entry.get(field, "")) for field in ("date", "begin_date", "end_date", "year", "begin_year"))


class ServiceAdderHelper(DbHelperBase):
    """Helper for adding a service entry to a person.

    The entry is given a uuid, so builders such as the synergistic
    activities can select it.
    """

    # btype must be the same as helper target in helper.py
    btype = "a-service"
    needed_colls = [PEOPLE_COLL]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        rc = self.rc
        rc.coll = PEOPLE_COLL
        self.gtx[PEOPLE_COLL] = sorted(all_docs_from_collection(rc.client, PEOPLE_COLL), key=_id_key)

    def db_updater(self):
        rc = self.rc
        wanted = rc.person or rc._get("default_user_id")
        if not wanted:
            raise RuntimeError(
                "No person was given and there is no default_user_id in your user config. "
                "Please re-run with --person."
            )
        person, candidates = find_person(self.gtx[PEOPLE_COLL], wanted)
        if not person:
            offered = ", ".join(f"{candidate['_id']} ({candidate.get('name', '')})" for candidate in candidates)
            raise RuntimeError(
                f"No single person has the id, name or aka {wanted}."
                + (f" People it might mean: {offered}." if offered else "")
                + " Please re-run with the id of the person."
            )
        if rc.date and (rc.begin_date or rc.end_date):
            raise RuntimeError(
                "Both a date and begin or end dates were given. Please re-run with --date for a one-off "
                "service, or --begin-date and --end-date for one that ran for a while."
            )
        entry = {"name": rc.name, "type": rc.type}
        for field in ("date", "begin_date", "end_date"):
            if getattr(rc, field):
                entry[field] = date_parser.parse(getattr(rc, field)).date()
        if entry.get("begin_date") and entry.get("end_date") and entry["begin_date"] > entry["end_date"]:
            raise ValueError(
                f"The begin date {entry['begin_date']} is after the end date {entry['end_date']}. "
                "Please re-run with a begin date before the end date."
            )
        for field in ("role", "description"):
            if getattr(rc, field):
                entry[field] = getattr(rc, field)
        if rc.notes:
            entry["notes"] = rc.notes
        duplicates = [
            existing
            for existing in person.get("service") or []
            if str(existing.get("name", "")).casefold() == rc.name.casefold() and _dates(existing) == _dates(entry)
        ]
        if duplicates:
            raise RuntimeError(
                f"{person['_id']} already has the service {rc.name} with these dates. "
                "Please change it with u_person --edit service instead."
            )
        entry["uuid"] = get_uuid()
        problems = validate_field("service", [entry], person["_id"], rc.schemas)
        if problems:
            raise ValueError(
                "The service entry does not fit the people schema:\n    "
                + "\n    ".join(problems)
                + "\nPlease correct it and re-run."
            )

        public_database, private_database = public_and_private_databases(rc.databases)
        database = (private_database if rc.private else public_database) or rc.database
        parts = person_parts(rc, person["_id"])
        write_field(rc, database, person["_id"], "service", list(parts[database].get("service") or []) + [entry])
        print(f"The service {rc.name} has been added to {person['_id']} in {database}")
        if rc.private and not private_database:
            print(
                f"    No database in regolithrc.json is marked private, so it went to {database}. To keep it "
                'private, add a database with "public": false to regolithrc.json.'
            )
        return
