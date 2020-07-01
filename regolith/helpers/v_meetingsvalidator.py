"""Validator for group meetings.

"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.dates import get_due_date, is_current
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id, search_collection,
    fuzzy_retrieval,
)
from regolith.dates import get_dates

TARGET_COLL = "meetings"
HELPER_TARGET = "v_meetings"
ALLOWED_STATI = ["proposed", "started", "finished", "back_burner", "paused", "cancelled"]



def subparser(subpi):
    subpi.add_argument("-v", "--verbose", action="store_true", help='increase verbosity of output')
    subpi.add_argument("-c", "--current", action="store_true", help='get only current group members ')
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs")
    subpi.add_argument("-k", "--keys", nargs="+", help="Specify what keys to return values from when running "
                                                       "--filter. If no argument is given the default is just the id.")

    subpi.add_argument("-p", "--prior", action="store_true", help='get only former group members ')
    return subpi


class MeetingsValidatorHelper(SoutHelperBase):
    """Validator for group meetings.

    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        try:
            if not rc.database:
                rc.database = rc.databases[0]["name"]
        except:
            pass
        colls = [
            sorted(
                all_docs_from_collection(rc.client, collname), key=_id_key
            )
            for collname in self.needed_dbs
        ]
        for db, coll in zip(self.needed_dbs, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip



    def sout(self):
        gtx = self.gtx
        rc = self.rc
        for meeting in gtx['meetings']:
            #print(meeting)
            if meeting.get('journal_club'):
                if isinstance(meeting.get('journal_club'), list) or meeting.get('journal_club').get('doi') == 'TBD':
                    print(f'{meeting.get("_id")} does not have a journal club doi')
            if isinstance(meeting.get('presentation'), list) or meeting.get('presentation').get('link') == 'TBD':
                print(f'{meeting.get("_id")} does not have a presentation link')
            if isinstance(meeting.get('presentation'), list) or meeting.get('presentation').get('title') == 'TBD':
                print(f'{meeting.get("_id")} does not have a presentation title')


