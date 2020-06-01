"""Helper for adding a proposal to the proposals.yml collection.
"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
)

TARGET_COLL = "proposals"
ALLOWED_TYPES = ["nsf", "doe", "other"]
ALLOWED_STATI = ["proposed", "started", "finished", "back_burner", "paused",
                 "cancelled"]
MILESTONES_ALLOWED_STATI = ["proposed", "scheduled", "finished", "cancelled"]


def subparser(subpi):
    # Do not delete --database arg
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file."
                       )
    subpi.add_argument("name", help="A short but unique name for the proposal",
                       default=None
                       )
    subpi.add_argument("-amt", "--amount", help="value of award",
                       default=None
                       )
    subpi.add_argument("-a", "--authors",
                       help="Other investigator names"
                       )
    subpi.add_argument("--begin_day", nargs="+",
                       help="The start day for the proposed grant in format YYYY-MM-DD."
                       )
    subpi.add_argument("--begin_month", nargs="+",
                       help="The start month for the proposed grant in format YYYY-MM-DD."
                       )
    subpi.add_argument("--begin_year", nargs="+",
                       help="The start year for the proposed grant in format YYYY-MM-DD."
                       )
    subpi.add_argument("--end_date", nargs="+",
                       help="The end date for the proposed grant in format YYYY-MM-DD."
                       )
    subpi.add_argument("--call_for_proposals", nargs="+",
                       help="Url for call for proposals"
                       )
    subpi.add_argument("--cpp_info", nargs="+",
                       help="Extra information needed for building current and"
                            "pending form"
                       )
    subpi.add_argument("-c", "--currency",
                       help="Currency in which amount is specified."
                            " Typically $ or USD"
                       )
    subpi.add_argument("--submitted_date",
                       help="Day on which the proposal is submitted in format YYYY-MM-DD"
                       )
    subpi.add_argument("--due_date", nargs="+",
                       help="The due date for the proposal in format YYYY-MM-DD."
                       )
    subpi.add_argument("-d", "--duration",
                       help="Duration of proposal in years"
                       )
    subpi.add_argument("--funder", nargs="+",
                       help="Who funds the proposal. As funder in grants"
                       )
    subpi.add_argument("--full", nargs="+",
                       help="Full body of the proposal"
                       )
    subpi.add_argument("-n", "--notes", nargs="+",
                       help="Anything to note"
                       )
    subpi.add_argument("--pi", "--principal_investigator", nargs="+",
                       help="Name of principal investigator"
                       )
    subpi.add_argument("--pre", nargs="+",
                       help="Information about pre-posal"
                       )
    subpi.add_argument("-s", "--status",
                        help=f"status, from {ALLOWED_STATI}. default is accepted")
    subpi.add_argument("-m", "--team_members", nargs="+",
                       help="Information about the team members participating"
                            "in the grant"
                       )
    subpi.add_argument("-t", "--title",
                        help="Actual title of the proposal"
                       )
    subpi.add_argument("--title_short", nargs="+",
                        help="Short title of the proposal"
                       )
    return subpi


class ProposalAdderHelper(DbHelperBase):
    """Helper for adding a proposal to the proposals collection.

       Proposals are...
    """
    # btype must be the same as helper target in helper.py
    btype = "a_proposal"
    needed_dbs = [f'{TARGET_COLL}', 'groups', 'people']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(
            all_docs_from_collection(rc.client, rc.coll), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        if not rc.submitted_date:
            now = dt.date.today()
        else:
            now = date_parser.parse(rc.submitted_date).date()
        key = f"{str(now.year)[2:]}{rc.lead[:2]}_{''.join(rc.name.casefold().split()).strip()}"

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError(
                "This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update({'_id': key})
        if rc.amount:
            pdoc.update({'amount': rc.amount})
        else:
            pdoc.update({'amount': 'tbd'})
        if rc.authors:
            if isinstance(rc.authors, str):
                pdoc.update({'authors': [rc.authors]})
            else:
                pdoc.update({'authors': rc.authors})
        else:
            pdoc.update({'authors': 'tbd'})
        pdoc.update({
            'begin_day': rc.begin_day,
            'begin_month': rc.begin_month,
            'begin_year': rc.begin_year,
            'call_for_proposals': rc.call_for_proposals,
            # 'cpp_info':
        })
        if rc.currency:
            pdoc.update({'currency': rc.currency})
        else:
            pdoc.update({'currency': 'USD'})
        pdoc.update({'day': now.day
                     'due_date': rc.due_date
                     })
        if rc.duration:
            pdoc.update('duration': rc.duration)
        else:
            pdoc.update({'duration': 'tbd'})
        pdoc.update({
            'end_day': rc.end_day,
            'end_month': rc.end_month,
            'end_year': rc.end_year,
            'funder': rc.funder,
            'full': rc.full
            'month': now.month # convert numeric to string
            'notes': rc.notes
        })
        if rc.pi:
            pdoc.update({'pi': rc.pi})
        else:
            pdoc.update({'pi': 'tbd'})
        if rc.status:
            pdoc.update({'status': rc.status})
        else:
            pdoc.update({'status': 'tbd'})
        # pdoc.update({'team':})
        if rc.title:
            pdoc.update({'title': rc.title})
        else:
            pdoc.update({'title': 'tbd'})
        pdoc.update({'title_short': rc.title_short
                     'year': now.year
                     })


        pdoc.update({"_id": key})
        pdoc.update({"deliverable": {
            "due_date": now + relativedelta(years=1),
            "audience": ["beginning grad in chemistry"],
            "success_def": "audience is happy",
            "scope": [
                "UCs that are supported or some other scope description if it software",
                "sketch of science story if it is paper"],
            "platform": "description of how and where the audience will access the deliverable.  journal if it is a paper",
            "roll_out": [
                "steps that the audience will take to access and interact with the deliverable",
                "not needed for paper submissions"],
            "status": "proposed"}
        })
        pdoc.update({"kickoff": {
            "due_date": now + relativedelta(days=7),
            "audience": ["lead", "pi", "group_members"],
            "name": "Kick off meeting",
            "objective": "introduce project to the lead",
            "status": "proposed"
        }})

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
