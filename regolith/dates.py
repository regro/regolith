"""Date based tools"""
import datetime

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
    "tbd": 1
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
    for i in range(len(dateslist)-1):
        if dateslist[i+1][0] <= dateslist[i][1] and not overlaps_ok:
            status = False
        elif (dateslist[i+1][0] - dateslist[i][1]).days > 1:
            status = False
    return status

def beg_end_dates(thing):
    bd = thing.get('begin_day')
    bm = thing.get('begin_month')
    by = thing.get('begin_year')
    ed = thing.get('end_day')
    em = thing.get('end_month')
    ey = thing.get('end_year')
    begin_date = datetime.date(by, month_to_int(bm), bd)
    end_date = datetime.date(ey, month_to_int(em), ed)
    return begin_date, end_date

