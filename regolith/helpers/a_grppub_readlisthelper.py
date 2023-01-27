"""Builder for Current and Pending Reports."""
import datetime as dt
import dateutil.parser as date_parser

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection, get_tags
)
from gooey import GooeyParser

ALLOWED_TYPES = ["nsf", "doe", "other"]
ALLOWED_STATI = ["invited", "accepted", "declined", "downloaded", "inprogress",
                 "submitted", "cancelled"]


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs['widget'] = 'DateChooser'

    subpi.add_argument("list_name", help="A short but unique name for the list. "
                                         "If the list already exists it will be updated. "
                                         "input 'all' here and for the tag argument "
                                         "to build lists for all the tags found in "
                                         "the citations collection.",
                        default=None)
    subpi.add_argument("tags", help="list of tags, separated by spaces, to use "
                                    "to find papers in citations collection that "
                                    "will be added to the list. type 'all' if building"
                                    "lists from all tags in the db. OR logic is used "
                                    "so this will return all papers that "
                                    "contain this OR that tag in the tags string in "
                                    "citations.  for example, 'neutron superconductor' "
                                    "(without the quotes) will return all neutron "
                                    "and all superconductor papers.",
                       nargs="+")
    subpi.add_argument("-t", "--title", help="A title for the list that will be "
                                     "rendered when the list is built. Required if "
                                             "this is new list.")
    subpi.add_argument("-p", "--purpose",
                        help="The purpose or intended use for the reading. This will "
                             "not be rendered when the list is built"
                        )
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file."
                       )
    subpi.add_argument("--date",
                       help="The date that will be used for testing.",
                       **date_kwargs
                       )
    return subpi


class GrpPubReadListAdderHelper(DbHelperBase):
    """Build a helper"""
    btype = "a_grppub_readlist"
    needed_colls = ['citations', "reading_lists"]

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

    def build_reading_list(self, update_date):
        rc = self.rc
        if rc.list_name == 'all':
            listname = rc.tags[0].split()
        else:
            listname = rc.list_name.split()
        key = "{}".format("_".join(listname).strip())
        pdocl = list(filter(lambda doc: doc["_id"] == key, self.gtx[rc.coll]))
        if len(pdocl) > 0:
            pdoc = pdocl[0]
            pdoc["papers"] = []   # rebuild the list from scratch
        else:
            pdoc = {}
            pdoc.update({
                "_id": key,
                'date': update_date,
                'papers': []
                    })
        if rc.purpose and rc.list_name != 'all':
            pdoc.update({'purpose': rc.purpose})
        if rc.list_name == 'all':
            pdoc.update({'title': f"List built for tag {rc.tags[0]} from citations collection"})
        elif rc.title:
            pdoc.update({'title': rc.title})
        try:
            pdoc['title']
        except KeyError:
            raise KeyError("ERROR: a title is required for a new list.  Please rerun specifying -t")
        for cite in self.gtx["citations"]:
            for tag in rc.tags:
                if tag in cite.get("tags", ""):
                    dupe_doi = [paper for paper in pdoc.get("papers", []) if cite.get("doi") == paper.get("doi")]
                    if len(dupe_doi) == 0:
                        pprs = pdoc["papers"]
                        doi = cite.get("doi", '')
                        url = cite.get("url", '')
                        year = int(cite.get('year', 0))
                        if len(doi) > 0 and doi != 'tbd':
                            pprs.append({"doi": doi,
                                         "text": cite.get("synopsis",
                                                          f"no synopsis in {cite.get('_id')}"),
                                         "year": year
                                         })
                        elif len(url) > 0 and url != 'tbd':
                            pprs.append({"url": url,
                                         "text": cite.get("synopsis",
                                                          f"no synopsis in {cite.get('_id')}"),
                                         "year": year
                                         })
                        else:
                            pprs.append({'doi': 'tbd',
                                         "text": cite.get("synopsis",
                                                          f"no synopsis in {cite.get('_id')}"),
                                         "year": year
                                         })
                        pdoc["papers"] = pprs
        pprs = pdoc["papers"]
        pprs.sort(key=lambda pper: pper.get('year'),
                  reverse=True)
        [ppr.pop("year") for ppr in pprs]
        pdoc["papers"] = pprs
        return key, pdoc

    def db_updater(self):
        rc = self.rc
        all_tags = get_tags(self.gtx["citations"])
        print(f"List of all tags in citations collection:\n{all_tags}")
        if rc.date:
            update_date = date_parser.parse(rc.date).date()
        else:
            update_date = dt.date.today()

        if rc.list_name.strip().lower() == 'all' and rc.tags[0].strip().lower() == 'all':
            print(f"building lists for all tags in the citation collection")
            for tag in all_tags:
                rc.tags = [tag]
                key, pdoc = self.build_reading_list(update_date)
                rc.client.insert_one(rc.database, rc.coll, pdoc)
                print(f"{key} has been added/updated in reading_lists")
        else:
            key, pdoc = self.build_reading_list(update_date)
            rc.client.insert_one(rc.database, rc.coll, pdoc)
            print(f"{key} has been added/updated in reading_lists")


        return

