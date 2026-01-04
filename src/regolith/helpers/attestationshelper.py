import calendar
from datetime import date, timedelta

import dateutil.parser as date_parser
import matplotlib.pyplot as plt
import numpy as np

from regolith.dates import get_dates
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    fuzzy_retrieval,
    get_appointments,
    merge_collections_superior,
    strip_str,
)

# print([k for k,v in chained_db['people'].items()])

MONTH_COST = 3400


def daterange(date1, date2):
    return [date1 + timedelta(n) for n in range(int((date2 - date1).days) + 1)]


def subparser(subpi):
    subpi.add_argument(
        "-g", "--grant", type=strip_str, help="grant id for the grant you want to find appointments."
    )
    subpi.add_argument(
        "-b",
        "--begin-date",
        type=strip_str,
        help="effort reporting period begins on this date, format YYYY-MM-DD. "
        "Attestations run from the beginning to the end of the grant.",
    )
    subpi.add_argument(
        "-e",
        "--end-date",
        type=strip_str,
        help="effort reporting period ends on this date. "
        "Attestations run from the beginning to the end of the grant.",
    )
    subpi.add_argument(
        "--effort-reporting",
        action="store_true",
        help="list loadings by grant per month per person across " "all grants.",
    )
    subpi.add_argument("--verbose", action="store_true", help="increase verbosity.  Show who incurred expenses")
    subpi.add_argument("--no-plot", action="store_true", help="suppress the plotting")
    return subpi


class AttestationsHelper(DbHelperBase):
    """Helper for attestations."""

    # btype must be the same as helper target in helper.py
    btype = "attestation"
    needed_colls = ["people", "grants", "proposals", "expenses"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        # if not rc.database:
        #     rc.database = rc.databases[0]["name"]
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["expenses"] = sorted(all_docs_from_collection(rc.client, "expenses"), key=_id_key)
        gtx["grants"] = sorted(all_docs_from_collection(rc.client, "grants"), key=_id_key)
        gtx["proposals"] = sorted(all_docs_from_collection(rc.client, "proposals"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        expenses = self.gtx["expenses"]
        people = self.gtx["people"]
        grants = merge_collections_superior(self.gtx["proposals"], self.gtx["grants"], "proposal_id")
        if not rc.grant and not rc.effort_reporting:
            raise RuntimeError(
                "Grant needed for Attestation.  Please rerun specifying "
                "--grant GRANT_ALIAS or specify --effort-reporting if you "
                "want an effort report."
            )
        if rc.effort_reporting and not rc.begin_date:
            print(rc.begin_date)
            raise RuntimeError(
                "Begin date needed for effort reporting.  Please rerun specifying "
                "--begin-date YYYY-MM-DD (and preferably --end-date YYYY-MM-DD) "
                "or remove --effort-reporting if you "
                "want an attestation report for a grant"
            )
        if rc.effort_reporting and rc.grant:
            raise print(
                "WARNING: Ignoring the value specified for --grant as "
                "--effort reporting was specified which is over"
                "all grants."
            )
        grant = fuzzy_retrieval(grants, ["name", "_id", "alias"], rc.grant)
        if rc.effort_reporting:
            begin_date = date_parser.parse(rc.begin_date).date()
            if rc.end_date:
                end_date = date_parser.parse(rc.end_date).date()
            else:
                end_date = date.today()
        else:
            print(
                f"Instructions/Notes:\n"
                f"  Quarters are: Q1 July thru Sept, Q2 Oct - Dec, Q3 Jan - Mar, Q4 Apr - Jun\n"
                f"  Grad salaries are about ${MONTH_COST} per month"
            )
            print(f"Collecting Appointments for grant {rc.grant}:")
            begin_date = get_dates(grant).get("begin_date")
            end_date = get_dates(grant).get("end_date")

        plot_date_list = daterange(begin_date, end_date)
        months = [plot_date_list[0]]
        for day in plot_date_list:
            if day.day == 1:
                months.append(day)
        # only if period starts at the beginning of the month the first month will be
        # double counted
        if months[0].day == 1:
            months = months[1:]
        appts = []
        if rc.effort_reporting:
            for person in people:
                if person.get("appointments"):
                    appts = get_appointments(person, appts)
        else:
            for person in people:
                if person.get("appointments"):
                    appts = get_appointments(person, appts, rc.grant)
        appts = [app for app in appts if app[1] < end_date and app[2] >= begin_date]
        appts.sort(key=lambda x: (x[0], x[1]))
        folks = [app[0] for app in appts]
        folks = list(set(folks))
        if not rc.effort_reporting:
            for app in appts:
                print(
                    f"{app[0]}, from {app[1].strftime('%Y-%m-%d')} to "
                    f"{app[2].strftime('%Y-%m-%d')}, loading {app[3]}. Total months: "
                    f"{app[4]}"
                )
        plots, people_loadings = [], []
        loadingc = np.zeros(len(plot_date_list))
        for folk in folks:
            fig, ax = plt.subplots()
            loadinga = np.zeros(len(plot_date_list))
            for app in appts:
                if app[0] == folk:
                    loadingl = []
                    for day in plot_date_list:
                        if app[1] <= day <= app[2]:
                            loadingl.append(app[3])
                        else:
                            loadingl.append(0)
                    loadinga = loadinga + np.array(loadingl)
            loadingc = loadingc + loadinga

            loadingm, accum, days = [], 0, 0
            for day, load in zip(plot_date_list, loadinga):
                accum = accum + load
                days += 1
                if day.day == calendar.monthrange(day.year, day.month)[-1]:
                    loadingm.append(accum * MONTH_COST / days)
                    accum, days = 0, 0
            # capture any partial month at the end of the period
            if days > 0:
                loadingm.append(accum * MONTH_COST / days)

            people_loadings.append((folk, loadinga, loadingm))
            if not rc.no_plot:
                ax.plot_date(plot_date_list, loadinga, ls="-", marker="", label=folk)
                ax.set_xlabel("date")
                ax.set_ylabel(f"loading for student {app[0]}")
                ax.legend(loc="best")
                fig.autofmt_xdate()
                plots.append(fig)

        if not rc.no_plot:
            fig, ax = plt.subplots()
            ax.plot_date(plot_date_list, loadingc, ls="-", marker="")

        if rc.effort_reporting:
            toprow = ","
            for month in months:
                toprow = f"{toprow}, {month.isoformat()}"
            print(toprow)
            for appt in appts:
                row = f"{appt[0]}, {appt[5]}"
                for month in months:
                    if month >= appt[1] and month < appt[2]:
                        row = f"{row}, {appt[3]*100}"
                    else:
                        row = f"{row}, 0.0"
                print(row)
        else:
            print("\n-----------\nLoadings by month\n------------")
            index = 0

            for month in months:
                print(f"{month.isoformat()}:")
                for person in people_loadings:
                    if person[2][index] > 0:
                        print(f"    {person[0]}\tloading: {round(person[2][index], 2)}")
                index += 1
            print("\n----------------\nExpenses\n----------------")
            expenses_on_grant = [expense for expense in expenses if rc.grant in expense.get("grants")]

            if len(expenses_on_grant) > 1:
                expenses_on_grant.sort(key=lambda x: get_dates(x).get("end_date"))
            for expense in expenses_on_grant:
                for reimb in expense.get("reimbursements"):
                    if reimb.get("amount") == 0:
                        amt = 0
                        for exp_item in expense.get("itemized_expenses", []):
                            amt += exp_item.get("unsegregated_expense")
                            amt += exp_item.get("prepaid_expense", 0)
                        reimb["amount"] = amt

            total_spend, month_spend, all_reimb_dates, all_reimb_amts = 0, 0, [], []
            for e in expenses_on_grant:
                reimb_amts = [round(i.get("amount"), 2) for i in e.get("reimbursements", [{}])]
                reimb_dates = [
                    get_dates(i).get("date", get_dates(e).get("end_date")) for i in e.get("reimbursements", [{}])
                ]
                all_reimb_dates.extend(reimb_dates)
                all_reimb_amts.extend(reimb_amts)
                total_spend += sum(reimb_amts)

                if rc.verbose:
                    for reim_date, amt in zip(reimb_dates, reimb_amts):
                        print(
                            f"{reim_date} (reimb date), {get_dates(e).get('end_date')} (expense date): amount: "
                            f"{amt}, "
                        )
                    print(f"  payee: {e.get('payee')} " f"purpose: {e.get('overall_purpose')[:60]}")
            for month in months:
                if month >= begin_date:
                    month_spend = 0
                    for amt, dte in zip(all_reimb_amts, all_reimb_dates):
                        if month.year == dte.year and month.month == dte.month:
                            month_spend += amt
                    print(f"{month}: expenses monthly total = {month_spend:.2f}")

            print(f"Total spend = {round(total_spend, 2)}")

        for plot in plots:
            plt.show()
