"""Helper for adding a group member to the people collection."""

import datetime as dt
import unicodedata

from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.person_records import PEOPLE_COLL, person_names
from regolith.schemas import alloweds
from regolith.tools import all_docs_from_collection, fuzzy_retrieval, public_and_private_databases, strip_str

# The status that goes with a position, when none is given
POSITION_STATUS = {
    "graduate research assistant": "phd",
    "post-doctoral scholar": "postdoc",
    "undergraduate research assistant": "undergrad",
    "masters research assistant": "ms",
}


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
    subpi.add_argument("name", type=strip_str, help="The person's full name, e.g. Ada Lovelace")
    subpi.add_argument(
        "--id",
        type=strip_str,
        help="The id for the person. Defaults to their first initial and last name, e.g. alovelace",
    )
    subpi.add_argument(
        "--aka", nargs="+", type=strip_str, help="Other names they are known by, besides their name"
    )
    # Stored as person_email, since email is regolith's own setting for sending email
    subpi.add_argument("--email", dest="person_email", type=strip_str, help="Their email address")
    subpi.add_argument("--github-id", type=strip_str, help="Their GitHub id")
    subpi.add_argument("--orcid-id", type=strip_str, help="Their ORCID id")
    subpi.add_argument("--title", type=strip_str, help="Their title, e.g. Dr.")
    subpi.add_argument(
        "--position",
        default="graduate research assistant",
        choices=alloweds["SORTED_POSITION"],
        help="Their position in the group. Defaults to graduate research assistant.",
    )
    subpi.add_argument(
        "--status",
        choices=alloweds["POSITION_STATI"],
        help="Their status, e.g. phd. Defaults to the usual one for their position.",
    )
    subpi.add_argument(
        "--organization", required=True, type=strip_str, help="The id or name of the institution employing them"
    )
    subpi.add_argument("--department", type=strip_str, help="The id or name of their department")
    subpi.add_argument(
        "--begin-date", type=strip_str, help="The day they start in the group. Defaults to today.", **date_kwargs
    )
    subpi.add_argument(
        "--end-date",
        type=strip_str,
        help="The day they are expected to leave, e.g. graduate. Planning appointments needs it.",
        **date_kwargs,
    )
    subpi.add_argument(
        "--group",
        type=strip_str,
        help="The id of their group. Defaults to the group whose id, name or aka is the groupname in "
        "regolithrc.json.",
    )
    # Do not delete --database arg
    subpi.add_argument(
        "-d",
        "--database",
        type=strip_str,
        help="The database the person is added to. Defaults to the first database marked public in "
        "regolithrc.json.",
    )
    return subpi


def default_id(name):
    """Return an id made from a name's first initial and last name.

    Parameters
    ----------
    name : str
        The full name.

    Returns
    -------
    str
        The id, in lower case letters only, e.g. alovelace for Ada
        Lovelace.
    """
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    words = [word for word in plain.replace("-", " ").split() if word.strip(".")]
    if not words:
        return ""
    first, last = words[0], words[-1]
    return "".join(character for character in (first[0] + last).lower() if character.isalnum())


class PersonAdderHelper(DbHelperBase):
    """Helper for adding a group member to the people collection.

    The person is added to the public database with their position in
    the group, so that it shows on the group pages and appointments can
    be planned for them.
    """

    # btype must be the same as helper target in helper.py
    btype = "a-person"
    needed_colls = [PEOPLE_COLL, "groups", "contacts"]

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

    def db_updater(self):
        rc = self.rc
        person_id = rc.id or default_id(rc.name)
        if not person_id:
            raise ValueError(f"No id could be made from the name {rc.name}. Please re-run giving one with --id.")
        wanted = {str(name).casefold() for name in [person_id, rc.name] + (rc.aka or [])}
        clashes = [
            person
            for person in self.gtx[PEOPLE_COLL]
            if any(str(name).casefold() in wanted for name in person_names(person) if name)
        ]
        if clashes:
            raise RuntimeError(
                f"{rc.name} may already be in the people collection, as "
                + ", ".join(f"{person['_id']} ({person.get('name', '')})" for person in clashes)
                + ". Please update them with u_person, or re-run with a different --id if this is someone else."
            )
        today = dt.date.today()
        employment = {
            "position": rc.position,
            "organization": rc.organization,
            "group": self._group_id(),
            "begin_date": date_parser.parse(rc.begin_date).date() if rc.begin_date else today,
        }
        if rc.end_date:
            employment["end_date"] = date_parser.parse(rc.end_date).date()
            if employment["end_date"] < employment["begin_date"]:
                raise ValueError(
                    f"The end date {employment['end_date']} is before the begin date {employment['begin_date']}. "
                    "Please re-run with an end date after the begin date."
                )
        if rc.department:
            employment["department"] = rc.department
        status = rc.status or POSITION_STATUS.get(rc.position)
        if status:
            employment["status"] = status
        person = {
            "_id": person_id,
            "name": rc.name,
            "aka": [rc.name] + [aka for aka in (rc.aka or []) if aka != rc.name],
            "active": True,
            "position": rc.position,
            "avatar": "",
            "bio": "",
            "education": [],
            "employment": [employment],
        }
        if rc.person_email:
            person["email"] = rc.person_email
        for field in ("github_id", "orcid_id", "title"):
            if getattr(rc, field):
                person[field] = getattr(rc, field)
        public_database, _ = public_and_private_databases(rc.databases)
        database = public_database or rc.database
        rc.client.insert_one(database, PEOPLE_COLL, person)
        print(f"{person_id} has been added in {PEOPLE_COLL} in {database}")
        if not rc.end_date:
            print(
                f"    No end date was given. Add the date they are expected to leave with u_person {person_id} "
                "--end-date, so their appointments can be planned."
            )
        else:
            print(f"    Plan their appointments with u_appointments {person_id} --edit")
        return
