"""Helper for finding and listing abstracts from the presentations.yml database.
Prints author, meeting name(if applicable), location (if applicable), date (if applicable),
and abstract of the presentation.
"""
# add author change id to name?
# no location leads to no output -fix and make roboust
#get tests to pass


from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id
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
        metavar='',
        action="store_true",
        help="Increases the verbosity of the output.")
    subpi.add_argument(
        "-a",
        "--author",
        metavar='',
        help='authors group ID(single argument only) to use to find presentation abstract.')
    subpi.add_argument(
        "-y",
        "--year",
        metavar='',
        help='Start or end year of the presentation (single argument only) to use to find presentation.')
    subpi.add_argument(
        "-l",
        "--location",
        metavar='',
        help='Location of presentation, either a country, city, state, or university.')
    subpi.add_argument(
        "-t",
        "--title",
        help='Fragment of the title of the abstract or talk to use to filter presentations.')
    args = subpi.parse_args()
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
                rc.database = rc.databases[0]["author"]
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
        collection = self.gtx["presentation"]
        if args.year is None:
            args.year = ''
        if args.location is None:
            args.location = ''
        if args.title is None:
            args.title = ''

        for key in collection.items():
            if args.author in key[1]['authors']:
                if "location" in key[1] and args.location.lower() in key[1]["location"].lower():
                    if args.title.lower() in key[1]["title"].lower():
                        if "end_year" in key[1] and "begin_year" in key[1]:
                            if args.year in str(key[1]["end_year"]) or args.year in str(key[1]["begin_year"]):
                                print("---------------------------------------")
                                a = "Authors: "
                                for i in range(0, len(key[1]["authors"])):
                                    a = a + "- " + key[1]["authors"][i] + " "
                                print(a)
                                if "meeting_name" in key[1]:
                                    print(key[1]["meeting_name"])
                                if "institution" in key[1]:
                                    print("Institution: " + key[1]["institution"], end=' ')
                                if "department" in key[1]:
                                    print(", Department: " + key[1]["department"])
                                print("Location: " + key[1]["location"])
                                if "begin_day" and "begin_month" in key[1]:
                                    print("Start: " + str(key[1]["begin_day"]) + "-" + str(key[1]["begin_month"])
                                          + "-" + str(key[1]["begin_year"]))
                                if ("end_day" and "end_month" in key[1]):
                                    print("End: " + str(key[1]["end_day"]) + "-" + str(key[1]["end_month"])
                                          + "-" + str(key[1]["end_year"]))
                                if ("type" and "status" and "title" in key[1]):
                                    print("Type: " + key[1]["type"] + ", Status: " + key[1]["status"])
                                    print("Project: " + key[1]["project"][0])
                                    print("\nTitle: " + key[1]["title"])
                                print("Abstract: " + key[1]["abstract"])
        return

