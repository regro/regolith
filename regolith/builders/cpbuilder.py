"""Builder for Current and Pending Reports."""
from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import month_to_int
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    filter_grants,
    fuzzy_retrieval,
    has_started,
    is_current,
)


def is_pending(sy, sm, sd):
    return not has_started(sy, sm, sd)


class CPBuilder(LatexBuilderBase):
    """Build current and pending report from database entries"""

    btype = "current-pending"

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
        gtx["grants"] = sorted(
            all_docs_from_collection(rc.client, "grants"), key=_id_key
        )
        gtx["groups"] = sorted(
            all_docs_from_collection(rc.client, "groups"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        for group in self.gtx["groups"]:
            pi = fuzzy_retrieval(self.gtx["people"], ["aka", "name"], group["pi_name"])

            grants = list(self.gtx["grants"])
            current_grants = [
                g
                for g in grants
                if is_current(
                    *[
                        g.get(s, 1)
                        for s in [
                            "begin_year",
                            "end_year",
                            "begin_month",
                            "begin_day",
                            "end_month",
                            "end_day",
                        ]
                    ]
                )
            ]
            pending_grants = [
                g
                for g in grants
                if is_pending(
                    *[g[s] for s in ["begin_year", "begin_month", "begin_day"]]
                )
            ]
            current_grants, _, _ = filter_grants(
                current_grants, {pi["name"]}, pi=False, multi_pi=True
            )
            pending_grants, _, _ = filter_grants(
                pending_grants, {pi["name"]}, pi=False, multi_pi=True
            )
            grants = pending_grants + current_grants
            for grant in grants:
                grant.update(
                    award_start_date="{2}-{1}-{0}".format(
                        grant["begin_day"],
                        month_to_int(grant["begin_month"]),
                        grant["begin_year"],
                    ),
                    award_end_date="{2}-{1}-{0}".format(
                        grant["end_day"],
                        month_to_int(grant["end_month"]),
                        grant["end_year"],
                    ),
                )
            self.render(
                "current_pending.tex",
                "cpp.tex",
                pi=pi,
                pending=pending_grants,
                current=current_grants,
                pi_upper=pi["name"].upper(),
                group=group,
            )
            self.pdf("cpp")
