"""Plan, show, read back and check the appointments of group members.

Appointments live on each person, in ``appointments``, a dict keyed by
appointment id.  Each appointment has begin and end dates, a type, a
loading and a status, and is paid either by a ``grant`` (its id or
alias) or by ``outside_funding``, such as a fellowship or a teaching
assistantship.
"""

import datetime as dt

from dateutil.relativedelta import relativedelta
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from regolith.dates import get_dates, has_dates
from regolith.schemas import alloweds
from regolith.tools import fuzzy_retrieval, grant_burn

# The employment positions an appointment pays for, with the appointment type for the academic year and
# for the summer
FUNDED_POSITIONS = {
    "graduate research assistant": ("gra", "ss"),
    "post-doctoral scholar": ("pd", "pd"),
}
# Appointment quarters as (first month, last month, id prefix). The summer runs July to September
QUARTERS = ((10, 12, "f"), (1, 3, "w"), (4, 6, "s"), (7, 9, "ss"))
SUMMER_PREFIX = "ss"
# The placeholder grant for an appointment not yet funded. makeappointments counts it to show how much
# new funding is needed and by when
FUTURE_GRANT = "future_grant"
# Grants that once stood for outside funding. Appointments on them are read as outside funding
LEGACY_OUTSIDE_GRANTS = (
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
)
# The days a grant may be overspent by before it counts as run out, as in makeappointments
OVERSPEND_ALLOWANCE_DAYS = 5
BURN_KEYS = {"gra": "student_days", "pd": "postdoc_days", "ss": "ss_days"}
APPOINTMENT_FIELDS = (
    "_id",
    "begin_date",
    "end_date",
    "type",
    "loading",
    "grant",
    "outside_funding",
    "status",
    "notes",
)


def _as_date(value):
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value))


def _dates(thing):
    dates = get_dates(dict(thing)) if has_dates(thing) else {}
    return dates.get("begin_date"), dates.get("end_date")


def _days(begin_date, end_date):
    return [begin_date + dt.timedelta(days=offset) for offset in range((end_date - begin_date).days + 1)]


def _ranges(days):
    """Return runs of consecutive days as (first, last) pairs."""
    runs = []
    for day in sorted(days):
        if runs and day == runs[-1][1] + dt.timedelta(days=1):
            runs[-1][1] = day
        else:
            runs.append([day, day])
    return [tuple(run) for run in runs]


def is_outside(appointment):
    """Return True when an appointment is paid by outside funding.

    Parameters
    ----------
    appointment : dict
        The appointment.

    Returns
    -------
    bool
        The answer to whether it has outside_funding, or is on a grant
        that once stood for outside funding.
    """
    return bool(appointment.get("outside_funding")) or appointment.get("grant") in LEGACY_OUTSIDE_GRANTS


def quarter_periods(begin_date, end_date):
    """Return the appointment quarters between two dates.

    Parameters
    ----------
    begin_date : datetime.date
        The first day to cover.
    end_date : datetime.date
        The last day to cover.

    Returns
    -------
    list of tuple
        The first day, last day and id of each quarter, cut to the dates
        given. The id is the quarter's prefix and the year it begins in,
        such as f26 or ss27.
    """
    periods = []
    month_start = dt.date(begin_date.year, begin_date.month, 1)
    while month_start <= end_date:
        for first_month, last_month, prefix in QUARTERS:
            if first_month <= month_start.month <= last_month:
                quarter_begin = dt.date(month_start.year, first_month, 1)
                quarter_end = dt.date(month_start.year, last_month, 1) + relativedelta(months=1, days=-1)
                periods.append(
                    (max(quarter_begin, begin_date), min(quarter_end, end_date), f"{prefix}{quarter_begin:%y}")
                )
                month_start = quarter_end + dt.timedelta(days=1)
                break
    return periods


def funded_employment(person, group_id):
    """Return the funded positions a person holds in the group.

    Parameters
    ----------
    person : dict
        The person.
    group_id : str
        The id of the group, as used in the group field of employment.

    Returns
    -------
    list of dict
        Each funded position, with its position, begin_date and end_date,
        where end_date is None when none is recorded.
    """
    positions = []
    for employment in person.get("employment", []):
        position = str(employment.get("position", "")).casefold()
        if employment.get("group") != group_id or position not in FUNDED_POSITIONS:
            continue
        begin_date, end_date = _dates(employment)
        positions.append({"position": position, "begin_date": begin_date, "end_date": end_date})
    return positions


def daily_loading(appointments, begin_date, end_date):
    """Return the total loading of the appointments on each day.

    Parameters
    ----------
    appointments : iterable of dict
        The appointments.
    begin_date : datetime.date
        The first day to count.
    end_date : datetime.date
        The last day to count.

    Returns
    -------
    dict
        The total loading on each day, keyed by date.
    """
    loading = {day: 0.0 for day in _days(begin_date, end_date)}
    for appointment in appointments:
        appointment_begin, appointment_end = _dates(appointment)
        if not appointment_begin or not appointment_end:
            continue
        for day in _days(max(appointment_begin, begin_date), min(appointment_end, end_date)):
            loading[day] += float(appointment.get("loading", 0))
    return loading


def gap_appointments(person, appointments, group_id, today):
    """Return proposed appointments on the future grant that fill the
    gaps in a person's funding from today until their position ends.

    A gap is filled in each quarter, with the loading the person still
    needs, so the plan shows what is not yet funded.

    Parameters
    ----------
    person : dict
        The person.
    appointments : list of dict
        Their appointments.
    group_id : str
        The id of the group.
    today : datetime.date
        The first day to plan from.

    Returns
    -------
    list of dict
        The appointments that fill the gaps, without ids.
    """
    gaps = []
    for position in funded_employment(person, group_id):
        if not position["end_date"] or position["end_date"] < today:
            continue
        academic_type, summer_type = FUNDED_POSITIONS[position["position"]]
        begin_date = max(today, position["begin_date"] or today)
        loading = daily_loading(appointments, begin_date, position["end_date"])
        for quarter_begin, quarter_end, quarter_id in quarter_periods(begin_date, position["end_date"]):
            days = _days(quarter_begin, quarter_end)
            short = {day: round(1 - loading[day], 4) for day in days}
            appointment_type = summer_type if quarter_id.startswith(SUMMER_PREFIX) else academic_type
            run_begin = days[0]
            # A run is a stretch of days short by the same loading
            for day in days[1:] + [None]:
                if day is not None and short[day] == short[run_begin]:
                    continue
                if short[run_begin] > 0:
                    gaps.append(
                        {
                            "begin_date": run_begin,
                            "end_date": day - dt.timedelta(days=1) if day else quarter_end,
                            "type": appointment_type,
                            "loading": short[run_begin],
                            "grant": FUTURE_GRANT,
                            "status": "proposed",
                        }
                    )
                run_begin = day
    return gaps


def new_appointment_id(appointment, taken_ids):
    """Return an id for a new appointment from the quarter it begins in.

    Parameters
    ----------
    appointment : dict
        The appointment, with a begin_date.
    taken_ids : collection of str
        The ids already in use.

    Returns
    -------
    str
        An id such as f26, or f26-2 when f26 is taken.
    """
    begin_date = _as_date(appointment["begin_date"])
    quarter_id = quarter_periods(begin_date, begin_date)[0][2]
    candidate, number = quarter_id, 1
    while candidate in taken_ids:
        number += 1
        candidate = f"{quarter_id}-{number}"
    return candidate


def _shown(value):
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return "[" + ", ".join(str(_shown(item)) for item in value) + "]"
    if isinstance(value, str) and (not value or value != value.strip() or any(c in value for c in ":#[]{},'\"")):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def appointments_to_text(person, appointments, end_date=None, alerts=None):
    """Return appointments as YAML to edit, with a header saying how.

    Parameters
    ----------
    person : dict
        The person the appointments belong to.
    appointments : list of dict
        The appointments, each with its _id if it has one.
    end_date : datetime.date, optional
        The day the person's funded position ends, shown for reference.
    alerts : list of str, optional
        The alerts about the appointments, shown at the top.

    Returns
    -------
    str
        The text to edit.
    """
    lines = [f"# Appointments for {person.get('name', person['_id'])} from today"]
    if end_date:
        lines[0] += f" until their position ends on {end_date}"
    lines += [
        "# One entry per appointment. Each has begin_date and end_date (YYYY-MM-DD), a type (gra, ss, pd or",
        "# ug), a loading (1 for full time, 0.5 for half), and either a grant (its id or alias) or",
        "# outside_funding saying what pays, such as NSF GRFP or TA. Split a quarter that is half on outside",
        f"# funding into two entries of loading 0.5. Entries on {FUTURE_GRANT} are not yet funded.",
        "# status is proposed for a plan, appointed once requested, and finalized once confirmed.",
        "# Delete an entry to remove it. New entries need no _id. Earlier appointments are kept as they are.",
        "# Save and close the editor to store them. To leave them unchanged, close without saving.",
    ]
    for alert in alerts or []:
        lines.append(f"# ALERT: {alert}")
    lines.append("")
    for appointment in appointments:
        fields = [field for field in APPOINTMENT_FIELDS if appointment.get(field) not in (None, "", [])]
        fields += sorted(key for key in appointment if key not in APPOINTMENT_FIELDS)
        for position, field in enumerate(fields):
            lines.append(f"{'- ' if position == 0 else '  '}{field}: {_shown(appointment[field])}")
    if not appointments:
        lines.append("[]")
    return "\n".join(lines) + "\n"


def appointments_from_text(text):
    """Return the appointments in YAML text, and the problems with them.

    Parameters
    ----------
    text : str
        The YAML, as written by appointments_to_text and then edited.

    Returns
    -------
    appointments : list of dict
        The appointments, with dates as datetime.date, loading as float,
        status defaulting to proposed and notes as a list.  Empty when
        the text cannot be read.
    problems : list of str
        Every problem found, in words for someone who does not program.
        Empty when the appointments are good.
    """
    # Every value is read as text and converted here, so that one bad value does not stop the rest being
    # checked
    try:
        loaded = YAML(typ="base").load(text)
    except YAMLError as error:
        return [], [f"The appointments could not be read as YAML: {error}"]
    if loaded is None or loaded == "[]":
        loaded = []
    if not isinstance(loaded, list) or not all(isinstance(entry, dict) for entry in loaded):
        return [], ["The appointments must be a list, each entry starting with '- begin_date:' or '- _id:'."]
    types, stati = alloweds["APPOINTMENTS_TYPES"], alloweds["APPOINTMENTS_STATI"]
    appointments, problems, seen_ids = [], [], set()
    for number, entry in enumerate(loaded, start=1):
        appointment = {key: value for key, value in entry.items() if value not in (None, "")}
        name = f"Entry {number}" + (f" ({appointment['_id']})" if appointment.get("_id") else "")
        if appointment.get("_id"):
            if appointment["_id"] in seen_ids:
                problems.append(f"{name} has the same _id as an earlier entry. Each _id must be different.")
            seen_ids.add(appointment["_id"])
        for field in ("begin_date", "end_date"):
            if appointment.get(field) is None:
                problems.append(f"{name} has no {field}.")
                continue
            try:
                appointment[field] = _as_date(appointment[field])
            except ValueError:
                problems.append(f"{name} has the {field} {appointment[field]}, which is not a YYYY-MM-DD date.")
        if appointment.get("type") not in types:
            problems.append(
                f"{name} has the type {appointment.get('type')}. It must be one of {', '.join(types)}."
            )
        try:
            appointment["loading"] = float(appointment.get("loading"))
            if not 0 < appointment["loading"] <= 1:
                problems.append(
                    f"{name} has the loading {appointment['loading']:g}. It must be above 0 and at most 1."
                )
        except (TypeError, ValueError):
            problems.append(f"{name} has the loading {appointment.get('loading')}, which is not a number.")
        if appointment.get("grant") and appointment.get("outside_funding"):
            problems.append(
                f"{name} has both a grant and outside_funding. Give one, or split it into two entries."
            )
        elif not appointment.get("grant") and not appointment.get("outside_funding"):
            problems.append(
                f"{name} says nothing about what pays for it. Give a grant, outside_funding, or {FUTURE_GRANT}."
            )
        appointment.setdefault("status", "proposed")
        if appointment["status"] not in stati:
            problems.append(
                f"{name} has the status {appointment['status']}. It must be one of {', '.join(stati)}."
            )
        notes = appointment.get("notes")
        if notes is not None and not isinstance(notes, list):
            appointment["notes"] = [notes]
        unknown = sorted(key for key in appointment if key not in APPOINTMENT_FIELDS)
        if unknown:
            problems.append(
                f"{name} has {', '.join(unknown)}, which an appointment cannot hold. "
                f"The fields allowed are {', '.join(APPOINTMENT_FIELDS)}."
            )
        begin_date, end_date = appointment.get("begin_date"), appointment.get("end_date")
        if isinstance(begin_date, dt.date) and isinstance(end_date, dt.date) and begin_date > end_date:
            problems.append(f"{name} begins on {begin_date}, after it ends on {end_date}.")
        appointments.append(appointment)
    return appointments, problems


def appointment_alerts(person, appointments, grants, all_appointments, group_id, today):
    """Return the alerts about a person's appointments from today on.

    These do not stop the appointments being stored, since a plan may
    run ahead of the funding, but they need attention.

    Parameters
    ----------
    person : dict
        The person.
    appointments : list of dict
        Their appointments.
    grants : list of dict
        The grants, merged with their proposals.
    all_appointments : list of dict
        Every appointment of every person, used to work out how much
        money each grant has left.
    group_id : str
        The id of the group.
    today : datetime.date
        The first day to check.

    Returns
    -------
    list of str
        The alerts, in words for someone who does not program.
    """
    alerts = []
    burns = {}
    # Name each grant by its id, so the money spent is counted whichever way an appointment names it
    grant_ids = {}
    for grant in grants:
        for name in (grant.get("_id"), grant.get("alias")):
            if name:
                grant_ids.setdefault(str(name).casefold(), grant["_id"])
    all_appointments = [
        {
            **appointment,
            "grant": grant_ids.get(str(appointment.get("grant", "")).casefold(), appointment.get("grant")),
        }
        for appointment in all_appointments
    ]
    for appointment in sorted(appointments, key=lambda a: str(a.get("begin_date"))):
        begin_date, end_date = _dates(appointment)
        if not begin_date or not end_date or end_date < today:
            continue
        name = f"{appointment.get('_id') or 'The new appointment'} ({begin_date} to {end_date})"
        if is_outside(appointment):
            continue
        grant_name = appointment.get("grant")
        if grant_name == FUTURE_GRANT:
            alerts.append(f"{name} is not yet funded.")
            continue
        grant = fuzzy_retrieval(grants, ["_id", "alias"], grant_name, case_sensitive=False)
        if not grant:
            alerts.append(f"{name} is on the grant {grant_name}, which is not in the grants collection.")
            continue
        grant_begin, grant_end = _dates(grant)
        if grant_end and end_date > grant_end:
            alerts.append(f"{name} runs past the end of the grant {grant_name} on {grant_end}.")
        if grant_begin and begin_date < grant_begin:
            alerts.append(f"{name} begins before the grant {grant_name} begins on {grant_begin}.")
        burn_key = BURN_KEYS.get(appointment.get("type"))
        if not burn_key:
            continue
        if not grant.get("budget"):
            alerts.append(f"The grant {grant_name} has no budget, so whether it can pay for {name} is not known.")
            continue
        if grant["_id"] not in burns:
            burns[grant["_id"]] = grant_burn(grant, all_appointments)
        overspent = [
            day
            for day in _days(max(begin_date, today), end_date)
            if day in burns[grant["_id"]] and burns[grant["_id"]][day][burn_key] < -OVERSPEND_ALLOWANCE_DAYS
        ]
        if overspent:
            alerts.append(
                f"The grant {grant_name} runs out of {burn_key.replace('_days', '')} months on {overspent[0]}, "
                f"during {name}."
            )
    positions = funded_employment(person, group_id)
    for position in positions:
        if not position["end_date"]:
            alerts.append(
                f"The {position['position']} position has no end date in employment, so gaps cannot be found. "
                "Please add the date they are expected to graduate or leave."
            )
            continue
        if position["end_date"] < today:
            continue
        begin_date = max(today, position["begin_date"] or today)
        loading = daily_loading(appointments, begin_date, position["end_date"])
        for first, last in _ranges(day for day, value in loading.items() if value < 0.9999):
            alerts.append(f"There is a gap in the appointments from {first} to {last}.")
        for first, last in _ranges(day for day, value in loading.items() if value > 1.0001):
            alerts.append(f"The appointments add up to more than full time from {first} to {last}.")
    position_ends = [position["end_date"] for position in positions if position["end_date"]]
    if position_ends:
        last_end = max(position_ends)
        late = [
            appointment.get("_id") or str(_dates(appointment)[0])
            for appointment in appointments
            if _dates(appointment)[1] and _dates(appointment)[1] > last_end
        ]
        if late:
            alerts.append(f"{', '.join(late)} run past {last_end}, when their position ends.")
    return alerts
