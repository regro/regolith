"""Builder for Lists of Presentations.

This builder will build a presentation list for each group-member in each group
listed in groups.yml.  Group members are indicated in the employment and
education sections of the individual in people.yml.

There are a number of filtering options, i.e., for presentation-type (invited,
colloquium, seminar, poster, contributed_oral) and for whether the invitation
was accepted or declined.  As of now, these filters can only be updated by
editing this file but may appear as command-line options later.  It will also
get institution and department information from institutions.yml if they are
there.

The author list is built from information in people.yml where possible.  The
does a fuzzy search for the person in people.yml but if the person is absent
from people, it will still build but using the string name given in
the presentations.yml.

The presentations are output in a ./_build directory."""

from copy import deepcopy

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    fuzzy_retrieval,
    get_person_contact,
    number_suffix,
    group_member_ids, latex_safe, filter_presentations
)
from regolith.stylers import sentencecase, month_fullnames
from regolith.dates import get_dates

class PresListBuilder(LatexBuilderBase):
    """Build list of talks and posters (presentations) from database entries"""

    btype = "preslist"
    needed_colls = ['groups', 'institutions', 'people', 'grants',
                  'presentations', 'contacts']


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
        gtx["contacts"] = sorted(
            all_docs_from_collection(rc.client, "contacts"),
            key=position_key,
            reverse=True,
        )
        gtx["grants"] = sorted(
            all_docs_from_collection(rc.client, "grants"), key=_id_key
        )
        gtx["groups"] = sorted(
            all_docs_from_collection(rc.client, "groups"), key=_id_key
        )
        gtx["presentations"] = sorted(
            all_docs_from_collection(rc.client, "presentations"), key=_id_key
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
        everybody = self.gtx["people"] + self.gtx["contacts"]
        for group in self.gtx["groups"]:
            grp = group["_id"]
            grpmember_ids = group_member_ids(self.gtx['people'], grp)
            for member in grpmember_ids:
                if self.rc.people:
                    if member not in self.rc.people:
                        continue
                presclean = filter_presentations(everybody,
                                                 self.gtx["presentations"],
                                                 self.gtx["institutions"],
                                                 member,
                                                 statuses=["accepted"])

                if len(presclean) > 0:
                    presclean = sorted(
                        presclean,
                        key=lambda k: k.get("date", None),
                        reverse=True,
                    )
                    outfile = "presentations-" + grp + "-" + member
                    pi = [
                        person
                        for person in self.gtx["people"]
                        if person["_id"] is member
                    ][0]
                    self.render(
                        "preslist.tex",
                        outfile + ".tex",
                        pi=pi,
                        presentations=presclean,
                        sentencecase=sentencecase,
                        monthstyle=month_fullnames,
                    )
                    self.env.trim_blocks = True
                    self.env.lstrip_blocks = True
                    self.render(
                        "preslist.txt",
                        outfile + ".txt",
                        pi=pi,
                        presentations=presclean,
                        sentencecase=sentencecase,
                        monthstyle=month_fullnames,
                    )
                    self.pdf(outfile)
