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
import matplotlib
import matplotlib.pyplot as plt

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
                    day = appt_begin + relativedelta(days=x)
                    if not outdated_period:
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

        grants_begin = min(get_dates(grant)['begin_date'] for grant in self.gtx["grants"])
        grants_end = max(get_dates(grant)['end_date'] for grant in self.gtx["grants"])
        grants_timespan = grants_end - grants_begin
        datearray = []

        for x in range(grants_timespan.days + 1):
            datearray.append(grants_begin + relativedelta(days=x))
        dates = matplotlib.dates.date2num(datearray)
        cum_student, cum_pd, cum_ss = [0.0] * len(datearray), [0.0] * len(datearray), [0.0] * len(datearray)

        for grant in self.gtx["grants"]:
            if grant.get('_id') in BLACKLIST or grant.get('alias') in BLACKLIST:
                continue
            grt_begin, grt_end = get_dates(grant)['begin_date'], get_dates(grant)['end_date']
            grt_duration = (grt_end - grt_begin).days + 1
            grant_dates = []
            this_student, this_pd, this_ss = [0.0] * grt_duration, [0.0] * grt_duration, [0.0] * grt_duration
            grant_amts = grant_burn(grant, all_appts, begin_date=grt_begin, end_date=grt_end)
            grant_amt = grant_amts[-1].get('student_days') + grant_amts[-1].get('postdoc_days') + grant_amts[-1].get('ss_days')
            if grant_amt > 30.5:
                underspent.append("    {}: grant: {}, underspend amount: {} months".format(
                    str(grt_end), grant.get('_id'), round(grant_amt/30.5, 2)))
            elif grant_amt < -30.5:
                overspent.append("    {}: grant: {}, overspend amount: {} months".format(
                    str(grt_end), grant.get('_id'), round(grant_amt/30.5, 2)))
            a, b = 0, 1
            for x in range (grants_timespan.days + 1):
                if is_current(grant, now=datearray[x]):
                    grant_dates.append(datearray[x])
                    this_student[a] = grant_amts[b].get('student_days')
                    cum_student[x] += grant_amts[b].get('student_days')
                    this_pd[a] = grant_amts[b].get('postdoc_days')
                    cum_pd[x] += grant_amts[b].get('postdoc_days')
                    this_ss[a] = grant_amts[b].get('ss_days')
                    cum_ss[x] += grant_amts[b].get('ss_days')
                    a += 1
                    b += 1
            plt.plot_date(grant_dates, this_student, ls='-', marker="", label="student days")
            plt.plot_date(grant_dates, this_pd, ls='-', marker="", label="postdoc days")
            plt.plot_date(grant_dates, this_ss, ls='-', marker="", label="ss days")
            plt.xlabel('date')
            plt.ylabel('budget days remaining')
            plt.title(f"{grant.get('_id')}")
            plt.legend(loc='best')
            plt.show()

        plt.plot_date(dates, cum_student, ls='-', marker="", label="student days")
        plt.plot_date(dates, cum_pd, ls='-', marker="", label="postdoc days")
        plt.plot_date(dates, cum_ss, ls='-', marker="", label="ss days")
        plt.xlabel('date')
        plt.ylabel('budget days remaining')
        plt.title("Cumulative burn")
        plt.legend(loc='best')
        plt.show()

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
