"""Builder for Current and Pending Reports."""
import datetime as dt
import dateutil.parser as date_parser

from regolith.helpers.basehelper import SoutHelperBase, DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
)

ALLOWED_TYPES = ["nsf", "doe", "other"]
ALLOWED_STATI = ["invited", "accepted", "declined", "downloaded", "inprogress",
                 "submitted", "cancelled"]


def subparser(subpi):
    subpi.add_argument("list_name", help="A short but unique name for the list",
                        default=None)
    subpi.add_argument("title", help="A title for the list that will be "
                                     "rendered with the list")
    subpi.add_argument("tags", help="list of tags, separated by spaces, to use "
                                    "to find papers in citations collection that "
                                    "will be added to the list.  OR logic is used "
                                    "so this that will return all papers that "
                                    "contain this OR that in the tags string in "
                                    "citations",
                       nargs="+")
    subpi.add_argument("-p", "--purpose",
                        help="The purpose or intended use for the reading"
                        )
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file."
                       )
    subpi.add_argument("--date",
                       help="The date that will be used for testing."
                       )
    return subpi

class GrpPubReadListAdderHelper(DbHelperBase):
    """Build a helper"""
    btype = "a_grppub_readlist"
    needed_dbs = ['citations', "reading_lists"]

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        rc.coll = "reading_lists"
        gtx["citations"] = sorted(
            all_docs_from_collection(rc.client, "citations"), key=_id_key
        )
        gtx["reading_lists"] = sorted(
            all_docs_from_collection(rc.client, "reading_lists"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip


    def db_updater(self):
        rc = self.rc
        if rc.date:
            update_date = date_parser.parse(rc.date).date()
        else:
            update_date = dt.date.today()
        key = "{}".format("_".join(rc.list_name.split()).strip())

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            pdoc = dict(pdocl[0])
            pdoc["papers"] = dict(pdoc["papers"])
        else:
            pdoc = {}
            pdoc.update({
                "_id": key,
                'date': update_date,
                'papers': []
                    })
        updatables = {'purpose': rc.purpose, 'title': rc.title}
        for up_key, up_val in updatables.items():
            if pdoc.get(up_key, '') == '':
                if up_val:
                    pdoc.update({up_key: up_val})
                else:
                    pdoc['purpose'] = ''
            else:
                print(f"INFO: {up_key} statement not updated, entry already has "
                      f"{up_key} statement: {pdoc.get(up_key)}")


        for cite in self.gtx["citations"]:
            #print(f"{cite.get('_id')}: {cite.get('tags', '')}")  # save for filtering for untagged entries
            for tag in rc.tags:
                if tag in cite.get("tags", ""):
                    dupe_doi = [paper for paper in pdoc.get("papers", []) if cite.get("doi") == paper.get("doi")]
                    if len(dupe_doi) == 0:
                        pdoc["papers"].append({"doi": cite.get("doi"),
                                               "text": cite.get("synopsis", "")})
        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added/updated in reading_lists")

        return

