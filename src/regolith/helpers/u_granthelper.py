"""Helper for updating a grant in the grants collection."""

from pathlib import Path

from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.dates import get_dates, has_dates
from regolith.fsclient import _id_key
from regolith.grant_budget import budget_from_text, budget_notes, budget_to_text, edit_text, make_budget
from regolith.helpers.basehelper import DbHelperBase
from regolith.schemas import alloweds
from regolith.tools import (
    PUBLIC_GRANT_FIELDS,
    all_docs_from_collection,
    fragment_retrieval,
    public_and_private_databases,
    strip_str,
    validate_doc,
)

TARGET_COLL = "grants"
# Grant fields set directly from options of the same name
TEXT_FIELDS = ("title", "currency", "funder", "awardnr", "account", "alias", "program", "admin", "institution")
DATE_FIELDS = {"begin_date": "begin", "end_date": "end"}


def subparser(subpi):
    date_kwargs = {}
    notes_kwargs = {}
    file_kwargs = {}
    status_kwargs = {"choices": alloweds["GRANT_STATI"]}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        notes_kwargs["widget"] = "Textarea"
        file_kwargs["widget"] = "FileChooser"
        status_kwargs["widget"] = "Dropdown"

    subpi.add_argument(
        "grant_id",
        type=strip_str,
        help="The id of the grant to update, or a fragment of it to list the grants it matches",
    )
    subpi.add_argument("--awardnr", help="The number of the award from the agency", type=strip_str)
    subpi.add_argument("--account", help="The account number that holds the funds", type=strip_str)
    subpi.add_argument("--begin-date", help="The begin date of the grant", type=strip_str, **date_kwargs)
    subpi.add_argument("--end-date", help="The end date of the grant", type=strip_str, **date_kwargs)
    subpi.add_argument("--amount", help="The amount awarded", type=strip_str)
    subpi.add_argument("--currency", help="The currency of the amount", type=strip_str)
    subpi.add_argument("--title", help="The title of the grant", type=strip_str)
    subpi.add_argument("--funder", help="The agency funding the work", type=strip_str)
    subpi.add_argument("--program", help="The program the work was funded under", type=strip_str)
    subpi.add_argument("--alias", help="A short alias for the grant", type=strip_str)
    subpi.add_argument("--admin", help="The unit or group administering the grant", type=strip_str)
    subpi.add_argument("-i", "--institution", help="The host institution for the grant", type=strip_str)
    subpi.add_argument("--status", help="The new status of the grant", **status_kwargs)
    subpi.add_argument(
        "-n",
        "--notes",
        nargs="+",
        help="Notes to add to the grant's existing notes",
        type=strip_str,
        **notes_kwargs,
    )
    subpi.add_argument(
        "--edit-budget",
        action="store_true",
        help="Open the grant's budget periods in your text editor (set by the EDITOR environment variable). "
        "A grant with no budget starts with one period per grant year. Not available in the helper GUI: "
        "use --budget-file there.",
    )
    subpi.add_argument(
        "--budget-file",
        type=strip_str,
        help="A YAML file of budget periods to replace the grant's budget with, written the way "
        "--edit-budget shows it",
        **file_kwargs,
    )
    subpi.add_argument(
        "--annual-amounts",
        nargs="+",
        type=float,
        help="Replace the budget with one period per grant year, with these amounts, one for each year",
    )
    subpi.add_argument(
        "--public-database",
        type=strip_str,
        help="The database for public details the grant does not have yet: its title, amount, currency, "
        "award number, funder, team and dates. Defaults to the first database marked public in "
        "regolithrc.json.",
    )
    subpi.add_argument(
        "--private-database",
        type=strip_str,
        help="The database for private details the grant does not have yet, such as the account. Defaults "
        "to the first database marked private in regolithrc.json.",
    )
    # Do not delete --database arg
    subpi.add_argument(
        "-d",
        "--database",
        type=strip_str,
        help="The database that will be updated when regolithrc.json has no public and private pair. "
        "Defaults to the first database in the regolithrc.json file.",
    )
    return subpi


def _legacy_fields(grant, prefix):
    return [f"{prefix}_{part}" for part in ("year", "month", "day") if f"{prefix}_{part}" in grant]


class GrantUpdaterHelper(DbHelperBase):
    """Helper for updating a grant in the grants collection.

    Each detail is written to the database that already holds it. A
    detail the grant does not have yet goes to the public database if it
    may be shown publicly, and to the private database otherwise.
    """

    # btype must be the same as helper target in helper.py
    btype = "u-grant"
    needed_colls = [TARGET_COLL]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = TARGET_COLL
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def _updates(self, grant):
        rc = self.rc
        updates = {field: getattr(rc, field) for field in TEXT_FIELDS if getattr(rc, field)}
        for field in DATE_FIELDS:
            value = getattr(rc, field)
            if value:
                updates[field] = date_parser.parse(value).date()
        if rc.amount:
            updates["amount"] = float(rc.amount)
        if rc.status:
            updates["status"] = rc.status
        if rc.notes:
            existing_notes = grant.get("notes")
            updates["notes"] = " ".join(([existing_notes] if existing_notes else []) + rc.notes)
        return updates

    def _budget(self, grant, updated_grant):
        rc = self.rc
        chosen = [option for option in ("edit_budget", "budget_file", "annual_amounts") if getattr(rc, option)]
        if not chosen:
            return None
        if len(chosen) > 1:
            raise RuntimeError(
                f"Only one of --{', --'.join(option.replace('_', '-') for option in chosen)} can be given. "
                "Please re-run with just one of them."
            )
        dates = get_dates(dict(updated_grant)) if has_dates(updated_grant) else {}
        grant_dates = (dates.get("begin_date"), dates.get("end_date"))
        amount = updated_grant.get("amount")
        if rc.annual_amounts or (rc.edit_budget and not grant.get("budget")):
            if not all(grant_dates):
                raise RuntimeError(
                    f"{rc.grant_id} has no begin and end dates, so its budget years are not known. "
                    "Please re-run with --begin-date and --end-date."
                )
        if rc.annual_amounts:
            return make_budget(*grant_dates, annual_amounts=rc.annual_amounts)
        if rc.budget_file:
            budget, problems = budget_from_text(Path(rc.budget_file).read_text(encoding="utf-8"))
            if problems:
                raise ValueError(
                    f"The budget in {rc.budget_file} has these problems:\n    "
                    + "\n    ".join(problems)
                    + "\nPlease correct the file and re-run."
                )
            return budget
        starting_budget = grant.get("budget") or make_budget(*grant_dates, amount=amount)
        original_text = budget_to_text(rc.grant_id, starting_budget, grant_dates, amount)
        text = original_text
        while True:
            edited_text = edit_text(text)
            if edited_text == original_text:
                print(f"The budget of {rc.grant_id} was not changed.")
                return None
            budget, problems = budget_from_text(edited_text)
            if not problems:
                return budget
            print("The budget has these problems:\n    " + "\n    ".join(problems))
            answer = input(
                "Press Enter to fix them in the editor, or type q and Enter to leave the budget as it was: "
            )
            if answer.strip().lower().startswith("q"):
                print(f"The budget of {rc.grant_id} was not changed.")
                return None
            body = "\n".join(line for line in edited_text.splitlines() if not line.startswith("# PROBLEM: "))
            text = "".join(f"# PROBLEM: {problem}\n" for problem in problems) + body + "\n"

    def _target_databases(self, updates):
        rc = self.rc
        parts = {
            database["name"]: rc.client.find_one(database["name"], rc.coll, {"_id": rc.grant_id}) or {}
            for database in rc.databases
        }
        holding_grant = [name for name, part in parts.items() if part]
        public_database, private_database = public_and_private_databases(
            rc.databases, rc.public_database, rc.private_database
        )
        targets = {}
        for field in updates:
            holding_field = [name for name, part in parts.items() if field in part]
            if holding_field:
                # A read takes each field from the last database holding it
                target = holding_field[-1]
            elif field in PUBLIC_GRANT_FIELDS:
                target = public_database or holding_grant[-1]
            else:
                target = private_database or holding_grant[-1]
            targets.setdefault(target, {})[field] = updates[field]
        return targets, private_database

    def db_updater(self):
        rc = self.rc
        grant = next((doc for doc in self.gtx[rc.coll] if doc["_id"] == rc.grant_id), None)
        if not grant:
            matches = fragment_retrieval(self.gtx[rc.coll], ["_id", "alias"], rc.grant_id)
            if not matches:
                raise RuntimeError(
                    f"No grant matches {rc.grant_id}. "
                    "Please re-run with the id, or part of the id, of an existing grant."
                )
            print(f"There is no grant with the id {rc.grant_id}. Grants with similar ids:")
            for match in matches:
                print(f"    {match.get('_id')}     alias: {match.get('alias', '')}")
            print("Please re-run the helper giving the complete id.")
            return

        updates = self._updates(grant)
        budget = self._budget(grant, {**grant, **updates})
        if budget is not None:
            updates["budget"] = budget
        if not updates:
            if rc.edit_budget:
                return
            raise RuntimeError(
                f"Nothing was given to update in {rc.grant_id}. "
                "Please re-run with at least one option, for example --awardnr DMR-0001."
            )
        updated_grant = {**grant, **updates}
        dates = get_dates(dict(updated_grant)) if has_dates(updated_grant) else {}
        begin_date, end_date = dates.get("begin_date"), dates.get("end_date")
        if begin_date and end_date and begin_date > end_date:
            raise ValueError(
                f"The begin date {begin_date} would be after the end date {end_date}. "
                "Please re-run with a begin date that is before the end date."
            )
        valid, error_message = validate_doc(rc.coll, {"_id": rc.grant_id, **updates}, rc, partial=True)
        if not valid:
            raise ValueError(
                f"The update to {rc.grant_id} does not fit the grants schema:\n{error_message}"
                "Please correct the options and re-run."
            )

        targets, private_database = self._target_databases(updates)
        for database, fields in targets.items():
            rc.client.update_one(database, rc.coll, {"_id": rc.grant_id}, fields, partial=True, upsert=True)
        print(f"{rc.grant_id} has been updated in {TARGET_COLL}: {', '.join(sorted(updates))}")
        if len(targets) > 1:
            for database, fields in targets.items():
                print(f"    {', '.join(sorted(fields))} in {database}")
        exposed = [
            field
            for database, fields in targets.items()
            if database != private_database
            for field in fields
            if field not in PUBLIC_GRANT_FIELDS
        ]
        if exposed and not private_database:
            print(
                f"    No database in regolithrc.json is marked private, so {', '.join(sorted(exposed))} went to "
                'a public database. To keep them private, add a database with "public": false to '
                "regolithrc.json."
            )
        if "budget" in updates:
            dates = get_dates(dict(updated_grant)) if has_dates(updated_grant) else {}
            for note in budget_notes(
                updates["budget"], (dates.get("begin_date"), dates.get("end_date")), updated_grant.get("amount")
            ):
                print(f"Note: {note}")
        for field, prefix in DATE_FIELDS.items():
            stale = _legacy_fields(grant, prefix) if field in updates else []
            if stale:
                print(
                    f"Note: {rc.grant_id} still has {', '.join(stale)}. The new {field} is used in their place, "
                    "but you may want to delete them from the database by hand."
                )
        return
