"""Helper for listing proposals, and the grants seeded from them."""

from regolith.dates import get_dates, has_dates
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.schemas import alloweds
from regolith.tools import all_docs_from_collection, collection_str, key_value_pair_filter

TARGET_COLL = "proposals"
HELPER_TARGET = "l-proposals"
# The order the statuses are listed in, from the ones still in play to the ones decided
STATUS_ORDER = ("inprep", "submitted", "pending", "accepted", "declined")
TITLE_WIDTH = 60


def subparser(subpi):
    subpi.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="list every proposal. By default declined proposals, and proposals already seeded into a "
        "grant, are left out",
    )
    subpi.add_argument(
        "-s",
        "--status",
        nargs="+",
        choices=alloweds["PROPOSAL_STATI"],
        help="list only proposals with these statuses",
    )
    subpi.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="if set, the full title, team, call and notes are printed for each proposal",
    )
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs")
    subpi.add_argument(
        "-k",
        "--keys",
        nargs="+",
        help="Specify what keys to return values from when running --filter. If no argument is given the "
        "default is just the id.",
    )
    return subpi


def _dates(proposal):
    # get_dates writes the months and days it assumes into the dict it is given
    return get_dates(dict(proposal)) if has_dates(proposal) else {}


def _date_range(proposal):
    dates = _dates(proposal)
    begin, end = dates.get("begin_date"), dates.get("end_date")
    if not begin and not end:
        return "dates not set"
    return f"{begin or '?'} to {end or '?'}"


def _amount(proposal):
    amount = proposal.get("amount")
    if not isinstance(amount, (int, float)):
        return "amount not set"
    return f"{proposal.get('currency', '')} {amount:,.0f}".strip()


def _short_title(title):
    return title if len(title) <= TITLE_WIDTH else title[: TITLE_WIDTH - 3] + "..."


def _team_names(proposal):
    names = [member.get("name") for member in proposal.get("team", []) if member.get("name")]
    if not names:
        names = [name for name in [proposal.get("pi"), *proposal.get("authors", [])] if name]
    return list(dict.fromkeys(names))


def _submitted_date(proposal):
    if not (proposal.get("submitted_date") or proposal.get("submitted_year")):
        return None
    return get_dates(dict(proposal), "submitted").get("submitted_date")


class ProposalsListerHelper(SoutHelperBase):
    """Helper for listing proposals.

    Each proposal shows the grant that was seeded from it, if there is
    one, so a proposal still waiting to become a grant is easy to spot.
    """

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [TARGET_COLL, "grants"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = TARGET_COLL
        for coll in self.needed_colls:
            gtx[coll] = sorted(all_docs_from_collection(rc.client, coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        proposals = key_value_pair_filter(self.gtx[TARGET_COLL], rc.filter) if rc.filter else self.gtx[TARGET_COLL]
        grants_of = {}
        for grant in self.gtx["grants"]:
            if grant.get("proposal_id"):
                grants_of.setdefault(grant["proposal_id"], []).append(grant["_id"])
        if rc.status:
            proposals = [proposal for proposal in proposals if proposal.get("status") in rc.status]
        elif not rc.all:
            proposals = [
                proposal
                for proposal in proposals
                if proposal.get("status") != "declined" and proposal["_id"] not in grants_of
            ]
        if rc.keys:
            print(collection_str(proposals, rc.keys), end="")
            return
        if not proposals:
            print("There are no proposals to list. Use --all to list every proposal.")
            return

        statuses = [status for status in STATUS_ORDER if any(p.get("status") == status for p in proposals)]
        statuses += sorted({p.get("status", "no status") for p in proposals} - set(statuses))
        for status in statuses:
            print(f"\n{status}:")
            in_status = [p for p in proposals if p.get("status", "no status") == status]
            in_status.sort(key=lambda p: (str(_dates(p).get("begin_date", "")), p["_id"]), reverse=True)
            for proposal in in_status:
                grants = grants_of.get(proposal["_id"])
                grant_note = f"grant: {', '.join(grants)}" if grants else "no grant yet"
                print(
                    f"  {proposal['_id']} | {proposal.get('funder', 'funder not set')} | {_amount(proposal)} | "
                    f"{_date_range(proposal)} | {grant_note}"
                )
                print(f"      {_short_title(proposal.get('title', 'title not set'))}")
                if rc.verbose:
                    self._print_details(proposal)
        return

    def _print_details(self, proposal):
        details = {
            "title": proposal.get("title") if len(proposal.get("title", "")) > TITLE_WIDTH else None,
            "team": ", ".join(_team_names(proposal)),
            "submitted": _submitted_date(proposal),
            "call": proposal.get("call_for_proposals"),
            "notes": proposal.get("notes"),
        }
        for label, value in details.items():
            if value:
                if isinstance(value, list):
                    value = "; ".join(str(item) for item in value)
                print(f"      {label}: {value}")
