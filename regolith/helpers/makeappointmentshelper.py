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
from copy import deepcopy
import yaml
import textwrap

TARGET_COLL = "people"
HELPER_TARGET = "makeappointments"
ALLOWED_TYPES = ["gra", "pd", "ss"]


def subparser(subpi):

    subpi.add_argument("-v", "--verbose", action="store_true", help='increase verbosity of output')
    subpi.add_argument("begin_date", help='begin date of interval to check appointment, to specify')
    subpi.add_argument("end_date", help='end date of interval to check appointments')
    subpi.add_argument("-c", "--check", action="store_true", help="appointment adding mode")
    subpi.add_argument("-p", "-person", help='id of person to add appointment for', nargs="+", default="pseudo_person")
    subpi.add_argument("-a", "--appointment",  help='id of appointment', default="pseudo_appointment")
    subpi.add_argument("-b", "--a_begin", help='start date of appointment, defaults to entered begin date')
    subpi.add_argument("-e", "--a_end", help='end date of appointment, defaults to entered end date')
    subpi.add_argument("-t", "--type", help=f'type of appointment can be {ALLOWED_TYPES}', default='')
    subpi.add_argument("-l", "--loading", help='loading of appointment', default=1.0)
    subpi.add_argument("-g", "--grant", help='grant of appointment', default="pseudogrant")
    subpi.add_argument("-s", "--status", help='status of appointment', default="proposed")
    subpi.add_argument("-n", "--notes", help='any notes for appointment', nargs="+", default=[])

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
        outdated, depleted, underspent, overspent, ppl_coll = [], [], [], [], []
        begin_date = date_parser.parse(rc.begin_date).date()
        end_date = date_parser.parse(rc.end_date).date()

        if not rc.check:
            ppl_coll = self.gtx["people"]
        else:
            ppl_coll = deepcopy(self.gtx["people"])
            p = rc.client.find_one(rc.database, "people", {"_id": rc.person})
            if p:
                pdocl = list(filter(lambda doc: doc["_id"] == rc.appointment, collect_appts([p])))
                if len(pdocl) > 0:
                    raise RuntimeError(
                        "This entry appears to already exist in the collection")
                else:
                    pdoc = {}
            if rc.type and rc.type not in ALLOWED_TYPES:
                raise RuntimeError(f"appointment type must be one of {ALLOWED_TYPES}")
            pdoc.update({'_id': rc.appointment,
                         'begin_date': rc.a_begin if rc.a_begin else str(begin_date),
                         'end_date': rc.a_end if rc.a_end else str(end_date),
                         'grant': rc.grant,
                         'type': rc.type,
                         'loading': rc.loading,
                         'status': rc.status,
                         'notes': rc.notes,
                         }
                        )
            if p:
                # write an appointments updater for the fake ppl_coll
                pass
            else:
                new_person = [{rc.person: {"appointments": pdoc}}]
                with open('new_person.yaml', 'w') as f:
                    ppl_coll = yaml.dump(new_person, f)

        all_appts = collect_appts(ppl_coll)

        for person in ppl_coll:
            appts = collect_appts([person])
            if not appts:
                continue
            is_fully_appointed(person, begin_date, end_date)
            for appt in appts:
                grant = rc.client.find_one(rc.database, "grants", {"_id": appt.get("grant")})
                if not grant:
                    raise RuntimeError("    grant: {}, person: {}, appointment: {}, grant not found in grants database".format
                                     (appt.get("grant"), person.get("_id"), appt.get("_id")))
                a_begin, a_end = get_dates(appt)['begin_date'], get_dates(appt)['end_date']
                total_burn = grant_burn(grant, all_appts, begin_date=a_begin, end_date=a_end)
                timespan = a_end - a_begin
                outdated_period, depleted_period = False, False
                for x in range (timespan.days + 1):
                    if not outdated_period:
                        day = a_begin + relativedelta(days=x)
                        if not is_current(grant, now=day):
                            outdated.append("    person: {}, appointment: {}, grant: {},\n"
                                            "            from {} until {}".format(
                                person.get('_id'), appt.get('_id'), grant.get('_id'), str(day),
                                str(min(a_end, get_dates(grant)['begin_date']))))
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
                                person.get('_id'), appt.get('_id'), grant.get('_id'), str(day), str(a_end)))
                            depleted_period = True


        for grant in self.gtx["grants"]:
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
