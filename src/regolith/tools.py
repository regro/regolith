"""Misc.

regolith tools.
"""

import email.utils
import os
import pathlib
import platform
import re
import sys
import uuid
from copy import copy, deepcopy
from datetime import date, datetime
from urllib.parse import urlparse

import requests
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from habanero import Crossref
from requests.exceptions import ConnectionError, HTTPError

from regolith.dates import date_to_float, get_dates, is_current, month_to_int
from regolith.schemas import alloweds
from regolith.sorters import doc_date_key_high, ene_date_key, id_key

try:
    from bibtexparser.bibdatabase import BibDatabase
    from bibtexparser.bwriter import BibTexWriter

    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

LATEX_OPTS = ["-halt-on-error", "-file-line-error"]

if sys.version_info[0] >= 3:
    string_types = (str, bytes)
    unicode_type = str
else:
    pass

DEFAULT_ENCODING = sys.getdefaultencoding()

ON_WINDOWS = platform.system() == "Windows"
ON_MAC = platform.system() == "Darwin"
ON_LINUX = platform.system() == "Linux"
ON_POSIX = os.name == "posix"

APPOINTMENTS_TYPES = alloweds.get("APPOINTMENTS_TYPES")
PRESENTATION_TYPES = alloweds.get("PRESENTATION_TYPES")
PRESENTATION_STATI = alloweds.get("PRESENTATION_STATI")
OPTIONAL_KEYS_INSTITUTIONS = alloweds.get("OPTIONAL_KEYS_INSTITUTIONS")


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
    """Decorator for returning the object if cond is true and a backup
    if cond is false."""

    def dec(obj):
        return obj if cond else backup

    return dec


def all_docs_from_collection(client, collname, copy=True):
    """Yield all entries in all collections of a given name in a given
    database."""
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


def filter_publications(
    citations,
    authors,
    reverse=False,
    bold=True,
    since=None,
    before=None,
    ackno=False,
    grants=None,
    facilities=None,
):
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
    ackno : bool
        Move the acknowledgement statement to note so that it is displayed in the
        publication list
    grants : string or list of strings, optional
        The grant or grants to filter over
    facilities: string, optional
        The facilities to filter over
    """
    pubs_by_date, pubs_by_grant, pubs_by_facilities = [], [], []
    if not isinstance(citations, list):
        citations = list(citations)
    cites = deepcopy(citations)
    for pub in cites:
        if len((set(pub.get("author", [])) | set(pub.get("editor", []))) & authors) == 0:
            continue
        if bold:
            bold_self = []
            for a in pub["author"]:
                if a in authors:
                    bold_self.append("\\textbf{" + a + "}")
                else:
                    bold_self.append(a)
            pub["author"] = bold_self
        if ackno:
            if pub.get("ackno"):
                pub["note"] = latex_safe(
                    f"\\newline\\newline\\noindent "
                    f"Acknowledgement:\\newline\\noindent "
                    f"{pub.get('ackno')}\\newline\\newline\\noindent "
                )
        if since:
            bibdate = date(int(pub.get("year")), month_to_int(pub.get("month", 12)), int(pub.get("day", 28)))
            if bibdate > since:
                if before:
                    if bibdate < before:
                        pubs_by_date.append(pub)
                else:
                    pubs_by_date.append(pub)
        else:
            pubs_by_date.append(pub)

        if grants:
            if isinstance(grants, str):
                grants = [grants]
            for grant in grants:
                if grant in pub.get("grant", ""):
                    pubs_by_grant.append(pub)
        else:
            pubs_by_grant.append(pub)

        if facilities:
            if facilities in pub.get("facility", ""):
                pubs_by_facilities.append(pub)
        else:
            pubs_by_facilities.append(pub)

    pubs = [x for x in pubs_by_date if x in pubs_by_grant]
    pubs = [x for x in pubs if x in pubs_by_facilities]
    pubs.sort(key=doc_date_key_high, reverse=reverse)
    return pubs


def filter_projects(projects, people, reverse=False, active=True, group=None, ptype=None):
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
    active : bool, optional
        Only active projects will be returned if True. Only non-active projects
        will be returned if False.  Run twice with trae and false to get all
        projects.  defaults to True
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
        if active:
            if not proj.get("active"):
                continue
        else:
            if proj.get("active"):
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
    """Filter grants by those involved.

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
        grant_dates = get_dates(grant)
        datenames = ["begin_", "end_"]
        for datename in datenames:
            grant[f"{datename}year"] = grant_dates[f"{datename}date"].year
            grant[f"{datename}month"] = grant_dates[f"{datename}date"].month
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
                grant["pi"] = [x for x in grant["team"] if x["position"].lower() == "pi"][0]
                grant["me"] = person
        grants.append(grant)
    grants.sort(key=ene_date_key, reverse=reverse)
    return grants, total_amount, subaward_amount


def filter_employment_for_advisees(peoplecoll, begin_period, status, advisor, now=None):
    """Filter people to get advisees since begin_period.

    Parameters
    ----------
    people: list of dicts
        The people collection
    begin_period: date
        Only select advisees who were active after this date (i.e., their end date
        is after begin_period
    status: str
        the status of the person in the group to filter for,  e.g., ms, phd, postdoc
    """
    people = deepcopy(peoplecoll)
    if not now:
        now = date.today()
    advisees = []
    if isinstance(begin_period, str):
        begin_period = date_parser.parse(begin_period).date()
    for p in people:
        for i in p.get("employment", []):
            if i.get("advisor", "no advisor") == advisor:
                if i.get("status") == status:
                    emp_dates = get_dates(i)
                    begin_date = emp_dates.get("begin_date")
                    end_date = emp_dates.get("end_date")
                    if not end_date:
                        end_date = now
                    if end_date >= begin_period:
                        p["role"] = i.get("position")
                        p["begin_year"] = begin_date.year
                        if not emp_dates.get("end_date"):
                            p["end_year"] = "present"
                        else:
                            p["end_year"] = end_date.year
                        p["status"] = status
                        p["position"] = i.get("position")
                        p["end_date"] = end_date
                        advisees.append(p)
                        advisees.sort(key=lambda x: x["end_date"], reverse=True)
    return advisees


def filter_service(p, begin_period, type):
    myservice = []
    for i in p.get("service", []):
        if i.get("type") == type:
            i_dates = get_dates(i)
            end_date = i_dates.get("end_date", i_dates.get("date"))
            if not end_date:
                end_date = date.today()
            if end_date >= begin_period:
                myservice.append(i)
    return myservice


def filter_committees(person, begin_period, type):
    mycommittees = []
    for committee in person.get("committees", []):
        if committee.get("type") == type:
            committee_dates = get_dates(committee)
            end_date = committee_dates.get("end_date", committee_dates.get("date"))
            if not end_date:
                end_date = date.today()
            if end_date >= begin_period:
                mycommittees.append(committee)
    return mycommittees


def filter_facilities(people, begin_period, type, verbose=False):
    facilities = []
    for p in people:
        myfacility = []
        svc = copy(p.get("facilities", []))
        for i in svc:
            if i.get("type") == type:
                if i.get("year"):
                    end_year = i.get("year")
                elif i.get("end_year"):
                    end_year = i.get("end_year")
                else:
                    end_year = date.today().year
                end_date = date(end_year, i.get("end_month", 12), i.get("end_day", 28))
                if end_date >= begin_period:
                    if not i.get("month"):
                        month = i.get("begin_month", 0)
                        i["month"] = SHORT_MONTH_NAMES[month_to_int(month)]
                    else:
                        i["month"] = SHORT_MONTH_NAMES[month_to_int(i["month"])]
                    myfacility.append(i)
        if verbose:
            print("p['facilities'] = {}".format(myfacility))
        p["facilities"] = myfacility
        if len(p["facilities"]) > 0:
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
                for inv in i["inventors"]
            ]
            person = fuzzy_retrieval(
                people,
                ["aka", "name", "_id"],
                target,
                case_sensitive=False,
            )
            if person in inventors:
                if i.get("end_year"):
                    end_year = i.get("end_year")
                else:
                    end_year = date.today().year
                end_date = date(end_year, i.get("end_month", 12), i.get("end_day", 28))
                if since:
                    if end_date >= since:
                        if not i.get("month"):
                            month = i.get("begin_month", 0)
                            i["month"] = SHORT_MONTH_NAMES[month_to_int(month)]
                        else:
                            i["month"] = SHORT_MONTH_NAMES[month_to_int(i["month"])]

                        events = [
                            event
                            for event in i["events"]
                            if date(event["year"], event["month"], event.get("day", 28)) > since
                        ]
                        events = sorted(
                            events, key=lambda event: date(event["year"], event["month"], event.get("day", 28))
                        )
                        i["events"] = events
                        patents.append(i)
                else:
                    events = [event for event in i["events"]]
                    events = sorted(events, key=lambda event: date(event["year"], event["month"], 28))
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
                for inv in i["inventors"]
            ]
            person = fuzzy_retrieval(
                people,
                ["aka", "name", "_id"],
                target,
                case_sensitive=False,
            )
            if person in inventors:
                if i.get("end_year"):
                    end_year = i.get("end_year")
                else:
                    end_year = date.today().year
                end_date = date(end_year, i.get("end_month", 12), i.get("end_day", 28))
                if since:
                    if end_date >= since:
                        if not i.get("month"):
                            month = i.get("begin_month", 0)
                            i["month"] = SHORT_MONTH_NAMES[month_to_int(month)]
                        else:
                            i["month"] = SHORT_MONTH_NAMES[month_to_int(i["month"])]
                        total = sum([event.get("amount") for event in i["events"]])
                        i["total_amount"] = total
                        events = [
                            event
                            for event in i["events"]
                            if date(event["year"], event["month"], event.get("day", 28)) > since
                        ]
                        events = sorted(
                            events, key=lambda event: date(event["year"], event["month"], event.get("day", 28))
                        )
                        i["events"] = events
                        licenses.append(i)
                else:
                    total = sum([event.get("amount") for event in events])
                    i["total_amount"] = total
                    events = [event for event in i["events"]]
                    events = sorted(events, key=lambda event: date(event["year"], event["month"], 28))
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
                idates = get_dates(i)
                if idates["end_date"] >= begin_period:
                    usedate = idates.get("begin_date", idates.get("date"))
                    i["year"] = usedate.year
                    i["month"] = SHORT_MONTH_NAMES[month_to_int(usedate.month)]
                    myactivity.append(i)
        p["activities"] = myactivity
        if len(p["activities"]) > 0:
            activities.append(p)
    return activities


def filter_presentations(
    people, presentations, institutions, target, types=None, since=None, before=None, statuses=None
):
    f"""
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
      {*PRESENTATION_TYPES, }
    since: date.  Optional, default is None
        The begin date to filter from
    before: date. Optional, default is None
        The end date to filter for.  None does not apply this filter
    statuses: list of str.  Optional. Default is accepted
      The list of statuses to filter for.  Allowed statuses are
        {PRESENTATION_STATI}

    Returns
    -------
    list of presentation documents

    """
    if not types:
        types = ["all"]
    if not statuses:
        statuses = ["accepted"]
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
        authorids = [author["_id"] if author is not None else author for author in authors]
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
            if get_dates(pres).get("date"):
                presdate = get_dates(pres).get("date")
            else:
                presdate = get_dates(pres).get("begin_date")
            if presdate > since:
                fourthclean.append(pres)
    else:
        fourthclean = thirdclean
    if before:
        for pres in fourthclean:
            if get_dates(pres).get("date"):
                presdate = get_dates(pres).get("date")
            else:
                presdate = get_dates(pres).get("begin_date")
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
            (
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
            )
            for author in pauthors
        ]
        authorlist = ", ".join(pres["authors"])
        pres["authors"] = authorlist
        if get_dates(pres).get("date"):
            presdate = get_dates(pres).get("date")
        else:
            presdate = get_dates(pres).get("begin_date")
        pres["begin_month"] = presdate.month
        pres["begin_year"] = presdate.year
        pres["begin_day"] = presdate.day
        end_date = get_dates(pres).get("end_date")
        if end_date:
            pres["end_day"] = end_date.day
        pres["date"] = presdate
        for day in ["begin_", "end_", ""]:
            try:
                pres["{}day_suffix".format(day)] = number_suffix(get_dates(pres).get(f"{day}date").day)
            except AttributeError:
                print(f"presentation {pres.get('_id')} has no {day}date")
        if "institution" in pres:
            inst = {"institution": pres.get("institution"), "department": pres.get("department")}
            dereference_institution(inst, institutions)
            pres["institution"] = {
                "name": inst.get("institution", ""),
                "city": inst.get("city"),
                "state": inst.get("state"),
                "country": inst.get("country"),
            }
            pres["department"] = {"name": inst.get("department")}
    if len(presclean) > 0:
        presclean = sorted(
            presclean,
            key=lambda k: k.get("date", None),
            reverse=True,
        )
    return presclean


def filter_software(people, software, institutions, target, types=None, since=None, before=None, statuses=None):
    """Filters presentations for different types and date ranges.

    Parameters
    ----------
    people: iterable of dicts
      The people collection
    software: iterable of dicts
      The software collection
    institutions: iterable of dicts
      The institutions collection
    target: str
      The id of the person you will build the list for
    types: list of strings.  Optional, default = all
      The types to filter for.  Allowed types are release_types.
    since: date.  Optional, default is None
        The begin date to filter from
    before: date. Optional, default is None
        The end date to filter for.  None does not apply this filter
    statuses: list of str.  Optional. Default is active.
      The list of statuses to filter for.

    Returns
    -------
    list of software documents
    """
    if not types:
        types = ["all"]
    if not statuses:
        statuses = ["active"]
    software = deepcopy(software)

    firstclean = list()
    secondclean = list()
    thirdclean = list()
    fourthclean = list()
    presclean = list()

    # build the filtered collection
    # only list the talk if the group member is an author
    for sof in software:
        pauthors = sof["authors"]
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
        authorids = [author["_id"] if author is not None else author for author in authors]
        if target in authorids:
            firstclean.append(sof)
    # only list the presentation if it has status in statuses
    for sof in firstclean:
        if sof["status"] in statuses or "all" in statuses:
            secondclean.append(sof)
    # only list the presentation if it has type in types
    for sof in secondclean:
        if sof["type"] in types or "all" in types:
            thirdclean.append(sof)
    # if specified, only list presentations in specified date ranges
    if since:
        for sof in thirdclean:
            if get_dates(sof).get("date"):
                presdate = get_dates(sof).get("date")
            else:
                presdate = get_dates(sof).get("begin_date")
            if presdate > since:
                fourthclean.append(sof)
    else:
        fourthclean = thirdclean
    if before:
        for sof in fourthclean:
            if get_dates(sof).get("date"):
                presdate = get_dates(sof).get("date")
            else:
                presdate = get_dates(sof).get("begin_date")
            if presdate < before:
                presclean.append(sof)
    else:
        presclean = fourthclean

    # build author list
    for sof in presclean:
        pauthors = sof["authors"]
        if isinstance(pauthors, str):
            pauthors = [pauthors]
        sof["authors"] = [
            (
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
            )
            for author in pauthors
        ]
        authorlist = ", ".join(sof["authors"])
        sof["authors"] = authorlist
        if get_dates(sof).get("date"):
            presdate = get_dates(sof).get("date")
        else:
            presdate = get_dates(sof).get("begin_date")
        sof["begin_month"] = presdate.month
        sof["begin_year"] = presdate.year
        sof["begin_day"] = presdate.day
        end_date = get_dates(sof).get("end_date")
        if end_date:
            sof["end_day"] = end_date.day
        sof["date"] = presdate
        for day in ["begin_", "end_", ""]:
            try:
                sof["{}day_suffix".format(day)] = number_suffix(get_dates(sof).get(f"{day}date").day)
            except AttributeError:
                print(f"presentation {sof.get('_id')} has no {day}date")
        if "institution" in sof:
            inst = {"institution": sof.get("institution"), "department": sof.get("department")}
            dereference_institution(inst, institutions)
            sof["institution"] = {
                "name": inst.get("institution", ""),
                "city": inst.get("city"),
                "state": inst.get("state"),
                "country": inst.get("country"),
            }
            sof["department"] = {"name": inst.get("department")}
    if len(presclean) > 0:
        presclean = sorted(
            presclean,
            key=lambda k: k.get("date", None),
            reverse=True,
        )
    return presclean


def awards_grants_honors(person, target_name, funding=True, service_types=None):
    """Make sorted awards grants and honors list.

    Parameters
    ----------
    person : dict
        The person entry
    """
    if not service_types:
        service_types = ["profession"]
    aghs = []
    if funding:
        if person.get("funding"):
            for fund in person.get("funding", ()):
                d = {
                    "description": "{0} ({1}{2:,})".format(
                        latex_safe(fund["name"]),
                        fund.get("currency", "$").replace("$", r"\$"),
                        fund["value"],
                    ),
                    "year": fund["year"],
                    "_key": date_to_float(fund["year"], fund.get("month", 0)),
                }
                aghs.append(d)
    target = person.get(target_name, [])
    for fund in target:
        if target_name != "service" or target_name == "service" and fund.get("type") in service_types:
            d = {"description": latex_safe(fund["name"])}
            if "year" in fund:
                fund["date"] = date(fund["year"], 1, 1)
                del fund["year"]
            x_dates = get_dates(fund)
            if x_dates.get("date"):
                d.update(
                    {
                        "year": x_dates["date"].year,
                        "_key": date_to_float(x_dates["date"].year, x_dates["date"].month),
                    }
                )
            elif x_dates.get("begin_date") and x_dates.get("end_date"):
                d.update(
                    {
                        "year": "{}-{}".format(x_dates["begin_date"].year, x_dates["end_date"].year),
                        "_key": date_to_float(x_dates["begin_date"].year, x_dates["begin_date"].month),
                    }
                )
            elif x_dates.get("begin_date"):
                d.update(
                    {
                        "year": "{}".format(x_dates["begin_date"].year),
                        "_key": date_to_float(x_dates["begin_date"].year, x_dates["begin_date"].month),
                    }
                )
            aghs.append(d)
    aghs.sort(key=(lambda x: x.get("_key", 0.0)), reverse=True)
    return aghs


def awards(
    p,
    since=None,
    before=None,
):
    """Make sorted awards and honors.

    Parameters
    ----------
    p : dict
        The person entry
    since : date.  Optional, default is None
        The begin date to filter from
    before : date. Optional, default is None
        The end date to filter for.  None does not apply this filter
    """
    if not since:
        since = date(1500, 1, 1)
    a = []
    for x in p.get("honors", []):
        if "year" in x:
            if date(x.get("year"), 12, 31) > since:
                d = {
                    "description": latex_safe(x["name"]),
                    "year": x["year"],
                    "_key": date_to_float(x["year"], x.get("month", 0)),
                }
                a.append(d)
        elif "begin_year" in x and "end_year" in x:
            if date(x.get("begin_year", 12, 31)) > since:
                d = {
                    "description": latex_safe(x["name"]),
                    "year": "{}-{}".format(x["begin_year"], x["end_year"]),
                    "_key": date_to_float(x["begin_year"], x.get("month", 0)),
                }
                a.append(d)
        elif "begin_year" in x:
            if date(x.get("begin_year"), 12, 31) > since:
                d = {
                    "description": latex_safe(x["name"]),
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
    """Make string latex safe.

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
                end=(latex_safe(s[url_search.end() :])),
                wrapper=wrapper,
                s=latex_safe_url(s[url_search.start() : url_search.end()]),
            )
            return url
    return s.replace("&", r"\&").replace("$", r"\$").replace("#", r"\#").replace("_", r"\_")


def make_bibtex_file(pubs, pid, person_dir="."):
    """Make a bibtex file given the publications.

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
        if ent.get("doi") == "tbd":
            del ent["doi"]
        if ent.get("supplementary_info_urls"):
            ent.update({"supplementary_info_urls": ", ".join(ent.get("supplementary_info_urls"))})
        if isinstance(ent.get("editor"), list):
            for n in ["author", "editor"]:
                if n in ent:
                    ent[n] = " and ".join(ent[n])
        else:
            if "author" in ent:
                ent["author"] = " and ".join(ent["author"])
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
    """Get a specific document by one of its values.

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
    """Retrieve a document from the documents where value is compared
    against multiple potential sources.

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
            returns = [reti.lower() for reti in returns if isinstance(reti, str)]
            if isinstance(value, str):
                if value.lower() in frozenset(returns):
                    return doc
        else:
            if value in frozenset(returns):
                return doc


def number_suffix(number):
    """Returns the suffix that adjectivises a number (st, nd, rd, th)

    Parameters
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


def dereference_institution(input_record, institutions, verbose=False):
    """Tool for replacing placeholders for institutions with the actual
    institution data. Note that the replacement is done inplace.

    Parameters
    ----------
    input_record : dict
        The record to dereference
    institutions : iterable of dicts
        The institutions

    Returns
    -------
    nothing
    """
    inst = input_record.get("institution") or input_record.get("organization")
    if verbose:
        if not inst:
            print(f"WARNING: no institution or organization in entry: {input_record}")
            return
    db_inst = fuzzy_retrieval(institutions, ["name", "_id", "aka"], inst)
    if not db_inst:
        print(
            f"WARNING: {input_record.get('institution', input_record.get('organization', 'unknown'))} "
            "not found in institutions"
        )
        db_inst = {
            "name": input_record.get("institution", input_record.get("organization", "unknown")),
            "location": input_record.get(
                "location", f"{input_record.get('city', 'unknown')}, {input_record.get('state', 'unknown')}"
            ),
            "city": input_record.get("city", "unknown"),
            "country": input_record.get("country", "unknown"),
            "state": input_record.get("state", "unknown"),
            "departments": {
                input_record.get("department", "unknown"): {"name": input_record.get("department", "unknown")}
            },
        }
    if input_record.get("department") and not db_inst.get("departments"):
        if verbose:
            print(f"WARNING: no departments in {db_inst.get('_id')}. " f"{input_record.get('department')} sought")
        db_inst.update(
            {
                "departments": {
                    input_record.get("department", "unknown"): {"name": input_record.get("department", "unknown")}
                }
            }
        )
    if db_inst.get("country") == "USA":
        state_country = db_inst.get("state")
    else:
        state_country = db_inst.get("country")
    # now update the input record in place with what we have found
    input_record["location"] = db_inst.get("location", f"{db_inst['city']}, {state_country}")
    input_record["institution"] = db_inst["name"]
    input_record["organization"] = db_inst["name"]
    input_record["city"] = db_inst["city"]
    input_record["country"] = db_inst["country"]
    for optional_key in OPTIONAL_KEYS_INSTITUTIONS:
        if optional_key not in ["departments", "schools"]:
            if db_inst.get(optional_key):
                input_record[optional_key] = db_inst.get(optional_key)
    if "department" in input_record:
        for k, v in db_inst.get("departments").items():
            v.update({"_id": k})
        extracted_department = fuzzy_retrieval(
            db_inst["departments"].values(), ["name", "aka", "_id"], input_record["department"]
        )
        if extracted_department:
            input_record["department"] = extracted_department.get("name")
        else:
            input_record["department"] = input_record.get("department", "")
    else:
        input_record["department"] = "unknown"

    return


def merge_collections_all(a, b, target_id):
    """Merge two collections into a single merged collection.

    for keys that are in both collections, the value in b will be kept

    Parameters
    ----------
    a  the inferior collection (will lose values of shared keys)
    b  the superior collection (will keep values of shared keys)
    target_id  str  the name of the key used in b to dereference ids in a

    Returns
    -------
    the combined collection.  Note that it returns a collection containing
    all items from a and b with the items dereferenced in b merged with the
    dereferenced items in a.

    see also merge_intersection that returns collection that is just referenced
    in both

    Examples
    --------
    >>>  grants = merge_collections_all(self.gtx["proposals"], self.gtx["grants"], "proposal_id")

    This would merge all entries in the proposals collection with entries in the
    grants collection for which "_id" in proposals has the value of
    "proposal_id" in grants, returning also unchanged any other entries that are
    not linked.
    """
    intersect = merge_collections_intersect(a, b, target_id)
    for j in intersect:
        for i in b:
            if i.get("_id") == j.get("_id"):
                b.remove(i)
    for j in intersect:
        for i in a:
            if i.get("_id") == j.get(target_id):
                a.remove(i)
    bdis, adis = b, a
    return adis + intersect + bdis


def merge_collections_superior(a, b, target_id):
    """Merge two collections into a single merged collection.

    for keys that are in both collections, the value in b will be kept

    Parameters
    ----------
    a  the inferior collection (will lose values of shared keys)
    b  the superior collection (will keep values of shared keys)
    target_id  str  the name of the key used in b to dereference ids in a

    Returns
    -------
    the combined collection.  Note that it returns a collection containing
    all items from a and b with the items dereferenced in b merged with the
    dereferenced items in a.

    see also merge_intersection that returns collection that is just referenced
    in both

    Examples
    --------
    >>>  grants = merge_collections_all(self.gtx["proposals"], self.gtx["grants"], "proposal_id")

    This would merge all entries in the proposals collection with entries in the
    grants collection for which "_id" in proposals has the value of
    "proposal_id" in grants, returning also unchanged any other entries that are
    not linked.
    """
    intersect = merge_collections_intersect(a, b, target_id)
    b = list(b)
    for j in intersect:
        for i in b:
            if i.get("_id") == j.get("_id"):
                b.remove(i)
    bdis = b
    return intersect + bdis


def get_person_contact(name, people_coll, contacts_coll):
    """Return a person document if found in either people or contacts
    collections.

    If the person is found in the people collection this person is returned.  If
    not found in people but found in contacts, the person found in contacts is
    returned.  If the person is not found in either collection, None is returned

    Parameters
    ----------
    name: str
      The name or id of the person to look for
    people_coll: collection (list of dicts)
      The people collection
    contacts_coll: collection (list of dicts)
      The contacts collection

    Returns
    -------
    person: dict
      The found person document
    """
    people_person = fuzzy_retrieval(
        people_coll,
        ["aka", "name", "_id"],
        name,
        case_sensitive=False,
    )
    contacts_person = fuzzy_retrieval(
        contacts_coll,
        ["aka", "name", "_id"],
        name,
        case_sensitive=False,
    )
    if people_person:
        return people_person
    elif contacts_person:
        return contacts_person
    else:
        return None


def merge_collections_intersect(a, b, target_id):
    """Merge two collections such that just the intersection is
    returned.

    for shared keys that are in both collections, the value in b will be kept

    Parameters
    ----------
    a  the inferior collection (will lose values of shared keys)
    b  the superior collection (will keep values of shared keys)
    target_id  str  the name of the key used in b to dereference ids in a

    Returns
    -------
    the combined collection.  Note that it returns a collection only containing
    merged items from a and b that are dereferenced in b, i.e., the merged
    intercept.

    see also merge_collections_all that returns all items in a, b and the intersect
    and merge_collections_superior that returns all items in b and the intercept

    Examples
    --------
    >>>  grants = merge_collections_intesect(self.gtx["proposals"], self.gtx["grants"], "proposal_id")

    This would merge all entries in the proposals collection with entries in the
    grants collection for which "_id" in proposals has the value of
    "proposal_id" in grants, returning just those items that have the dereference
    """
    intersect = [{**j, **i} for j in a for i in b if j.get("_id") == i.get(target_id)]
    return intersect


def update_schemas(default_schema, user_schema):
    """Merging the user schema into the default schema recursively and
    return the merged schema. The default schema and user schema will
    not be modified during the merging.

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
        if (
            (key in updated_schema)
            and isinstance(updated_schema[key], dict)
            and isinstance(user_schema[key], dict)
        ):
            updated_schema[key] = update_schemas(updated_schema[key], user_schema[key])
        else:
            updated_schema[key] = user_schema[key]

    return updated_schema


def get_person(person_id, rc):
    """Get the person's name."""
    person_found = fuzzy_retrieval(
        all_docs_from_collection(rc.client, "people"), ["name", "aka", "_id"], person_id, case_sensitive=False
    )
    if person_found:
        return person_found
    person_found = fuzzy_retrieval(
        all_docs_from_collection(rc.client, "contacts"), ["name", "aka", "_id"], person_id, case_sensitive=False
    )
    if person_found:
        return person_found
    print("WARNING: {} missing from people and contacts. Check aka.".format(person_id))
    return None


def group(db, by):
    """Group the document in the database according to the value of the
    doc[by] in db.

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
    """Gets the database id of the group PI.

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
    pi_ref = [i.get("pi_name") for i in groupiter if i.get("name").casefold() == rc.groupname.casefold()]
    pi = fuzzy_retrieval(peoplecoll, ["_id", "aka", "name"], pi_ref[0])
    return pi.get("_id")


def group_member_ids(ppl_coll, grpname):
    """Get a list of all group member ids.

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


def group_member_employment_start_end(person, grpname):
    """Get start and end dates of group member employment.

    Parameters
    ----------
    person dict
      The person whose dates we want
    grpname
      The code for the group we want the dates of employment from

    Returns
    -------
    list of dicts
       The employment periods, with person id, begin and end dates
    """
    grpmember = []
    for k in ["employment"]:
        for position in person.get(k, {}):
            if position.get("group", None) == grpname:
                dates = get_dates(position)
                if not dates.get("end_date") and not position.get("permanent"):
                    raise RuntimeError(
                        "WARNING: {} has no end date in employment for {} starting {}".format(
                            person["_id"], grpname, dates.get("begin_date")
                        )
                    )
                grpmember.append(
                    {
                        "_id": person["_id"],
                        "begin_date": dates.get("begin_date"),
                        "end_date": dates.get("end_date"),
                        "permanent": position.get("permanent"),
                        "status": position.get("status"),
                    }
                )
    return grpmember


def compound_dict(doc, li):
    """Recursive function that collects all the strings from a document
    that is a dictionary.

    Parameters
    ----------
    doc dict
      The specific document we are traversing
    li
      The recursive list that holds all the strings

    Returns
    -------
    list of strings
       The strings that make up the nested attributes of this object
    """
    for key in doc:
        res = doc.get(key)
        if isinstance(res, str):
            li.append(res)
        elif isinstance(res, list):
            li.extend(compound_list(res, []))
        elif isinstance(res, dict):
            li.extend(compound_dict(res, []))
    return li


def compound_list(doc, li):
    """Recursive function that collects all the strings from a document
    that is a list.

    Parameters
    ----------
    doc list
      The specific document we are traversing
    li
      The recursive list that holds all the strings

    Returns
    -------
    list of strings
       The strings that make up the nested attributes of this list
    """
    for item in doc:
        if isinstance(item, dict):
            li.extend(compound_dict(item, []))
        elif isinstance(item, str):
            li.append(item)
        elif isinstance(item, list):
            li.extend(compound_list(item, []))
    return li


def fragment_retrieval(coll, fields, fragment, case_sensitive=False):
    """Retrieves a list of all documents from the collection where the
    fragment appears in any one of the given fields.

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
            ret = doc.get(k, None)
            if ret is not None:
                if isinstance(ret, list):
                    ret = compound_list(ret, [])
                elif isinstance(ret, dict):
                    ret = compound_dict(ret, [])
                elif isinstance(ret, bool):
                    ret = [str(ret)]
                else:
                    ret = [ret]

            else:
                ret = []
            returns.extend(ret)
        if not case_sensitive:
            returns = [reti.lower() for reti in returns if isinstance(reti, str)]
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
    person = fuzzy_retrieval(coll, ["name", "aka", "_id"], name, case_sensitive=False)
    if person:
        return person["_id"]
    else:
        return None


def is_fully_appointed(person, begin_date, end_date):
    """Checks if a collection of appointments for a person is valid and
    fully loaded for a given interval of time.

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
        >>> appts = [{"begin_year": 2017, "begin_month": 6, "begin_day": 1, "end_year": 2017,\
         "end_month": 6, "end_day": 15, "grant": "grant1", "loading": 1.0, "type": "pd", },\
        {"begin_year": 2017, "begin_month": 6, "begin_day": 20,  "end_year": 2017,  "end_month": 6,\
         "end_day": 30, "grant": "grant2", "loading": 1.0, "type": "pd",} ]
        >>> aejaz = {"name": "Adiba Ejaz", "_id": "aejaz", "appointments": appts}
        >>> is_fully_appointed(aejaz, "2017-06-01", "2017-06-30")

        In this case, we have an invalid loading from 2017-06-16 to 2017-06-19 hence it would return False and
        print "appointment gap for aejaz from 2017-06-16 to 2017-06-19".
    """

    if not person.get("appointments"):
        print("No appointments defined for this person")
        return False
    status = True
    appts = person.get("appointments")
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
                print(
                    "WARNING: appointment gap for {} from {} to {}".format(
                        person.get("_id"), str(start_gap), str(day - relativedelta(days=1))
                    )
                )
            good_period = True
        if x == timespan.days and not good_period:
            if day != start_gap:
                print(
                    "WARNING: appointment gap for {} from {} to {}".format(
                        person.get("_id"), str(start_gap), str(day)
                    )
                )
            else:
                print("WARNING: appointment gap for {} on {}".format(person.get("_id"), str(day)))
    return status


def key_value_pair_filter(collection, arguments):
    """Retrieves a list of all documents from the collection where the
    fragment appears in any one of the given fields.

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
    """Retrieves a list of all documents from the collection where the
    fragment appears in any one of the given fields.

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
        keys = ["_id"]
    if "_id" not in keys:
        keys.insert(0, "_id")
    output = ""
    for doc in collection:
        for key in keys:
            if key == "_id":
                output += doc.get(key) + "    "
            else:
                output += "{}: {}    ".format(key, doc.get(key))
        output += "\n"
    return output


def search_collection(collection, arguments, keys=None):
    """Retrieves a list of all documents from the collection where the
    fragment appears in any one of the given fields.

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
    """Retrieves a list of all the appointments on the given grant(s) in
    the given interval of time for each person in the given people
    collection.

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
    if (bool(filter_key) ^ bool(filter_value)) or (
        filter_key and filter_value and len(filter_key) != len(filter_value)
    ):
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
        p_appts = p.get("appointments")
        if not p_appts:
            continue
        for a in p_appts:
            if p_appts[a].get("type") not in APPOINTMENTS_TYPES:
                raise ValueError(
                    "invalid  type {} for appointment {} of {}".format(p_appts[a].get("type"), a, p.get("_id"))
                )
            if filter_key:
                if all(p_appts[a].get(filter_key[x]) == filter_value[x] for x in range(len(filter_key))):
                    if begin_date:
                        for y in range(timespan.days + 1):
                            day = begin_date + relativedelta(days=y)
                            if is_current(p_appts[a], now=day):
                                appts.append(p_appts[a])
                                appts[-1].update({"person": p.get("_id"), "_id": a})
                                break
                    else:
                        appts.append(p_appts[a])
                        appts[-1].update({"person": p.get("_id"), "_id": a})
            elif timespan:
                for y in range(timespan.days + 1):
                    day = begin_date + relativedelta(days=y)
                    if is_current(p_appts[a], now=day):
                        appts.append(p_appts[a])
                        appts[-1].update({"person": p.get("_id"), "_id": a})
                        break
            else:
                appts.append(p_appts[a])
                appts[-1].update({"person": p.get("_id"), "_id": a})

    return appts


def grant_burn(grant, appts, begin_date=None, end_date=None):
    """Retrieves the total burn of a grant over an interval of time by
    integrating over all appointments made on the grant.

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
    dict:
        A dictionaries whose keys are the dates and values are a dict containing the corresponding grant amounts
        on that date

    Examples
    --------
    >>> grant_burn(mygrant, myappts, begin_date="2020-09-01", end_date="2020-09-03")
    returns
    >>> {datetime.date(2020, 9, 1): {'student_days': 5.0, 'postdoc_days': 12.0, 'ss_days': 20.0}, \
         datetime.date(2020, 9, 2): {'student_days': 4.0, 'postdoc_days': 11.5, 'ss_days': 15.0}, \
         datetime.date(2020, 9, 3): {'student_days': 3.0, 'postdoc_days': 11.0, 'ss_days': 10.0}}
    """

    if not grant.get("budget"):
        raise ValueError("{} has no specified budget".format(grant.get("_id")))
    if bool(begin_date) ^ bool(end_date):
        raise RuntimeError("please enter both begin date and end date or neither")
    begin_date = date_parser.parse(begin_date).date() if isinstance(begin_date, str) else begin_date
    end_date = date_parser.parse(end_date).date() if isinstance(end_date, str) else end_date
    if isinstance(appts, dict):
        appts = collect_appts([{"appointments": appts}])
    grad_val, pd_val, ss_val = 0.0, 0.0, 0.0
    grant_amounts = {}
    budget_dates = get_dates(grant.get("budget")[0])
    budget_begin, budget_end = budget_dates["begin_date"], budget_dates["end_date"]
    for period in grant.get("budget"):
        period_dates = get_dates(period)
        period_begin, period_end = period_dates["begin_date"], period_dates["end_date"]
        budget_begin = period_begin if period_begin < budget_begin else budget_begin
        budget_end = period_end if period_end > budget_end else budget_end
        grad_val += (period.get("student_months", 0) - period.get("student_writeoff", 0)) * 30.5
        pd_val += (period.get("postdoc_months", 0) - period.get("postdoc_writeoff", 0)) * 30.5
        ss_val += (period.get("ss_months", 0) - period.get("ss_writeoff", 0)) * 30.5
        span = period_end - period_begin
        for x in range(span.days + 1):
            day = period_begin + relativedelta(days=x)
            for a in appts:
                if (a.get("grant") == grant.get("_id") or a.get("grant") == grant.get("alias")) and is_current(
                    a, now=day
                ):
                    if a.get("type") == "gra":
                        grad_val -= a.get("loading") * 1
                    elif a.get("type") == "pd":
                        pd_val -= a.get("loading") * 1
                    elif a.get("type") == "ss":
                        ss_val -= a.get("loading") * 1
            if (not begin_date) or (begin_date <= day <= end_date):
                gvals = {
                    "student_days": round(grad_val, 2),
                    "postdoc_days": round(pd_val, 2),
                    "ss_days": round(ss_val, 2),
                }
                grant_amounts.update({day: gvals})
    return grant_amounts


def validate_meeting(meeting, date):
    """Validates a meeting by checking is it has a journal club doi, a
    presentation link, and a presentation title. This function will
    return nothing is the meeting is valid, otherwise it will raise a
    ValueError.

    Parameters
    ----------
    meeting: dict
        The meeting object that needs to be validated
    date: datetime object
        The date we want to use to see if a meeting has happened or not
    """
    meeting_date = date_parser.parse(meeting.get("_id")[3:]).date()
    if meeting.get("journal_club") and meeting_date < date:
        if meeting.get("journal_club").get("doi").lower() == "tbd":
            raise ValueError(f'{meeting.get("_id")} does not have a journal club doi')
    if meeting_date < date and meeting.get("presentation").get("link").lower() == "tbd":
        raise ValueError(f'{meeting.get("_id")} does not have a presentation link')
    if meeting_date < date and meeting.get("presentation").get("title").lower() == "tbd":
        raise ValueError(f'{meeting.get("_id")} does not have a presentation title')


def print_task(task_list, stati, index=True):
    """Print tasks in a nice format.

    Parameters
    ----------
    task_list : list
      The list of tasks that will be printed.
    stati : list
      The list of task stati that will be printed
    index : bool Optional  Default is True
      The bool that can suppress printing the preamble of importance, days to due and index
    """
    for status in stati:
        if f"'status': '{status}'" in str(task_list):
            print(f"{status}:")
        for task in task_list:
            if index and task.get("status") != "finished":
                task["preamble"] = (
                    f"({task.get('importance')})({task.get('days_to_due')} days): "
                    f"({task.get('running_index', 0)}) "
                )
            elif index and task.get("status") == "finished":
                task["preamble"] = f"({task.get('end_date')}): " f"({task.get('running_index', 0)}) "
            else:
                task["preamble"] = ""
            if task.get("status") == status:
                print(
                    f"{task.get('preamble')}{task.get('description').strip()} "
                    f"({task.get('days_to_due')}|{task.get('importance')}|{str(task.get('duration'))}|"
                    f"{','.join(task.get('tags', []))}|{task.get('assigned_by')}|{task.get('uuid', [])[:6]})"
                )
                if task.get("notes"):
                    for note in task.get("notes"):
                        print(f"     - {note}")
    print("-" * 76)
    if stati == ["finished"]:
        print("(Completion Date): (Task number) Task (decreasing priority going up)")
    else:
        print("(importance)(days to due): (Task number) Task (decreasing priority going up)")
    print("-" * 76)
    if stati != ["finished"]:
        deadline_list = [task for task in task_list if task.get("deadline") and task.get("status") in stati]
        deadline_list.sort(key=lambda x: x.get("due_date"), reverse=True)
        for task in deadline_list:
            print(
                f"{task.get('due_date')}({task.get('days_to_due')} days): ({task.get('running_index', 0)}) "
                f"{task.get('description').strip()} ({task.get('days_to_due')}|{task.get('importance')}|"
                f"{str(task.get('duration'))}|{','.join(task.get('tags', []))}"
                f"|{task.get('assigned_by')}|{task.get('uuid')[:6]})"
            )
            if task.get("notes"):
                for note in task.get("notes"):
                    print(f"     - {note}")
        print(f"{'-' * 30}\nDeadlines:\n{'-' * 30}")
    return


def get_formatted_crossref_reference(doi):
    """Given a doi, return the full reference and the date of the
    reference from Crossref REST-API.

    parameters
    ----------
    doi str
      the doi of the digital object to pull from Crossref

    return
    ------
    ref str
      the nicely formatted reference including title
    ref_date datetime.date
      the date of the reference
    returns None None in the article cannot be found given the doi
    """

    cr = Crossref()
    try:
        article = cr.works(ids=doi)
    except HTTPError:
        print(f"WARNING: not able to find reference {doi} in Crossref")
        return None, None
    except ConnectionError:
        print(
            "WARNING: not able to connect to internet. To obtain publication information "
            "rerun when you have an internet connection"
        )
        return None, None

    authorlist = [
        f"{a['given'].strip()} {a['family'].strip()}" for a in article.get("message", {}).get("author", "")
    ]
    try:
        journal = article.get("message").get("short-container-title")[0]
    except IndexError:
        try:
            journal = article.get("message").get("container-title")[0]
        except IndexError:
            journal = ""
    if article.get("message").get("volume"):
        if len(authorlist) > 1:
            authorlist[-1] = "and {}".format(authorlist[-1])
        sauthorlist = ", ".join(authorlist)
        ref_date_list = article.get("message").get("issued").get("date-parts")
        ref = "{}, {}, {}, v. {}, pp. {}, ({}).".format(
            article.get("message").get("title")[0],
            sauthorlist,
            journal,
            article.get("message").get("volume"),
            article.get("message").get("page"),
            ref_date_list[0][0],
        )
    else:
        if len(authorlist) > 1:
            authorlist[-1] = "and {}".format(authorlist[-1])
        sauthorlist = ", ".join(authorlist)
        ref_date_list = article.get("message").get("issued").get("date-parts")
        ref = "{}, {}, {}, pp.{}, ({}).".format(
            article.get("message").get("title")[0],
            sauthorlist,
            journal,
            article.get("message").get("page"),
            ref_date_list[0][0],
        )
    ref_date_list = ref_date_list[0]
    ref_date_list += [6] * (3 - len(ref_date_list))
    ref_date = date(*ref_date_list)

    return ref, ref_date


def remove_duplicate_docs(coll, key):
    """Find all docs where the target key has the same value and remove
    duplicates.

    The doc found first will be kept and subsequent docs will be removed

    parameters
    ----------
    target iterable of dicts
      the list of documents
    key string
      the key that will be used to compare

    return
    ------
    The list of docs with duplicates (as described above) removed
    """
    values, newcoll = [], []
    for doc in coll:
        if doc.get(key) in values:
            continue
        elif not doc.get(key):
            raise RuntimeError(f"ERROR: Target key, {key} not found in {doc}")
        else:
            newcoll.append(doc)
            values.append(doc.get(key))

    return newcoll


def validate_doc(collection_name, doc, rc):
    from pprint import pformat

    from regolith.schemas import validate

    v = validate(collection_name, doc, rc.schemas)
    error_message = ""
    if v[0] is False:
        error_message += f"ERROR in {doc['_id']}:\n{pformat(v[1])}\n"
        for vv in v[1]:
            error_message += f"{pformat(doc.get(vv))}\n"
        error_message += "-" * 15
        error_message += "\n"
    return v[0], error_message


def add_to_google_calendar(event):
    """Takes a newly created event, and adds it to the user's google
    calendar.

    Parameters:
        event - a dictionary containing the event details to be added to google calendar
                https://developers.google.com/calendar/api/v3/reference/events

    Returns:
        None
    """

    tokendir = os.path.expanduser("~/.config/regolith/tokens/google_calendar_api")
    creds = None
    os.makedirs(tokendir, exist_ok=True)
    tokenfile = os.path.join(tokendir, "token.json")
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(tokenfile):
        creds = Credentials.from_authorized_user_file(
            tokenfile, ["https://www.googleapis.com/auth/calendar.events"]
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print(
                "The google calendar feature needs authentication information to run. "
                "This needs to be done just once for each new device. "
                "Please grant permission to regolith to access your calendar. "
                "If this process takes more than 1 minute you will have to rerun "
                "the helper to complete the addition of the presentation."
            )
            return 0
        with open(tokenfile, "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    event = service.events().insert(calendarId="primary", body=event).execute()
    print("Event created: %s" % (event.get("htmlLink")))
    return 1


def google_cal_auth_flow():
    """First time authentication, this function opens a window to
    request user consent to use google calendar API, and then returns a
    token."""
    tokendir = os.path.expanduser("~/.config/regolith/tokens/google_calendar_api")
    os.makedirs(tokendir, exist_ok=True)
    tokenfile = os.path.join(tokendir, "token.json")
    curr = pathlib.Path(__file__).parent.resolve()
    flow = InstalledAppFlow.from_client_secrets_file(
        os.path.join(curr, "credentials.json"), ["https://www.googleapis.com/auth/calendar.events"]
    )
    creds = flow.run_local_server(port=0)
    with open(tokenfile, "w") as token:
        token.write(creds.to_json())
    # Save the credentials for the next run


def get_target_repo_info(target_repo_id, repos):
    """Checks if repo information is defined and valid in rc.

    Parameters:
      target_repo_id - string
        the id of the doc with the target repo information
      repos - list
        the list of repos.  A repo must have a name, a url and a params
            kwarg.

    Returns:
        The target repo document, or False if it is not present or properly
        formulatedinformation
    """
    setup_message = (
        "INFO: If you would like regolith to automatically create a repository in GitHub/GitLab, "
        "please add your repository information in reolgithrc.json and "
        "your private authentication token in "
        "user.json respectively. See regolith documentation for details."
    )

    target_repo = [repo for repo in repos if repo.get("_id", "") == target_repo_id]
    if len(target_repo) == 0:
        print(setup_message)
        return False
    if len(target_repo) > 1:
        print(f"more than on repo found in regolithrc.json with the name {target_repo_id}")
        return False
    target_repo = target_repo[0]
    message_params_not_defined = (
        f"WARNING: The request parameters may not be defined. "
        f"Info we have: {target_repo}"
        f"If you would like regolith to automatically create a repository in GitHub/GitLab, "
        f"please add repository information in regolithrc.json. See regolith documentation "
        f"for details."
    )
    message_url_not_defined = (
        "WARNING: The request url may not be valid. "
        "If you would like regolith to automatically create a repository in GitHub/GitLab, "
        "please add repository information in regolithrc.json. See regolith documentation "
        "for details."
    )
    if not target_repo.get("params"):
        print(message_params_not_defined)
        return False
    if not target_repo.get("params").get("name"):
        print(message_params_not_defined)
        return False
    if not target_repo.get("url"):
        print(message_url_not_defined)
        return False
    else:
        built_url = f"{target_repo.get('url')}{target_repo.get('api_route')}"
        url = urlparse(built_url)
        if url.scheme and url.netloc and url.path:
            target_repo["params"].update({"name": target_repo.get("params").get("name").strip().replace(" ", "_")})
            target_repo["built_url"] = built_url
            return target_repo
        else:
            print(message_url_not_defined)
            return False


def get_target_token(target_token_id, tokens):
    """Checks if API authentication token is defined and valid in rc.

    Parameters:
        target_token_id - string
            the name of the personal access token (defined in rc)
        rc - run control object

    Returns:
        The token if the token exists and False if not
    """
    message_token_not_defined = (
        "WARNING: Cannot find an authentication token.  It may not be correctly defined. "
        "If you would like regolith to automatically create a repository in GitHub/GitLab, "
        "please add your private authentication token in user.json. "
        "See regolith documentation for details."
    )

    target_token = [token for token in tokens if token.get("_id") == target_token_id]
    if len(target_token) == 0:
        print(message_token_not_defined)
        return None
    if len(target_token) > 1:
        print(f"more than one token found in regolithrc.json with the name {target_token_id}")
        return None
    if target_token[0].get("token", ""):
        return target_token[0].get("token")


def create_repo(destination_id, token_info_id, rc):
    """Creates a repo at the target destination.

    tries to fail gracefully if repo information and token is not defined

    Parameters:
        destination_id - string
            the id of the target repo information document
        token_info_id - string
            the id for the token info document (e.g. 'priv_token')
        rc - run control object
          the run control object that should contain rc.repos and rc.tokens docs

    Returns:
        Success message (repo target_repo has been created in talks) if repo is successfully created in target_repo
        Warning/setup messages if unsuccessful (or if repo info or token are not valid)
    """

    repo_info = get_target_repo_info(destination_id, rc.repos)
    token = get_target_token(token_info_id, rc.tokens)
    if repo_info and token:
        try:
            response = requests.post(
                repo_info.get("built_url"), params=repo_info["params"], headers={"PRIVATE-TOKEN": token}
            )
            response.raise_for_status()
            clone_text = (
                f"{repo_info.get('url').replace('https://', '')}:"
                f"{repo_info.get('namespace_name', '<group/org name>')}"
                f"/{repo_info['params'].get('name')}.git"
            )
            return (
                f"repo {repo_info.get('params').get('name', 'unknown')} "
                f"has been created at {repo_info.get('url')}.\nClone this "
                f"to your local using (HTTPS):\ngit clone https://{clone_text}\n"
                f"or (SSH):\ngit clone git@{clone_text}"
            )
        except requests.exceptions.HTTPError:
            raise HTTPError(
                f"WARNING: Unsuccessful attempt at making a GitHub/GitLab etc., repository "
                f"due to an issue with the API call (status code: {response.status_code}). "
                f"If you would like regolith to automatically create a repository in GitHub/GitLab, "
                f"please add repository information in regolithrc.json. See regolith documentation "
                f"for details."
            )
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    else:
        return


def get_tags(coll):
    """Given a collection with a tags field, returns the set of tags as
    a list.

    The tags field is expected to be a string with comma or space separated tags.
    get_tags splits the tags and returns the set of unique tags as a list of
    strings.

    Parameters
    ----------
    coll collection
      the collection

    Returns
    -------
    the set of all tags as a list
    """

    all_tags = []
    for paper in coll:
        tag_long = paper.get("tags", "")
        if not isinstance(tag_long, str):
            raise TypeError("ERROR: valid tags are comma or space separated strings of tag names")
        tags = tag_long.split(",")
        tags = [sub_item for item in tags for sub_item in item.split()]
        all_tags.extend(tags)
    all_tags = [item.strip() for item in all_tags]
    all_tags = list(set(all_tags))
    all_tags.sort()
    return all_tags


def get_uuid():
    """Returns a uuid.uuid4 string."""
    return str(uuid.uuid4())


def get_appointments(person, appointments, target_grant=None):
    """Get appointments from a person from the people collection.

    Parameters
    ----------
    person: dict
      The person from whom to harvest appointments from
    appointments: list of tuples
      The list of appointments.  Each tuple contains (person_id, begin-date,
      end-date, loading (a number between 0 and 1), and weighted duration
      (i.e., actual duration in months * loading) in units of months
    target_grant: str
      optional.  id of grant for which you want to search for appointments.
      If not specified it will return appointments for that person in that
      date range for all/any grants

    Returns
    -------
    updated appointments list
    """
    for appt_id, appt in person.get("appointments").items():
        if target_grant is None or appt.get("grant", "no_grant") == target_grant:
            bd = get_dates(appt).get("begin_date")
            ed = get_dates(appt).get("end_date")
            weighted_duration = (ed - bd).days / 30.4 * appt.get("loading")
            appointments.append(
                (person.get("_id"), bd, ed, appt.get("loading"), round(weighted_duration, 2), appt.get("grant"))
            )
    return appointments
