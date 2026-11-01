"""Helper for adding a grant to the grants collection, optionally seeded
from a funded proposal."""

from dateutil import parser as date_parser
from gooey import GooeyParser

from regolith.dates import get_dates
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import (
    MISSING_INFO,
    all_docs_from_collection,
    fragment_retrieval,
    fuzzy_retrieval,
    get_person_affiliation,
    get_pi_id,
    public_and_private_databases,
    split_grant,
    strip_str,
    validate_doc,
)

TARGET_COLL = "grants"
PROPOSAL_COLL = "proposals"
# Proposal fields copied to the grant unchanged
COPIED_FIELDS = ("title", "amount", "currency", "funder", "call_for_proposals")
# Proposal cpp_info fields and the grant fields they become
CPP_INFO_FIELDS = {
    "institution": "institution",
    "person_months_academic": "person_months_academic",
    "person_months_summer": "person_months_summer",
    "project_scope": "scope",
}
# Proposals with these statuses may still be funded and seeded into a grant
SEEDABLE_STATI = ("submitted", "pending", "accepted")
TEAM_FIELDS = ("name", "position", "institution", "cv", "subaward_amount", "admin_people")
# Grant fields set directly from options of the same name
OPTION_FIELDS = ("title", "funder", "currency", "institution", "awardnr", "account", "alias", "program", "admin")


def subparser(subpi):
    date_kwargs = {}
    notes_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        notes_kwargs["widget"] = "Textarea"

    subpi.add_argument("grant_id", help="A short but unique id for the grant, e.g., dmref26", type=strip_str)
    subpi.add_argument(
        "--from-proposal",
        help="The id of the funded proposal to seed the grant from. Its title, amount, dates, team and "
        "other details are copied, the options below override them, and the proposal is marked accepted.",
        type=strip_str,
    )
    subpi.add_argument(
        "--begin-date",
        help="The actual begin date of the grant, if not as proposed",
        type=strip_str,
        **date_kwargs,
    )
    subpi.add_argument(
        "--end-date", help="The actual end date of the grant, if not as proposed", type=strip_str, **date_kwargs
    )
    subpi.add_argument("--amount", help="The amount awarded, if not as proposed", type=strip_str)
    subpi.add_argument("--title", help="The title of the grant, if not as proposed", type=strip_str)
    subpi.add_argument("--funder", help="The agency funding the work", type=strip_str)
    subpi.add_argument("--currency", help="The currency of the amount, if not as proposed", type=strip_str)
    subpi.add_argument("-i", "--institution", help="The host institution for the grant", type=strip_str)
    subpi.add_argument(
        "-p",
        "--pi",
        help="The id of the principal investigator, when not seeding from a proposal. Defaults to the "
        "group pi id in regolithrc.json",
        type=strip_str,
    )
    subpi.add_argument("--awardnr", help="The number of the award from the agency", type=strip_str)
    subpi.add_argument("--account", help="The account number that holds the funds", type=strip_str)
    subpi.add_argument("--alias", help="A short alias for the grant", type=strip_str)
    subpi.add_argument("--program", help="The program the work was funded under", type=strip_str)
    subpi.add_argument("--admin", help="The unit or group administering the grant", type=strip_str)
    subpi.add_argument("-n", "--notes", nargs="+", help="Notes about the grant", type=strip_str, **notes_kwargs)
    subpi.add_argument(
        "--public-database",
        type=strip_str,
        help="The database for the public part of the grant: its title, amount, currency, award number, "
        "funder, team and dates. Defaults to the first database marked public in regolithrc.json.",
    )
    subpi.add_argument(
        "--private-database",
        type=strip_str,
        help="The database for the rest of the grant, such as the account and budget. Defaults to the "
        "first database marked private in regolithrc.json.",
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


def _proposal_dates(proposal):
    # get_dates writes the months and days it assumes into the dict it is given
    return get_dates(dict(proposal))


def _proposal_team(proposal, people):
    team = [
        {key: member[key] for key in TEAM_FIELDS if key in member}
        for member in proposal.get("team", [])
        if member.get("name")
    ]
    if team:
        return team
    investigators = [(proposal["pi"], "pi")] if proposal.get("pi") else []
    investigators.extend((author, "copi") for author in proposal.get("authors", []))
    for name, position in investigators:
        person = fuzzy_retrieval(people, ["_id", "aka", "name"], name, case_sensitive=False)
        canonical_name = person["name"] if person else name
        if all(member["name"] != canonical_name for member in team):
            team.append({"name": canonical_name, "position": position})
    return team


class GrantAdderHelper(DbHelperBase):
    """Helper for adding a grant to the grants collection.

    When a proposal is funded, seed the grant from it with
    --from-proposal and override whatever changed, such as the actual
    begin date or the amount awarded.
    """

    # btype must be the same as helper target in helper.py
    btype = "a-grant"
    needed_colls = [TARGET_COLL, PROPOSAL_COLL, "people", "contacts", "institutions", "groups"]

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

    def _find_proposal(self, proposal_id):
        proposals = self.gtx[PROPOSAL_COLL]
        proposal = next((doc for doc in proposals if doc["_id"] == proposal_id), None)
        if proposal:
            return proposal
        matches = fragment_retrieval(proposals, ["_id"], proposal_id)
        similar = f" Proposals with similar ids: {', '.join(doc['_id'] for doc in matches)}." if matches else ""
        raise RuntimeError(
            f"There is no proposal with the id {proposal_id}.{similar} "
            "Please re-run with the complete id of an existing proposal."
        )

    def _unseeded_proposals(self):
        seeded = {doc.get("proposal_id") for doc in self.gtx[TARGET_COLL]}
        return [
            doc["_id"]
            for doc in self.gtx[PROPOSAL_COLL]
            if doc.get("status") in SEEDABLE_STATI and doc["_id"] not in seeded
        ]

    def _no_proposal_note(self):
        candidates = self._unseeded_proposals()
        if not candidates:
            return "no proposal was given with --from-proposal, and no proposal is waiting to become a grant"
        return (
            "no proposal was given with --from-proposal. These proposals have not been turned into a grant: "
            f"{', '.join(candidates)} (see them with the l_proposals helper)"
        )

    def _resolve_team_institutions(self, team, missing):
        for member in team:
            if member.get("institution"):
                continue
            try:
                affiliation = get_person_affiliation(
                    member["name"],
                    self.gtx["people"],
                    self.gtx["contacts"],
                    self.gtx["institutions"],
                    strict=False,
                )
            except ValueError:
                affiliation = {}
            institution = affiliation.get("institution")
            if institution and institution != MISSING_INFO:
                member["institution"] = institution
            else:
                missing.append(
                    f"the institution of team member {member['name']} (add them to the people or contacts "
                    "collection with their institution, for example with the u_contact helper)"
                )

    def _store(self, grant):
        rc = self.rc
        public_database, private_database = public_and_private_databases(
            rc.databases, rc.public_database, rc.private_database
        )
        public_part, private_part = split_grant(grant)
        if public_database and private_database and public_database != private_database:
            rc.client.insert_one(public_database, rc.coll, public_part, partial=True)
            rc.client.insert_one(private_database, rc.coll, private_part, partial=True)
            print(f"{rc.grant_id} has been added in {TARGET_COLL}")
            print(f"    public details in {public_database}, private details in {private_database}")
            return
        database = private_database or rc.database
        rc.client.insert_one(database, rc.coll, grant)
        print(f"{rc.grant_id} has been added in {TARGET_COLL}")
        private_fields = sorted(key for key in private_part if key != "_id")
        if database != private_database and private_fields:
            print(
                f"    No database in regolithrc.json is marked private, so its private details "
                f"({', '.join(private_fields)}) were stored in {database} too. To keep them private, add a "
                'database with "public": false to regolithrc.json.'
            )

    def db_updater(self):
        rc = self.rc
        if any(doc["_id"] == rc.grant_id for doc in self.gtx[TARGET_COLL]):
            raise RuntimeError(
                f"A grant with the id {rc.grant_id} is already in the {TARGET_COLL} collection. "
                "Please re-run with a different grant id."
            )

        grant = {"_id": rc.grant_id}
        proposal = None
        if rc.from_proposal:
            proposal = self._find_proposal(rc.from_proposal)
            seeded = [doc["_id"] for doc in self.gtx[TARGET_COLL] if doc.get("proposal_id") == proposal["_id"]]
            if seeded:
                raise RuntimeError(
                    f"The proposal {proposal['_id']} already has the grant {', '.join(seeded)}. "
                    "Please update that grant instead of adding another."
                )
            for field in COPIED_FIELDS:
                if proposal.get(field) not in (None, ""):
                    grant[field] = proposal[field]
            for proposal_field, grant_field in CPP_INFO_FIELDS.items():
                value = proposal.get("cpp_info", {}).get(proposal_field)
                if value not in (None, ""):
                    grant[grant_field] = value
            proposal_dates = _proposal_dates(proposal)
            for field in ("begin_date", "end_date"):
                if proposal_dates.get(field):
                    grant[field] = proposal_dates[field]
            grant["team"] = _proposal_team(proposal, self.gtx["people"])
            grant["proposal_id"] = proposal["_id"]
        else:
            pi_id = rc.pi if rc.pi else get_pi_id(rc)
            person = fuzzy_retrieval(self.gtx["people"], ["_id", "aka", "name"], pi_id, case_sensitive=False)
            grant["team"] = [{"name": person["name"] if person else pi_id, "position": "pi"}]
            grant["currency"] = "USD"

        for field in OPTION_FIELDS:
            value = getattr(rc, field)
            if value:
                grant[field] = value
        if rc.amount:
            grant["amount"] = float(rc.amount)
        for field in ("begin_date", "end_date"):
            value = getattr(rc, field)
            if value:
                grant[field] = date_parser.parse(value).date()
        if rc.notes:
            grant["notes"] = " ".join(rc.notes)
        if rc.institution:
            for member in grant["team"]:
                if member.get("position") == "pi" and not member.get("institution"):
                    member["institution"] = rc.institution
        grant["status"] = "accepted"

        missing = []
        if not proposal and any(field not in grant for field in ("title", "amount", "funder")):
            missing.append(f"a proposal to seed the grant from, or the details below: {self._no_proposal_note()}")
        for field, option in (
            ("title", "--title"),
            ("amount", "--amount"),
            ("funder", "--funder"),
            ("begin_date", "--begin-date"),
            ("end_date", "--end-date"),
        ):
            if field not in grant:
                missing.append(f"the {field.replace('_', ' ')} (give it with {option})")
        if not grant["team"]:
            missing.append("a team (give the principal investigator with --pi)")
        self._resolve_team_institutions(grant["team"], missing)
        if missing:
            raise RuntimeError(
                f"The grant {rc.grant_id} could not be added because these are missing:\n    "
                + "\n    ".join(missing)
                + "\nPlease supply them and re-run."
            )
        if grant["begin_date"] > grant["end_date"]:
            raise ValueError(
                f"The begin date {grant['begin_date']} is after the end date {grant['end_date']}. "
                "Please re-run with a begin date that is before the end date."
            )
        valid, error_message = validate_doc(TARGET_COLL, grant, rc)
        if not valid:
            raise ValueError(
                f"The grant {rc.grant_id} does not fit the grants schema:\n{error_message}"
                "Please correct the options, or the proposal it was seeded from, and re-run."
            )

        self._store(grant)
        if proposal:
            print(f"    seeded from the proposal {proposal['_id']}")
            if proposal.get("status") != "accepted":
                rc.client.update_one(
                    self.where_stored(PROPOSAL_COLL, proposal["_id"]) or rc.database,
                    PROPOSAL_COLL,
                    {"_id": proposal["_id"]},
                    {"status": "accepted"},
                )
                print(f"    the proposal {proposal['_id']} has been marked accepted")
        unset = [option for option in ("awardnr", "account") if not grant.get(option)]
        if unset:
            print(f"    still to fill in when known: {', '.join(unset)}")
        if not proposal:
            print(f"    not seeded from a proposal: {self._no_proposal_note()}")
        return
