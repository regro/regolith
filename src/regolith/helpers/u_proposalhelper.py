"""Helper for updating a proposal in the proposals collection."""

import datetime as dt

from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.schemas import alloweds
from regolith.tools import all_docs_from_collection, fragment_retrieval, strip_str

TARGET_COLL = "proposals"
DATE_OPTIONS = {
    "begin_date": "begin",
    "end_date": "end",
    "due_date": None,
    "submitted_date": "submitted",
}
SUBMITTED_STATI = ("submitted", "pending")


def subparser(subpi):
    date_kwargs = {}
    notes_kwargs = {}
    status_kwargs = {"choices": alloweds["PROPOSAL_STATI"]}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        notes_kwargs["widget"] = "Textarea"
        status_kwargs["widget"] = "Dropdown"

    subpi.add_argument(
        "proposal_id",
        type=strip_str,
        help="The id of the proposal to update, or a fragment of it to list the proposals it matches",
    )
    subpi.add_argument(
        "--status",
        help="The new status. Use pending once the proposal is submitted and awaiting a decision, "
        "so that it appears in the current and pending form. Setting submitted or pending also "
        "records today as the submitted date if the proposal has none.",
        **status_kwargs,
    )
    subpi.add_argument(
        "--submitted-date", help="The date the proposal was submitted", type=strip_str, **date_kwargs
    )
    subpi.add_argument("--due-date", help="The due date for the proposal", type=strip_str, **date_kwargs)
    subpi.add_argument("--begin-date", help="The begin date for the proposed grant", type=strip_str, **date_kwargs)
    subpi.add_argument("--end-date", help="The end date for the proposed grant", type=strip_str, **date_kwargs)
    subpi.add_argument("--amount", help="The requested amount", type=strip_str)
    subpi.add_argument("--title", help="The title of the proposal", type=strip_str)
    subpi.add_argument(
        "--call-for-proposals", help="The URL of the solicitation or call for proposals", type=strip_str
    )
    subpi.add_argument(
        "-n",
        "--notes",
        nargs="+",
        help="Notes to add to the proposal's existing notes",
        type=strip_str,
        **notes_kwargs,
    )
    # Do not delete --database arg
    subpi.add_argument(
        "-d",
        "--database",
        type=strip_str,
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
    )
    subpi.add_argument("--date", help="The date that will be used for testing.", type=strip_str, **date_kwargs)
    return subpi


def _legacy_fields(proposal, prefix):
    return [f"{prefix}_{part}" for part in ("year", "month", "day") if f"{prefix}_{part}" in proposal]


class ProposalUpdaterHelper(DbHelperBase):
    """Helper for updating a proposal in the proposals collection.

    Use it to move a proposal through its statuses and to correct its
    details as they change.
    """

    # btype must be the same as helper target in helper.py
    btype = "u-proposal"
    needed_colls = [f"{TARGET_COLL}"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        today = date_parser.parse(rc.date).date() if rc.date else dt.date.today()
        filterid = {"_id": rc.proposal_id}
        proposal = rc.client.find_one(rc.database, rc.coll, filterid)
        if not proposal:
            matches = fragment_retrieval(self.gtx[rc.coll], ["_id"], rc.proposal_id)
            if not matches:
                raise RuntimeError(
                    f"No proposal matches {rc.proposal_id}. "
                    "Please re-run with the id, or part of the id, of an existing proposal."
                )
            print(f"There is no proposal with the id {rc.proposal_id}. Proposals with similar ids:")
            for match in matches:
                print(f"    {match.get('_id')}     status: {match.get('status')}")
            print("Please re-run the helper giving the complete id.")
            return

        updates = {}
        if rc.status:
            updates["status"] = rc.status
        for field in DATE_OPTIONS:
            value = getattr(rc, field)
            if value:
                updates[field] = date_parser.parse(value).date()
        if rc.status in SUBMITTED_STATI and "submitted_date" not in updates and not proposal.get("submitted_date"):
            updates["submitted_date"] = today
        if rc.amount:
            updates["amount"] = float(rc.amount)
        if rc.title:
            updates["title"] = rc.title
        if rc.call_for_proposals:
            updates["call_for_proposals"] = rc.call_for_proposals
        if rc.notes:
            existing_notes = proposal.get("notes", [])
            if isinstance(existing_notes, str):
                existing_notes = [existing_notes]
            updates["notes"] = existing_notes + rc.notes
        if not updates:
            raise RuntimeError(
                f"Nothing was given to update in {rc.proposal_id}. "
                "Please re-run with at least one option, for example --status pending."
            )

        begin_date = updates.get("begin_date", proposal.get("begin_date"))
        end_date = updates.get("end_date", proposal.get("end_date"))
        if isinstance(begin_date, str):
            begin_date = date_parser.parse(begin_date).date()
        if isinstance(end_date, str):
            end_date = date_parser.parse(end_date).date()
        if isinstance(begin_date, dt.date) and isinstance(end_date, dt.date) and begin_date > end_date:
            raise ValueError(
                f"The begin date {begin_date} would be after the end date {end_date}. "
                "Please re-run with a begin date that is before the end date."
            )

        rc.client.update_one(rc.database, rc.coll, filterid, updates)
        print(f"{rc.proposal_id} has been updated in {TARGET_COLL}: {', '.join(sorted(updates))}")
        for field, prefix in DATE_OPTIONS.items():
            if field in updates and prefix:
                stale = _legacy_fields(proposal, prefix)
                if stale:
                    print(
                        f"Note: {rc.proposal_id} still has {', '.join(stale)}. The new {field} is used in "
                        "their place, but you may want to delete them from the database by hand."
                    )
        return
