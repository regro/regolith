"""Work out how many students and postdocs the group's grants can
support.

The grants' budgets give months of support (student, postdoc and summer
months, treated alike since they cost about the same).  Unspent months
carry forward within a grant until it ends, and a federal grant is
assumed to get a one-year no-cost extension, used only when nothing else
can pay.  The months needed come from the appointments already made,
from current group members until their positions end, and from the hires
being considered.  Each month, the people needing support are paid from
the grant that ends soonest and still has money, which wastes the least.
What no grant can pay must come from new funding.
"""

import datetime as dt
from itertools import product

from dateutil.relativedelta import relativedelta

from regolith.appointments import FUTURE_GRANT, daily_loading, funded_employment, is_outside
from regolith.dates import get_dates, has_dates
from regolith.tools import grant_burn

DAYS_PER_MONTH = 30.5
# Funders whose grants normally get a one-year no-cost extension, matched at the start of the funder
FEDERAL_FUNDERS = (
    "nsf",
    "national science foundation",
    "doe",
    "department of energy",
    "nih",
    "national institutes of health",
    "dod",
    "department of defense",
    "defense",
    "dtra",
    "darpa",
    "afosr",
    "air force",
    "aro",
    "army",
    "onr",
    "navy",
    "nasa",
    "nist",
    "noaa",
)
EXTENSION_YEARS = 1
# Proposals still waiting for a decision
PENDING_STATI = ("submitted", "pending")


def first_of_month(day):
    return dt.date(day.year, day.month, 1)


def month_starts(begin_date, end_date):
    """Return the first day of each month from one date to another.

    Parameters
    ----------
    begin_date : datetime.date
        A day in the first month.
    end_date : datetime.date
        A day in the last month.

    Returns
    -------
    list of datetime.date
        The first day of each month, in order.
    """
    months, month = [], first_of_month(begin_date)
    while month <= end_date:
        months.append(month)
        month += relativedelta(months=1)
    return months


def monthly_loading(begin_date, end_date, loading=1.0):
    """Return the months of support something needs in each month.

    Parameters
    ----------
    begin_date : datetime.date
        The first day.
    end_date : datetime.date
        The last day.
    loading : float, optional
        The loading, 1 for full time.

    Returns
    -------
    dict
        The months needed, keyed by the first day of each month.
    """
    needs = {}
    for day, value in daily_loading(
        [{"begin_date": begin_date, "end_date": end_date, "loading": loading}], begin_date, end_date
    ).items():
        needs[first_of_month(day)] = needs.get(first_of_month(day), 0.0) + value / DAYS_PER_MONTH
    return needs


def is_federal(grant):
    """Return True when a grant's funder normally gives no-cost
    extensions.

    Parameters
    ----------
    grant : dict
        The grant.

    Returns
    -------
    bool
        The answer to whether its funder starts with a federal funder's
        name.
    """
    funder = str(grant.get("funder", "")).casefold().strip()
    return any(funder == name or funder.startswith((name + " ", name + "-")) for name in FEDERAL_FUNDERS)


def _budget_months(period):
    return sum(
        float(period.get(f"{kind}_months", 0) or 0) - float(period.get(f"{kind}_writeoff", 0) or 0)
        for kind in ("student", "postdoc", "ss")
    )


def grant_supplies(grants, all_appointments, plan_start, extensions=True):
    """Return the months of support each grant has from the start of the
    plan.

    Parameters
    ----------
    grants : list of dict
        The grants, merged with their proposals. Grants with no dates or
        no budget, or that end before the plan starts, are left out.
    all_appointments : list of dict
        Every appointment, used for the money spent before the plan
        starts.
    plan_start : datetime.date
        The first day of the first month of the plan.
    extensions : bool, optional
        The switch for giving federal grants a no-cost extension year.

    Returns
    -------
    supplies : list of dict
        For each grant, its _id and alias, its end date, the end date
        with any extension, the months left the day before the plan
        starts, and the months its later budget periods add, keyed by
        month.
    unreadable : list of str
        The grants left out because a budget period has no dates.
    """
    supplies, unreadable = [], []
    for grant in grants:
        if not has_dates(grant) or not grant.get("budget"):
            continue
        dates = get_dates(dict(grant))
        if not dates.get("end_date") or not dates.get("begin_date"):
            continue
        end_date = dates["end_date"]
        extended_end = (
            end_date + relativedelta(years=EXTENSION_YEARS) if extensions and is_federal(grant) else end_date
        )
        if extended_end < plan_start:
            continue
        if any(
            not get_dates(dict(period)).get("begin_date") or not get_dates(dict(period)).get("end_date")
            for period in grant["budget"]
        ):
            unreadable.append(grant.get("alias") or grant["_id"])
            continue
        before_start = plan_start - dt.timedelta(days=1)
        burn = grant_burn(grant, all_appointments)
        if before_start in burn:
            balance = sum(burn[before_start].values()) / DAYS_PER_MONTH
        elif burn and before_start > max(burn):
            balance = sum(burn[max(burn)].values()) / DAYS_PER_MONTH
        else:
            balance = 0.0
        additions = {}
        for period in grant["budget"]:
            period_begin = get_dates(dict(period)).get("begin_date")
            if period_begin and period_begin >= plan_start:
                month = first_of_month(period_begin)
                additions[month] = additions.get(month, 0.0) + _budget_months(period)
        supplies.append(
            {
                "_id": grant["_id"],
                "alias": grant.get("alias") or grant["_id"],
                "end_date": end_date,
                "extended_end": extended_end,
                "balance": balance,
                "additions": additions,
            }
        )
    return supplies, unreadable


def committed_needs(people, grants, group_id, plan_start, plan_end):
    """Return the months of support already needed: by appointments on a
    grant, and by current group members with no grant yet.

    Parameters
    ----------
    people : list of dict
        The people, with their appointments.
    grants : list of dict
        The grants, to find which one an appointment names.
    group_id : str
        The id of the group, to find funded positions.
    plan_start : datetime.date
        The first day of the plan.
    plan_end : datetime.date
        The last day of the plan.

    Returns
    -------
    pinned : dict
        The months needed on each grant, keyed by grant id and then by
        month.
    open_needs : dict
        The months needed with no grant yet, keyed by month.
    """
    grant_ids = {}
    for grant in grants:
        for name in (grant.get("_id"), grant.get("alias")):
            if name:
                grant_ids.setdefault(str(name).casefold(), grant["_id"])
    pinned, open_needs = {}, {}
    for person in people:
        appointments = [
            {**appointment, "_id": appointment_id}
            for appointment_id, appointment in (person.get("appointments") or {}).items()
        ]
        for appointment in appointments:
            if is_outside(appointment) or not has_dates(appointment):
                continue
            dates = get_dates(dict(appointment))
            begin_date, end_date = max(dates["begin_date"], plan_start), min(dates["end_date"], plan_end)
            if begin_date > end_date:
                continue
            needs = monthly_loading(begin_date, end_date, float(appointment.get("loading", 0)))
            grant_id = grant_ids.get(str(appointment.get("grant", "")).casefold())
            target = (
                open_needs
                if not grant_id or appointment.get("grant") == FUTURE_GRANT
                else pinned.setdefault(grant_id, {})
            )
            for month, months in needs.items():
                target[month] = target.get(month, 0.0) + months
        # The rest of a funded position, until it ends or the plan does, needs funding too
        for position in funded_employment(person, group_id):
            if not position["end_date"]:
                continue
            begin_date = max(plan_start, position["begin_date"] or plan_start)
            end_date = min(position["end_date"], plan_end)
            if begin_date > end_date:
                continue
            covered = daily_loading(appointments, begin_date, end_date)
            for day, loading in covered.items():
                if loading < 1:
                    month = first_of_month(day)
                    open_needs[month] = open_needs.get(month, 0.0) + (1 - loading) / DAYS_PER_MONTH
    return pinned, open_needs


def hire_needs(count, start_date, years):
    """Return the months of support a number of new hires need.

    Parameters
    ----------
    count : int
        The number of hires.
    start_date : datetime.date
        The day they start.
    years : float
        How long each stays, in years.

    Returns
    -------
    dict
        The months needed, keyed by month.
    """
    if not count:
        return {}
    end_date = start_date + relativedelta(months=round(years * 12)) - dt.timedelta(days=1)
    return {month: count * months for month, months in monthly_loading(start_date, end_date).items()}


def simulate(supplies, pinned, open_needs, months):
    """Pay the months needed from the grants, month by month.

    Appointments on a grant are paid from it first. Everything else is
    paid from the grant that ends soonest and still has money, counting
    its end without any extension, so an extension year is used only
    when nothing else can pay.

    Parameters
    ----------
    supplies : list of dict
        The grants, as returned by grant_supplies.
    pinned : dict
        The months needed on each grant, by grant id and month.
    open_needs : dict
        The months needed with no grant, by month.
    months : list of datetime.date
        The months of the plan.

    Returns
    -------
    dict
        paid: the months each grant pays, by grant id and month;
        unpaid: the months no grant can pay, by month;
        extension: the months paid in extension years, by grant id;
        lost: the months left unspent when each grant ends, by grant id.
    """
    balance = {supply["_id"]: supply["balance"] for supply in supplies}
    paid = {supply["_id"]: {} for supply in supplies}
    unpaid, extension, lost = {}, {}, {}
    by_end = sorted(supplies, key=lambda supply: (supply["end_date"], supply["_id"]))
    for month in months:
        month_end = month + relativedelta(months=1, days=-1)
        for supply in supplies:
            balance[supply["_id"]] += supply["additions"].get(month, 0.0)
        needed = open_needs.get(month, 0.0)
        for grant_id, grant_needs in pinned.items():
            want = grant_needs.get(month, 0.0)
            if grant_id in balance and balance[grant_id] > 0:
                take = min(want, balance[grant_id])
                balance[grant_id] -= take
                paid[grant_id][month] = paid[grant_id].get(month, 0.0) + take
                want -= take
            needed += want
        for supply in by_end:
            if needed <= 1e-9:
                break
            if supply["extended_end"] < month or balance[supply["_id"]] <= 1e-9:
                continue
            take = min(needed, balance[supply["_id"]])
            balance[supply["_id"]] -= take
            paid[supply["_id"]][month] = paid[supply["_id"]].get(month, 0.0) + take
            if month > supply["end_date"]:
                extension[supply["_id"]] = extension.get(supply["_id"], 0.0) + take
            needed -= take
        if needed > 1e-9:
            unpaid[month] = needed
        for supply in supplies:
            if supply["extended_end"] <= month_end and supply["_id"] not in lost:
                lost[supply["_id"]] = max(balance[supply["_id"]], 0.0)
    return {"paid": paid, "unpaid": unpaid, "extension": extension, "lost": lost}


def months_per_dollar(grants):
    """Return the months of support a dollar of the group's grants has
    bought, to turn a proposal's amount into months.

    Parameters
    ----------
    grants : list of dict
        The grants.

    Returns
    -------
    float or None
        The months of support in the budgets divided by the amounts of
        the grants with both, or None when there are none.
    """
    total_months = total_amount = 0.0
    for grant in grants:
        months = sum(_budget_months(period) for period in grant.get("budget") or [])
        amount = grant.get("amount")
        if months > 0 and isinstance(amount, (int, float)) and amount > 0:
            total_months += months
            total_amount += amount
    return total_months / total_amount if total_amount else None


def expected_new_funding(proposals, success_rate, rate_of_months, months, flat_per_year=0.0):
    """Return the months of support new funding is expected to bring in
    each month.

    Parameters
    ----------
    proposals : list of dict
        The proposals. Those still waiting for a decision count, spread
        over their proposed dates, or over three years from the start
        of the plan when they have none.
    success_rate : float
        The chance a proposal is funded.
    rate_of_months : float or None
        The months of support a dollar buys.
    months : list of datetime.date
        The months of the plan.
    flat_per_year : float, optional
        The months of support a year expected from proposals not yet
        written, added to those from pending proposals.

    Returns
    -------
    dict
        The months expected, keyed by month.
    """
    expected = {month: (flat_per_year or 0.0) / 12 for month in months}
    if not rate_of_months:
        return expected
    for proposal in proposals:
        if proposal.get("status") not in PENDING_STATI or not isinstance(proposal.get("amount"), (int, float)):
            continue
        dates = get_dates(dict(proposal)) if has_dates(proposal) else {}
        begin_date = dates.get("begin_date") or months[0]
        end_date = dates.get("end_date") or begin_date + relativedelta(years=3, days=-1)
        if end_date < begin_date:
            continue
        spread = monthly_loading(begin_date, end_date)
        total = sum(spread.values())
        for month, share in spread.items():
            if month in expected:
                expected[month] += success_rate * proposal["amount"] * rate_of_months * share / total
    return expected


def evaluate_plans(supplies, pinned, open_needs, months, expected, hires):
    """Work out every hiring plan and suggest one.

    A plan is covered when, in every month, the months no grant can pay
    so far are no more than the new funding expected so far, since new
    money can be saved but not spent before it arrives.

    Parameters
    ----------
    supplies : list of dict
        The grants, as returned by grant_supplies.
    pinned : dict
        The months already needed on each grant.
    open_needs : dict
        The months already needed with no grant.
    months : list of datetime.date
        The months of the plan.
    expected : dict
        The months of support new funding is expected to bring, by
        month.
    hires : dict
        For "students" and "postdocs", the most to consider, the start
        date and the years each stays.

    Returns
    -------
    list of dict
        One entry per plan, with the numbers of students and postdocs,
        the simulation, the months lost, used in extensions and needing
        new funding, the most it falls short of expected new funding by
        and the first month it does, and whether it is covered. The
        suggested plan is first: the most hires that are covered, then
        the least use of extensions, then the least money lost.
    """
    plans = []
    for students, postdocs in product(range(hires["students"]["most"] + 1), range(hires["postdocs"]["most"] + 1)):
        needs = dict(open_needs)
        for kind, count in (("students", students), ("postdocs", postdocs)):
            for month, months_needed in hire_needs(count, hires[kind]["start"], hires[kind]["years"]).items():
                needs[month] = needs.get(month, 0.0) + months_needed
        result = simulate(supplies, pinned, needs, months)
        unpaid_so_far = expected_so_far = short_by = 0.0
        first_short = None
        for month in months:
            unpaid_so_far += result["unpaid"].get(month, 0.0)
            expected_so_far += expected.get(month, 0.0)
            if unpaid_so_far - expected_so_far > 1e-6:
                short_by = max(short_by, unpaid_so_far - expected_so_far)
                first_short = first_short or month
        plans.append(
            {
                "students": students,
                "postdocs": postdocs,
                "result": result,
                "lost": sum(result["lost"].values()),
                "extension": sum(result["extension"].values()),
                "unpaid": sum(result["unpaid"].values()),
                "short_by": short_by,
                "first_short": first_short,
                "covered": first_short is None,
            }
        )
    plans.sort(
        key=lambda plan: (
            not plan["covered"],
            -(plan["students"] + plan["postdocs"]) if plan["covered"] else plan["short_by"],
            round(plan["extension"], 2),
            round(plan["lost"], 2),
            -plan["students"],
        )
    )
    return plans
