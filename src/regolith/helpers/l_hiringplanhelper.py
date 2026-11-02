"""Helper for working out how many students and postdocs to hire."""

import datetime as dt

from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
from gooey import GooeyParser

from regolith.appointments import LEGACY_OUTSIDE_GRANTS, funded_employment
from regolith.dates import get_dates, has_dates
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.hiring_plan import (
    committed_needs,
    evaluate_plans,
    expected_new_funding,
    first_of_month,
    grant_supplies,
    month_starts,
    months_per_dollar,
)
from regolith.tools import all_docs_from_collection, fuzzy_retrieval, merge_collections_superior, strip_str

HELPER_TARGET = "l-hiringplan"
# Students arrive in October, at least this many months after the plan is made
STUDENT_START_MONTH = 10
STUDENT_LEAD_MONTHS = 6
POSTDOC_LEAD_MONTHS = 4


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
    subpi.add_argument(
        "--student-start",
        help="The day new students start. Defaults to the first October at least six months away.",
        type=strip_str,
        **date_kwargs,
    )
    subpi.add_argument("--student-years", type=float, default=4.5, help="How long a student stays, in years")
    subpi.add_argument("--students-most", type=int, default=4, help="The most new students to consider")
    subpi.add_argument(
        "--postdoc-start",
        help="The day new postdocs start. Defaults to four months from now.",
        type=strip_str,
        **date_kwargs,
    )
    subpi.add_argument("--postdoc-years", type=float, default=2, help="How long a postdoc stays, in years")
    subpi.add_argument("--postdoc-third-year", action="store_true", help="Plan for postdocs to stay a third year")
    subpi.add_argument("--postdocs-most", type=int, default=3, help="The most new postdocs to consider")
    subpi.add_argument(
        "--success-rate",
        type=float,
        default=0.25,
        help="The chance a pending proposal is funded, used to estimate new funding",
    )
    subpi.add_argument(
        "--new-funding-per-year",
        type=float,
        default=0.0,
        help="The months of support a year expected from proposals not yet written, added to the pending ones",
    )
    subpi.add_argument(
        "--no-extension",
        action="store_true",
        help="Do not assume federal grants get a one-year no-cost extension",
    )
    subpi.add_argument(
        "--plan",
        type=strip_str,
        help="The plan to show in detail, as students,postdocs, e.g. 2,1. Defaults to the suggested plan.",
    )
    subpi.add_argument(
        "--group",
        type=strip_str,
        help="The id of the group in the group field of employment. Defaults to the group whose id, name or "
        "aka is the groupname in regolithrc.json.",
    )
    subpi.add_argument("--date", help="The date to plan from. Defaults to today.", type=strip_str, **date_kwargs)
    return subpi


def _months(value):
    return f"{value:6.1f}"


class HiringPlanHelper(SoutHelperBase):
    """Helper for working out how many students and postdocs to hire.

    Every combination of new students and postdocs is tried against the
    grants' budgets, the appointments already made and the current group
    members, and the largest plan that expected new funding can cover is
    suggested.
    """

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = ["people", "grants", "proposals", "groups"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        for coll in self.needed_colls:
            gtx[coll] = sorted(all_docs_from_collection(rc.client, coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def _group_id(self):
        rc = self.rc
        if rc.group:
            return rc.group
        groupname = str(rc._get("groupname", "") or "")
        group = fuzzy_retrieval(self.gtx["groups"], ["_id", "name", "aka"], groupname, case_sensitive=False)
        return group["_id"] if group else groupname

    def sout(self):
        rc = self.rc
        today = date_parser.parse(rc.date).date() if rc.date else dt.date.today()
        plan_start = first_of_month(today) + relativedelta(months=1)
        if rc.student_start:
            student_start = date_parser.parse(rc.student_start).date()
        else:
            earliest = today + relativedelta(months=STUDENT_LEAD_MONTHS)
            student_start = dt.date(earliest.year, STUDENT_START_MONTH, 1)
            if student_start < earliest:
                student_start = dt.date(earliest.year + 1, STUDENT_START_MONTH, 1)
        if rc.postdoc_start:
            postdoc_start = date_parser.parse(rc.postdoc_start).date()
        else:
            postdoc_start = first_of_month(today + relativedelta(months=POSTDOC_LEAD_MONTHS))
        postdoc_years = rc.postdoc_years + (1 if rc.postdoc_third_year else 0)
        hires = {
            "students": {"most": rc.students_most, "start": student_start, "years": rc.student_years},
            "postdocs": {"most": rc.postdocs_most, "start": postdoc_start, "years": postdoc_years},
        }
        plan_end = max(
            plan_start + relativedelta(years=3, days=-1),
            student_start + relativedelta(months=round(rc.student_years * 12), days=-1),
            postdoc_start + relativedelta(months=round(postdoc_years * 12), days=-1),
        )

        # Grants that once stood for outside funding pay for nothing from the group's money
        grants = [
            grant
            for grant in merge_collections_superior(self.gtx["proposals"], self.gtx["grants"], "proposal_id")
            if grant.get("_id") not in LEGACY_OUTSIDE_GRANTS and grant.get("alias") not in LEGACY_OUTSIDE_GRANTS
        ]
        people = self.gtx["people"]
        group_id = self._group_id()
        all_appointments = [
            {**appointment, "_id": appointment_id, "person": person["_id"]}
            for person in people
            for appointment_id, appointment in (person.get("appointments") or {}).items()
        ]
        supplies, unreadable = grant_supplies(grants, all_appointments, plan_start, extensions=not rc.no_extension)
        pinned, open_needs = committed_needs(people, grants, group_id, plan_start, plan_end)
        rate = months_per_dollar(grants)
        months = month_starts(plan_start, plan_end)
        expected = self._expected = expected_new_funding(
            self.gtx["proposals"], rc.success_rate, rate, months, rc.new_funding_per_year
        )
        plans = evaluate_plans(supplies, pinned, open_needs, months, expected, hires)

        self._print_assumptions(today, plan_start, plan_end, hires, supplies, expected, rate)
        self._print_warnings(grants, people, group_id, plan_start, plan_end, unreadable)
        self._print_plans(plans)
        if rc.plan:
            students, postdocs = (int(number) for number in rc.plan.split(","))
            chosen = next(
                (plan for plan in plans if (plan["students"], plan["postdocs"]) == (students, postdocs)), None
            )
            if not chosen:
                raise ValueError(
                    f"The plan {rc.plan} is not among those tried. Please give at most --students-most students "
                    "and --postdocs-most postdocs, or raise them."
                )
        else:
            chosen = plans[0]
        self._print_detail(chosen, supplies, plan_start, plan_end, suggested=not rc.plan)
        if not rc.plan and chosen["covered"]:
            at_limit = [
                f"--{kind}-most"
                for kind, count in (("students", chosen["students"]), ("postdocs", chosen["postdocs"]))
                if count == hires[kind]["most"]
            ]
            if at_limit:
                print(
                    f"  This is the most {' and '.join(option[2:-5] for option in at_limit)} tried; raise "
                    f"{' and '.join(at_limit)} to see whether more could be supported."
                )

    def _print_assumptions(self, today, plan_start, plan_end, hires, supplies, expected, rate):
        rc = self.rc
        students, postdocs = hires["students"], hires["postdocs"]
        print(f"Hiring plan from {plan_start}, made on {today}")
        print(
            f"  new students start {students['start']} for {students['years']:g} years; "
            f"new postdocs start {postdocs['start']} for {postdocs['years']:g} years"
        )
        extended = sorted(supply["alias"] for supply in supplies if supply["extended_end"] != supply["end_date"])
        print(f"  grants counted: {', '.join(sorted(supply['alias'] for supply in supplies)) or 'none'}")
        if extended:
            print(f"  assumed to get a one-year no-cost extension: {', '.join(extended)}")
        if rate:
            how = (
                f"pending proposals x {rc.success_rate:g} success rate, at {rate * 100000:.1f} months per "
                "$100k, the rate of the group's grants"
            )
        else:
            how = "no grants have both a budget and an amount, so pending proposals cannot be turned into months"
        if rc.new_funding_per_year:
            how += f", plus {rc.new_funding_per_year:g} months a year from proposals not yet written"
        print(f"  new funding expected by {plan_end}: {sum(expected.values()):.1f} months ({how})")
        print("  months are months of support, student and postdoc alike")

    def _print_warnings(self, grants, people, group_id, plan_start, plan_end, unreadable):
        warnings = [
            f"{alias} has a budget period with no begin or end date, so it is not counted; fix it with "
            f"u_grant {alias} --edit-budget"
            for alias in unreadable
        ]
        for grant in grants:
            dates = get_dates(dict(grant)) if has_dates(grant) else {}
            if dates.get("end_date") and dates["end_date"] >= plan_start and not grant.get("budget"):
                warnings.append(
                    f"{grant.get('alias') or grant['_id']} is current but has no budget, so it is not counted"
                )
        for person in people:
            for position in funded_employment(person, group_id):
                if not position["end_date"]:
                    warnings.append(f"{person['_id']} has no end date for their {position['position']} position")
                elif position["end_date"] > plan_end + relativedelta(years=5):
                    warnings.append(
                        f"{person['_id']}'s {position['position']} position ends on {position['end_date']}, "
                        f"which looks like a placeholder; the plan funds them to {plan_end}"
                    )
        if warnings:
            print("\nCheck these, since the plan depends on them:")
            for warning in warnings:
                print(f"  {warning}")

    def _print_plans(self, plans):
        print(
            "\nmonths of support for each plan: lost when grants end unspent, paid in no-cost extension years,\n"
            "needing new funding, and the most that falls short of the new funding expected by then"
        )
        print("students postdocs    lost  extension  new funding  short by  first short  covered")
        for plan in sorted(plans, key=lambda plan: (plan["students"], plan["postdocs"])):
            print(
                f"{plan['students']:>8} {plan['postdocs']:>8} {_months(plan['lost']):>7} "
                f"{_months(plan['extension']):>10} {_months(plan['unpaid']):>12} {_months(plan['short_by']):>9}"
                f"  {str(plan['first_short'] or '-'):>11}  {'yes' if plan['covered'] else 'no'}"
            )

    def _print_detail(self, plan, supplies, plan_start, plan_end, suggested):
        label = "Suggested plan" if suggested else "Plan"
        if suggested and not plan["covered"]:
            label = "No plan is covered by the new funding expected; the closest is"
        print(f"\n{label}: {plan['students']} students and {plan['postdocs']} postdocs")
        result = plan["result"]
        years = list(range(plan_start.year, plan_end.year + 1))
        print("months paid each year:")
        print("  " + "grant".ljust(22) + "".join(f"{year:>8}" for year in years))
        aliases = {supply["_id"]: supply["alias"] for supply in supplies}
        for grant_id, paid in result["paid"].items():
            if not paid:
                continue
            row = [sum(value for month, value in paid.items() if month.year == year) for year in years]
            print("  " + aliases[grant_id][:22].ljust(22) + "".join(f"{value:8.1f}" for value in row))
        row = [sum(value for month, value in result["unpaid"].items() if month.year == year) for year in years]
        print("  " + "needs new funding".ljust(22) + "".join(f"{value:8.1f}" for value in row))
        row = [sum(value for month, value in self._expected.items() if month.year == year) for year in years]
        print("  " + "new funding expected".ljust(22) + "".join(f"{value:8.1f}" for value in row))
        for grant_id, months in sorted(result["extension"].items()):
            print(f"  {aliases[grant_id]} pays {months:.1f} months in its no-cost extension year, which is a risk")
        for grant_id, months in sorted(result["lost"].items()):
            if months > 0.05:
                print(
                    f"  {aliases[grant_id]} ends with {months:.1f} months unspent: people paid before it ends, "
                    "such as an earlier postdoc, would use them"
                )
