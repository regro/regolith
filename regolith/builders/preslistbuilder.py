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

from copy import deepcopy, copy
import datetime, sys

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    fuzzy_retrieval,
    number_suffix,
)
from regolith.stylers import sentencecase, month_fullnames
from regolith.dates import month_to_int


class PresListBuilder(LatexBuilderBase):
    """Build list of talks and posters (presentations) from database entries"""

    btype = "preslist"

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

    def group_member_ids(self, grp):
        """Get a list of all group member ids

        Parameters
        ----------
        grp: string
            The id of the group in groups.yml

        Returns
        -------
        set:
            The set of ids of the people in the group

        Notes
        -----
        - Groups that are being tracked are listed in the groups.yml collection
        with a name and an id.
        - People are in a group during an educational or employment period.
        - To assign a person to a tracked group during one such period, add
        a "group" key to that education/employment item with a value
        that is the group id.
        - This function takes the group id that is passed and searches
        the people collection for all people that have been
        assigned to that group in some period of time and returns a list of
        """
        grpmembers = set()
        for person in self.gtx["people"]:
            for k in ["education", "employment"]:
                for position in person.get(k, {}):
                    if position.get("group", None) == grp:
                        grpmembers.add(person["_id"])
        return grpmembers

    def latex(self):
        """Render latex template"""
        # just a reminder placeholder how to access these.  These
        # print statements will be removed when the builder is updated
        # to use them!
        print(self.rc.from_date)
        print(self.rc.to_date)
        print(self.rc.people)
        print(self.rc.grants)

        for group in self.gtx["groups"]:
            grp = group["_id"]
            grpmember_ids = self.group_member_ids(grp)
            for member in grpmember_ids:
                presentations = deepcopy(self.gtx["presentations"])
                types = ["all"]
                #                types = ['invited']
                #statuses = ["all"]
                statuses = ['accepted']

                firstclean = list()
                secondclean = list()
                presclean = list()

                # build the filtered collection
                # only list the talk if the group member is an author
                for pres in presentations:
                    pauthors = pres["authors"]
                    if isinstance(pauthors, str):
                        pauthors = [pauthors]
                    authors = [
                        fuzzy_retrieval(
                            self.gtx["people"],
                            ["aka", "name", "_id"],
                            author,
                            case_sensitive=False,
                        )
                        for author in pauthors
                    ]
                    authorids = [
                        author["_id"]
                        for author in authors
                        if author is not None
                    ]
                    if member in authorids:
                        firstclean.append(pres)
                # only list the presentation if it is accepted
                for pres in firstclean:
                    if pres["status"] in statuses or "all" in statuses:
                        secondclean.append(pres)
                # only list the presentation if it is invited
                for pres in secondclean:
                    if pres["type"] in types or "all" in types:
                        presclean.append(pres)

                # build author list
                for pres in presclean:
                    pauthors = pres["authors"]
                    if isinstance(pauthors, str):
                        pauthors = [pauthors]
                    pres["authors"] = [
                        author
                        if fuzzy_retrieval(
                            self.gtx["people"],
                            ["aka", "name", "_id"],
                            author,
                            case_sensitive=False,
                        )
                        is None
                        else fuzzy_retrieval(
                            self.gtx["people"],
                            ["aka", "name", "_id"],
                            author,
                            case_sensitive=False,
                        )["name"]
                        for author in pauthors
                    ]
                    authorlist = ", ".join(pres["authors"])
                    pres["authors"] = authorlist
                    pres["begin_month"] = month_to_int(pres["begin_month"])
                    pres["date"] = datetime.date(
                        pres["begin_year"],
                        pres["begin_month"],
                        pres["begin_day"],
                    )
                    for day in ["begin_day", "end_day"]:
                        pres["{}_suffix".format(day)] = number_suffix(
                            pres.get(day, None)
                        )
                    if "institution" in pres:
                        try:
                            pres["institution"] = fuzzy_retrieval(
                                self.gtx["institutions"],
                                ["aka", "name", "_id"],
                                pres["institution"],
                                case_sensitive=False,
                            )
                            if pres["institution"] is None:
                                sys.exit(
                                    "ERROR: institution {} not found in "
                                    "institutions.yml.  Please add and "
                                    "rerun".format(pres["institution"])
                                )
                        except:
                            sys.exit(
                                "ERROR: institution {} not found in "
                                "institutions.yml.  Please add and "
                                "rerun".format(pres["institution"])
                            )
                        if "department" in pres:
                            try:
                                pres["department"] = pres["institution"][
                                    "departments"
                                ][pres["department"]]
                            except:
                                print(
                                    "WARNING: department {} not found in"
                                    " {} in institutions.yml.  Pres list will"
                                    " build but please check this entry carefully and"
                                    " please add the dept to the institution!".format(
                                        pres["department"],
                                        pres["institution"]["_id"],
                                    )
                                )
                                pres["department"] = {
                                    "name": pres["department"]
                                }
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
                    self.pdf(outfile)
