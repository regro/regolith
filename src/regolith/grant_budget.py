"""Make, show and read back the yearly budget periods of a grant."""

import datetime as dt
import os
import shlex
import subprocess
import tempfile
from pathlib import Path

from dateutil.relativedelta import relativedelta
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

# The fields of a budget period, in the order they are shown for editing
PERIOD_FIELDS = ("begin_date", "end_date", "amount", "student_months", "postdoc_months", "ss_months")
DATE_FIELDS = ("begin_date", "end_date")
NUMBER_FIELDS = ("amount", "student_months", "postdoc_months", "ss_months")


def _as_date(value):
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value))


def yearly_periods(begin_date, end_date):
    """Return the begin and end dates of each grant year.

    Each year starts on the anniversary of the begin date, and the last
    one stops at the end date.

    Parameters
    ----------
    begin_date : datetime.date
        The first day of the grant.
    end_date : datetime.date
        The last day of the grant.

    Returns
    -------
    list of tuple of datetime.date
        The first and last day of each grant year, in order.
    """
    periods = []
    year = 0
    while begin_date + relativedelta(years=year) <= end_date:
        period_begin = begin_date + relativedelta(years=year)
        period_end = min(begin_date + relativedelta(years=year + 1) - dt.timedelta(days=1), end_date)
        periods.append((period_begin, period_end))
        year += 1
    return periods


def make_budget(begin_date, end_date, amount=None, annual_amounts=None):
    """Return one budget period for each year of a grant.

    Parameters
    ----------
    begin_date : datetime.date
        The first day of the grant.
    end_date : datetime.date
        The last day of the grant.
    amount : float, optional
        The total of the grant, shared between the years in proportion to
        their length when no annual amounts are given.
    annual_amounts : list of float, optional
        The amount for each year, one per grant year.

    Returns
    -------
    list of dict
        The budget periods, each with a begin_date, end_date and amount
        when one is known.

    Raises
    ------
    ValueError
        When the number of annual amounts is not the number of grant
        years.
    """
    periods = yearly_periods(begin_date, end_date)
    if annual_amounts is not None:
        if len(annual_amounts) != len(periods):
            raise ValueError(
                f"{len(annual_amounts)} annual amounts were given, but the grant runs from {begin_date} to "
                f"{end_date}, which is {len(periods)} budget years. Please give one amount for each year."
            )
        amounts = [float(value) for value in annual_amounts]
    elif amount is not None:
        total_days = (end_date - begin_date).days + 1
        amounts = [round(amount * ((end - begin).days + 1) / total_days) for begin, end in periods]
        # Put any rounding left over in the last year, so the years add up to the amount
        amounts[-1] += amount - sum(amounts)
        amounts = [float(value) for value in amounts]
    else:
        amounts = [None] * len(periods)
    budget = []
    for (begin, end), period_amount in zip(periods, amounts):
        period = {"begin_date": begin, "end_date": end}
        if period_amount is not None:
            period["amount"] = period_amount
        budget.append(period)
    return budget


def budget_to_text(grant_id, budget, grant_dates=None, grant_amount=None):
    """Return a budget as YAML to edit, with a header saying how.

    Parameters
    ----------
    grant_id : str
        The id of the grant the budget belongs to.
    budget : list of dict
        The budget periods.
    grant_dates : tuple of datetime.date, optional
        The begin and end dates of the grant, shown for reference.
    grant_amount : float, optional
        The amount of the grant, shown for reference.

    Returns
    -------
    str
        The text to edit.
    """
    lines = [f"# Budget for {grant_id}: one entry per budget period, usually one per grant year."]
    if grant_dates and all(grant_dates):
        lines.append(f"# The grant runs from {grant_dates[0]} to {grant_dates[1]}.")
    if isinstance(grant_amount, (int, float)):
        lines.append(f"# The grant amount is {grant_amount:,.2f}; the periods should add up to it.")
    lines += [
        "# Each period has a begin_date and end_date (YYYY-MM-DD) and an amount. It may also have",
        "# student_months, postdoc_months and ss_months (summer months).",
        "# Save and close the editor to store the budget. To leave it unchanged, close without saving.",
        "",
    ]
    for period in budget:
        fields = [field for field in PERIOD_FIELDS if period.get(field) is not None]
        fields += sorted(key for key in period if key not in PERIOD_FIELDS)
        for position, field in enumerate(fields):
            value = period[field]
            if isinstance(value, dt.date):
                value = value.isoformat()
            lines.append(f"{'- ' if position == 0 else '  '}{field}: {value}")
    if not budget:
        lines.append("[]")
    return "\n".join(lines) + "\n"


def budget_from_text(text):
    """Return the budget periods in YAML text, and the problems with
    them.

    Parameters
    ----------
    text : str
        The YAML, as written by budget_to_text and then edited.

    Returns
    -------
    budget : list of dict
        The budget periods, with dates as datetime.date and numbers as
        float.  Empty when the text cannot be read.
    problems : list of str
        Every problem found, in words for someone who does not program.
        Empty when the budget is good.
    """
    # Every value is read as text and converted here, so that one bad date does not stop the rest
    # being checked
    try:
        loaded = YAML(typ="base").load(text)
    except YAMLError as error:
        return [], [f"The budget could not be read as YAML: {error}"]
    if loaded is None or loaded == "[]":
        loaded = []
    if not isinstance(loaded, list) or not all(isinstance(period, dict) for period in loaded):
        return [], ["The budget must be a list of periods, each starting with '- begin_date:'."]
    budget = []
    problems = []
    for number, period in enumerate(loaded, start=1):
        period = {key: value for key, value in period.items() if value not in (None, "")}
        for field in DATE_FIELDS:
            if period.get(field) is None:
                problems.append(f"Period {number} has no {field}.")
                continue
            try:
                period[field] = _as_date(period[field])
            except ValueError:
                problems.append(
                    f"Period {number} has the {field} {period[field]}, which is not a YYYY-MM-DD date."
                )
        for field in NUMBER_FIELDS:
            if period.get(field) is None:
                continue
            try:
                period[field] = float(period[field])
            except (TypeError, ValueError):
                problems.append(f"Period {number} has the {field} {period[field]}, which is not a number.")
        unknown = sorted(key for key in period if key not in PERIOD_FIELDS)
        if unknown:
            problems.append(
                f"Period {number} has {', '.join(unknown)}, which a budget period cannot hold. "
                f"The fields allowed are {', '.join(PERIOD_FIELDS)}."
            )
        budget.append(period)
    dated = [
        (number, period)
        for number, period in enumerate(budget, start=1)
        if all(isinstance(period.get(field), dt.date) for field in DATE_FIELDS)
    ]
    for number, period in dated:
        if period["begin_date"] > period["end_date"]:
            problems.append(
                f"Period {number} begins on {period['begin_date']}, after it ends on {period['end_date']}."
            )
    for (number, period), (next_number, next_period) in zip(dated, dated[1:]):
        if next_period["begin_date"] <= period["end_date"]:
            problems.append(
                f"Period {next_number} begins on {next_period['begin_date']}, before period {number} ends on "
                f"{period['end_date']}. The periods must be in order and must not overlap."
            )
    return budget, problems


def budget_notes(budget, grant_dates=None, grant_amount=None):
    """Return the ways a good budget differs from its grant.

    These do not stop a budget being stored, since a grant may be
    rebudgeted, but they are worth a look.

    Parameters
    ----------
    budget : list of dict
        The budget periods, with dates as datetime.date.
    grant_dates : tuple of datetime.date, optional
        The begin and end dates of the grant.
    grant_amount : float, optional
        The amount of the grant.

    Returns
    -------
    list of str
        The differences found.
    """
    notes = []
    amounts = [period.get("amount") for period in budget]
    if isinstance(grant_amount, (int, float)) and budget and None not in amounts:
        total = sum(amounts)
        if abs(total - grant_amount) > 0.005:
            notes.append(f"The periods add up to {total:,.2f}, but the grant amount is {grant_amount:,.2f}.")
    if grant_dates and all(grant_dates) and budget:
        if budget[0]["begin_date"] != grant_dates[0]:
            notes.append(
                f"The first period begins on {budget[0]['begin_date']}, not on the grant's {grant_dates[0]}."
            )
        if budget[-1]["end_date"] != grant_dates[1]:
            notes.append(f"The last period ends on {budget[-1]['end_date']}, not on the grant's {grant_dates[1]}.")
    return notes


def editor_command():
    """Return the command for the user's text editor.

    It is taken from VISUAL or EDITOR in the environment, falling back
    to notepad on Windows and nano elsewhere.

    Returns
    -------
    list of str
        The editor command, ready to have a file name added.
    """
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if not editor:
        editor = "notepad" if os.name == "nt" else "nano"
    return shlex.split(editor)


def edit_text(text):
    """Open text in the user's editor and return it as saved.

    Parameters
    ----------
    text : str
        The text to start the editor with.

    Returns
    -------
    str
        The text as it was when the editor closed.

    Raises
    ------
    RuntimeError
        When the editor cannot be started.
    """
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "budget.yml"
        path.write_text(text, encoding="utf-8")
        command = editor_command()
        try:
            subprocess.run(command + [str(path)], check=True)
        except (OSError, subprocess.CalledProcessError) as error:
            raise RuntimeError(
                f"The editor {' '.join(command)} could not be started ({error}). Please set the EDITOR "
                "environment variable to your editor, for example EDITOR=nano, or give the budget in a file "
                "with --budget-file."
            )
        return path.read_text(encoding="utf-8")
