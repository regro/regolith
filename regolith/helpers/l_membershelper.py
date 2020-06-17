"""Helper for listing group members.

"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.dates import get_due_date, is_current
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id, search_collection,
    key_value_pair_filter, collection_str
)

TARGET_COLL = "people"
HELPER_TARGET = "l_members"
ALLOWED_STATI = ["proposed", "started", "finished", "back_burner", "paused", "cancelled"]



def subparser(subpi):
    subpi.add_argument("-v", "--verbose", action="store_true", help='increase verbosity of output')
    subpi.add_argument("-c", "--current", action="store_true", help='get only current group members ')
    subpi.add_argument("-f", "--filter", nargs="+", help="Search this collection by giving key element pairs")
    subpi.add_argument("-k", "--keys", nargs="+", help="Specify what keys to return values from when running "
                                                       "--filter. If no argument is given the default is just the id.")

    subpi.add_argument("-p", "--prior", action="store_true", help='get only former group members ')
    return subpi


class MembersListerHelper(SoutHelperBase):
    """Helper for listing group members.

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
        except:
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
        if rc.filter:
            collection = key_value_pair_filter(self.gtx["people"], rc.filter)
        else:
            collection = self.gtx["people"]
        bad_stati = ["finished", "cancelled", "paused", "back_burner"]
        people = []
        for person in collection:
            if rc.current and not person.get('active'):
                continue
            people.append(person)

        if rc.filter and not rc.verbose:
            results = (collection_str(people, rc.keys))
            print(results, end="")
            return

        for person in self.gtx["people"]:
            if rc.current:
                if not person.get('active'):
                    continue
                people.append(person)
            elif rc.prior:
                if person.get('active'):
                    continue
                people.append(person)
            else:
                people.append(person)

        for i in people:
            if rc.verbose:
                print("{}, {} | group_id: {}".format(i.get('name'), i.get('position'), i.get('_id')))
                print("    orcid: {} | github_id: {}".format(i.get('orcid_id'), i.get('github_id')))
                for employment in i.get('employment'):
                    if is_current(employment):
                        print("    current organization: {}".format(employment.get('organization')))
                        print("    current position: {}".format(employment.get('position')))
                    if not i.get('active'):
                        if employment.get('group') == "bg":
                            print("    billinge group position: {}".format(employment.get('position')))
            else:
                print("{}".format(i.get('name')))
        return
