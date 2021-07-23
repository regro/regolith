from regolith.dates import get_dates
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    get_person_contact,
    _id_key
)
from gooey import GooeyParser

TARGET_COLL = "presentations"
HELPER_TARGET = "l_abstract"


def subparser(subpi):
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        int_kwargs['widget'] = 'IntegerField'
        int_kwargs['gooey_options'] = {'min': 2000, 'max': 2100}

    subpi.add_argument(
        "-a",
        "--author",
        help="Filter abstracts or this author ID (e.g., sbillinge)."
             )
    subpi.add_argument(
        "-y",
        "--year",
        help='Get presentations since this year'
    )
    subpi.add_argument(
        "-l",
        "--loc_inst",
        help='location of presentation, either a fragment of an institution, '
             'country, city, state, or university. If an institution is entered,'
             'the search will be for seminars or colloquiums, otherwise the '
             'search will be for all other meetings')
    subpi.add_argument(
        "-t",
        "--title",
        help='fragment of the title of the abstract or talk to use to '
             'filter presentations')
    return subpi


class AbstractListerHelper(SoutHelperBase):
    """Helper for finding and listing abstracts from the presentations.yml file
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f'{TARGET_COLL}', 'people', 'contacts']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_colls:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        colls = [
            sorted(
                all_docs_from_collection(rc.client, collname), key=_id_key
            )
            for collname in self.needed_colls
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
        SEMINAR_TYPES = ['seminar', 'colloquium']
        filtered_title, filtered_authors, filtered_years, filtered_inst, filtered_loc = ([] for i in range(5))

        if (not rc.author) and (not rc.year) and (not rc.loc_inst) and (not rc.title):
            print("-------------------------------------------")
            print("please rerun specifying at least one filter")
            print("-------------------------------------------")
            return

        if rc.title:
            filtered_title = [presentation for presentation in presentations
                              if rc.title.casefold() in presentation.get('title').casefold()]
        if rc.author:
            filtered_authors = [presentation for presentation in presentations
                                if rc.author in presentation.get('authors')]
        if rc.year:
            filtered_years = [presentation for presentation in presentations
                              if get_dates(presentation).get("date",
                                                             get_dates(presentation).get("end_date",
                                                             get_dates(presentation).get("begin_date"))).year == int(rc.year)]
        if rc.loc_inst:
            filtered_inst = [presentation for presentation in presentations
                             if presentation.get('type') in SEMINAR_TYPES and
                             rc.loc_inst.casefold() in presentation.get('institution',"").casefold()]
            filtered_loc = [presentation for presentation in presentations
                            if rc.loc_inst.casefold() in presentation.get('location',"").casefold()]


        filtered_presentations_by_args = [filtered_inst, filtered_years, filtered_title,
                                          filtered_authors, filtered_loc]
        nonempty_filtered_presentations_by_args = [filtered_presentations
                                                   for filtered_presentations in filtered_presentations_by_args
                                                   if filtered_presentations]
        filtered_presentations = [talk for presentations in nonempty_filtered_presentations_by_args
                                  for talk in presentations
                                  if all(talk in presentations
                                         for presentations in nonempty_filtered_presentations_by_args)]
        flat_filtered_presentations = list({talk['_id']: talk for talk in filtered_presentations}.values())

        for presentation in flat_filtered_presentations:
            print("---------------------------------------")
            print(f"Title: {presentation.get('title')}\n")
            author_list = [author
                           if not get_person_contact(author, self.gtx["people"], self.gtx["contacts"])
                           else get_person_contact(author, self.gtx["people"], self.gtx["contacts"]).get('name')
                           for author in presentation.get('authors')]
            print(", ".join(author_list))
            print(f"\nAbstract: {presentation.get('abstract')}")
        return
