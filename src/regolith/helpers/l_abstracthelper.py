import operator

from gooey import GooeyParser

from regolith.dates import get_dates
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import (
    all_docs_from_collection,
    dereference_institution,
    get_person_contact,
    get_pi_id,
    strip_str,
)

TARGET_COLL = "presentations"
HELPER_TARGET = "l_abstract"


def subparser(subpi):
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        int_kwargs["widget"] = "IntegerField"
        int_kwargs["gooey_options"] = {"min": 2000, "max": 2100}

    subpi.add_argument(
        "-a", "--author", help="Filter abstracts or this author ID (e.g., sbillinge).", type=strip_str
    )
    subpi.add_argument("-y", "--year", help="Get presentations since this year", type=strip_str)
    subpi.add_argument(
        "-l",
        "--loc-inst",
        help="location of presentation, either a fragment of an institution, "
        "country, city, state, or university. If an institution is entered,"
        "the search will be for seminars or colloquiums, otherwise the "
        "search will be for all other meetings",
        type=strip_str,
    )
    subpi.add_argument(
        "-t",
        "--title",
        type=strip_str,
        help="fragment of the title of the abstract or talk to use to " "filter presentations",
    )
    return subpi


class AbstractListerHelper(SoutHelperBase):
    """Helper for finding and listing abstracts from the
    presentations.yml file."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "people", "contacts", "institutions"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        colls = [
            sorted(all_docs_from_collection(rc.client, collname), key=_id_key) for collname in self.needed_colls
        ]
        for db, coll in zip(self.needed_colls, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc

        presentations = self.gtx["presentations"]
        institutions = self.gtx["institutions"]
        SEMINAR_TYPES = ["seminar", "colloquium"]
        filtered_title, filtered_authors, filtered_years, filtered_inst, filtered_loc = ([] for i in range(5))

        if (not rc.author) and (not rc.year) and (not rc.loc_inst) and (not rc.title):
            print("-------------------------------------------")
            print("please rerun specifying at least one filter")
            print("-------------------------------------------")
            return

        if rc.title:
            filtered_title = [
                presentation
                for presentation in presentations
                if rc.title.casefold() in presentation.get("title").casefold()
            ]
        else:
            filtered_title = [presentation for presentation in presentations]

        if rc.author:
            filtered_authors = [
                presentation for presentation in filtered_title if rc.author in presentation.get("authors")
            ]
        else:
            filtered_authors = filtered_title

        if rc.year:
            filtered_years = [
                presentation
                for presentation in filtered_authors
                if get_dates(presentation)
                .get("date", get_dates(presentation).get("end_date", get_dates(presentation).get("begin_date")))
                .year
                == int(rc.year)
            ]
        else:
            filtered_years = filtered_authors

        if rc.loc_inst:
            filtered_inst = [
                presentation
                for presentation in filtered_years
                if presentation.get("type") in SEMINAR_TYPES
                and rc.loc_inst.casefold() in presentation.get("institution", "").casefold()
            ]
            filtered_loc = [
                presentation
                for presentation in filtered_years
                if rc.loc_inst.casefold() in presentation.get("location", "").casefold()
            ]
        else:
            filtered_inst = filtered_years
            filtered_loc = filtered_years

        filtered_presentations_by_args = [filtered_inst, filtered_loc]

        nonempty_filtered_presentations_by_args = [
            filtered_presentations
            for filtered_presentations in filtered_presentations_by_args
            if filtered_presentations
        ]
        filtered_presentations = [
            talk
            for presentations in nonempty_filtered_presentations_by_args
            for talk in presentations
            if all(talk in presentations for presentations in nonempty_filtered_presentations_by_args)
        ]
        for talk in filtered_presentations:
            talk.update(
                {
                    "meeting_date": get_dates(talk).get(
                        "date", get_dates(talk).get("end_date", get_dates(talk).get("begin_date"))
                    )
                }
            )
        filtered_presentations_sorted = sorted(filtered_presentations, key=operator.itemgetter("meeting_date"))
        flat_filtered_presentations = list({talk["_id"]: talk for talk in filtered_presentations_sorted}.values())
        for presentation in flat_filtered_presentations:
            if presentation.get("type") in SEMINAR_TYPES:
                dereference_institution(presentation, institutions)
                meeting_info = (
                    f"{presentation.get('type').title()} {presentation.get('department')}, "
                    f"{presentation.get('institution')}"
                )
            else:
                meeting_info = f"{presentation.get('meeting_name')}, {presentation.get('location')}"
            print("\n---------------------------------------")
            print(f"{presentation.get('meeting_date').isoformat()} - {meeting_info}")
            print("---------------------------------------")
            print(f"Title: {presentation.get('title')}\n")
            author_list = [
                (
                    author
                    if not get_person_contact(author, self.gtx["people"], self.gtx["contacts"])
                    else get_person_contact(author, self.gtx["people"], self.gtx["contacts"]).get("name")
                )
                for author in presentation.get("authors")
            ]
            print(", ".join(author_list))
            print(f"\nAbstract: {presentation.get('abstract')}")
        return
