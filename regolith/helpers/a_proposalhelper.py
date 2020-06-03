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

def subparser(subpi):
    # Do not delete --database arg
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file."
                       )
    subpi.add_argument("name", help="A short but unique name for the proposal",
                       default=None
                       )
    subpi.add_argument("amount", help="value of award",
                       default=None
                       )
    subpi.add_argument("authors", help="Other investigator names"
                       )
    subpi.add_argument("currency", help="Currency in which amount is specified."
                                        " Typically $ or USD"
                       )
    subpi.add_argument("due_date", help="The due date for the proposal in format YYYY-MM-DD."
                       )
    subpi.add_argument("duration", help="Duration of proposal in years"
                       )
    subpi.add_argument("submitted_date", help="Day on which the proposal is submitted "
                                              "in format YYYY-MM-DD"
                       )
    subpi.add_argument("pi", help="Name of principal investigator"
                       )
    subpi.add_argument("title", help="Actual title of the proposal"
                       )
    subpi.add_argument("-b", "--begin_date", nargs="+",
                       help="The start date for the proposed grant in format YYYY-MM-DD."
                       )
    subpi.add_argument("--cpp_flag", nargs="+",
                       help="Current and pending form (true or false)"
                       )
    subpi.add_argument("--cpp_agencies", nargs="+",
                       help="Other agencies to which the proposal has been submitted"
                       )
    subpi.add_argument("--cpp_institution", nargs="+",
                       help="The institution to be stated on the current"
                            "and pending form"
                       )
    subpi.add_argument("--cpp_months_academic", nargs="+",
                       help="Number of working months in the academic year"
                            "to be stated on the current and pending form"
                       )
    subpi.add_argument("--cpp_months_summer", nargs="+",
                       help="Number of working months in the summer to be"
                            "stated on the current and pending form"
                       )
    subpi.add_argument("--cpp_scope", nargs="+",
                       help="Scope of the project"
                       )
    subpi.add_argument("-e","--end_date", nargs="+",
                       help="The end date for the proposed grant in format YYYY-MM-DD."
                       )
    subpi.add_argument("-f", "--funder", nargs="+",
                       help="Who funds the proposal. As funder in grants"
                       )
    subpi.add_argument("-n", "--notes", nargs="+",
                       help="Anything to note"
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
        submitted_date = date_parser.parse(rc.submitted_date).date()
        key = f"{str(submitted_date.year)[2:]}_{''.join(rc.name.casefold().split()).strip()}"

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
            pdoc.update({'authors': ['tbd']})
        if rc.begin_date:
            pdoc.update({'begin_date': rc.begin_date})
        cpp_info = {}
        if rc.cpp_flag:
            cpp_info['cppflag'] = rc.cpp_flag
        if rc.cpp_agencies:
            cpp_info['other_agencies_submitted'] = rc.cpp_agencies
        if rc.cpp_institution:
            cpp_info['institution'] = rc.cpp_institution
        if rc.rc.cpp_months_academic:
             cpp_info['person_months_academic'] = rc.cpp_months_academic
        if rc.cpp_months_summer:
            cpp_info['person_months_summer'] =  rc.cpp_months_summer
        if rc.cpp_scope:
            cpp_info['project_scope'] = rc.cpp_scope
        if cpp_info:
            pdoc.update({'cpp_info':cpp_info})
        if rc.currency:
            pdoc.update({'currency': rc.currency})
        else:
            pdoc.update({'currency': 'USD'})
        if rc.submitted_date:
            pdoc.update({'submitted_date': submitted_date})
        else:
            pdoc.update({'submitted_date': 'tbd'})
        if rc.due_date:
            pdoc.update({'due_date': rc.due_date})
        else:
            pdoc.update({'due_date': 'tbd'})
        if rc.duration:
            pdoc.update({'duration': rc.duration})
        else:
            pdoc.update({'duration': 'tbd'})
        if rc.end_date:
            pdoc.update({'end_date': rc.end_date})
        if rc.funder:
            pdoc.update({'funder': rc.funder})
        if rc.full:
            pdoc.update({'full': rc.full})
        if rc.notes:
            pdoc.update({'notes': rc.notes})
        if rc.pi:
            pdoc.update({'pi': rc.pi})
        else:
            pdoc.update({'pi': 'tbd'})
        pdoc.update({'status': 'inprep'})
        sample_team = {'cv':'http://pdf.com/goodbye-cv',
                       'email':'goodbye@world.com',
                       'institution':'Columbia University',
                       'name': 'goodbyeworld',
                       'position':'Adieu Bidder',
                       'subaward_amount': 10.0
                       }
        pdoc.update({'team': [sample_team]})
        if rc.title:
            pdoc.update({'title': rc.title})
        else:
            pdoc.update({'title': 'tbd'})

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
