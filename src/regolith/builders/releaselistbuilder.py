"""Builder for software release lists."""

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.stylers import month_fullnames, sentencecase
from regolith.tools import all_docs_from_collection, filter_software, group_member_ids


class ReleaseListBuilder(LatexBuilderBase):
    """Build list of released software from database entries."""

    btype = "releaselist"
    needed_colls = ["groups", "people", "grants", "software", "contacts"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["contacts"] = sorted(
            all_docs_from_collection(rc.client, "contacts"),
            key=position_key,
            reverse=True,
        )
        gtx["grants"] = sorted(all_docs_from_collection(rc.client, "grants"), key=_id_key)
        gtx["groups"] = sorted(all_docs_from_collection(rc.client, "groups"), key=_id_key)
        gtx["software"] = sorted(all_docs_from_collection(rc.client, "software"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template."""
        everybody = self.gtx["people"] + self.gtx["contacts"]
        for group in self.gtx["groups"]:
            grp = group["_id"]
            grpmember_ids = group_member_ids(self.gtx["people"], grp)
            for member in grpmember_ids:
                if self.rc.people:
                    if member not in self.rc.people:
                        continue
                progclean = filter_software(everybody, self.gtx["software"], member)

                if len(progclean) > 0:
                    progclean = sorted(
                        progclean,
                        key=lambda k: max(release["release_date"] for release in k["release"]),
                        reverse=True,
                    )
                outfile = "software-report"
                pi = [person for person in self.gtx["people"] if person["_id"] == member][0]
                self.render(
                    "releaselist.tex",
                    outfile + ".tex",
                    pi=pi,
                    software=progclean,
                    sentencecase=sentencecase,
                    monthstyle=month_fullnames,
                )
                self.env.trim_blocks = True
                self.env.lstrip_blocks = True
                # self.render(
                # "releaselist.txt",
                # outfile + ".txt",
                # pi=pi,
                # software=progclean,
                #  sentencecase=sentencecase,
                #  monthstyle=month_fullnames,
            # )
            # self.pdf(outfile)
