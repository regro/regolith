"""Misc. regolith tools.
"""
import os
import re
import sys
import platform
import email.utils
from datetime import datetime

if sys.version_info[0] >= 3:
    string_types = (str, bytes)
    unicode_type = str
else:
    string_types = (str, unicode)
    unicode_type = unicode

DEFAULT_ENCODING = sys.getdefaultencoding()

ON_WINDOWS = (platform.system() == 'Windows')
ON_MAC = (platform.system() == 'Darwin')
ON_LINUX = (platform.system() == 'Linux')
ON_POSIX = (os.name == 'posix')


def dbdirname(db, rc):
    """Gets the database dir name."""
    dbsdir = os.path.join(rc.builddir, '_dbs')
    dbdir = os.path.join(dbsdir, db['name'])
    return dbdir


def dbpathname(db, rc):
    """Gets the database path name."""
    dbdir = dbdirname(db, rc)
    dbpath = os.path.join(dbdir, db['path'])
    return dbpath


def fallback(cond, backup):
    """Decorator for returning the object if cond is true and a backup if cond is false.
    """
    def dec(obj):
        return obj if cond else backup
    return dec


def all_docs_from_collection(client, collname):
    """Yield all entries in for all collections of a given name in a given database."""
    for dbname in client.keys():
        if dbname == 'local':
            continue
        if collname not in client.collection_names(dbname):
            continue
        yield from client.all_documents(dbname, collname)


MONTHS = {
    'jan': 1,
    'jan.': 1,
    'january': 1,
    'feb': 2,
    'feb.': 2,
    'february': 2,
    'mar': 3,
    'mar.': 3,
    'march': 3,
    'apr': 4,
    'apr.': 4,
    'april': 4,
    'may': 5,
    'may.': 5,
    'jun': 6,
    'jun.': 6,
    'june': 6,
    'jul': 7,
    'jul.': 7,
    'july': 7,
    'aug': 8,
    'aug.': 8,
    'august': 8,
    'sep': 9,
    'sep.': 9,
    'sept': 9,
    'sept.': 9,
    'september': 9,
    'oct': 10,
    'oct.': 10,
    'october': 10,
    'nov': 11,
    'nov.': 11,
    'november': 11,
    'dec': 12,
    'dec.': 12,
    'december': 12,
    }

SHORT_MONTH_NAMES = (None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                     'Aug', 'Sept', 'Oct', 'Nov', 'Dec')

def month_to_int(m):
    """Converts a month to an integer."""
    try:
        m = int(m)
    except ValueError:
        m = MONTHS[m.lower()]
    return m


def date_to_float(y, m, d=0):
    """Converts years / months / days to a float, eg 2015.0818 is August 18th 2015."""
    y = int(y)
    m = month_to_int(m)
    d = int(d)
    return y + (m/100.0) + (d/100000.0)


def date_to_rfc822(y, m, d=1):
    """Converts a date to an RFC 822 formatted string."""
    d = datetime(int(y), month_to_int(m), int(d))
    return email.utils.format_datetime(d)


def rfc822now():
    """Creates a string of the current time according to RFC 822."""
    now = datetime.utcnow()
    return email.utils.format_datetime(now)


def gets(seq, key, default=None):
    """Gets a key from every element of a sequence if possible."""
    for x in seq:
        yield x.get(key, default)


def month_and_year(m=None, y=None):
    """Creates a string from month and year data, if available."""
    if y is None:
        return "present"
    if m is None:
        return str(y)
    m = month_to_int(m)
    return '{0} {1}'.format(SHORT_MONTH_NAMES[m], y)

