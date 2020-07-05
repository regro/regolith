"""Builder for Proposal Reivews."""
import datetime
import time
from nameparser import HumanName

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import month_to_int
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    filter_grants,
    fuzzy_retrieval,
)


class PropReportBuilder(LatexBuilderBase):
    """Build a proposal review from database entries"""
    btype = "propreport"
    needed_dbs = ['presentations', 'projecta', 'people']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["projecta"] = sorted(
            all_docs_from_collection(rc.client, "projecta"), key=_id_key
        )
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"), key=_id_key
        )
        gtx["presentations"] = sorted(
            all_docs_from_collection(rc.client, "presentations"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
