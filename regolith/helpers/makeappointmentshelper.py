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
import matplotlib.pyplot as plt

TARGET_COLL = "people"
HELPER_TARGET = "makeappointments"
BLACKLIST = ['ta', 'physmatch', 'chemmatch', 'bridge16', 'collgf', 'afgrf14',
             'zurabSNF16']
ALLOWED_TYPES = ["gra", "pd", "ss"]


def subparser(subpi):

    subpi.add_argument("-r", "--run", action="store_true", help='run the helper')
    subpi.add_argument("--no_plot", action="store_true", help='suppress plotting feature')

    return subpi

def plotter(datearray, student=None, pd=None, ss=None, title=None):
    if student:
        plt.plot_date(datearray, student, ls='-', marker="", label="student days")
    if pd:
        plt.plot_date(datearray, pd, ls='-', marker="", label="postdoc days")
    if ss:
        plt.plot_date(datearray, ss, ls='-', marker="", label="ss days")
    plt.xlabel('date')
    plt.ylabel('budget days remaining')
    plt.title(title)
    plt.legend(loc='best')
    plt.show()
    return "plotting mode is on"


class MakeAppointmentsHelper(SoutHelperBase):
    """Helper for managing appointments on grants and studying the burn of grants over time.
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

        for person in self.gtx['people']:
            appts = collect_appts([person])
            if not appts:
                continue
            this_begin = min(get_dates(appt)['begin_date'] for appt in appts)
            this_end = max(get_dates(appt)['end_date'] for appt in appts)
            is_fully_appointed(person, this_begin, this_end)
            for appt in appts:
                if appt.get("grant") in BLACKLIST:
                    continue
                grant = rc.client.find_one(rc.database, "grants", {"_id": appt.get("grant")})
                if not grant:
                    raise RuntimeError("    grant: {}, person: {}, appointment: {}, grant not found in grants database".
                                       format(appt.get("grant"), person.get("_id"), appt.get("_id")))
                appt_begin, appt_end = get_dates(appt)['begin_date'], get_dates(appt)['end_date']
                this_burn = grant_burn(grant, all_appts, begin_date=appt_begin, end_date=appt_end)
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
                            day_burn = this_burn[x].get('student_days')
                        elif appt.get('type') == 'pd':
                            day_burn = this_burn[x].get('postdoc_days')
                        elif appt.get('type') == 'ss':
                            day_burn = this_burn[x].get('ss_days')
                        if day_burn < 0:
                            depleted.append("    person: {}, appointment: {}, grant: {},\n"
                                            "            from {} until {}".format(
                                person.get('_id'), appt.get('_id'), grant.get('_id'), str(day), str(appt_end)))
                            depleted_period = True

        datearray, cum_student, cum_pd, cum_ss = [], None, None, None
        if not rc.no_plot:
            grants_begin = min(get_dates(grant)['begin_date'] for grant in self.gtx["grants"])
            grants_end = max(get_dates(grant)['end_date'] for grant in self.gtx["grants"])
            grants_timespan = grants_end - grants_begin
            for x in range(grants_timespan.days + 1):
                datearray.append(grants_begin + relativedelta(days=x))
            cum_student, cum_pd, cum_ss = [0.0] * len(datearray), [0.0] * len(datearray), [0.0] * len(datearray)

        for grant in self.gtx["grants"]:
            if grant.get('_id') in BLACKLIST or grant.get('alias') in BLACKLIST:
                continue
            grant_begin, grant_end = get_dates(grant)['begin_date'], get_dates(grant)['end_date']
            grant_amounts = grant_burn(grant, all_appts)
            end_amount = grant_amounts[-1].get('student_days') + grant_amounts[-1].get('postdoc_days') + \
                        grant_amounts[-1].get('ss_days')
            if end_amount > 30.5:
                underspent.append("    {}: grant: {}, underspend amount: {} months".format(
                    str(grant_end), grant.get('_id'), round(end_amount/30.5, 2)))
            elif end_amount < -30.5:
                overspent.append("    {}: grant: {}, overspend amount: {} months".format(
                    str(grant_end), grant.get('_id'), round(end_amount/30.5, 2)))
            if not rc.no_plot:
                grant_dates = []
                grant_duration = (grant_end - grant_begin).days + 1
                this_student, this_pd, this_ss = [0.0] * grant_duration, [0.0] * grant_duration, [0.0] * grant_duration
                counter = 0
                for x in range(len(datearray)):
                    if is_current(grant, now=datearray[x]):
                        grant_dates.append(datearray[x])
                        this_student[counter] = grant_amounts[counter].get('student_days')
                        cum_student[x] += grant_amounts[counter].get('student_days')
                        this_pd[counter] = grant_amounts[counter].get('postdoc_days')
                        cum_pd[x] += grant_amounts[counter].get('postdoc_days')
                        this_ss[counter] = grant_amounts[counter].get('ss_days')
                        cum_ss[x] += grant_amounts[counter].get('ss_days')
                        counter += 1
                plotter(grant_dates, student=this_student, pd=this_pd, ss=this_ss, title=f"{grant.get('_id')}")

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

        if not rc.no_plot:
            print(plotter(datearray, student=cum_student, pd=cum_pd, ss=cum_ss, title="Cumulative burn"))

        return
