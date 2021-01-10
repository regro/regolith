# add author change id to name?
# no location leads to no output -fix and make roboust
#get tests to pass

from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    get_person_contact
)

TARGET_COLL = "presentations"
HELPER_TARGET = "l_abstract"

def subparser(subpi):
    subpi.add_argument(
        "run",
        help='run the lister. To see allowed optional arguments, type "regolith helper l_abstracts".')
    subpi.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increases the verbosity of the output.")
    subpi.add_argument(
        "-a",
        "--author",
        help='authors group ID(single argument only) to use to find presentation abstract.')
    subpi.add_argument(
        "-y",
        "--year",
        help='Start or end year of the presentation (single argument only) to use to find presentation.')
    subpi.add_argument(
        "-l",
        "--location",
        help='Location of presentation, either a country, city, state, or university.')
    subpi.add_argument(
        "-t",
        "--title",
        help='Fragment of the title of the abstract or talk to use to filter presentations.')
    return subpi



class AbstractListerHelper(SoutHelperBase):
    """Helper for finding and listing abstracts from the presentations.yml file
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}', 'authors']

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
                rc.database = rc.databases[0]["authors"]
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
        collection = self.gtx["presentations"]

        if rc.year is None:
            rc.year = ''
        if rc.location is None:
            rc.location = ''
        if rc.title is None:
            rc.title = ''

        for key in collection:
            if rc.author in key[1]['authors']:
                if "location" in key[1] and rc.location.lower() in key[1]["location"].lower():
                    if rc.title.lower() in key[1]["title"].lower():
                        if "end_year" in key[1] and "begin_year" in key[1]:
                            if rc.year in str(key[1]["end_year"]) or rc.year in str(key[1]["begin_year"]):
                                print("---------------------------------------")
                                if "title" in key[1]:
                                    print("Title: " + key[1]["title"]+"\n")
                                a = ""
                                for i in range(0, len(key[1]["authors"])):
                                    auth=key[1]["authors"][i]
                                    auth=get_person_contact(auth, self.gtx["people"], self.gtx["contacts"])
                                    a = a + auth + ", "
                                print(a)
                                print("\nAbstract: " + key[1]["abstract"])
        return