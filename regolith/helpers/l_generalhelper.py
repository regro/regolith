"""Helper for finding people's information in the people collection
"""
import dateutil
import dateutil.parser as date_parser
from regolith.dates import (
    is_current,
    get_dates
)
from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    fragment_retrieval
)

TARGET_COLL = "people"
HELPER_TARGET = "list"


def subparser(subpi):
    subpi.add_argument(
        "people",
        help='run the lister. To see allowed optional arguments, type "regolith helper l_contacts"')
    subpi.add_argument(
        "-l",
        "--",
        help='name or name fragment (single argument only) to use to find people')

    return subpi

class GeneralListerHelper(SoutHelperBase):
    """Helper for finding and listing people's information from people.yml
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc

        return
