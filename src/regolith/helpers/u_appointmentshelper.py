"""Helper for planning and updating a group member's appointments."""

import datetime as dt
from pathlib import Path

from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.appointments import (
    appointment_alerts,
    appointments_from_text,
    appointments_to_text,
    funded_employment,
    gap_appointments,
    new_appointment_id,
    planning_end,
)
from regolith.dates import get_dates, has_dates
from regolith.fsclient import _id_key
from regolith.grant_budget import edit_text
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import (
    all_docs_from_collection,
    fragment_retrieval,
    fuzzy_retrieval,
    merge_collections_superior,
    public_and_private_databases,
    strip_str,
)

TARGET_COLL = "people"


def subparser(subpi):
    date_kwargs = {}
    file_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        file_kwargs["widget"] = "FileChooser"

    subpi.add_argument(
        "person",
        type=strip_str,
        help="The id, name or aka of the group member. Without --edit or --file, their appointments from "
        "today and any alerts about them are printed.",
    )
    subpi.add_argument(
        "--edit",
        action="store_true",
        help="Open their appointments from today in your text editor (set by the EDITOR environment "
        "variable), with the gaps until their position ends filled with proposed appointments on "
        "future_grant. Not available in the helper GUI: use --file there.",
    )
    subpi.add_argument(
        "--file",
        type=strip_str,
        help="A YAML file of appointments, written the way --edit shows them, to replace their "
        "appointments from today with",
        **file_kwargs,
    )
    subpi.add_argument(
        "--group",
        type=strip_str,
        help="The id of the group in the group field of employment. Defaults to the id of the group whose "
        "id, name or aka is the groupname in regolithrc.json.",
    )
    subpi.add_argument(
        "--private-database",
        type=strip_str,
        help="The database for appointments. Defaults to the first database marked private in " "regolithrc.json.",
    )
    # Do not delete --database arg
    subpi.add_argument(
        "-d",
        "--database",
        type=strip_str,
        help="The database that will be updated when regolithrc.json has no private database. Defaults to "
        "the first database in the regolithrc.json file.",
    )
    subpi.add_argument("--date", help="The date to plan from. Defaults to today.", type=strip_str, **date_kwargs)
    subpi.add_argument(
        "--until",
        help="The last date to plan to, if before their position ends. Defaults to five years from today.",
        type=strip_str,
        **date_kwargs,
    )
    return subpi


def _clashes(appointments, earlier):
    return [
        f"{appointment['_id']} is the id of an earlier appointment. Please give it another _id, or none."
        for appointment in appointments
        if appointment.get("_id") in earlier
    ]


def _end_date(appointment):
    return get_dates(dict(appointment)).get("end_date") if has_dates(appointment) else None


class AppointmentsUpdaterHelper(DbHelperBase):
    """Helper for planning and updating a group member's appointments.

    Appointments are kept on the person, in the private database. Each
    is paid by a grant or by outside funding, and the plan runs from
    today until their funded position ends.
    """

    # btype must be the same as helper target in helper.py
    btype = "u-appointments"
    needed_colls = [TARGET_COLL, "grants", "proposals", "groups"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = TARGET_COLL
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        for coll in self.needed_colls:
            gtx[coll] = sorted(all_docs_from_collection(rc.client, coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def _group_id(self):
        rc = self.rc
        if rc.group:
            return rc.group
        groupname = str(rc._get("groupname", "") or "")
        # groupname may be the group's id, its name or one of its akas
        group = fuzzy_retrieval(self.gtx["groups"], ["_id", "name", "aka"], groupname, case_sensitive=False)
        return group["_id"] if group else groupname

    def _all_appointments(self, person_id, appointments):
        everyone = []
        for person in self.gtx[TARGET_COLL]:
            if person["_id"] == person_id:
                continue
            for appointment_id, appointment in (person.get("appointments") or {}).items():
                everyone.append({**appointment, "_id": appointment_id, "person": person["_id"]})
        return everyone + [{**appointment, "person": person_id} for appointment in appointments]

    def _alerts(self, person, appointments, today):
        grants = merge_collections_superior(self.gtx["proposals"], self.gtx["grants"], "proposal_id")
        return appointment_alerts(
            person,
            appointments,
            grants,
            self._all_appointments(person["_id"], appointments),
            self._group_id(),
            today,
            self._until(),
        )

    def _until(self):
        return date_parser.parse(self.rc.until).date() if self.rc.until else None

    def _store(self, person_id, appointments):
        rc = self.rc
        _, private_database = public_and_private_databases(rc.databases, None, rc.private_database)
        holding = [
            database["name"]
            for database in rc.databases
            if (rc.client.find_one(database["name"], rc.coll, {"_id": person_id}) or {}).get("appointments")
        ]
        target = private_database or (holding[-1] if holding else self.where_stored(rc.coll, person_id))
        target = target or rc.database
        rc.client.update_one(
            target, rc.coll, {"_id": person_id}, {"appointments": appointments}, partial=True, upsert=True
        )
        for database in holding:
            if database != target:
                rc.client.update_one(database, rc.coll, {"_id": person_id}, {"appointments": {}}, partial=True)
                print(f"    their appointments were moved from {database} to {target}")
        if not private_database:
            print(
                f"    No database in regolithrc.json is marked private, so the appointments were stored in "
                f'{target}. To keep them private, add a database with "public": false to regolithrc.json.'
            )

    def db_updater(self):
        rc = self.rc
        today = date_parser.parse(rc.date).date() if rc.date else dt.date.today()
        people = self.gtx[TARGET_COLL]
        person = fuzzy_retrieval(people, ["_id", "aka", "name"], rc.person, case_sensitive=False)
        if not person:
            matches = fragment_retrieval(people, ["_id", "aka", "name"], rc.person)
            if not matches:
                raise RuntimeError(
                    f"No one in the people collection matches {rc.person}. "
                    "Please re-run with the id, name or aka of a group member."
                )
            print(f"No one has the id, name or aka {rc.person}. People it might mean:")
            for match in matches:
                print(f"    {match['_id']}     {match.get('name', '')}")
            print("Please re-run the helper giving the complete id.")
            return
        if rc.edit and rc.file:
            raise RuntimeError("Only one of --edit and --file can be given. Please re-run with just one of them.")

        stored = {
            appointment_id: {**appointment, "_id": appointment_id}
            for appointment_id, appointment in (person.get("appointments") or {}).items()
        }
        earlier = {
            appointment_id: appointment
            for appointment_id, appointment in stored.items()
            if _end_date(appointment) and _end_date(appointment) < today
        }
        planned = sorted(
            (appointment for appointment_id, appointment in stored.items() if appointment_id not in earlier),
            key=lambda appointment: (str(appointment.get("begin_date", "")), appointment["_id"]),
        )
        group_id = self._group_id()
        position_ends = [
            position["end_date"] for position in funded_employment(person, group_id) if position["end_date"]
        ]
        end_date = max(position_ends) if position_ends else None
        alerts = self._alerts(person, planned, today)
        plan_end = planning_end(today, self._until())

        if not rc.edit and not rc.file:
            print(appointments_to_text(person, planned, end_date, alerts, plan_end), end="")
            return

        if rc.file:
            appointments, problems = appointments_from_text(Path(rc.file).read_text(encoding="utf-8"))
            problems += _clashes(appointments, earlier)
            if problems:
                raise ValueError(
                    f"The appointments in {rc.file} have these problems:\n    "
                    + "\n    ".join(problems)
                    + "\nPlease correct the file and re-run."
                )
        else:
            plan = sorted(
                planned + gap_appointments(person, planned, group_id, today, self._until()),
                key=lambda appointment: str(appointment.get("begin_date", "")),
            )
            gap_alerts = self._alerts(person, plan, today)
            original_text = appointments_to_text(person, plan, end_date, gap_alerts, plan_end)
            text = original_text
            while True:
                edited_text = edit_text(text)
                if edited_text == original_text:
                    print(f"The appointments of {person['_id']} were not changed.")
                    return
                appointments, problems = appointments_from_text(edited_text)
                problems += _clashes(appointments, earlier)
                if not problems:
                    break
                print("The appointments have these problems:\n    " + "\n    ".join(problems))
                answer = input(
                    "Press Enter to fix them in the editor, or type q and Enter to leave the appointments as "
                    "they were: "
                )
                if answer.strip().lower().startswith("q"):
                    print(f"The appointments of {person['_id']} were not changed.")
                    return
                body = "\n".join(line for line in edited_text.splitlines() if not line.startswith("# PROBLEM: "))
                text = "".join(f"# PROBLEM: {problem}\n" for problem in problems) + body + "\n"

        taken_ids = set(earlier) | {appointment["_id"] for appointment in appointments if appointment.get("_id")}
        for appointment in appointments:
            if not appointment.get("_id"):
                appointment["_id"] = new_appointment_id(appointment, taken_ids)
                taken_ids.add(appointment["_id"])
        updated = {
            appointment_id: {key: value for key, value in appointment.items() if key != "_id"}
            for appointment_id, appointment in {
                **earlier,
                **{appointment["_id"]: appointment for appointment in appointments},
            }.items()
        }
        self._store(person["_id"], updated)
        print(f"The appointments of {person['_id']} have been updated: {len(appointments)} from today on.")
        for alert in self._alerts(person, appointments, today):
            print(f"ALERT: {alert}")
        return
