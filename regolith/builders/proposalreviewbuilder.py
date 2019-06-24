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


class PropRevBuilder(LatexBuilderBase):
    """Build a proposal review from database entries"""
    btype = "propreview"

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["proposalReviews"] = sorted(
            all_docs_from_collection(rc.client, "proposalReviews"), key=_id_key
        )
        gtx["institutions"] = sorted(
            all_docs_from_collection(rc.client, "institutions"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        for rev in self.gtx["proposalReviews"]:
            outname = "{}_{}".format(_id_key(rev),rev["reviewer"])
            multiauth = False
            if isinstance(rev["names"],str):
                rev["names"] = [rev["names"]]
            if len(rev["names"]) > 1:
                multiauth = True
            firstauthor = HumanName(rev["names"][0])
            firstauthorlastname = firstauthor.last
            instn = fuzzy_retrieval(
                self.gtx["institutions"], ["aka", "name", "_id"], rev["institution"]
            )
            if instn:
                institution = instn["name"]
            else:
                institution = rev["institution"]

            self.render(
                "propreport.txt",
                "{}.txt".format(outname),
                trim_blocks=True,
                agency=rev["agency"],
                appropriateness=rev["doe_appropriateness_of_approach"],
                title=rev["title"],
                institution=institution,
                multiauthor=multiauth,
                firstAuthorLastName=firstauthorlastname,
                competency=rev["competency_of_team"],
                adequacy=rev["adequacy_of_resources"],
                does_what=rev["does_what"],
                relevance=rev["doe_relevance_to_program_mission"],
                budget=rev["doe_reasonableness_of_budget"],
                does_how=rev["does_how"],
                goals=rev["goals"],
                importance=rev["importance"],
                summary=rev["summary"],
                freewrite=rev["freewrite"],
                broader_impacts=rev["nsf_broader_impacts"],
                creativity_originality=rev["nsf_create_original_transformative"],
                benefit_to_society=rev["nsf_pot_to_benefit_society"],
                plan_good=rev["nsf_plan_good"],
                advance_knowledge=rev["nsf_pot_to_Advance_knowledge"]
            )
