"""Helper for finding and listing abstracts from the presentations.yml database.
Prints author, meeting name(if applicable), location (if applicable), date (if applicable),
and abstract of the presentation.
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
    fuzzy_retrieval,
    search_collection,
)

TARGET_COLL = "presentations"
HELPER_TARGET = "l_abstract"

def subparser(subpi):
    subpi.add_argument(
        "run",
        help='run the lister. To see allowed optional arguments, type "regolith helper l_abstracts".')
    subpi.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increases the verbosity of the output.")
    subpi.add_argument(
        "-a",
        "--author",
        help='authors group ID(single argument only) to use to find presentation abstract.')
    subpi.add_argument(
        "-y",
        "--year",
        help='start or end year of the presentation (single argument only) to use to find presentation abstract.')
    subpi.add_argument(
        "-l",
        "--location",
        help='Location of presentation, either a country, city, state, or university(single argument only).')
    subpi.add_argument(
        "-t",
        "--title",
        help='a word or more from the title of the abstract or talk to use to find presentation in particular.')
    return subpi



class AbstractListerHelper(SoutHelperBase):
    """Helper for finding and listing abstracts from the presentations.yml file
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = [f'{TARGET_COLL}', 'institutions']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
            rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        try:
            if not rc.database:
                rc.database = rc.databases[0]["name"]
        except BaseException:
            pass
        colls = [
            sorted(
                all_docs_from_collection(rc.client, collname), key=_id_key
            )
            for collname in self.needed_dbs
        ]
        for db, coll in zip(self.needed_dbs, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        list_search = []
        collection = self.gtx["presentation"]
        if rc.name:
            list_search.extend(["authors", rc.name])
        if rc.inst:
            list_search.extend(["location", rc.inst])
        if rc.notes:
            list_search.extend(["title", rc.notes])
        if rc.filter:
            list_search.extend(rc.filter)
        filtered_presentations_id = (search_collection(collection, list_search)).strip('    \n')
        filtered_presentations_id = list(filtered_presentations_id.split('    \n'))
        if rc.date:
            date_list = []
            temp_dat = date_parser.parse(rc.date).date()
            temp_dict = {"begin_date": (temp_dat - dateutil.relativedelta.relativedelta(
                                        months=int(rc.range))).isoformat(),
                         "end_date": (temp_dat + dateutil.relativedelta.relativedelta(
                                     months=int(rc.range))).isoformat()}
            for presentation in collection:
                curr_d = get_dates(presentation)['date']
                if is_current(temp_dict, now=curr_d):
                    date_list.append(presentation.get('_id'))
                filtered_presentations_id = [value for value in filtered_presentations_id if value in date_list]
        filtered_presentations = []
        string_presentations = ''
        for presentation in collection:
            if presentation.get('_id') in filtered_presentations_id:
                filtered_presentations.append(presentation)
                institution = presentation.get('institution')
                institution_name = fuzzy_retrieval(self.gtx['institutions'],
                                                   ['name', '_id', 'aka'], institution)
                if institution_name:
                    presentation['institution'] = institution_name.get('name')
                if rc.verbose:
                    contact_str = f"{presentation.get('name')}\n"
                    for k in ['_id', 'email', 'institution', 'department', 'notes', 'aka']:
                        if presentation.get(k):
                            if isinstance(presentation.get(k), list):
                                lst_expanded = '\n        -'.join(map(str, presentation.get(k)))
                                contact_str += f"    {k}:\n        -{lst_expanded}\n"
                            else:
                                contact_str += f"    {k}: {presentation.get(k)}\n"
                    string_presentations += contact_str
                else:
                    string_presentations += f"{presentation.get('name')}  |  {presentation.get('_id')}  |" \
                                       f"  institution: {presentation.get('institution')}  |" \
                                       f"  email: {presentation.get('email', 'missing')}\n"
        print(string_presentations.strip('\n'))
        return
