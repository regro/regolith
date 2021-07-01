"""Builder for CVs."""
from copy import deepcopy
from datetime import datetime, date 

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import is_current
from regolith.fsclient import _id_key
from regolith.sorters import ene_date_key, position_key
from regolith.stylers import sentencecase, month_fullnames
from regolith.tools import (
    all_docs_from_collection,
    filter_publications,
    filter_projects,
    filter_grants,
    awards_grants_honors,
    make_bibtex_file,
    filter_employment_for_advisees,
    dereference_institution,
    merge_collections_superior,
    filter_presentations, fuzzy_retrieval, filter_employment_for_group_members,
    get_age,
)


def get_current_rank(person):
    current_ranks = []
    for rank in person.get("rank"):
        if is_current(rank):
            current_ranks.append(rank)
    if len(current_ranks) > 1:
        raise RuntimeError(f"{person.get('name')} appears to have more than one "
                           f"current rank.")
    if len(current_ranks) == 0:
        print(f"WARNING: no current rank found for {person.get('name')}")

    return current_ranks[0]
        


class GrpSummaryBuilder(LatexBuilderBase):
    """Build CV from database entries"""

    btype = "cv"
    needed_dbs = ['groups', 'institutions','people', 'grants', 'citations', 'projects',
                  'proposals', 'presentations']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["presentations"] = sorted(
            all_docs_from_collection(rc.client, "presentations"), key=_id_key
        )
        gtx["groups"] = sorted(
            all_docs_from_collection(rc.client, "groups"), key=_id_key
        )
        gtx["institutions"] = sorted(
            all_docs_from_collection(rc.client, "institutions"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def latex(self):
        """Render latex template"""
        rc = self.rc
        begin_period = date(1900,1,1)
        for group in self.gtx["groups"]:
            group['pi'] = fuzzy_retrieval(self.gtx['people'],
                                                   ["_id", "name", "aka"],
                                                   group.get('pi_id', group.get('pi_name')
                                                             )) 
            group['pi_rank'] = get_current_rank(group['pi'])
            groupies = filter_employment_for_group_members(self.gtx["people"],
                                                           begin_period,
                                                           group.get("_id"))

            for p in groupies:
                # so we don't modify the dbs when de-referencing
                current_rank = get_current_rank(p)
                p['current_rank'] = current_rank.get("rank")
                p['years_in_rank'], p['months_in_rank'] = get_age(current_rank, dobkey="begin_date")  
                p['age'], _ = get_age(p)
                p['years_in_group'], p['months_in_group'] = get_age(p,dobkey="empl_begin_date")
                reviews = p.get("reviews", [])
                if len(reviews) > 0:
                    sorted(reviews, key=lambda x: x.get("review_date"),
                           reverse=True)
                    p['latest_review'] = reviews.pop()
                    print(p["latest_review"])
            self.render(
                "grpsummary.tex",
                f"{group['_id']}_{group.get('_id')}.tex",
                people=groupies,
                group=group,
                sentencecase=sentencecase,
                monthstyle=month_fullnames,
            )
            self.pdf(p["_id"])
