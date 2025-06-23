"""Helper for finding and listing contacts from the contacts.yml
database.

Prints name, institution, and email (if applicable) of the contact.
"""

import dateutil
import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.dates import get_dates, is_current
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import all_docs_from_collection, fuzzy_retrieval, get_pi_id, search_collection

TARGET_COLL = "contacts"
HELPER_TARGET = "l_contacts"


def subparser(subpi):
    date_kwargs = {}
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"
        int_kwargs["widget"] = "IntegerField"
    else:
        subpi.add_argument(
            "run", help='run the lister. To see allowed optional arguments, type "regolith helper l_contacts".'
        )
    subpi.add_argument("-v", "--verbose", action="store_true", help="Increases the verbosity of the output.")
    subpi.add_argument(
        "-n", "--name", help="name or name fragment (single argument only) to use to find contacts."
    )
    subpi.add_argument(
        "-i",
        "--inst",
        help="institution or an institution fragment (single argument only) to use to find contacts.",
    )
    subpi.add_argument(
        "-d",
        "--date",
        help="approximate date corresponding to when the contact was entered in the database. "
        "Comes with a default range of 4 months centered around the date; change range using --range argument.",
        **date_kwargs,
    )
    subpi.add_argument(
        "-r",
        "--range",
        help="range (in months) centered around date d specified by --date, i.e. (d +/- r/2).",
        default=4,
        **int_kwargs,
    )
    subpi.add_argument(
        "-o", "--notes", help="fragment (single argument only) to be found in the notes section of a contact."
    )
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs.")
    subpi.add_argument(
        "-k",
        "--keys",
        nargs="+",
        help="Specify what keys to return values from when running --filter. "
        "If no argument is given the default is just the id.",
    )
    return subpi


class ContactsListerHelper(SoutHelperBase):
    """Helper for finding and listing contacts from the contacts.yml
    file."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "institutions"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        colls = [
            sorted(all_docs_from_collection(rc.client, collname), key=_id_key) for collname in self.needed_colls
        ]
        for db, coll in zip(self.needed_colls, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        list_search = []
        collection = self.gtx["contacts"]
        if rc.name:
            list_search.extend(["name", rc.name])
        if rc.inst:
            list_search.extend(["institution", rc.inst])
        if rc.notes:
            list_search.extend(["notes", rc.notes])
        if rc.filter:
            list_search.extend(rc.filter)
        filtered_contacts_id = (search_collection(collection, list_search)).strip("    \n")
        filtered_contacts_id = list(filtered_contacts_id.split("    \n"))
        if rc.date:
            date_list = []
            temp_dat = date_parser.parse(rc.date).date()
            temp_dict = {
                "begin_date": (temp_dat - dateutil.relativedelta.relativedelta(months=int(rc.range))).isoformat(),
                "end_date": (temp_dat + dateutil.relativedelta.relativedelta(months=int(rc.range))).isoformat(),
            }
            for contact in collection:
                curr_d = get_dates(contact)["date"]
                if is_current(temp_dict, now=curr_d):
                    date_list.append(contact.get("_id"))
                filtered_contacts_id = [value for value in filtered_contacts_id if value in date_list]
        filtered_contacts = []
        string_contacts = ""
        for contact in collection:
            if contact.get("_id") in filtered_contacts_id:
                filtered_contacts.append(contact)
                institution = contact.get("institution")
                institution_name = fuzzy_retrieval(self.gtx["institutions"], ["name", "_id", "aka"], institution)
                if institution_name:
                    contact["institution"] = institution_name.get("name")
                if rc.verbose:
                    contact_str = f"{contact.get('name')}\n"
                    for k in ["_id", "email", "institution", "department", "notes", "aka"]:
                        if contact.get(k):
                            if isinstance(contact.get(k), list):
                                lst_expanded = "\n        -".join(map(str, contact.get(k)))
                                contact_str += f"    {k}:\n        -{lst_expanded}\n"
                            else:
                                contact_str += f"    {k}: {contact.get(k)}\n"
                    string_contacts += contact_str
                else:
                    string_contacts += (
                        f"{contact.get('name')}  |  {contact.get('_id')}  |"
                        f"  institution: {contact.get('institution')}  |"
                        f"  email: {contact.get('email', 'missing')}\n"
                    )
        print(string_contacts.strip("\n"))
        return
