"""Helper for managing appointments.

- Returns members with gap in appointments
- Returns members supported on an outdated grant
- Returns members supported on a depleted grant
- Suggests appointments to make for these members
- Suggests new appointments
"""

from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
from gooey import GooeyParser

from regolith.dates import get_dates

# from regolith.schemas import APPOINTMENTS_TYPES
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import (
    all_docs_from_collection,
    collect_appts,
    fuzzy_retrieval,
    get_pi_id,
    grant_burn,
    group_member_employment_start_end,
    is_fully_appointed,
    merge_collections_superior,
)

TARGET_COLL = "people"
HELPER_TARGET = "makeappointments"
BLACKLIST = [
    "ta",
    "physmatch",
    "chemmatch",
    "bridge16",
    "collgf",
    "afgrf14",
    "summer@seas",
    "frap",
    "startup",
    "they_pay",
]
MONTHLY_COST_QUANTUM = 3262

_future_grant = {
    "_id": "_future_grant",
    "account": "n/a",
    "activity": 0,
    "admin": "tbd",
    "alias": "future_grant",
    "amount": 0,
    "awardnr": "tbd",
    "budget": [
        {
            "begin_date": "2020-05-01",
            "end_date": "2099-12-31",
            "amount": 0,
            "student_months": 0,
            "postdoc_months": 0,
            "ss_months": 0,
        }
    ],
}


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
    else:
        subpi.add_argument(
            "run",
            help="Run the helper"
            'The grant "future_grant" is available internally '
            "to assign people to for making projections.  It "
            "will be plotted to show when you need new funding "
            "by and how much.",
        )
    subpi.add_argument(
        "-d",
        "--projection-from-date",
        help="the date from which projections into the future " "will be calculated",
        **date_kwargs,
    )
    subpi.add_argument("--no-plot", action="store_true", help="suppress plotting feature")
    subpi.add_argument(
        "--no-gui", action="store_true", help="suppress interactive matplotlib GUI (used for " "running tests)"
    )
    subpi.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Plot all non-blacklisted grants.  If not set, grants "
        "that ended more than 2 years ago won't be plotted",
    )
    # Do not delete --database arg
    subpi.add_argument(
        "--database", help="The database that will be updated. Defaults to first database in regolithrc.json"
    )

    return subpi


def plotter(datearray, student=None, pd=None, ss=None, title=None):
    fig, ax = plt.subplots()
    sta = numpy.array(student) / 30.5
    pda = numpy.array(pd) / 30.5
    ssa = numpy.array(ss) / 30.5
    if student:
        ax.plot(datearray, sta, ",-", label="student months")
    if pd:
        ax.plot(datearray, pda, ",-", label="postdoc months")
    if ss:
        ax.plot(datearray, ssa, ",-", label="ss months")
    if student and pd:
        ax.plot(datearray, sta + pda, ",-", label="student+postdoc days")
    ax.set_xlabel("date")
    ax.set_ylabel("budget months remaining")
    ax.set_title(title)
    ax.legend(loc="best")
    fig.autofmt_xdate()
    return fig, ax, "plotting mode is on"


class MakeAppointmentsHelper(SoutHelperBase):
    """Helper for managing appointments on grants and studying the burn
    of grants over time."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "grants", "proposals"]

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
        except Exception:
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
        outdated, depleted, underspent, overspent = [], [], [], []
        people = list(self.gtx["people"])
        all_appts = collect_appts(people, filter_key="type", filter_value="gra")
        all_appts.extend(collect_appts(people, filter_key="type", filter_value="ss"))
        all_appts.extend(collect_appts(people, filter_key="type", filter_value="pd"))
        if rc.projection_from_date:
            projection_from_date = date_parser.parse(rc.projection_from_date).date()
        else:
            projection_from_date = date.today()

        # collecting amounts and time interval for all grants
        _future_grant["begin_date"] = projection_from_date
        _future_grant["end_date"] = projection_from_date + timedelta(days=2190)
        _future_grant["budget"][0]["begin_date"] = projection_from_date
        _future_grant["budget"][0]["end_date"] = projection_from_date + timedelta(days=2190)
        _future_grant["burn"] = grant_burn(_future_grant, all_appts)
        all_grants = merge_collections_superior(self.gtx["proposals"], self.gtx["grants"], "proposal_id")
        all_grants.append(_future_grant)
        most_grants_id = [grant for grant in all_grants if grant.get("_id") not in BLACKLIST]
        most_grants = [grant for grant in most_grants_id if grant.get("alias") not in BLACKLIST]
        collecting_grants_with_appts = []
        for person in self.gtx["people"]:
            appts = collect_appts([person], filter_key="type", filter_value="gra")
            appts.extend(collect_appts([person], filter_key="type", filter_value="ss"))
            appts.extend(collect_appts([person], filter_key="type", filter_value="pd"))
            if len(appts) > 0:
                person.update({"appts": appts})
                collecting_grants_with_appts.extend([appt.get("grant") for appt in appts])
        grants_with_appts = list(set(collecting_grants_with_appts))
        appointed_grants = [
            grant
            for grant in most_grants
            if grant.get("_id") in grants_with_appts or grant.get("alias") in grants_with_appts
        ]
        grants_end, grants_begin = None, None
        for grant in appointed_grants:
            grant["burn"] = grant_burn(grant, all_appts)
            grant_begin = get_dates(grant)["begin_date"]
            grant_end = get_dates(grant)["end_date"]
            grant.update({"begin_date": grant_begin, "end_date": grant_end})
            if not grants_begin or grant_begin < grants_begin:
                grants_begin = grant_begin
            if not grants_end or grant_end > grants_end:
                grants_end = grant_end

        # checking appointments
        cum_months_to_cover = 0
        for person in self.gtx["people"]:
            if not person.get("appts"):
                continue
            appts = person.get("appts")
            person_dates = group_member_employment_start_end(person, "bg")
            emps = [person_date for person_date in person_dates if not person_date.get("permanent")]
            emps.sort(key=lambda x: x.get("end_date", 0))
            is_fully_appointed(
                person,
                min(get_dates(appt)["begin_date"] for appt in appts),
                max(get_dates(appt)["end_date"] for appt in appts),
            )
            for appt in appts:
                if appt.get("grant") in BLACKLIST:
                    continue
                this_grant = fuzzy_retrieval(appointed_grants, ["_id", "alias"], appt.get("grant"))
                if not this_grant:
                    raise RuntimeError(
                        "    grant: {}, person: {}, appointment: {}, grant not found in grants database".format(
                            appt.get("grant"), person.get("_id"), appt.get("_id")
                        )
                    )
                appt_begin, appt_end = get_dates(appt)["begin_date"], get_dates(appt)["end_date"]
                outdated_period, depleted_period = False, False
                for x in range((appt_end - appt_begin).days + 1):
                    day = appt_begin + relativedelta(days=x)
                    if not outdated_period:
                        if not this_grant.get("burn"):
                            print(this_grant.get("_id"))
                        if not this_grant["burn"].get(day):
                            outdated_period = True
                            outdated.append(
                                "    person: {}, appointment: {}, grant: {},\n"
                                "            from {} until {}".format(
                                    person.get("_id"),
                                    appt.get("_id"),
                                    appt.get("grant"),
                                    (
                                        str(day)
                                        if day < this_grant["begin_date"]
                                        else this_grant["end_date"] + relativedelta(days=1)
                                    ),
                                    (
                                        str(min(appt_end, this_grant["begin_date"]))
                                        if day < this_grant["begin_date"]
                                        else str(day)
                                    ),
                                )
                            )
                    else:
                        if this_grant["burn"].get(day):
                            outdated_period = False
                    if not (depleted_period or outdated_period):
                        day_burn, this_burn = 0, this_grant["burn"]
                        if appt.get("type") == "gra":
                            day_burn = this_burn[day]["student_days"]
                        elif appt.get("type") == "pd":
                            day_burn = this_burn[day]["postdoc_days"]
                        elif appt.get("type") == "ss":
                            day_burn = this_burn[day]["ss_days"]
                        if day_burn < -5:
                            # FIXME change to display depleted until next >-5 amt instead of appt_end
                            depleted.append(
                                "    person: {}, appointment: {}, grant: {},\n"
                                "            from {} until {}".format(
                                    person["_id"], appt["_id"], appt.get("grant"), str(day), str(appt_end)
                                )
                            )
                            depleted_period = True

        # setup for plotting grants
        datearray, cum_student, cum_pd, cum_ss = [], None, None, None
        if not rc.no_plot:
            for x in range((grants_end - grants_begin).days + 1):
                datearray.append(grants_begin + relativedelta(days=x))
            cum_student, cum_pd, cum_ss = [0.0] * len(datearray), [0.0] * len(datearray), [0.0] * len(datearray)
        plots = []

        # calculating grant surplus and deficit
        cum_underspend = 0
        for grant in appointed_grants:
            tracking = [balance for balance in grant.get("tracking", []) if balance]
            # if all_grants[grant]:
            #     tracking = [balance for balance in all_grants[grant].get('tracking',[]) if balance]
            # else:
            #     tracking = []
            if len(tracking) > 0:
                tracking.sort(key=lambda x: x[0])
                recent_balance = tracking[-1]
                recent_balance[1] = recent_balance[1] / MONTHLY_COST_QUANTUM
            else:
                recent_balance = [projection_from_date, 0]
            budget_begin = min(get_dates(period)["begin_date"] for period in grant.get("budget"))
            budget_end = max(get_dates(period)["end_date"] for period in grant.get("budget"))
            if grant["begin_date"] != budget_begin:
                raise RuntimeError(
                    f"grant {grant.get('alias')} does not have a correct budget begin date. "
                    f"grant begin: {grant['begin_date']} budget begin: {budget_begin}"
                )
            elif grant["end_date"] != budget_end:
                raise RuntimeError(
                    f"grant {grant.get('alias')} does not have a correct budget end date."
                    f" grant end: {grant['end_date']} budget end: {budget_end}"
                )
            days_to_go = (grant["end_date"] - projection_from_date).days
            this_burn = grant["burn"]
            end_amount = (
                this_burn.get(grant["end_date"])["student_days"]
                + this_burn.get(grant["end_date"])["ss_days"]
                + this_burn.get(grant["end_date"])["postdoc_days"]
            )
            if end_amount > 15.25:
                underspent.append(
                    (
                        grant["end_date"],
                        grant.get("alias"),
                        round(end_amount / 30.5, 2),
                        round(end_amount / days_to_go, 2),
                    )
                )
                cum_underspend += end_amount
            elif end_amount < -30.5:
                overspent.append(
                    "    end: {}, grant: {}, overspend amount: {} months".format(
                        str(grant["end_date"]), grant.get("alias"), round(end_amount / 30.5, 2)
                    )
                )
            # values for individual and cumulative grant burn plots
            if not rc.no_plot:
                grant_dates = [
                    grant["begin_date"] + relativedelta(days=x)
                    for x in range((grant["end_date"] - grant["begin_date"]).days + 1)
                ]
                this_student, this_pd, this_ss = (
                    [0.0] * len(grant_dates),
                    [0.0] * len(grant_dates),
                    [0.0] * len(grant_dates),
                )
                counter = 0
                for x in range(len(datearray)):
                    day_burn = this_burn.get(datearray[x])
                    if day_burn:
                        this_student[counter] = day_burn["student_days"]
                        this_pd[counter] = day_burn["postdoc_days"]
                        this_ss[counter] = day_burn["ss_days"]
                        cum_student[x] += day_burn["student_days"]
                        cum_pd[x] += day_burn["postdoc_days"]
                        cum_ss[x] += day_burn["ss_days"]
                        counter += 1
                if not rc.verbose:
                    if max(grant_dates) >= projection_from_date - timedelta(days=730):
                        plots.append(
                            plotter(
                                grant_dates, student=this_student, pd=this_pd, ss=this_ss, title=grant.get("alias")
                            )[0]
                        )
                else:
                    plots.append(
                        plotter(
                            grant_dates, student=this_student, pd=this_pd, ss=this_ss, title=grant.get("alias")
                        )[0]
                    )

        if outdated:
            outdated.sort(key=lambda mess: mess[-10:])
            print("appointments on outdated grants:")
            for appt in outdated:
                print(appt)
        if depleted:
            depleted.sort(key=lambda mess: mess[-10:])
            print("appointments on depleted grants:")
            for appt in depleted:
                print(appt)
        if underspent:
            underspent.sort(key=lambda x: x[0])
            print("underspent grants:")
            for grant_info in underspent:
                print(
                    f"    {grant_info[1]}: end: {grant_info[0]}\n"
                    f"      projected underspend: {grant_info[2]} months, "
                    f"balance as of {recent_balance[0]}: {recent_balance[1]}\n"
                    f"      required ss+gra burn: {grant_info[3]}"
                )
            print(
                f"cumulative underspend = {round(cum_underspend/30.5, 2)} months, "
                f"cumulative months to support = {round(cum_months_to_cover, 2)}"
            )
        if overspent:
            print("overspent grants:")
            for grant in overspent:
                print(grant)

        if not rc.no_plot:
            for plot in plots:
                if not rc.no_gui:
                    plt.show()
            cum_plot, cum_ax, outp = plotter(
                datearray, student=cum_student, pd=cum_pd, ss=cum_ss, title="Cumulative burn"
            )
            if not rc.no_gui:
                plt.show()

            print(outp)

        return
