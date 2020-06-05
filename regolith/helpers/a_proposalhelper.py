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
                       )
    subpi.add_argument("amount", help="value of award",
                       )
    subpi.add_argument("title", help="Actual title of the proposal"
                       )
    subpi.add_argument("--begin_date", help="The begin date for the proposed grant "
                                          "in format YYYY-MM-DD.",
                       #default = 'tbd'
                       )
    subpi.add_argument("-d", "--duration", help="Duration of proposal in months",
                       #default = 'tbd'
                       )
    subpi.add_argument("--due_date", help="The due date for the proposal in format YYYY-MM-DD.",
                       default = 'tbd'
                       )
    subpi.add_argument("-a", "--authors", nargs="+",
                       help="Other investigator names", default = []
                       )
    subpi.add_argument("-c", "--currency",
                       help="Currency in which amount is specified. Defaults to USD",
                       default = 'USD'
                       )
    subpi.add_argument("-p", "--pi",
                       help="ID of principal investigator. Defaults to"
                            "group pi id in regolithrc.json", default = ''
                       )
    subpi.add_argument("--cppflag", help="Current and pending form (true or false)",
                       default = True
                       )
    subpi.add_argument("--other_agencies", help="Other agencies to which the proposal has been "
                                                "submitted", default = False
                       )
    subpi.add_argument("-i", "--institution", nargs="+",
                       help="The institution where the work will primarily"
                             "be carried out", default = []
                       )
    subpi.add_argument("--months_academic", help="Number of working months in the academic year"
                                                 "to be stated on the current and pending form",
                       default = 0
                       )
    subpi.add_argument("--months_summer", help="Number of working months in the summer to be"
                                                "stated on the current and pending form",
                       default = 0
                       )
    subpi.add_argument("-s", "--scope", help="Scope of project and statement of any overlaps "
                                             "with other current and pending grants",
                       default = ''
                       )
    subpi.add_argument("-f", "--funder", help="Agency where the proposal is being submitted",
                       default = ''
                       )
    subpi.add_argument("-n", "--notes", nargs="+",
                       help="Anything to note", default = ''
                       )
    return subpi

class ProposalAdderHelper(DbHelperBase):
    """Helper for adding a proposal to the proposals collection.

       A proposal is a dictionary object describing a research or
        project proposal submitted by the group.
    """
    # btype must be the same as helper target in helper.py
    btype = "a_proposal"
    needed_dbs = [f'{TARGET_COLL}', 'people', 'groups']

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
        gtx = self.gtx
        rc = self.rc
        now = dt.date.today()
        key = f"{str(now.year)[2:]}_{''.join(rc.name.casefold().split()).strip()}"

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError(
                "This entry appears to already exist in the collection")
        else:
            pdoc = {}
        pdoc.update({'_id': key,
                     'amount': rc.amount
                     })
        if rc.authors:
            if isinstance(rc.authors, str):
                pdoc.update({'authors': [rc.authors]})
            else:
                pdoc.update({'authors': rc.authors})
        if rc.begin_date:
            pdoc.update({'begin_date': rc.begin_date})
        else:
            pdoc.update({'begin_date': 'tbd'})
        cpp_info = {}
        if rc.cppflag:
            cpp_info['cppflag'] = rc.cppflag
        if rc.other_agencies:
            cpp_info['other_agencies_submitted'] = rc.other_agencies
        if rc.institution:
            cpp_info['institution'] = rc.institution
        if rc.months_academic:
             cpp_info['person_months_academic'] = rc.months_academic
        if rc.months_summer:
            cpp_info['person_months_summer'] =  rc.months_summer
        if rc.scope:
            cpp_info['project_scope'] = rc.scope
        if cpp_info:
            pdoc.update({'cpp_info':cpp_info})
        if rc.currency:
            pdoc.update({'currency': rc.currency})
        else:
            pdoc.update({'currency': 'USD'})
        if rc.due_date:
            pdoc.update({'due_date': rc.due_date})
        else:
            pdoc.update({'due_date': 'tbd'})
        if rc.duration:
            pdoc.update({'duration': rc.duration})
            if rc.begin_date:
                begin_date = date_parser.parse(rc.begin_date).date()
                pdoc.update({'end_date': begin_date + relativedelta(months = rc.duration)})
            else:
                pdoc.update({'end_date': 'tbd'})
        else:
            pdoc.update({'duration': 'tbd',
                         'end_date': 'tbd'
                         })
        if rc.funder:
            pdoc.update({'funder': rc.funder})
        if rc.notes:
            pdoc.update({'notes': rc.notes})
        if rc.pi:
            pdoc.update({'pi': rc.pi})
        else:
            #pdoc.update({'pi': rc.pi_id})
            pdoc.update({'pi': ''})
        pdoc.update({'status': 'inprep'})
        sample_team = {'name': '',
                       'subaward_amount': ''
                       }
        pdoc.update({'team': [sample_team]})
        pdoc.update({'title': rc.title})

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
