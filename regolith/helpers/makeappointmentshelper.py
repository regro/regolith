"""Helper for managing appointments.

   - Returns members with gap in appointments
   - Returns members supported on an outdated grant
   - Returns members supported on a depleted grant
   - Suggests appointments to make for these members
   - Suggests new appointments
"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.dates import get_due_date
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    is_fully_appointed
)
from regolith.dates import (
    is_current,
    has_finished,
)

TARGET_COLL = "people"
HELPER_TARGET = "makeappointments"


def subparser(subpi):

    subpi.add_argument("-v", "--verbose", action="store_true", help='increase verbosity of output')
    subpi.add_argument("-b", "--begin_date", help='begin date of interval to check appointment, to specify')
    subpi.add_argument("-e", "--end_date", help='end date of interval to check appointments')
    subpi.add_argument("-m", "-member", help='suggest appointments for this member')
    subpi.add_argument("-a", "--appoint", action="store_true", help='suggest new appointments')

    return subpi


class MakeAppointmentsHelper(SoutHelperBase):
    """Helper for managing appointments.

       Appointments are...
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}', "grants"]

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
        rc = self.rc
        outdated, depleted, underspent, overspent = [], [], [], []
        if rc.begin_date:
            begin_date = date_parser.parse(rc.begin_date).date()
        else:
            begin_date = None
        if rc.end_date:
            end_date = date_parser.parse(rc.end_date).date()
        else:
            end_date = None

        for person in self.gtx["people"]:
            appts = person.get("appointments")
            is_fully_appointed(appts, begin_date=begin_date, end_date=end_date)
            for appt in appts:
                grant = rc.client.find_one(rc.database, self.gtx["grants"], {"_id": appt.get("grant")})
                timespan = end_date - begin_date
                for x in range(0, timespan.days):
                    day = begin_date + relativedelta(days=x)
                    if not is_current(grant, day):
                        outdated.append(
                        f"person: {person.get('_id')} appointment: {appt.get('_id')} grant: {grant.get('_id')} "
                        f"date: {str(day)}")
                    if grant.get('amount') < 1:
                        depleted.append(
                        f"person: {person.get('_id')} appointment: {appt.get('_id')} grant: {grant.get('_id')} "
                        f"date: {str(day)}")

        if outdated:
            print("Appointments supported on outdated grants:")
            for appt in outdated:
                print(appt)

        return
