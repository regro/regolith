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
    fuzzy_retrieval,
    is_fully_appointed
)
from regolith.dates import (
    is_current,
    has_finished,
)

TARGET_COLL = "people"
HELPER_TARGET = "makeappointments"


def subparser(subpi):

    subpi.add_argument("--date", help="date to check appointments and grants against")
    subpi.add_argument("-v", "--verbose", action="store_true", help='increase verbosity of output')
    subpi.add_argument("-g", "--gap", action="store_true",
                       help='get group members with a gap in their appointments')
    subpi.add_argument("-b", "--begin_date", help='begin date of interval to check appointments')
    subpi.add_argument("-e", "--end_date", help='end date of interval to check appointments', default=None)
    subpi.add_argument("-o", "--out_of_date", action="store_true",
                       help='get group members supported on an out of date grant')
    subpi.add_argument("-d", "--depleted", action="store_true",
                       help='get group members supported on a depleted grant')
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
        gaps = []
        outdated = []
        depleted = []

        if rc.begin_date and rc.date:
            raise ValueError("Please enter either an interval or a date, not both")
        if rc.date:
            desired_date = date_parser.parse(rc.date).date()
        else:
            desired_date = dt.date.today()
        for person in self.gtx["people"]:
            appts = person.get("appointments")
            if rc.gap:
                if rc.begin_date:
                    if not is_fully_appointed(appts, begin=rc.begin_date, end=rc.end_date)[0]:
                        gaps.append(person.get('name'))
                        gaps.append((is_fully_appointed(appts, begin=rc.begin_date, end=rc.end_date))[1])
                else:
                    if not is_fully_appointed(appts, now=desired_date)[0]:
                        gaps.append(person.get('name'))
                        gaps.append((is_fully_appointed(appts, now=desired_date))[1])
            if rc.out_of_date:
                for appt in appts:
                    grant = fuzzy_retrieval(self.gtx["grants"], ['_id'], appt.get("grant"), case_sensitive=False)
                    if has_finished(grant, desired_date):
                        outdated.append(f"person: {person.get('_id')} appointment: {appt.get('_id')} grant: {grant.get('_id')}")
            if rc.depleted:
                for appt in appts:
                    grant_amount = fuzzy_retrieval(self.gtx["grants"], ['_id'], appt.get("grant"), case_sensitive=False).get('budget').get('months')
                    if 30*grant_amount < 1:
                        outdated.append(
                            f"person: {person.get('_id')} appointment: {appt.get('_id')} grant: {grant.get('_id')}")
        if rc.gap:
            print("People with gaps in their appointments:")
            for thing in gaps:
                print(thing)
        if rc.out_of_date:
            print("Appointments supported on outdated grants:")
            for appt in outdated:
                print(appt)

        return

