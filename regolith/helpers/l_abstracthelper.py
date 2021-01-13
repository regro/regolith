
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
    needed_dbs = [f'{TARGET_COLL}', 'people', 'contacts']

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
                rc.database = rc.databases[0]
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
        presentations = self.gtx["presentations"]

        for presentation in presentations:
            if rc.title is not None:
                if rc.title.casefold() not in presentation.get('title').casefold():
                    continue
            if rc.location is not None and 'location' in presentation:
                if rc.location.casefold() not in presentation.get('location').casefold():
                    continue
            if rc.location is not None and 'location' not in presentation:
                continue
            if rc.year is not None and 'begin_year' in presentation:
                if int(rc.year) != presentation.get('begin_year'):
                    continue
            elif rc.year is not None and 'end_year' in presentation:
                if int(rc.year) != presentation.get("end_year"):
                    continue
            if rc.author is not None:
                for authors in presentation.get('authors'):
                    if rc.author not in authors:
                        continue
            print("---------------------------------------")
            print(f"Title: {presentation.get('title')}\n")
            author_list = [author
                           if not get_person_contact(author, self.gtx["people"], self.gtx["contacts"])
                           else get_person_contact(author, self.gtx["people"], self.gtx["contacts"]).get('name')
                           for author in presentation.get('authors')]
            print(", ".join(author_list))
            print(f"\nAbstract: {presentation.get('abstract')}")
        return
