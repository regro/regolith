"""Date based tools."""

import calendar
import datetime

from dateutil import parser as date_parser

MONTHS = {
    "jan": 1,
    "jan.": 1,
    "january": 1,
    "feb": 2,
    "feb.": 2,
    "february": 2,
    "mar": 3,
    "mar.": 3,
    "march": 3,
    "apr": 4,
    "apr.": 4,
    "april": 4,
    "may": 5,
    "may.": 5,
    "jun": 6,
    "jun.": 6,
    "june": 6,
    "jul": 7,
    "jul.": 7,
    "july": 7,
    "aug": 8,
    "aug.": 8,
    "august": 8,
    "sep": 9,
    "sep.": 9,
    "sept": 9,
    "sept.": 9,
    "september": 9,
    "oct": 10,
    "oct.": 10,
    "october": 10,
    "nov": 11,
    "nov.": 11,
    "november": 11,
    "dec": 12,
    "dec.": 12,
    "december": 12,
    "": 1,
    "tbd": 12,
}


def month_to_int(m):
    """Converts a month to an integer."""
    try:
        m = int(m)
    except ValueError:
        m = MONTHS[m.lower()]
    return m


def month_to_str_int(m):
    """Converts a month to an int form, str type, with a leading
    zero."""
    mi = month_to_int(m)
    if mi < 10:
        ms = "0{}".format(mi)
    else:
        ms = str(mi)
    return ms


def day_to_str_int(d):
    """Converts a day to an int form, str type, with a leading zero."""
    if d < 10:
        ds = "0{}".format(d)
    else:
        ds = str(d)
    return ds


def date_to_float(y, m, d=0):
    """Converts years / months / days to a float, eg 2015.0818 is August
    18th 2015."""
    y = int(y)
    m = month_to_int(m)
    d = int(d)
    return y + (m / 100.0) + (d / 10000.0)


def find_gaps_overlaps(dateslist, overlaps_ok=False):
    """Find whether there is a gap or an overlap in a list of date-
    ranges.

    Parameters
    ----------
    dateslist: list of tuples of datetime.date objects
      The list of date-ranges.
    overlaps_ok: bool
      Returns false if there are gaps but true if there are overlaps but no gaps

    Returns
    -------
      True if there are no gaps or overlaps else False
    """

    status = True
    dateslist.sort(key=lambda x: x[0])
    for i in range(len(dateslist) - 1):
        if dateslist[i + 1][0] <= dateslist[i][1] and not overlaps_ok:
            status = False
        elif (dateslist[i + 1][0] - dateslist[i][1]).days > 1:
            status = False
    return status


def last_day(year, month):
    """Returns the last day of the month for the month given.

    Parameters
    ----------
    year: integer
      the year that the month is in
    month: integer or string
      the month.  if a string should be resolvable using regolith month_to_int

    Returns
    -------
    The last day of that month
    """
    return calendar.monthrange(year, month_to_int(month))[1]


def convert_doc_iso_to_date(doc):
    def convert_date(obj):
        """Recursively goes through the dictionary obj and converts date
        from iso to datetime.date."""
        if isinstance(obj, str):
            try:
                date = datetime.datetime.strptime(obj, "%Y-%m-%d").date()
            except ValueError:
                return obj
            else:
                return date
        if isinstance(obj, (int, float)):
            return obj
        if isinstance(obj, dict):
            new = obj.__class__()
            for k, v in obj.items():
                new[k] = convert_date(v)
        elif isinstance(obj, (list, set, tuple)):
            new = obj.__class__(convert_date(v) for v in obj)
        else:
            return obj
        return new

    return convert_date(doc)


def get_dates(thing, date_field_prefix=None):
    """Given a dict like thing, return the date items.

    Parameters
    ----------
    thing: dict
      the dict that contains the dates
    date_field_prefix: string (optional)
      the prefix to look for before the date parameter. For example given "submission"
      the function will search for submission_day, submission_year, etc.

    Returns
    -------
       dict containing datetime.date objects for valid begin_date end_date and date, and
       prefix_date if a prefix string was passed.  Missing and empty dates and
       date items that contain the string 'tbd' are not returned.  If no valid
       date items are found, an empty dict is returned

    Description
    -----------
    If "begin_date", "end_date" or "date" values are found, if these are are in
    an ISO format string they will be converted to datetime.date objects and
    returned in the dictionary under keys of the same name.  A specified date
    will override any date built from year/month/day data.

    If they are not found the function will look for begin_year, end_year and
    year.

    If "year", "month" and "day" are found the function will return these in the
    "date" field and begin_date and end_date will match the "date" field. If only
    a "year" is found, then the date attribute will be none but the begin and end
    dates will be the first and last day of that respective year.

    If year is found but no month or day are found the function will return
    begin_date and end_date with the beginning and the end of the given year/month.
    The returned date will be None.

    If end_year is found, the end month and end day are missing they are set to
    12 and 31, respectively

    If begin_year is found, the begin month and begin day are missing they are set to
    1 and 1, respectively

    If a date field prefix is passed in this function will search for prefix_year as
    well as prefix_month, prefix_day, and prefix_date. For example, if the prefix string
    passed in is "submitted" then this function will look for submitted_date instead of
    just date.

    Examples
    --------
    >>> get_dates({'submission_day': 10, 'submission_year': 2020, 'submission_month': 'Feb'}, "submission")

    This would return a dictionary consisting of the begin date, end, date, and date for the given input.
    Instead of searching for "day" in the thing, it would search for "submission_day" since a prefix was
    given. The following dictionary is returned (note that a submission_date and a date key are in the
    dictionary):
    {'begin_date': datetime.date(2020, 2, 10),
     'end_date': datetime.date(2020, 2, 10),
     'submission_date': datetime.date(2020, 2, 10),
     'date': datetime.date(2020, 2, 10)
    }

    >>> get_dates({'begin_year': 2019, 'end_year': 2020, 'end_month': 'Feb'})

    This will return a dictionary consisting of the begin date, end date, and date for the given input.
    Because no prefix string was passed in, the function will search for "date" in the input instead of
    prefix_input. The following dictionary is returned:
    {'begin_date': datetime.date(2019, 1, 1),
     'end_date': datetime.date(2020, 2, 29),
    }
    """

    datenames = ["day", "month", "year", "date"]
    if date_field_prefix:
        datenames = [f"{date_field_prefix}_{datename}" for datename in datenames]

    minimal_set = ["end_year", "begin_year", "year", "begin_date", "end_date", "date"]
    minimal_things = (
        list(set([thing.get(i) for i in datenames]))
        if date_field_prefix
        else list(set([thing.get(i) for i in minimal_set]))
    )
    if len(minimal_things) == 1 and not minimal_things[0]:
        print(f"WARNING: cannot find any dates in {thing.get('_id', '(no id)')}")
        dates = {}
        return dates
    for key, value in thing.items():
        if key in minimal_set or key in ["month", "day", "begin_day", "begin_month"]:
            if isinstance(value, str):
                if value.strip().lower() == "tbd":
                    thing[key] = None
                else:
                    try:
                        thing[key] = int(value)
                    except ValueError:
                        pass
    if thing.get("end_year") and not thing.get("begin_year"):
        print(f"WARNING: end_year specified without begin_year {thing.get('_id', '(no id)')}")
    begin_date, end_date, date = None, None, None
    if thing.get("begin_year"):
        if not thing.get("begin_month"):
            thing["begin_month"] = 1
        if not thing.get("begin_day"):
            thing["begin_day"] = 1
        begin_date = datetime.date(thing["begin_year"], month_to_int(thing["begin_month"]), thing["begin_day"])
    if thing.get("end_year"):
        if not thing.get("end_month"):
            thing["end_month"] = 12
        if not thing.get("end_day"):
            thing["end_day"] = last_day(thing["end_year"], thing["end_month"])
        end_date = datetime.date(thing["end_year"], month_to_int(thing["end_month"]), thing["end_day"])
    if thing.get(datenames[2]):  # prefix_year
        if not thing.get(datenames[1]):  # prefix_month
            if thing.get("begin_year"):
                print(
                    f"WARNING: both year and begin_year specified in {thing.get('_id', '(no id)')}. "
                    "Year info will be used"
                )
            begin_date = datetime.date(thing[datenames[2]], 1, 1)
            end_date = datetime.date(thing[datenames[2]], 12, 31)
        elif not thing.get(datenames[0]):  # prfix_day
            if thing.get("begin_year"):
                print(
                    f"WARNING: both year and begin_year specified in {thing.get('_id', '(no id)')}. "
                    "Year info will be used"
                )
            begin_date = datetime.date(thing[datenames[2]], month_to_int(thing[datenames[1]]), 1)
            end_date = datetime.date(
                thing[datenames[2]],
                month_to_int(thing[datenames[1]]),
                last_day(thing[datenames[2]], thing[datenames[1]]),
            )
        else:
            date = datetime.date(thing[datenames[2]], month_to_int(thing[datenames[1]]), int(thing[datenames[0]]))
            begin_date = datetime.date(
                int(thing[datenames[2]]), month_to_int(thing[datenames[1]]), int(thing[datenames[0]])
            )
            end_date = datetime.date(
                int(thing[datenames[2]]), month_to_int(thing[datenames[1]]), int(thing[datenames[0]])
            )
    if thing.get("begin_date"):
        if isinstance(thing.get("begin_date"), str):
            begin_date = date_parser.parse(thing.get("begin_date")).date()
        else:
            begin_date = thing.get("begin_date")
    if thing.get("end_date"):
        if isinstance(thing.get("end_date"), str):
            end_date = date_parser.parse(thing.get("end_date")).date()
        else:
            end_date = thing.get("end_date")
    if thing.get(datenames[3]):
        if isinstance(thing.get(datenames[3]), str):
            date = date_parser.parse(thing.get(datenames[3])).date()
        else:
            date = thing.get(datenames[3])

    if date_field_prefix:
        dates = {"begin_date": begin_date, "end_date": end_date, datenames[3]: date, "date": date}
    else:
        dates = {"begin_date": begin_date, "end_date": end_date, "date": date}
    dates_no_nones = {k: v for k, v in dates.items() if v is not None}
    return dates_no_nones


def get_due_date(thing):
    """

    Parameters
    ----------
    thing: dict
      gets the field named 'due_date' from doc and ensurese it is a
      datetime.date object

    Returns
    -------
    The due date as a datetime.date object

    """
    due_date = thing.get("due_date")
    if isinstance(due_date, str):
        due_date = date_parser.parse(due_date).date()
    elif isinstance(due_date, datetime.date):
        pass
    else:
        raise RuntimeError("due date not a known type")
    return due_date


def is_current(thing, now=None):
    """Given a thing with dates, returns true if the thing is current
    looks for begin_ and end_ date things (date, year, month, day), or
    just the date things themselves. e.g., begin_date, end_month, month,
    and so on.

    Parameters
    ----------
    thing: dict
      the thing that we want to know whether or not it is current
    now: datetime.date object
      a date for now.  If it is None it uses the current date.  Default is None

    Returns
    -------
    True if the thing is current and false otherwise
    """
    if now is None:
        now = datetime.date.today()
    dates = get_dates(thing)
    current = False
    if not dates.get("end_date"):
        dates["end_date"] = datetime.date(5000, 12, 31)
    try:
        if dates.get("begin_date") <= now <= dates.get("end_date"):
            current = True
    except RuntimeError:
        raise RuntimeError(f"Cannot find begin_date in document:\n {thing['_id']}")
    return current


def has_started(thing, now=None):
    """Given a thing with dates, returns true if the thing has started.

    Parameters
    ----------
    thing: dict
      the thing that we want to know whether or not it is has started
    now: datetime.date object
      a date for now.  If it is None it uses the current date.  Default is None

    Returns
    -------
    True if the thing has started and false otherwise
    """
    if not now:
        now = datetime.date.today()
    dates = get_dates(thing)
    started = False
    try:
        if dates.get("begin_date") <= now:
            started = True
    except RuntimeError:
        raise RuntimeError(f"Cannot find begin_date in document:\n {thing}")
    return started


def has_finished(thing, now=None):
    """Given a thing with dates, returns true if the thing has finished.

    Parameters
    ----------
    thing: dict
      the thing that we want to know whether or not it has finished
    now: datetime.date object
      a date for now.  If it is None it uses the current date.  Default is None

    Returns
    -------
    True if the thing has finished and false otherwise
    """
    if not now:
        now = datetime.date.today()
    dates = get_dates(thing)
    finished = False
    if not dates.get("end_date"):
        dates["end_date"] = datetime.date(5000, 12, 31)
    if dates.get("end_date") < now:
        finished = True
    return finished


def is_before(thing, now=None):
    """Given a thing with a date, returns true if the thing is before
    the input date.

    Parameters
    ----------
    thing: dict
      the thing that we want to know whether or not is before a date
    now: datetime.date object
      a date for now.  If it is None it uses the current date.  Default is None

    Returns
    -------
    True if the thing is before the date
    """
    if not now:
        now = datetime.date.today()
    dates = get_dates(thing)
    before = False
    try:
        if dates.get("date") < now:
            before = True
    except RuntimeError:
        raise RuntimeError(f"Cannot find date in document:\n {thing}")
    return before


def is_after(thing, now=None):
    """Given a thing with a date, returns true if the thing is after the
    input date.

    Parameters
    ----------
    thing: dict
      the thing that we want to know whether or not is after a date
    now: datetime.date object
      a date for now.  If it is None it uses the current date.  Default is None

    Returns
    -------
    True if the thing is after the date
    """
    if not now:
        now = datetime.date.today()
    dates = get_dates(thing)
    after = False
    try:
        if now < dates.get("date"):
            after = True
    except RuntimeError:
        raise RuntimeError(f"Cannot find date in document:\n {thing}")
    return after


def is_between(thing, start=None, end=None):
    """Given a thing with a date, returns true if the thing is between
    the start and end date.

    Parameters
    ----------
    thing: dict
      the thing that we want to know whether or not is after a date
    start: datetime.date object
      a date for the start.  If it is None it uses the current date.  Default is None
    end: datetime.date object
      a date for the end.  If it is None it uses the current date.  Default is None

    Returns
    -------
    True if the thing is between the start and end
    """
    if not start:
        start = datetime.date.today()
    if not end:
        end = datetime.date.today()
    between = False
    if is_after(thing, start) and is_before(thing, end):
        between = True
    return between
