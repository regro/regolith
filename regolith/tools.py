"""Misc. regolith tools.
"""
import email.utils
import os
import platform
import re
import sys
import time
from copy import deepcopy, copy
from calendar import monthrange
from copy import deepcopy
from datetime import datetime, date, timedelta
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from regolith.chained_db import ChainDB
from regolith.dates import month_to_int, date_to_float, get_dates, last_day, is_current
from regolith.sorters import doc_date_key, id_key, ene_date_key, date_key
from regolith.chained_db import ChainDB

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

LATEX_OPTS = ["-halt-on-error", "-file-line-error"]

if sys.version_info[0] >= 3:
    string_types = (str, bytes)
    unicode_type = str
else:
    pass
    # string_types = (str, unicode)
    # unicode_type = unicode

DEFAULT_ENCODING = sys.getdefaultencoding()

ON_WINDOWS = platform.system() == "Windows"
ON_MAC = platform.system() == "Darwin"
ON_LINUX = platform.system() == "Linux"
ON_POSIX = os.name == "posix"


def dbdirname(db, rc):
    """Gets the database dir name."""
    if db.get("local", False) is False:
        dbsdir = os.path.join(rc.builddir, "_dbs")
        dbdir = os.path.join(dbsdir, db["name"])
    else:
        dbdir = db["url"]
    return dbdir


def dbpathname(db, rc):
    """Gets the database path name."""
    dbdir = dbdirname(db, rc)
    dbpath = os.path.join(dbdir, db["path"])
    return dbpath


def fallback(cond, backup):
    """Decorator for returning the object if cond is true and a backup if
    cond is false. """

    def dec(obj):
        return obj if cond else backup

    return dec


def all_docs_from_collection(client, collname, copy=True):
    """Yield all entries in for all collections of a given name in a given
    database. """
    yield from client.all_documents(collname, copy=copy)


SHORT_MONTH_NAMES = (
    None,
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sept",
    "Oct",
    "Nov",
    "Dec",
)


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
    return "{0} {1}".format(SHORT_MONTH_NAMES[m], y)


def get_team_from_grant(grantcol):
    for grant in grantcol:
        return gets(grant["team"], "name")


def filter_publications(citations, authors, reverse=False, bold=True,
                        since=None, before=None, ):
    """Filter publications by the author(s)/editor(s)

    Parameters
    ----------
    citations : list of dict
        The publication citations
    authors : set of str
        The authors to be filtered against
    reverse : bool, optional
        If True reverse the order, defaults to False
    bold : bool, optional
        If True put latex bold around the author(s) in question
    since : date, optional
        The date after which papers must have been published
    before : date, optional
        The date before which papers must have been published
    """
    pubs = []
    for pub in citations:
        if (
                len((set(pub.get("author", [])) | set(
                    pub.get("editor", []))) & authors)
                == 0
        ):
            continue
        if not pub.get("month") or pub.get("month") == "tbd":
#            print("WARNING: {} missing month will be ignored".format(pub.get("title")))
            continue
        pub = deepcopy(pub)
        if bold:
            bold_self = []
            for a in pub["author"]:
                if a in authors:
                    bold_self.append("\\textbf{" + a + "}")
                else:
                    bold_self.append(a)
            pub["author"] = bold_self
        else:
            pub = deepcopy(pub)
        if since:
            bibdate = date(int(pub.get("year")),
                           month_to_int(pub.get("month", 12)),
                           int(pub.get("day", 28)))
            if bibdate > since:
                if before:
                    if bibdate < before:
                        pubs.append(pub)
                else:
                    pubs.append(pub)
        else:
            pubs.append(pub)

    pubs.sort(key=doc_date_key, reverse=reverse)
    return pubs


def filter_projects(projects, people, reverse=False,
                    active_only=False, group=None, ptype=None):
    """Filter projects by the author(s)

    Parameters
    ----------
    projects : list of dict
        The publication citations
    people : set of list of str
        The people to be filtered against
    reverse : bool, optional
        If True reverse the order, defaults to False
    since : date, optional
        The date after which a highlight must be for a project to be returned,
        defaults to None
    before : date, optional
        The date before which a highlight must be for a project to be returned,
        defaults to None
    active_only : bool, optional
        Only active projects will be returned if True,
        defaults to False
    group : str, optional
        Only projects from this group will be returned if specified, otherwise
        projects from all groups will be returned, defaults to None
    ptype : str, optional
        The type of the project to filter for, such as ossoftware for open source
        software, defaults to None
    """
    projs = []
    # Fixme dereference team from grant collection if provided
    for proj in projects:
        team_names = set(gets(proj["team"], "name"))
        if len(team_names & people) == 0:
            continue
        if active_only:
            if not proj.get("active"):
                continue
        if group:
            if proj.get("group") != group:
                continue
        if ptype:
            if proj.get("type") != ptype:
                continue
        projs.append(proj)

    projs.sort(key=id_key, reverse=reverse)
    return projs


def filter_grants(input_grants, names, pi=True, reverse=True, multi_pi=False):
    """Filter grants by those involved

    Parameters
    ----------
    input_grants : list of dict
        The grants to filter
    names : set of str
        The authors to be filtered against
    pi : bool, optional
        If True add the grant amount to that person's total amount
    reverse : bool, optional
        If True reverse the order, defaults to False
    multi_pi : bool, optional
        If True compute sub-awards for multi PI grants, defaults to False
    """
    grants = []
    total_amount = 0.0
    subaward_amount = 0.0
    for grant in input_grants:
        team_names = set(gets(grant["team"], "name"))
        if len(team_names & names) == 0:
            continue
        grant = deepcopy(grant)
        person = [x for x in grant["team"] if x["name"] in names][0]
        if pi:
            if person["position"].lower() == "pi":
                total_amount += grant["amount"]
            else:
                continue
        elif multi_pi:
            grant["subaward_amount"] = person.get("subaward_amount", 0.0)
            grant["multi_pi"] = any(gets(grant["team"], "subaward_amount"))
        else:
            if person["position"].lower() == "pi":
                continue
            else:
                total_amount += grant["amount"]
                subaward_amount += person.get("subaward_amount", 0.0)
                grant["subaward_amount"] = person.get("subaward_amount", 0.0)
                grant["pi"] = [
                    x for x in grant["team"] if x["position"].lower() == "pi"
                ][0]
                grant["me"] = person
        grants.append(grant)
    grants.sort(key=ene_date_key, reverse=reverse)
    return grants, total_amount, subaward_amount


def filter_employment_for_advisees(people, begin_period, status, active=False):
    advisees = []
    for p in people:
        for i in p.get("employment", []):
            if i.get("status") == status:
                if i.get("end_year"):
                    end_date = date(i.get("end_year"),
                                    month_to_int(i.get("end_month", 12)),
                                    i.get("end_day", 28))
                else:
                    end_date = date.today()
                    i["end_year"] = end_date.year
                if end_date >= begin_period:
                    p['role'] = i.get("position")
                    p['status'] = status
                    p['end_year'] = i.get("end_year", "n/a")
                    p['position'] = i.get("position")
                    advisees.append(p)
                    advisees.sort(key=lambda x: x['end_year'], reverse=True)
    return advisees


def filter_service(ppl, begin_period, type, verbose=False):
    service = []
    people = copy(ppl)
    for p in people:
        myservice = []
        svc = copy(p.get("service", []))
        for i in svc:
            if i.get("type") == type:
                if i.get('year'):
                    end_year = i.get('year')
                    if verbose: print("end_year from {} = {}".format(i.get("name"[:10]),end_year))
                elif i.get('end_year'):
                    end_year = i.get('end_year')
                    if verbose: print("end_year from {} = {}".format(i.get("name"[:10]),end_year))
                else:
                    end_year = date.today().year
                    if verbose: print("no end_year, using today = {}".format(end_year))
                end_date = date(int(end_year),
                                month_to_int(i.get("end_month", 12)),
                                i.get("end_day", 28))
                if end_date >= begin_period:
                    if not i.get('month'):
                        month = i.get("begin_month", 0)
                        i['month'] = SHORT_MONTH_NAMES[month_to_int(month)]
                    else:
                        i['month'] = SHORT_MONTH_NAMES[month_to_int(i['month'])]
                    myservice.append(i)
        p['service'] = myservice
        if len(p['service']) > 0:
            service.append(p)
    return service


def filter_facilities(people, begin_period, type, verbose=False):
    facilities = []
    for p in people:
        myfacility = []
        svc = copy(p.get("facilities", []))
        for i in svc:
            if i.get("type") == type:
                if i.get('year'):
                    end_year = i.get('year')
                elif i.get('end_year'):
                    end_year = i.get('end_year')
                else:
                    end_year = date.today().year
                end_date = date(end_year,
                                i.get("end_month", 12),
                                i.get("end_day", 28))
                if end_date >= begin_period:
                    if not i.get('month'):
                        month = i.get("begin_month", 0)
                        i['month'] = SHORT_MONTH_NAMES[month_to_int(month)]
                    else:
                        i['month'] = SHORT_MONTH_NAMES[month_to_int(i['month'])]
                    myfacility.append(i)
        if verbose: print("p['facilities'] = {}".format(myfacility))
        p['facilities'] = myfacility
        if len(p['facilities']) > 0:
            facilities.append(p)
    return facilities


def filter_patents(patentscoll, people, target, since=None, before=None):
    patents = []
    allowed_statuses = ["active", "pending"]
    for i in patentscoll:
        if i.get("status") in allowed_statuses and i.get("type") in "patent":
            inventors = [
                fuzzy_retrieval(
                    people,
                    ["aka", "name", "_id"],
                    inv,
                    case_sensitive=False,
                )
                for inv in i['inventors']
            ]
            person = fuzzy_retrieval(
                people,
                ["aka", "name", "_id"],
                target,
                case_sensitive=False,
            )
            if person in inventors:
                if i.get('end_year'):
                    end_year = i.get('end_year')
                else:
                    end_year = date.today().year
                end_date = date(end_year,
                                i.get("end_month", 12),
                                i.get("end_day", 28))
                if since:
                    if end_date >= since:
                        if not i.get('month'):
                            month = i.get("begin_month", 0)
                            i['month'] = SHORT_MONTH_NAMES[month_to_int(month)]
                        else:
                            i['month'] = SHORT_MONTH_NAMES[
                                month_to_int(i['month'])]

                        events = [event for event in i["events"] if
                                  date(event["year"], event["month"],
                                       event.get("day", 28)) > since]
                        events = sorted(events,
                                        key=lambda event: date(
                                            event["year"],
                                            event["month"],
                                            event.get("day", 28)))
                        i["events"] = events
                        patents.append(i)
                else:
                    events = [event for event in i["events"]]
                    events = sorted(events,
                                    key=lambda event: date(event["year"],
                                                           event["month"],
                                                           28))
                    i["events"] = events
                    patents.append(i)
    return patents


def filter_licenses(patentscoll, people, target, since=None, before=None):
    licenses = []
    allowed_statuses = ["active", "pending"]
    for i in patentscoll:
        if i.get("status") in allowed_statuses and i.get("type") in "license":
            inventors = [
                fuzzy_retrieval(
                    people,
                    ["aka", "name", "_id"],
                    inv,
                    case_sensitive=False,
                )
                for inv in i['inventors']
            ]
            person = fuzzy_retrieval(
                people,
                ["aka", "name", "_id"],
                target,
                case_sensitive=False,
            )
            if person in inventors:
                if i.get('end_year'):
                    end_year = i.get('end_year')
                else:
                    end_year = date.today().year
                end_date = date(end_year,
                                i.get("end_month", 12),
                                i.get("end_day", 28))
                if since:
                    if end_date >= since:
                        if not i.get('month'):
                            month = i.get("begin_month", 0)
                            i['month'] = SHORT_MONTH_NAMES[month_to_int(month)]
                        else:
                            i['month'] = SHORT_MONTH_NAMES[
                                month_to_int(i['month'])]
                        total = sum([event.get("amount") for event in i["events"]])
                        i["total_amount"] = total
                        events = [event for event in i["events"] if
                                  date(event["year"], event["month"],
                                       event.get("day", 28)) > since]
                        events = sorted(events,
                                        key=lambda event: date(event["year"],
                                                               event["month"],
                                                               event.get("day", 28)))
                        i["events"] = events
                        licenses.append(i)
                else:
                    total = sum([event.get("amount") for event in events])
                    i["total_amount"] = total
                    events = [event for event in i["events"]]
                    events = sorted(events,
                                    key=lambda event: date(event["year"],
                                                           event["month"],
                                                           28))
                    i["events"] = events
                    licenses.append(i)

    return licenses


def filter_activities(people, begin_period, type, verbose=False):
    activities = []
    for p in people:
        myactivity = []
        svc = copy(p.get("activities", []))
        for i in svc:
            if i.get("type") == type:
                # if i.get('year'):
                #     end_year = i.get('year')
                #     if verbose: print("end_year from 'year' = {}".format(end_year))
                # elif i.get('end_year'):
                #     end_year = i.get('end_year')
                #     if verbose: print("end_year from 'end_year' = {}".format(end_year))
                # else:
                #     end_year = date.today().year
                #     if verbose: print("no end_year, using today = {}".format(end_year))                                i.get("end_month", 12),
                #                 i.get("end_day", last_day(end_year,  i.get("end_month")))
                # if verbose: print("end_date = {} and begin_period = {}".format(end_date,begin_period))
                # if verbose: print("condition end_date >= begin_period will be used")
                idates = get_dates(i)
                if idates["end_date"] >= begin_period:
                    usedate = idates.get('begin_date', idates.get('date'))
                    i['year'] = usedate.year
                    i['month'] = SHORT_MONTH_NAMES[month_to_int(usedate.month)]
                    myactivity.append(i)
        p['activities'] = myactivity
        if len(p['activities']) > 0:
            activities.append(p)
    return activities


def filter_presentations(people, presentations, institutions, target, types=["all"],
                         since=None, before=None, statuses=["accepted"]):
    '''
    filters presentations for different types and date ranges

    Parameters
    ----------
    people: iterable of dicts
      The people collection
    presentations: iterable of dicts
      The presentations collection
    institutions: iterable of dicts
      The institutions collection
    target: str
      The id of the person you will build the list for
    types: list of strings.  Optional, default = all
      The types to filter for.  Allowed types are
        "all",
        "award"
        "plenary"
        "keynote"
        "invited"
        "colloquium"
        "seminar"
        "tutorial"
        "contributed-oral"
        "poster"
    since: date.  Optional, default is None
        The begin date to filter from
    before: date. Optional, default is None
        The end date to filter for.  None does not apply this filter
    statuses: list of str.  Optional. Default is accepted
      The list of statuses to filter for.  Allowed statuses are
        "all"
        "accepted"
        "declined"
        "cancelled"

    Returns
    -------
    list of presentation documents

    '''
    presentations = deepcopy(presentations)

    firstclean = list()
    secondclean = list()
    thirdclean = list()
    fourthclean = list()
    presclean = list()

    # build the filtered collection
    # only list the talk if the group member is an author
    for pres in presentations:
        pauthors = pres["authors"]
        if isinstance(pauthors, str):
            pauthors = [pauthors]
        authors = [
            fuzzy_retrieval(
                people,
                ["aka", "name", "_id"],
                author,
                case_sensitive=False,
            )
            for author in pauthors
        ]
        authorids = [
            author["_id"]
            for author in authors
            if author is not None
        ]
        if target in authorids:
            firstclean.append(pres)
    # only list the presentation if it has status in statuses
    for pres in firstclean:
        if pres["status"] in statuses or "all" in statuses:
            secondclean.append(pres)
    # only list the presentation if it has type in types
    for pres in secondclean:
        if pres["type"] in types or "all" in types:
            thirdclean.append(pres)
    # if specified, only list presentations in specified date ranges
    if since:
        for pres in thirdclean:
            presdate = date((pres["begin_year"]),
                            month_to_int(pres["begin_month"]),
                            int(pres["begin_day"]))
            if presdate > since:
                fourthclean.append(pres)
    else:
        fourthclean = thirdclean
    if before:
        for pres in fourthclean:
            presdate = date((pres["begin_year"]),
                            month_to_int(pres["begin_month"]),
                            int(pres["begin_day"]))
            if presdate < before:
                presclean.append(pres)
    else:
        presclean = fourthclean

    # build author list
    for pres in presclean:
        pauthors = pres["authors"]
        if isinstance(pauthors, str):
            pauthors = [pauthors]
        pres["authors"] = [
            author
            if fuzzy_retrieval(
                people,
                ["aka", "name", "_id"],
                author,
                case_sensitive=False,
            )
               is None
            else fuzzy_retrieval(
                people,
                ["aka", "name", "_id"],
                author,
                case_sensitive=False,
            )["name"]
            for author in pauthors
        ]
        authorlist = ", ".join(pres["authors"])
        pres["authors"] = authorlist
        pres["begin_month"] = month_to_int(pres["begin_month"])
        pres["date"] = date(
            pres["begin_year"],
            pres["begin_month"],
            pres["begin_day"],
        )
        for day in ["begin_day", "end_day"]:
            pres["{}_suffix".format(day)] = number_suffix(
                pres.get(day, None)
            )
        if "institution" in pres:
            try:
                pres["institution"] = fuzzy_retrieval(
                    institutions,
                    ["aka", "name", "_id"],
                    pres["institution"],
                    case_sensitive=False,
                )
                if pres["institution"] is None:
                    print(
                        "WARNING: department {} not found in"
                        " {} in institutions.yml.  Pres list will"
                        " build but please check this entry carefully and "
                            "rerun to remove "
                        "errors".format(pres["institution"],pres["_id"])
                    )
            except:
                sys.exit(
                    "ERROR: institution {} not found in "
                    "institutions.yml.  Please add and "
                    "rerun".format(pres["institution"])
                )
            if "department" in pres:
                try:
                    pres["department"] = pres["institution"][
                        "departments"
                    ][pres["department"]]
                except:
                    print(
                        "WARNING: department {} not found in"
                        " {} in institutions.yml.  Pres list will"
                        " build but please check this entry carefully and"
                        " please add the dept to the institution!".format(
                            pres["department"],
                            pres["institution"],
                        )
                    )
                    pres["department"] = {
                        "name": pres["department"]
                    }
    if len(presclean) > 0:
        presclean = sorted(
            presclean,
            key=lambda k: k.get("date", None),
            reverse=True,
        )
    return presclean


def awards_grants_honors(p):
    """Make sorted awards grants and honors list.

    Parameters
    ----------
    p : dict
        The person entry
    """
    aghs = []
    if p.get("funding"):
        for x in p.get("funding", ()):
            d = {
                "description": "{0} ({1}{2:,})".format(
                    latex_safe(x["name"]),
                    x.get("currency", "$").replace("$", "\$"),
                    x["value"],
                ),
                "year": x["year"],
                "_key": date_to_float(x["year"], x.get("month", 0)),
            }
            aghs.append(d)
    for x in p.get("service", []) + p.get("honors", []):
        d = {"description": latex_safe(x["name"])}
        if "year" in x:
            d.update(
                {"year": x["year"],
                 "_key": date_to_float(x["year"], x.get("month", 0))}
            )
        elif "begin_year" in x and "end_year" in x:
            d.update(
                {
                    "year": "{}-{}".format(x["begin_year"], x["end_year"]),
                    "_key": date_to_float(x["begin_year"], x.get("month", 0)),
                }
            )
        elif "begin_year" in x:
            d.update(
                {
                    "year": "{}".format(x["begin_year"]),
                    "_key": date_to_float(x["begin_year"], x.get("month", 0)),
                }
            )
        aghs.append(d)
    aghs.sort(key=(lambda x: x.get("_key", 0.0)), reverse=True)
    return aghs


def awards(p, since=None, before=None, ):
    """Make sorted awards and honors

    Parameters
    ----------
    p : dict
        The person entry
    since : date.  Optional, default is None
        The begin date to filter from
    before : date. Optional, default is None
        The end date to filter for.  None does not apply this filter

    """
    if not since: since = date(1500, 1, 1)
    a = []
    for x in p.get("honors", []):
        if "year" in x:
            if date(x.get("year"), 12, 31) > since:
                d = {"description": latex_safe(x["name"]), "year": x["year"],
                     "_key": date_to_float(x["year"], x.get("month", 0))}
                a.append(d)
        elif "begin_year" in x and "end_year" in x:
            if date(x.get("begin_year", 12, 31)) > since:
                d = {"description": latex_safe(x["name"]),
                     "year": "{}-{}".format(x["begin_year"], x["end_year"]),
                     "_key": date_to_float(x["begin_year"], x.get("month", 0)),
                     }
                a.append(d)
        elif "begin_year" in x:
            if date(x.get("begin_year"), 12, 31) > since:
                d = {"description": latex_safe(x["name"]),
                     "year": "{}".format(x["begin_year"]),
                     "_key": date_to_float(x["begin_year"], x.get("month", 0)),
                     }
                a.append(d)
    a.sort(key=(lambda x: x.get("_key", 0.0)), reverse=True)
    return a


HTTP_RE = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
)


def latex_safe_url(s):
    """Makes a string that is a URL latex safe."""
    return s.replace("#", r"\#")


def latex_safe(s, url_check=True, wrapper="url"):
    """Make string latex safe

    Parameters
    ----------
    s : str
    url_check : bool, optional
        If True check for URLs and wrap them, if False check for URL but don't
        wrap, defaults to True
    wrapper : str, optional
        The wrapper for wrapping urls defaults to url
    """
    if not s:
        return s
    if url_check:
        # If it looks like a URL make it a latex URL
        url_search = HTTP_RE.search(s)
        if url_search:
            url = r"{start}\{wrapper}{{{s}}}{end}".format(
                start=(latex_safe(s[: url_search.start()])),
                end=(latex_safe(s[url_search.end():])),
                wrapper=wrapper,
                s=latex_safe_url(s[url_search.start(): url_search.end()]),
            )
            return url
    return (
        s.replace("&", r"\&")
            .replace("$", r"\$")
            .replace("#", r"\#")
            .replace("_", r"\_")
    )


def make_bibtex_file(pubs, pid, person_dir="."):
    """Make a bibtex file given the publications

    Parameters
    ----------
    pubs : list of dict
        The publications
    pid : str
        The person id
    person_dir : str, optional
        The person's directory
    """
    if not HAVE_BIBTEX_PARSER:
        return None
    skip_keys = {"ID", "ENTRYTYPE", "author"}
    bibdb = BibDatabase()
    bibwriter = BibTexWriter()
    bibdb.entries = ents = []
    for pub in pubs:
        ent = dict(pub)
        ent["ID"] = ent.pop("_id")
        ent["ENTRYTYPE"] = ent.pop("entrytype")
        for n in ["author", "editor"]:
            if n in ent:
                ent[n] = " and ".join(ent[n])
        for key in ent.keys():
            if key in skip_keys:
                continue
            # don't think I want the bibfile entries to be latex safe
            # ent[key] = latex_safe(ent[key])
            ent[key] = str(ent[key])
        ents.append(ent)
    fname = os.path.join(person_dir, pid) + ".bib"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(bibwriter.write(bibdb))
    return fname


def document_by_value(documents, address, value):
    """Get a specific document by one of its values

    Parameters
    ----------
    documents: generator
        Generator which yields the documents
    address: str or tuple
        The address of the data in the document
    value: any
        The expected value for the document

    Returns
    -------
    dict:
        The first document which matches the request
    """
    if isinstance(address, str):
        address = (address,)
    for g_doc in documents:
        doc = deepcopy(g_doc)
        for add in address:
            doc = doc[add]
        if doc == value:
            return g_doc


def fuzzy_retrieval(documents, sources, value, case_sensitive=True):
    """Retrieve a document from the documents where value is compared against
    multiple potential sources

    Parameters
    ----------
    documents: generator
        The documents
    sources: iterable
        The potential data sources
    value:
        The value to compare against to find the document of interest
    case_sensitive: Bool
        When true will match case (Default = True)

    Returns
    -------
    dict:
        The document

    Examples
    --------
    >>> fuzzy_retrieval(people, ['aka', 'name'], 'pi_name', case_sensitive = False)

    This would get the person entry for which either the alias or the name was
    ``pi_name``.

    """
    for doc in documents:
        returns = []
        for k in sources:
            ret = doc.get(k, [])
            if not isinstance(ret, list):
                ret = [ret]
            returns.extend(ret)
        if not case_sensitive:
            returns = [reti.lower() for reti in returns if
                       isinstance(reti, str)]
            if isinstance(value, str):
                if value.lower() in frozenset(returns):
                    return doc
        else:
            if value in frozenset(returns):
                return doc


def number_suffix(number):
    """returns the suffix that adjectivises a number (st, nd, rd, th)

    Paramters
    ---------
    number: integer
        The number.  If number is not an integer, returns an empty string

    Returns
    -------
    suffix: string
        The suffix (st, nd, rd, th)
    """
    if not isinstance(number, (int, float)):
        return ""
    if 10 < number < 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return suffix


def dereference_institution(input_record, institutions):
    """Tool for replacing placeholders for institutions with the actual
    institution data. Note that the replacement is done inplace

    Parameters
    ----------
    input_record : dict
        The record to dereference
    institutions : iterable of dicts
        The institutions
    """
    inst = input_record.get("institution") or input_record.get("organization")
    if not inst:
        error = input_record.get("position") or input_record.get("degree")
        print("WARNING: no institution or organization but found {}".format(
            error))
    db_inst = fuzzy_retrieval(institutions, ["name", "_id", "aka"], inst)
    if db_inst:
        input_record["institution"] = db_inst["name"]
        input_record["organization"] = db_inst["name"]
        if db_inst.get("country") == "USA":
            state_country = db_inst.get("state")
        else:
            state_country = db_inst.get("country")
        input_record["location"] = "{}, {}".format(db_inst["city"],
                                                   state_country)
        if not db_inst.get("departments"):
            print("WARNING: no departments in {}. {} sought".format(
                db_inst.get("_id"), inst))
        if "department" in input_record and db_inst.get("departments"):
            input_record["department"] = fuzzy_retrieval(
                [db_inst["departments"]], ["name", "aka"],
                input_record["department"]
            )
        else:
            input_record["department"] = inst


def merge_collections(a, b, target_id):
    """
    merge two collections into a single merged collection

    for keys that are in both collections, the value in b will be kept

    Parameters
    ----------
    a  the inferior collection (will lose values of shared keys)
    b  the superior collection (will keep values of shared keys)
    target_id  str  the name of the key used in b to dereference ids in a

    Returns
    -------
    the combined collection.  Note that it returns a collection only containing
    merged items from a and b that are dereferenced in b, i.e., the merged
    intercept.  If you want the union you can update the returned collection
    with a.

    Examples
    --------
    >>>  grants = merge_collections(self.gtx["proposals"], self.gtx["grants"], "proposal_id")

    This would merge all entries in the proposals collection with entries in the
    grants collection for which "_id" in proposals has the value of
    "proposal_id" in grants.
    """
    adict = {}
    for k in a:
        adict[k.get("_id")] = k
    bdict = {}
    for k in b:
        bdict[k.get("_id")] = k
    b_for_a = {}
    for k in adict:
        for kk, v in bdict.items():
            if v.get(target_id, "") == k:
                b_for_a[k] = kk
    chained = {}
    for k, v in b_for_a.items():
        chained[k] = ChainDB(adict[k], bdict[v])
    return list(chained.values())


def update_schemas(default_schema, user_schema):
    """
    Merging the user schema into the default schema recursively and return the
    merged schema. The default schema and user schema will not be modified
    during the merging.

    Parameters
    ----------
    default_schema : dict
        The default schema.
    user_schema : dict
        The user defined schema.

    Returns
    -------
    updated_schema : dict
        The merged schema.
    """
    updated_schema = deepcopy(default_schema)
    for key in user_schema.keys():
        if (key in updated_schema) and isinstance(updated_schema[key],
                                                  dict) and isinstance(
            user_schema[key], dict):
            updated_schema[key] = update_schemas(updated_schema[key],
                                                 user_schema[key])
        else:
            updated_schema[key] = user_schema[key]

    return updated_schema


def get_person(person_id, rc):
    """Get the person's name."""
    person_found = fuzzy_retrieval(
        all_docs_from_collection(rc.client, "people"),
        ["name", "aka", "_id"],
        person_id,
        case_sensitive=False
    )
    if person_found:
        return person_found
    person_found = fuzzy_retrieval(
        all_docs_from_collection(rc.client, "contacts"),
        ["name", "aka", "_id"],
        person_id,
        case_sensitive=False
    )
    if person_found:
        return person_found
    print("WARNING: {} missing from people and contacts. Check aka.".format(person_id))
    return None


def group(db, by):
    """
    Group the document in the database according to the value of the doc[by] in db.

    Parameters
    ----------
    db : iterable
        The database of documents.
    by : basestring
        The key to group the documents.

    Returns
    -------
    grouped: dict
        A dictionary mapping the feature value of group to the list of docs. All docs in the same generator have
        the same value of doc[by].

    Examples
    --------
    Here, we use a tuple of dict as an example of the database.
    >>> db = ({"k": "v0"}, {"k": "v1"}, {"k": "v0"})
    >>> group(db)
    This will return
    >>> {"v0": [{"k": "v0"}, {"k": "v0"}], "v1": [{"k": "v1"}]}
    """
    grouped = {}
    doc: dict
    for doc in db:
        key = doc.get(by)
        if not key:
            print("There is no field {} in {}".format(by, id_key(doc)))
        elif key not in grouped:
            grouped[key] = [doc]
        else:
            grouped[key].append(doc)
    return grouped


def get_pi_id(rc):
    """
    Gets the database id of the group PI

    Parameters
    ----------
    rc: runcontrol object
      The runcontrol object.  It must contain the 'groups' and 'people'
      collections in the needed databases

    Returns
    -------
    The database '_id' of the group PI

    """
    groupiter = list(all_docs_from_collection(rc.client, "groups"))
    peoplecoll = all_docs_from_collection(rc.client, "people")
    pi_ref = [i.get("pi_name") for i in groupiter if
              i.get("name").casefold() == rc.groupname.casefold()]
    pi = fuzzy_retrieval(peoplecoll, ["_id", "aka", "name"], pi_ref[0])
    return pi.get("_id")


def group_member_ids(ppl_coll, grpname):
    """Get a list of all group member ids

    Parameters
    ----------
    ppl_coll: collection (list of dicts)
        The people collection that should contain the group members
    grp: string
        The id of the group in groups.yml

    Returns
    -------
    set:
        The set of ids of the people in the group

    Notes
    -----
    - Groups that are being tracked are listed in the groups.yml collection
    with a name and an id.
    - People are in a group during an educational or employment period.
    - To assign a person to a tracked group during one such period, add
    a "group" key to that education/employment item with a value
    that is the group id.
    - This function takes the group id that is passed and searches
    the people collection for all people that have been
    assigned to that group in some period of time and returns a list of
    """
    grpmembers = set()
    for person in ppl_coll:
        for k in ["education", "employment"]:
            for position in person.get(k, {}):
                if position.get("group", None) == grpname:
                    grpmembers.add(person["_id"])
    return grpmembers


def fragment_retrieval(coll, fields, fragment, case_sensitive = False):
    """Retrieves a list of all documents from the collection where the fragment
    appears in any one of the given fields

    Parameters
    ----------
    coll: generator
        The collection containing the documents
    fields: iterable
        The fields of each document to check for the fragment
    fragment:
       The value to compare against to find the documents of interest
    case_sensitive: Bool
        When true will match case (Default = False)

    Returns
    -------
    list:
        A list of documents (that are dicts)

    Examples
    --------
    >>> fragment_retrieval(people, ['aka', 'name'], 'pi_name', case_sensitive = False)

    This would get all people for which either the alias or the name included
    the substring ``pi_name``.

    """

    ret_list = []
    for doc in coll:
        returns = []
        for k in fields:
            ret = doc.get(k, [])
            if not isinstance(ret, list):
                ret = [ret]
            returns.extend(ret)
        if not case_sensitive:
            returns = [reti.lower() for reti in returns if
                       isinstance(reti, str)]
            if isinstance(fragment, str):
                for item in frozenset(returns):
                    if fragment.lower() in item:
                        ret_list.append(doc)
                        break
        else:
            for item in frozenset(returns):
                if fragment in item:
                    ret_list.append(doc)
                    break
    return ret_list


def get_id_from_name(coll, name):
    person = fuzzy_retrieval(coll,["name", "aka", "_id"], name,
                             case_sensitive=False)
    if person:
        return person["_id"]
    else:
        return None


def is_fully_appointed(person, begin_date, end_date):
    """Checks if a collection of appointments for a person is valid and fully loaded
        for a given interval of time

        Parameters
        ----------
        person: dict
            The person whose appointments need to be checked
        begin_date: datetime, string, optional
            The start date of the interval of time to check appointments for
        end_date: datetime, string, optional
            The end date of the interval of time to check appointments for

        Returns
        -------
        bool:
            True if the person is fully appointed and False if not

        Examples
        --------
        >>> appts = [{"begin_year": 2017, "begin_month": 6, "begin_day": 1, "end_year": 2017, "end_month": 6,\
         "end_day": 15, "grant": "grant1", "loading": 1.0, "type": "pd", }, {"begin_year": 2017, "begin_month": 6, \
         "begin_day": 20,  "end_year": 2017,  "end_month": 6, "end_day": 30, "grant": "grant2", "loading": 1.0, \
         "type": "pd",} ]
        >>> aejaz = {"name": "Adiba Ejaz", "_id": "aejaz", "appointments": appts}
        >>> is_fully_appointed(aejaz, "2017-06-01", "2017-06-30")

        In this case, we have an invalid loading from 2017-06-16 to 2017-06-19 hence it would return False and
        print "appointment gap for aejaz from 2017-06-16 to 2017-06-19".
        """

    if not person.get('appointments'):
        print("No appointments defined for this person")
        return False
    status = True
    appts = person.get('appointments')
    if begin_date > end_date:
        raise ValueError("invalid begin and end dates")
    if isinstance(begin_date, str):
        begin_date = date_parser.parse(begin_date).date()
    if isinstance(end_date, str):
        end_date = date_parser.parse(end_date).date()
    timespan = end_date - begin_date
    good_period, start_gap = True, None
    for x in range(timespan.days + 1):
        day_loading = 0.0
        day = begin_date + relativedelta(days=x)
        for appt in appts:
            if is_current(appts[appt], now=day):
                day_loading += appts[appt].get("loading")
        if day_loading > 1.0 or day_loading < 1.0:
            status = False
            if good_period:
                start_gap = day
                good_period = False
        else:
            if not good_period:
                print("WARNING: appointment gap for {} from {} to {}".format(person.get('_id'),
                                                                     str(start_gap), str(day - relativedelta(days=1))))
            good_period = True
        if x == timespan.days and not good_period:
            if day != start_gap:
                print("WARNING: appointment gap for {} from {} to {}".format(person.get('_id'),
                                                                     str(start_gap), str(day - relativedelta(days=1))))
            else:
                print("WARNING: appointment gap for {} on {}".format(person.get('_id'), str(day)))
    return status

def key_value_pair_filter(collection, arguments):
    """Retrieves a list of all documents from the collection where the fragment
        appears in any one of the given fields

        Parameters
        ----------
        collection: generator
            The collection containing the documents
        arguments: list
            The name of the fields to look for and their accompanying substring

        Returns
        -------
        generator:
            The collection containing the elements that satisfy the search criteria

        Examples
        --------
        >>> key_value_pair_filter(people, ['name', 'ab', 'position', 'professor'])

        This would get all people for which their name contains the string 'ab'
        and whose position is professor and return them

        """

    if len(arguments) % 2 != 0:
        raise RuntimeError("Error: Number of keys and values do not match")
    elements = collection
    for i in range(0, len(arguments) - 1, 2):
        elements = fragment_retrieval(elements, [arguments[i]], arguments[i + 1])
    return elements


def collection_str(collection, keys=None):
    """Retrieves a list of all documents from the collection where the fragment
        appears in any one of the given fields

        Parameters
        ----------
        collection: generator
            The collection containing the documents
        keys: list, optional
            The name of the fields to return from the search. Defaults to none in which case only the id is returned

        Returns
        -------
        str:
            A str of all the values
    """
    if not keys:
        keys = ['_id']
    if '_id' not in keys:
        keys.insert(0, '_id')
    output = ""
    for doc in collection:
        for key in keys:
            if key == '_id':
                output += (doc.get(key) + '    ')
            else:
                output += ('{}: {}    '.format(key, doc.get(key)))
        output += '\n'
    return output


def search_collection(collection, arguments, keys=None):
    """Retrieves a list of all documents from the collection where the fragment
        appears in any one of the given fields

        Parameters
        ----------
        collection: generator
            The collection containing the documents
        arguments: list
            The name of the fields to look for and their accompanying substring
        keys: list, optional
            The name of the fields to return from the search. Defaults to none in which case only the id is returned

        Returns
        -------
        generator:
            The collection containing the elements that satisfy the search criteria

        Examples
        --------
        >>> search_collection(people, ['name', 'ab', 'position', 'professor'], ['_id', 'name'])

        This would get all people for which their name contains the string 'ab'
        and whose position is professor. It would return the name and id of the
        valid entries

        """
    collection = key_value_pair_filter(collection, arguments)
    return collection_str(collection, keys)


def collect_appts(ppl_coll, filter_key=None, filter_value=None, begin_date=None, end_date=None):
    """
    Retrieves a list of all the appointments on the given grant(s) in the given interval of time for each person in the
    given people collection.

    Parameters
    ----------
    ppl_coll: collection (list of dicts)
        The people collection containing persons with appointments
    filter_key: string, list, optional
        The key we want to filter appointments by
    filter_value: string, int, float, list, optional
        The values for each key that we want to filter appointments by
    begin_date: string, datetime, optional
        The start date for the interval in which we want to collect appointments
    end_date: string, datetime, optional
        The start date for the interval in which we want to collect appointments

    Returns
    -------
    list:
        a list of all appointments in the people collection that satisfy the provided conditions (if any)

    Examples
    --------
    >>> collect_appts(people,filter_key=['grant', 'status'], filter_value=['mrsec14', 'finalized'], \
    begin_date= '2020-09-01', end_date='2020-12-31')
    This would return all appointments on the grant 'mrsec14' with status 'finalized' that are valid on/during any
    dates from 2020-09-01 to 2020-12-31
    >>> collect_appts(people, filter_key=['grant', 'grant'], filter_value=['mrsec14', 'dmref19'])
    This would return all appointments on the grants 'mrsec14' and 'dmref19' irrespective of their dates.
    """

    if bool(begin_date) ^ bool(end_date):
        raise RuntimeError("please enter both begin date and end date or neither")
    filter_key = [filter_key] if not isinstance(filter_key, list) else filter_key
    filter_value = [filter_value] if not isinstance(filter_value, list) else filter_value
    if (bool(filter_key)^bool(filter_value)) or (filter_key and filter_value and len(filter_key) != len(filter_value)):
        raise RuntimeError("number of filter keys and filter values do not match")
    begin_date = date_parser.parse(begin_date).date() if isinstance(begin_date, str) else begin_date
    end_date = date_parser.parse(end_date).date() if isinstance(end_date, str) else end_date
    timespan = 0
    if begin_date:
        timespan = end_date - begin_date
        if timespan.days < 0:
            raise ValueError("begin date is after end date")
    appts = []
    for p in ppl_coll:
        p_appts = p.get('appointments')
        if not p_appts:
            continue
        for a in p_appts:
            if filter_key:
                if all(p_appts[a].get(filter_key[x]) == filter_value[x] for x in range(len(filter_key))):
                    if begin_date:
                        for y in range(timespan.days + 1):
                            day = begin_date + relativedelta(days=y)
                            if is_current(p_appts[a], now=day):
                                appts.append(p_appts[a])
                                appts[-1].update({'person': p.get('_id'), '_id': a})
                                break
                    else:
                        appts.append(p_appts[a])
                        appts[-1].update({'person': p.get('_id'), '_id': a})
            elif timespan:
                    for y in range(timespan.days + 1):
                        day = begin_date + relativedelta(days=y)
                        if is_current(p_appts[a], now=day):
                            appts.append(p_appts[a])
                            appts[-1].update({'person': p.get('_id'), '_id': a})
                            break
            else:
                appts.append(p_appts[a])
                appts[-1].update({'person': p.get('_id'), '_id': a})
    return appts


def grant_burn(grant, appts, begin_date=None, end_date=None):
    """
    Retrieves the total burn of a grant over an interval of time by integrating over all appointments
    made on the grant.

    Parameters
    ----------
    grant: dict
        The grant object whose burn needs to be retrieved
    appts: collection (list of dicts), dict
        The collection of appointments made on assorted grants
    begin_date: datetime, string, optional
        The start date of the interval of time to retrieve the grant burn for, either a date object or a string
        in YYYY-MM-DD format. Defaults to the begin_date of the grant.
    end_date: datetime, string, optional
        The end date of the interval of time to retrieve the grant burn for, either a date object or a string
        in YYYY-MM-DD format. Defaults to the end_date of the grant.

    Returns
    -------
    list:
        A list of dictionaries, each containing the date and the corresponding student_days, postdoc_days and
        ss_days on that date
    """

    if not grant.get('budget'):
        raise ValueError("{} has no specified budget".format(grant.get('_id')))
    if bool(begin_date) ^ bool(end_date):
        raise RuntimeError("please enter both begin date and end date or neither")
    grant_begin, grant_end = get_dates(grant)['begin_date'], get_dates(grant)['end_date']
    begin_date = grant_begin if not begin_date else begin_date
    begin_date = date_parser.parse(begin_date).date() if isinstance(begin_date, str) else begin_date
    end_date = grant_end if not end_date else end_date
    end_date = date_parser.parse(end_date).date() if isinstance(end_date, str) else end_date
    if begin_date > end_date:
        raise ValueError("begin date is after end date")
    timespan, grad_val, pd_val, ss_val = grant_end - grant_begin, 0.0, 0.0, 0.0
    grant_amounts = ["values for grant {} from {} to {}:".format(grant.get('_id'), str(begin_date), str(end_date))]
    for b in grant.get('budget'):
        if b.get('student_months'):
            grad_val += b.get('student_months') * 30.5
        if b.get('postdoc_months'):
            pd_val += b.get('postdoc_months') * 30.5
        if b.get('ss_months'):
            ss_val += b.get('ss_months') * 30.5
    if isinstance(appts, dict):
        appts = collect_appts([{"appointments": appts}])
    for x in range(timespan.days + 1):
        day = grant_begin + relativedelta(days=x)
        for a in appts:
            if (a.get('grant') == grant.get('_id') or a.get('grant') == grant.get('alias')) and is_current(a,now=day):
                if a.get('type') == 'gra':
                    grad_val -= a.get('loading') * 1
                elif a.get('type') == 'pd':
                    pd_val -= a.get('loading') * 1
                elif a.get('type') == 'ss':
                    ss_val -= a.get('loading') * 1
                else:
                    if a.get('person'):
                        raise ValueError("invalid  type {} for appointment {} of {}".format(a.get('type'), a.get('_id'),
                                                                                                    a.get('person')))
                    else:
                        raise ValueError("invalid  type for appointment {}".format(a))
        if begin_date <= day <= end_date:
            gvals = {"date": str(day), "student_days": round(grad_val, 2), "postdoc_days": round(pd_val, 2),
                   "ss_days": round(ss_val, 2)}
            grant_amounts.append(gvals)
    return grant_amounts
