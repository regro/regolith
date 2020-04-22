"""Date based tools"""
import calendar
import datetime
from calendar import monthrange

# dateutil
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
    "tbd": 1,
}


def month_to_int(m):
    """Converts a month to an integer."""
    try:
        m = int(m)
    except ValueError:
        m = MONTHS[m.lower()]
    return m


def month_to_str_int(m):
    """Converts a month to an int form, str type, with a leading zero"""
    mi = month_to_int(m)
    if mi < 10:
        ms = "0{}".format(mi)
    else:
        ms = str(mi)
    return ms


def day_to_str_int(d):
    """Converts a day to an int form, str type, with a leading zero"""
    if d < 10:
        ds = "0{}".format(d)
    else:
        ds = str(d)
    return ds


def date_to_float(y, m, d=0):
    """Converts years / months / days to a float, eg 2015.0818 is August
    18th 2015. """
    y = int(y)
    m = month_to_int(m)
    d = int(d)
    return y + (m / 100.0) + (d / 100000.0)


def find_gaps_overlaps(dateslist, overlaps_ok=False):
    '''
    Find whether there is a gap or an overlap in a list of date-ranges

    Parameters
    ----------
    dateslist: list of tuples of datetime.date objects
      The list of date-ranges.
    overlaps_ok: bool
      Returns false if there are gaps but true if there are overlaps but no gaps

    Returns
    -------
      True if there are no gaps or overlaps else False

    '''

    status = True
    dateslist.sort(key=lambda x: x[0])
    for i in range(len(dateslist) - 1):
        if dateslist[i + 1][0] <= dateslist[i][1] and not overlaps_ok:
            status = False
        elif (dateslist[i + 1][0] - dateslist[i][1]).days > 1:
            status = False
    return status


def begin_end_dates(thing):
    bd = thing.get('begin_day', 1)
    bm = thing.get('begin_month', 1)
    by = thing.get('begin_year')
    ed = thing.get('end_day')
    em = thing.get('end_month', 12)
    ey = thing.get('end_year')
    begin_date = datetime.date(by, month_to_int(bm), bd)
    end_date = datetime.date(ey, month_to_int(em), ed)
    return begin_date, end_date


def last_day(year, month):
    """
    Returns the last day of the month for the month given

    Parameters
    ----------
    year: integer
      the year that the month is in
    month: integer or string
      the month.  if an integer should be resolvable using regolith month_to_int

    Returns
    -------
    The last day of that month

    """
    return calendar.monthrange(year, month_to_int(month))[1]

def get_dates(thing):
    '''
    given a dict like thing, return the items

    Parameters
    ----------
    thing: dict
      the dict that contains the dates

    Returns
    -------
       dict containing datetime.date objects for begin_date end_date and date

    Description
    -----------
    If "begin_date", "end_date" or "date" values are found, if these are are in
    an ISO format string they will be converted to datetime.date objects and
    returned in the dictionary under keys of the same name.  A specified date
    will override any date built from year/month/day data.

    If they are not found the function will look for begin_year, end_year and
    year.

    If "year", "month" and "day" are found the function will return these in the
    "date" field and begin_date and end_date will be None

    If year is found but no month or day are found the function will return
    begin_date and end_date with the beginning and the end of the given year/month.
    The returned date will be None.

    If end_year is found, the end month and end day are missing they are set to
    12 and 31, respectively

    If begin_year is found, the begin month and begin day are missing they are set to
    1 and 1, respectively
    '''

    if thing.get("end_year") and not thing.get("begin_year"):
        print('WARNING: end_year specified without begin_year')
    begin_date, end_date, date = None, None, None
    if thing.get('begin_year'):
        if not thing.get('begin_month'):
            thing['begin_month'] = 1
        if not thing.get('begin_day'):
            thing['begin_day'] = 1
        print(thing['begin_month'])
        begin_date = datetime.date(thing['begin_year'],month_to_int(thing['begin_month']),
                                   thing['begin_day'])
    if thing.get('end_year'):
        if not thing.get('end_month'):
            thing['end_month'] = 12
        if not thing.get('end_day'):
            thing['end_day'] = last_day(thing['end_year'], thing['end_month'])
        end_date = datetime.date(thing['end_year'],month_to_int(thing['end_month']),
                                   thing['end_day'])
    if thing.get('year'):
        if not thing.get('month'):
            if thing.get('begin_year'):
                print("WARNING: both year and begin_year specified.  Year info will be used")
            begin_date = datetime.date(thing['year'],1,1)
            end_date = datetime.date(thing['year'],12,31)
        elif not thing.get('day'):
            if thing.get('begin_year'):
                print("WARNING: both year and begin_year specified.  Year info will be used")
            begin_date = datetime.date(thing['year'],month_to_int(thing['month']),
                                   1)
            end_date = datetime.date(thing['year'],
                                       month_to_int(thing['month']),
                                       last_day(thing['year'], thing['month']))
        else:
            date = datetime.date(thing['year'],
                                       month_to_int(thing['month']),
                                       thing['day'])
            begin_date = datetime.date(thing['year'],
                                       month_to_int(thing['month']),
                                       thing['day'])
            end_date = datetime.date(thing['year'],
                                       month_to_int(thing['month']),
                                       thing['day'])
    if thing.get('begin_date'):
        begin_date = date_parser.parse(thing.get('begin_date')).date()
    if thing.get('end_date'):
        end_date = date_parser.parse(thing.get('end_date')).date()
    if thing.get('date'):
        date = date_parser.parse(thing.get('date')).date()
    dates = {'begin_date': begin_date, 'end_date': end_date, 'date': date}
    return dates
