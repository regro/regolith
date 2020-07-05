"""Helper for managing appointments.

   - Returns members with gap in appointments
   - Returns members supported on an outdated grant
   - Returns members supported on a depleted grant
   - Suggests appointments to make for these members
   - Suggests new appointments
"""
from dateutil.relativedelta import relativedelta
import sys

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
BLACKLIST = ['ta', 'physmatch', 'chemmatch', 'bridge16', 'collgf', 'afgrf14',
             'zurabSNF16']
ALLOWED_TYPES = ["gra", "pd", "ss"]


def subparser(subpi):

    subpi.add_argument("-r", "--run", action="store_true", help='run the helper')

    return subpi


class MakeAppointmentsHelper(SoutHelperBase):
    """Helper for managing appointments.
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
        all_appts = collect_appts(self.gtx['people'])
        appts_begin = min(get_dates(appt)['begin_date'] for appt in all_appts)
        appts_end = max(get_dates(appt)['end_date'] for appt in all_appts)

        for person in self.gtx['people']:
            appts = collect_appts([person])
            if not appts:
                continue
            is_fully_appointed(person, appts_begin, appts_end)
            for appt in appts:
                if appt.get("grant") in BLACKLIST:
                    continue
                grant = rc.client.find_one(rc.database, "grants", {"_id": appt.get("grant")})
                if not grant:
                    raise RuntimeError("    grant: {}, person: {}, appointment: {}, grant not found in grants database".format
                                     (appt.get("grant"), person.get("_id"), appt.get("_id")))
                appt_begin, appt_end = get_dates(appt)['begin_date'], get_dates(appt)['end_date']
                total_burn = grant_burn(grant, all_appts, begin_date=appt_begin, end_date=appt_end)
                timespan = appt_end - appt_begin
                outdated_period, depleted_period = False, False
                for x in range (timespan.days + 1):
                    if not outdated_period:
                        day = appt_begin + relativedelta(days=x)
                        if not is_current(grant, now=day):
                            outdated.append("    person: {}, appointment: {}, grant: {},\n"
                                            "            from {} until {}".format(
                                person.get('_id'), appt.get('_id'), grant.get('_id'), str(day),
                                str(min(appt_end, get_dates(grant)['begin_date']))))
                            outdated_period = True
                    if not depleted_period and not outdated_period:
                        day_burn = 0
                        if appt.get('type') == 'gra':
                            day_burn = total_burn[x+1].get('student_days')
                        elif appt.get('type') == 'pd':
                            day_burn = total_burn[x+1].get('postdoc_days')
                        elif appt.get('type') == 'ss':
                            day_burn = total_burn[x+1].get('ss_days')
                        if day_burn < 0:
                            depleted.append("    person: {}, appointment: {}, grant: {},\n"
                                            "            from {} until {}".format(
                                person.get('_id'), appt.get('_id'), grant.get('_id'), str(day), str(appt_end)))
                            depleted_period = True

        for grant in self.gtx["grants"]:
            if grant.get('_id') in BLACKLIST or grant.get('alias') in BLACKLIST:
                continue
            g_end = get_dates(grant)['end_date']
            g_amt = grant_burn(grant, all_appts, begin_date=g_end, end_date=g_end)[1]
            g_amt = g_amt.get('student_days') + g_amt.get('postdoc_days') + g_amt.get('ss_days')
            if g_amt > 30.5:
                underspent.append("    {}: grant: {}, underspend amount: {} months".format(
                    str(g_end), grant.get('_id'), round(g_amt/30.5, 2)))
            elif g_amt < -30.5:
                overspent.append("    {}: grant: {}, overspend amount: {} months".format(
                    str(g_end), grant.get('_id'), round(g_amt/30.5, 2)))

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
            for grant in underspent:
                print(grant)
        if overspent:
            print("overspent grants:")
            for grant in overspent:
                print(grant)

        return
