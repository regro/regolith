"""Helper for listing what a person's record holds."""

import io

from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.dates import get_dates, has_dates
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.person_records import PEOPLE_COLL, _yaml, find_person, person_parts
from regolith.tools import all_docs_from_collection, strip_str

HELPER_TARGET = "l-person"
# The details shown first, in this order
SUMMARY_FIELDS = ("name", "aka", "title", "position", "email", "github_id", "orcid_id", "active", "office")


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
    subpi.add_argument(
        "person",
        type=strip_str,
        help="The id, name or aka of the person, or part of one to list the people it matches",
    )
    subpi.add_argument(
        "-f",
        "--field",
        nargs="+",
        type=strip_str,
        help="The fields to show in full, such as service or employment, grouped by the database each part is "
        "stored in, as u_person --edit shows them",
    )
    subpi.add_argument(
        "--since",
        type=strip_str,
        help="Show only the entries of a list that end on or after this date, or have no dates",
        **date_kwargs,
    )
    subpi.add_argument("-v", "--verbose", action="store_true", help="Show every field in full")
    return subpi


def _ends_on_or_after(entry, since):
    if not isinstance(entry, dict) or not has_dates(entry):
        return True
    dates = get_dates(dict(entry))
    last = dates.get("end_date") or dates.get("date") or dates.get("begin_date")
    return last is None or last >= since


SHOWN_LENGTH = 60


def _count(value):
    if isinstance(value, (list, dict)):
        return f"{len(value)} {'entry' if len(value) == 1 else 'entries'}"
    text = " ".join(str(value).split())
    return text if len(text) <= SHOWN_LENGTH else text[: SHOWN_LENGTH - 3] + "..."


class PersonListerHelper(SoutHelperBase):
    """Helper for listing what a person's record holds.

    It shows where each part is stored, so it can be read alongside
    u_person, which writes each part back to its own database.
    """

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [PEOPLE_COLL]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        rc = self.rc
        self.gtx[PEOPLE_COLL] = sorted(all_docs_from_collection(rc.client, PEOPLE_COLL), key=_id_key)

    def sout(self):
        rc = self.rc
        person, candidates = find_person(self.gtx[PEOPLE_COLL], rc.person)
        # Listing changes nothing, so a single person whose name contains what was given is shown
        if not person and len(candidates) == 1:
            person = candidates[0]
        if not person:
            if not candidates:
                print(f"No one in the people collection matches {rc.person}.")
                return
            print(f"No single person has the id, name or aka {rc.person}. People it might mean:")
            for candidate in candidates:
                print(f"    {candidate['_id']}     {candidate.get('name', '')}")
            return
        since = date_parser.parse(rc.since).date() if rc.since else None
        parts = person_parts(rc, person["_id"])
        visibility = {
            database["name"]: "public" if database.get("public") else "private" for database in rc.databases
        }
        print(f"{person['_id']}: {person.get('name', '')}")
        for field in SUMMARY_FIELDS:
            if field != "name" and person.get(field) not in (None, "", []):
                value = person[field]
                print(f"    {field}: {', '.join(value) if isinstance(value, list) else value}")
        fields = sorted({field for part in parts.values() for field in part if field != "_id"})
        if rc.verbose:
            shown = [field for field in fields if field not in SUMMARY_FIELDS]
        else:
            shown = [field for field in (rc.field or []) if field in fields]
            missing = [field for field in (rc.field or []) if field not in fields]
            if missing:
                print(f"    {person['_id']} has no {', '.join(missing)}")
        print("    stored in:")
        for field in fields:
            if field in SUMMARY_FIELDS:
                continue
            where = [f"{_count(part[field])} in {name}" for name, part in parts.items() if field in part]
            print(f"        {field}: {'; '.join(where)}")
        for field in shown:
            print(f"\n# {field}, under the database each part is stored in, as u_person --edit {field} shows it:")
            for name, part in parts.items():
                if field in part:
                    print(f"#   {name} is {visibility[name]}")
            if since:
                print(f"# Only the entries ending on or after {since} are shown, so do not use this as a --file.")
            grouped = {}
            for name, part in parts.items():
                if field not in part:
                    continue
                value = part[field]
                if since and isinstance(value, list):
                    value = [entry for entry in value if _ends_on_or_after(entry, since)]
                grouped[name] = value
            stream = io.StringIO()
            _yaml().dump(grouped, stream)
            print(stream.getvalue(), end="")
        if not shown and not rc.verbose:
            print(f"Show a field in full with l_person {person['_id']} --field <field>, e.g. --field service")
        return
