"""Helper for finishing prum in the projecta collection
"""
import datetime

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection


def subparser(subpi):
    """A subparser."""
    subpi.add_argument(
        "projectum_id",
        help="the ID or fragment of the ID of the projectum to be updated, e.g., 20sb")
    subpi.add_argument(
        "--idea",
        help="Summary of the beamline experiment and any conditions that might need to be accounted for, e.g. temperature ramp")
    subpi.add_argument(
        "--sample",
        help="Chemical composition and type of sample, e.g. film, powder, etc.")
    subpi.add_argument(
        "-s", "--database",
        help="The database that will be updated.  Defaults to "
             "first database in the regolithrc.json file.")
    return subpi


def process(doc: dict, idea: str, sample: str) -> dict:
    """Process the doc of the projecta."""
    dct = {
        "idea": idea,
        "sample": sample,
        "date_conceived": datetime.date.today()
    }
    if "beamtime" in doc:
        doc["beamtime"].append(dct)
    else:
        doc["beamtime"] = [dct]
    return doc


class PrumUpdaterHelper(DbHelperBase):
    """
    Helper for finishing prum in the projecta collection
    """
    # btype must be the same as helper target in helper.py
    btype = "u_prum"
    needed_dbs = ["projecta"]

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = self.needed_dbs[0]
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(
            all_docs_from_collection(rc.client, rc.coll), key=_id_key
        )

    def db_updater(self):
        rc = self.rc
        key = rc.projectum_id
        filterid = {'_id': key}
        found_projectum = rc.client.find_one(rc.database, rc.coll, filterid)
        found_projectum = process(
            found_projectum, idea=rc.idea, sample=rc.sample)
        rc.client.update_one(rc.database, rc.coll, filterid, found_projectum)
        return
