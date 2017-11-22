"""Misc. regolith tools.
"""
import os
import re
import sys
import platform
import email.utils
from copy import deepcopy

from datetime import datetime

from regolith.sorters import doc_date_key, id_key, ene_date_key

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase
    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

LATEX_OPTS = ['-halt-on-error', '-file-line-error']

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
    '': 1
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


def filter_publications(citations, authors, reverse=False, bold=True):
    pubs = []
    for pub in citations:
        if len(set(pub['author']) & authors) == 0:
            continue
        pub = deepcopy(pub)
        if bold:
            bold_self = []
            for a in pub['author']:
                if a in authors:
                    bold_self.append('\\textbf{' + a + '}')
                else:
                    bold_self.append(a)
            pub['author'] = bold_self
        else:
            pub = deepcopy(pub)
        pubs.append(pub)
    pubs.sort(key=doc_date_key, reverse=reverse)
    return pubs


def filter_projects(projects, authors, reverse=False):
    projs = []
    for proj in projects:
        team_names = set(gets(proj['team'], 'name'))
        if len(team_names & authors) == 0:
            continue
        proj = dict(proj)
        proj['team'] = [x for x in proj['team'] if x['name'] in authors]
        projs.append(proj)
    projs.sort(key=id_key, reverse=reverse)
    return projs


def filter_grants(input_grants, names, pi=True, reverse=True):
    grants = []
    total_amount = 0.0
    subaward_amount = 0.0
    for grant in input_grants:
        team_names = set(gets(grant['team'], 'name'))
        if len(team_names & names) == 0:
            continue
        grant = deepcopy(grant)
        person = [x for x in grant['team'] if x['name'] in names][0]
        if pi:
            if person['position'].lower() == 'pi':
                total_amount += grant['amount']
            else:
                continue
        else:
            if person['position'].lower() == 'pi':
                continue
            else:
                total_amount += grant['amount']
                subaward_amount += person.get('subaward_amount', 0.0)
                grant['subaward_amount'] = person.get('subaward_amount',
                                                      0.0)
                grant['pi'] = [x for x in grant['team'] if
                               x['position'].lower() == 'pi'][0]
                grant['me'] = person
        grants.append(grant)
    grants.sort(key=ene_date_key, reverse=reverse)
    return grants, total_amount, subaward_amount


def awards_grants_honors(p):
    """Make sorted awards grants and honors list."""
    aghs = []
    for x in p.get('funding', ()):
        d = {'description': '{0} ({1}{2:,})'.format(
            latex_safe(x['name']),
            x.get('currency', '$').replace('$', '\$'), x['value']),
            'year': x['year'],
            '_key': date_to_float(x['year'], x.get('month', 0)),
        }
        aghs.append(d)
    for x in p.get('service', []) + p.get('honors', []):
        d = {'description': latex_safe(x['name']),
             'year': x['year'],
             '_key': date_to_float(x['year'], x.get('month', 0)),
             }
        aghs.append(d)
    aghs.sort(key=(lambda x: x.get('_key', 0.0)), reverse=True)
    return aghs


def latex_safe(s):
    return s.replace('&', '\&').replace('$', '\$').replace('#', '\#')


def make_bibtex_file(pubs, pid, person_dir='.'):
    if not HAVE_BIBTEX_PARSER:
        return None
    skip_keys = {'ID', 'ENTRYTYPE', 'author'}
    bibdb = BibDatabase()
    bibwriter = BibTexWriter()
    bibdb.entries = ents = []
    for pub in pubs:
        ent = dict(pub)
        ent['ID'] = ent.pop('_id')
        ent['ENTRYTYPE'] = ent.pop('entrytype')
        for n in ['author', 'editor']:
            if n in ent:
                ent[n] = ' and '.join(ent[n])
        for key in ent.keys():
            if key in skip_keys:
                continue
            ent[key] = latex_safe(ent[key])
        ents.append(ent)
    fname = os.path.join(person_dir, pid) + '.bib'
    with open(fname, 'w') as f:
        f.write(bibwriter.write(bibdb))
    return fname
