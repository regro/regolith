import calendar
from datetime import date, timedelta

from regolith.dates import get_dates
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.helpers.makeappointmentshelper import _future_grant
from regolith.sorters import position_key
from regolith.tools import all_docs_from_collection, fuzzy_retrieval, merge_collections_superior

SEMESTER_START_MONTH = {"fall": (9, 12), "spring": (1, 5), "summer": (6, 8)}


def subparser(subpi):
    subpi.add_argument(
        "-d",
        "--date",
        help="the date from which its current appointments will be listed, " "defaults to today's date",
    )
    subpi.add_argument(
        "-s",
        "--semester",
        help="list all the appointments for the semester of the specified date",
        action="store_true",
    )
    return subpi


class CurrentAppointmentsListerHelper(SoutHelperBase):
    """Helper for managing appointments on grants and studying the burn
    of grants over time."""

    # btype must be the same as helper target in helper.py
    btype = "currentappointments"
    needed_colls = ["people", "grants", "proposals"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["grants"] = sorted(all_docs_from_collection(rc.client, "grants"), key=_id_key)
        gtx["proposals"] = sorted(all_docs_from_collection(rc.client, "proposals"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        since, before = None, None
        if rc.date:
            ondate = date(*[int(num) for num in rc.date.split("-")])
        else:
            ondate = date.today()

        if rc.semester:
            for v in SEMESTER_START_MONTH.values():
                if v[0] <= ondate.month <= v[1]:
                    since = date(ondate.year, v[0], 1)
                    last_day = calendar.monthrange(ondate.year, v[1])[1]
                    before = date(ondate.year, v[1], last_day)

        people = self.gtx["people"]
        jg = self.gtx["grants"]
        proposals = self.gtx["proposals"]
        grants = merge_collections_superior(proposals, jg, "proposal_id")
        _future_grant["begin_date"] = ondate
        _future_grant["end_date"] = ondate + timedelta(days=2190)
        _future_grant["budget"][0]["begin_date"] = ondate
        _future_grant["budget"][0]["end_date"] = ondate + timedelta(days=2190)
        grants.append(_future_grant)
        for person in people:
            p_appt = person.get("appointments", None)
            if p_appt:
                for _id, appt in p_appt.items():
                    grantid = appt.get("grant")
                    if not grantid:
                        print(f"No grant found in {person.get('_id')} appt {person.get('appt')}")
                    grant = fuzzy_retrieval(grants, ["name", "_id", "alias"], grantid)
                    if not grant:
                        print(f"No grant found for {grantid}")
                    try:
                        accountnr = grant.get("account", grant["alias"])
                    except Exception:
                        accountnr = ""
                    loading = appt.get("loading")
                    appt_dates = get_dates(appt)
                    bd = appt_dates.get("begin_date")
                    ed = appt_dates.get("end_date")
                    if since and before:
                        if (ed >= since) and (bd <= before):
                            print(
                                person.get("_id"),
                                grantid,
                                accountnr,
                                loading,
                                bd.strftime("%Y-%m-%d"),
                                ed.strftime("%Y-%m-%d"),
                            )
                    else:
                        if bd <= ondate <= ed:
                            print(
                                person.get("_id"),
                                grantid,
                                accountnr,
                                loading,
                                bd.strftime("%Y-%m-%d"),
                                ed.strftime("%Y-%m-%d"),
                            )
