"""Validator for meetings."""

import datetime as dt

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import all_docs_from_collection, get_pi_id, validate_meeting

TARGET_COLL = "meetings"
HELPER_TARGET = "v_meetings"


def subparser(subpi):
    subpi.add_argument("-t", "--test", action="store_true", help="Testing flag for meeting validator")
    return subpi


class MeetingsValidatorHelper(SoutHelperBase):
    """Helper for validating the entries of the meetings.yml file."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "institutions"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        try:
            if not rc.database:
                rc.database = rc.databases[0]["name"]
        except BaseException:
            pass
        colls = [
            sorted(all_docs_from_collection(rc.client, collname), key=_id_key) for collname in self.needed_colls
        ]
        for db, coll in zip(self.needed_colls, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        if rc.test:
            print("Meeting validator helper")
            return
        date = dt.date.today()
        collection = self.gtx["meetings"]
        for meeting in collection:
            validate_meeting(meeting, date)
        return
