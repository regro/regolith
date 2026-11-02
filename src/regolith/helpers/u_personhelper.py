"""Helper for updating a person in the people collection."""

import copy
from pathlib import Path

from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.dates import get_dates, has_dates
from regolith.fsclient import _id_key
from regolith.grant_budget import edit_text
from regolith.helpers.basehelper import DbHelperBase
from regolith.person_records import (
    PEOPLE_COLL,
    database_for,
    find_person,
    person_parts,
    section_from_text,
    section_to_text,
    write_field,
)
from regolith.schemas import SCHEMAS
from regolith.tools import all_docs_from_collection, fuzzy_retrieval, strip_str

# Fields set directly from options of the same name
TEXT_FIELDS = ("name", "github_id", "orcid_id", "title", "position", "office", "bio", "initials")
# Fields that hold lists or dicts, which are changed in the editor
EDITABLE_FIELDS = sorted(
    field
    for field, rule in SCHEMAS[PEOPLE_COLL].items()
    if isinstance(rule, dict) and rule.get("type") in ("list", "dict")
)


def subparser(subpi):
    date_kwargs = {}
    file_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        file_kwargs["widget"] = "FileChooser"
    subpi.add_argument(
        "person",
        type=strip_str,
        help="The id, name or aka of the person to update, or part of one to list the people it matches",
    )
    subpi.add_argument("--name", type=strip_str, help="Their full, canonical name")
    subpi.add_argument(
        "--add-aka", nargs="+", type=strip_str, help="Other names to add to those they are known by"
    )
    # Stored as person_email, since email is regolith's own setting for sending email
    subpi.add_argument("--email", dest="person_email", type=strip_str, help="Their email address")
    subpi.add_argument("--github-id", type=strip_str, help="Their GitHub id")
    subpi.add_argument("--orcid-id", type=strip_str, help="Their ORCID id")
    subpi.add_argument("--title", type=strip_str, help="Their title, e.g. Dr.")
    subpi.add_argument("--position", type=strip_str, help="Their position, as shown on group pages")
    subpi.add_argument("--office", type=strip_str, help="Their office")
    subpi.add_argument("--bio", type=strip_str, help="A short biography")
    subpi.add_argument("--initials", type=strip_str, help="Their initials")
    activity = subpi.add_mutually_exclusive_group()
    activity.add_argument("--active", dest="active", action="store_const", const=True, help="Mark them active")
    activity.add_argument(
        "--inactive", dest="active", action="store_const", const=False, help="Mark them inactive"
    )
    subpi.add_argument(
        "--end-date",
        type=strip_str,
        help="The day they are expected to leave their current position in the group, e.g. graduate",
        **date_kwargs,
    )
    subpi.add_argument(
        "--edit",
        choices=EDITABLE_FIELDS,
        help="Open one of their lists, such as employment, education or service, in your text editor (set by "
        "the EDITOR environment variable), grouped by the database each part is stored in. Not available in "
        "the helper GUI: use --file there.",
    )
    subpi.add_argument(
        "--file",
        type=strip_str,
        help="A YAML file to replace the list named by --edit with, written the way --edit shows it",
        **file_kwargs,
    )
    subpi.add_argument(
        "--group",
        type=strip_str,
        help="The id of the group, for --end-date. Defaults to the group whose id, name or aka is the "
        "groupname in regolithrc.json.",
    )
    return subpi


class PersonUpdaterHelper(DbHelperBase):
    """Helper for updating a person in the people collection.

    Simple details are options. Lists such as employment and service are
    changed in your text editor. Each change is written to the database
    that holds that part of their record.
    """

    # btype must be the same as helper target in helper.py
    btype = "u-person"
    needed_colls = [PEOPLE_COLL, "groups"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = PEOPLE_COLL
        for coll in self.needed_colls:
            gtx[coll] = sorted(all_docs_from_collection(rc.client, coll), key=_id_key)

    def _group_id(self):
        rc = self.rc
        if rc.group:
            return rc.group
        groupname = str(rc._get("groupname", "") or "")
        group = fuzzy_retrieval(self.gtx["groups"], ["_id", "name", "aka"], groupname, case_sensitive=False)
        return group["_id"] if group else groupname

    def _end_current_position(self, person_id, parts, end_date):
        group_id = self._group_id()
        positions = [
            (name, index, get_dates(dict(entry)).get("begin_date"))
            for name, part in parts.items()
            for index, entry in enumerate(part.get("employment") or [])
            if entry.get("group") == group_id and has_dates(entry)
        ]
        if not positions:
            raise RuntimeError(
                f"{person_id} has no position in the group {group_id} in employment. Please add one with "
                f"u_person {person_id} --edit employment, or give the group with --group."
            )
        database, index, begin_date = max(positions, key=lambda position: str(position[2]))
        if begin_date and end_date < begin_date:
            raise ValueError(
                f"The end date {end_date} is before their position began on {begin_date}. "
                "Please re-run with a later end date."
            )
        employment = copy.deepcopy(list(parts[database]["employment"]))
        employment[index] = {
            key: value
            for key, value in dict(employment[index]).items()
            if key not in ("end_year", "end_month", "end_day")
        }
        employment[index]["end_date"] = end_date
        write_field(self.rc, database, person_id, "employment", employment)
        return database

    def _edit(self, person, parts):
        rc = self.rc
        original_text = section_to_text(person, rc.edit, parts, rc.databases)
        if rc.file:
            changes, problems = section_from_text(
                Path(rc.file).read_text(encoding="utf-8"), rc.edit, person["_id"], parts, rc.schemas
            )
            if problems:
                raise ValueError(
                    f"The {rc.edit} in {rc.file} has these problems:\n    "
                    + "\n    ".join(problems)
                    + "\nPlease correct the file and re-run."
                )
            return changes
        text = original_text
        while True:
            edited_text = edit_text(text)
            if edited_text == original_text:
                return {}
            changes, problems = section_from_text(edited_text, rc.edit, person["_id"], parts, rc.schemas)
            if not problems:
                return changes
            print(f"The {rc.edit} has these problems:\n    " + "\n    ".join(problems))
            answer = input(
                f"Press Enter to fix them in the editor, or type q and Enter to leave the {rc.edit} as it was: "
            )
            if answer.strip().lower().startswith("q"):
                return {}
            body = "\n".join(line for line in edited_text.splitlines() if not line.startswith("# PROBLEM: "))
            text = "".join(f"# PROBLEM: {problem}\n" for problem in problems) + body + "\n"

    def db_updater(self):
        rc = self.rc
        person, candidates = find_person(self.gtx[PEOPLE_COLL], rc.person)
        if not person:
            if not candidates:
                raise RuntimeError(
                    f"No one in the people collection matches {rc.person}. "
                    "Please re-run with the id, name or aka of a person, or add them with a_person."
                )
            print(f"No single person has the id, name or aka {rc.person}. People it might mean:")
            for candidate in candidates:
                print(f"    {candidate['_id']}     {candidate.get('name', '')}")
            print("Please re-run the helper giving the complete id.")
            return
        if rc.file and not rc.edit:
            raise RuntimeError(
                "--file needs --edit to say which list it holds. Please re-run with --edit, e.g. --edit service."
            )
        person_id = person["_id"]
        parts = person_parts(rc, person_id)
        updated = []
        for field in TEXT_FIELDS:
            value = getattr(rc, field)
            if value:
                database = database_for(rc, parts, field)
                write_field(rc, database, person_id, field, value)
                updated.append(f"{field} in {database}")
        if rc.person_email:
            database = database_for(rc, parts, "email")
            write_field(rc, database, person_id, "email", rc.person_email)
            updated.append(f"email in {database}")
        if rc.active is not None:
            database = database_for(rc, parts, "active")
            write_field(rc, database, person_id, "active", rc.active)
            updated.append(f"active in {database}")
        if rc.add_aka:
            database = database_for(rc, parts, "aka")
            aka = parts[database].get("aka") or []
            aka = [aka] if isinstance(aka, str) else list(aka)
            write_field(rc, database, person_id, "aka", aka + [name for name in rc.add_aka if name not in aka])
            updated.append(f"aka in {database}")
        if rc.end_date:
            database = self._end_current_position(person_id, parts, date_parser.parse(rc.end_date).date())
            updated.append(f"the end date of their position in {database}")
        if rc.edit:
            changes = self._edit(person, parts)
            if not changes and not updated:
                print(f"The {rc.edit} of {person_id} was not changed.")
                return
            for database, value in changes.items():
                write_field(rc, database, person_id, rc.edit, value)
                updated.append(f"{rc.edit} in {database}")
        if not updated:
            raise RuntimeError(
                f"Nothing was given to update for {person_id}. "
                "Please re-run with at least one option, for example --email or --edit service."
            )
        print(f"{person_id} has been updated: {', '.join(updated)}")
        return
