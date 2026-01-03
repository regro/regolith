"""Builder for Current and Pending Reports."""

import datetime as dt

import dateutil.parser as date_parser
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection, get_tags

ALLOWED_TYPES = ["nsf", "doe", "other"]
ALLOWED_STATI = ["invited", "accepted", "declined", "downloaded", "inprogress", "submitted", "cancelled"]


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument(
        "tags",
        help="list of tags, separated by spaces, to use "
        "to find papers in citations collection that "
        "will be added to the list. type 'all' if building"
        "lists from all tags in the db. OR logic is used "
        "so this will return all papers that "
        "contain this OR that tag in the tags string in "
        "citations.  for example, 'neutron superconductor' "
        "(without the quotes) will return all neutron "
        "and all superconductor papers.",
        nargs="+",
    )
    subpi.add_argument(
        "-t",
        "--title",
        help="A title for the list that will be "
        "rendered when the list is built. Required if "
        "this is new list.",
    )
    subpi.add_argument(
        "-p",
        "--purpose",
        help="The purpose or intended use for the reading. This will " "not be rendered when the list is built",
    )
    subpi.add_argument(
        "--database",
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
    )
    subpi.add_argument("--date", help="The date that will be used for testing.", **date_kwargs)
    return subpi


class GrpPubReadListAdderHelper(DbHelperBase):
    """Build a helper."""

    btype = "a_grppub_readlist"
    needed_colls = ["citations", "reading_lists"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        rc.coll = "reading_lists"
        gtx["citations"] = sorted(all_docs_from_collection(rc.client, "citations"), key=_id_key)
        gtx["reading_lists"] = sorted(all_docs_from_collection(rc.client, "reading_lists"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def build_reading_list_from_citation_tag(self, tag, update_date):
        rc = self.rc
        key = f"{tag.strip()}"
        rlist_doc = rc.client.find_one(rc.database, rc.coll, {"_id": key})
        if not rlist_doc:
            rlist_doc = {"_id": key, "date": update_date}
        # rebuild list from scratch always
        rlist_doc.update({"papers": []})
        if rc.purpose and rc.tags[0] != "all":
            rlist_doc.update({"purpose": rc.purpose})
        if rc.title and rc.tags[0] != "all":
            rlist_doc.update({"title": rc.title})
        elif not rlist_doc.get("title"):
            rlist_doc.update({"title": f"List built for tag {key} from citations collection"})
        for cite in self.gtx["citations"]:
            if tag in cite.get("tags", ""):
                new_paper = {
                    "text": cite.get("synopsis", f"no synopsis in citation " f"{cite.get('_id')}"),
                    "year": int(cite.get("year", 0)),
                }
                if cite.get("doi") is not None and cite.get("doi") != "tbd":
                    new_paper.update({"doi": cite.get("doi")})
                elif cite.get("url") is not None and cite.get("url") != "tbd":
                    new_paper.update({"url": cite.get("url")})
                else:
                    new_paper.update({"doi": "tbd"})
                rlist_doc["papers"].append(new_paper)
        # sort by year then remove year
        rlist_doc["papers"].sort(key=lambda pper: pper.get("year"))
        [ppr.pop("year") for ppr in rlist_doc["papers"]]
        # remove duplicates
        rlist_doc["papers"] = [dict(t) for t in {tuple(paper.items()) for paper in rlist_doc["papers"]}]
        return rlist_doc

    def db_updater(self):
        rc = self.rc
        if rc.tags[0].strip().lower() == "all":
            all_tags = get_tags(self.gtx["citations"])
        else:
            all_tags = rc.tags
        print(f"Making lists for tags:\n{all_tags}")
        if rc.date:
            update_date = date_parser.parse(rc.date).date()
        else:
            update_date = dt.date.today()

        for tag in all_tags:
            pdoc = self.build_reading_list_from_citation_tag(tag, update_date)
            rc.client.insert_one(rc.database, rc.coll, pdoc)
            print(f"{tag} has been added/updated in reading_lists")

        return
