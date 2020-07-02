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
    is_fully_appointed,
    collect_appts,
    grant_burn,
)
from regolith.dates import (
    is_current,
    get_dates,
)

TARGET_COLL = "people"
HELPER_TARGET = "makeappointments"


def subparser(subpi):

    subpi.add_argument("-v", "--verbose", action="store_true", help='increase verbosity of output')
    subpi.add_argument("begin_date", help='begin date of interval to check appointment, to specify')
    subpi.add_argument("end_date", help='end date of interval to check appointments')
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
        begin_date = date_parser.parse(rc.begin_date).date()
        end_date = date_parser.parse(rc.end_date).date()

        all_appts = collect_appts(self.gtx["people"])


        for p in self.gtx["people"]:
            appts = collect_appts([p])
            if not appts:
                continue
            is_fully_appointed(p, begin_date, end_date)
            for a in appts:
                g = rc.client.find_one(rc.database, "grants", {"_id": a.get("grant")})
                if not g:
                    raise RuntimeError("grant: {}, person: {}, appointment: {}, grant not found in grants database".format
                                     (a.get("grant"), p.get("_id"), a.get("_id")))
                a_end = get_dates(a)['end_date']
                total_burn = grant_burn(g, all_appts, begin_date=begin_date, end_date=end_date)
                timespan = end_date - begin_date
                outdated_period, depleted_period = False, False
                for x in range (timespan.days + 1):
                    if not outdated_period:
                        day = begin_date + relativedelta(days=x)
                        if not is_current(g, now=day):
                            outdated.append("person: {}, appointment: {}, grant: {}, from {} until {}".format(
                                p.get('_id'), a.get('_id'), g.get('_id'), str(day), str(a_end)))
                            outdated_period = True
                    if not depleted_period:
                        day_burn = 0
                        if a.get('type') == 'gra':
                            day_burn = total_burn[x+1].get('student_days')
                        elif a.get('type') == 'pd':
                            day_burn = total_burn[x+1].get('postdoc_days')
                        elif a.get('type') == 'ss':
                            day_burn = total_burn[x+1].get('ss_days')
                        if day_burn < 0:
                            depleted.append("person: {}, appointment: {}, grant: {}, from {} until {}".format(
                                p.get('_id'), a.get('_id'), g.get('_id'), str(day), str(a_end)))
                            depleted_period = True


        for g in self.gtx["grants"]:
            g_end = get_dates(g)['end_date']
            g_amt = grant_burn(g, all_appts, begin_date=g_end, end_date=g_end)[1]
            g_amt = g_amt.get('student_days') + g_amt.get('postdoc_days') + g_amt.get('ss_days')
            if g_amt > 30.5:
                underspent.append("{}: grant: {}, underspend amount: {} months".format(
                    str(g_end), g.get('_id'), g_amt/30.5))
            elif g_amt < -30.5:
                overspent.append("{}: grant: {}, overspend amount: {} months".format(
                    str(g_end), g.get('_id'), g_amt/30.5))

        if outdated:
            print("appointments on outdated grants:")
            for appt in outdated:
                print(appt)
        if depleted:
            print("appointments on depleted grants:")
            for appt in depleted:
                print(appt)
        if underspent:
            print("underspent grants:")
            for g in underspent:
                print(g)
        if overspent:
            print("overspent grants:")
            for g in overspent:
                print(g)

        return
