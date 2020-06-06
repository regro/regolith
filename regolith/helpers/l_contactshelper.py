"""Helper for finding and listing contacts from the contacts.yml database.
Prints name, institution, and email (if applicable) of the contact.
"""
import dateutil
import dateutil.parser as date_parser
from collections import Counter
from regolith.dates import is_current
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    fragment_retrieval
)

TARGET_COLL = "contacts"
HELPER_TARGET = "l_contacts"


def subparser(subpi):
    subpi.add_argument(
        "-n",
        "--name",
        help='list of names or name fragments (multiple arguments allowed) to use to find contacts',
        nargs='+')
    subpi.add_argument(
        "-i",
        "--inst",
        help='institution or an institution fragment (single argument only) to use to find contacts')
    subpi.add_argument(
        "-d",
        "--date",
        help='approximate date in ISO format (YYYY-MM-DD) corresponding to when the contact was entered in the database. Comes with a default range of 4 months centered around the date; change range using --range argument')
    subpi.add_argument(
        "-r",
        "--range",
        help='range (in months) centered around date d specified by --date, i.e. (d +/- r/2)',
        default=4)
    subpi.add_argument(
        "-o",
        "--notes",
        help='list of fragments (multiple arguments allowed) to be found in the notes section of a contact',
        nargs='+')
    return subpi


class ContactsListerHelper(SoutHelperBase):
    """Helper for finding and listing contacts from the contacts.yml file
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        try:
            if not rc.database:
                rc.database = rc.databases[0]["name"]
        except BaseException:
            pass
        colls = [
            sorted(
                all_docs_from_collection(rc.client, collname), key=_id_key
            )
            for collname in self.needed_dbs
        ]
        for db, coll in zip(self.needed_dbs, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        contacts = []
        ret_list = []
        num = 0
        if rc.name:
            num += 1
            for name in rc.name:
                contacts.extend(
                    fragment_retrieval(
                        self.gtx['contacts'], [
                            "_id", "aka", "name"], name))
        if rc.inst:
            num += 1
            contacts.extend(
                fragment_retrieval(
                    self.gtx['contacts'],
                    ["institution"],
                    rc.inst))
        if rc.notes:
            num += 1
            for note in rc.notes:
                contacts.extend(
                    fragment_retrieval(
                        self.gtx['contacts'],
                        ["notes"],
                        note))
        if rc.date:
            num += 1
            temp_dat = date_parser.parse(rc.date).date()
            for contact in self.gtx["contacts"]:
                if rc.date:
                    temp_dict = {
                        "begin_date": (temp_dat -
                                       dateutil.relativedelta.relativedelta(
                                           months=int(
                                               rc.range))).isoformat(),
                        "end_date": (temp_dat +
                                     dateutil.relativedelta.relativedelta(
                                         months=int(
                                             rc.range))).isoformat()}
                    if is_current(temp_dict, now=temp_dat):
                        contacts.append(contact)
        for con in contacts:
            ret_list.append(
                f"name: {con.get('name')}, institution: {con.get('institution')}, email: {con.get('email','missing')}")
        temp_c = Counter(ret_list)
        for key in temp_c:
            if temp_c[key] == num:
                print(key)
        return
