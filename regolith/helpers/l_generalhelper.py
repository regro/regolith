"""Helper for finding people's information in the people collection
"""

from regolith.helpers.basehelper import SoutHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
    search_collection,
    collection_str,
)
HELPER_TARGET = "lister"
KEYS = {"abstracts":{"firstname": "first name of the author.",
                     "lastname": "last name of the author.",
                     "institution": "name of the institution",
                     "title": "title of the presentation/paper."},
        "assignments":{"category": "such as 'homework' or 'final'",
                       "courses": "ids of the courses that have this assignment"},
        "beamplan":{"project_lead": "The id for person who put out this plan",
                    "project": "The id for the project which the plan belongs to",
                    "begin_date": "The begin date of the beam time.",
                    "end_date": "The end date of the beam time.",
                    "objective":"What to study in the experiments. What goal to achieve."},
        "blog":{"author": "name or AKA of author",
                "title": "full human readable title",
                "year": "Publication year",
                "day": "Publication day",
                "month": "Publication month"},
        "contacts":{"institution": "the institution where they are located.",
                    "department": "Department at the institution",
                    "name": "the person's canonical name"},
        "grades":{"assignment":"assignment id",
                  "course": "course id",
                  "scores": "the number of points earned on each question",
                  "student": "student id"},
        "grants":{"amount": "value of award",
                  "grant_id": "the identifier for this work",
                  "institution": "the host institution for the grant",
                  "program": "the program the work was funded under",
                  "status": "status of the grant",
                  "title": "actual title of proposal / grant"},
        "groups":{"institution": "Name of the host institution",
                  "department": "Name of host department",
                  "name": "Name of the group",
                  "projects": "About line for projects",
                  "email": "Contact email for the group"},
        "institutions":{"aka": "list of all the different names the institution is known by",
                        "city": "the city where the institution is",
                        "country":  "The country where the institution is",
                        "departments": "all the departments and centers and various units in the institution",
                        "name": "the canonical name of the institutions",
                        "zip": "the zip or postal code of the institution"},
        "people":{"active": "If the person is an active member",
                  "name": "Full, canonical name for the person",
                  "position": "such as professor, graduate student, or scientist"},
        "presentations":{"authors": "Author list.",
                         "institution""meeting_name": "full name of the conference or meeting",
                         "title": "title of the presentation"},
        "projects":{"active": "true if the project is active",
                    "name":"name of the project.",
                    "team": "People who are/have been working on this project."},
        "proposalReviews":{"title": "The title of the proposal",
                           "reviewer": "short name of the reviewer.",
                           "status": "the status of the review",
                           "year": "The year the review was submitted"},
        "proposals":{"title":  "actual title of proposal",
                     "pi": "principal investigator name"},
        "refereeReports":{"journal": "name of the journal",
                          "reviewer":"name of person reviewing the paper",
                          "title": "title of the paper under review"},
        "students":{"university_id": "The university identifier for the student"},
        "expenses":{"project": "project or list of projects that this presentation is associated with.",
                    "expense_type": "The type of expense"},
        "projecta":{"lead": "lead of the prum", "name": "name of the Prum",
                    "pi_id":"id of the Principle Investigator"}

        }

def subparser(subpi):
    subpi.add_argument(
        "coll",
        help='collection where the lister is going to run.')
    subpi.add_argument(
        "--kv_filter",
        nargs="+",
        help='search the given collection by key element pairs')
    subpi.add_argument(
        "-r",
        nargs="+",
        help='the name of the fields to return from the search')
    subpi.add_argument(
        "-k", "--keys",
        action="store_true",
        help='list of the available keys and their description')
    return subpi

class GeneralListerHelper(SoutHelperBase):
    """Helper for finding and listing contacts from the contacts.yml file
    """
    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_dbs = ["abstracts", "assignments","beamplan", "beamtime",
                  "beam_time", "beam_proposals","blog","citations",
                  "contacts", "courses", "expenses", "grades", "grants",
                  "groups","institutions", "jobs", "meetings", "news",
                  "patents","people", "presentations", "pronouns",
                  "proposals", "proposalReviews", "projecta", "projects",
                  "reading_lists", "refereeReports","students"]

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if "groups" in self.needed_dbs:
            rc.pi_id = get_pi_id(rc)
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
        coll = self.gtx[rc.coll]
        if not rc.kv_filter and not rc.r and not rc.keys:
            print(collection_str(coll).strip())
        if rc.kv_filter:
            if rc.r:
                print((search_collection(coll, rc.kv_filter, rc.r)).strip())
            else:
                print((search_collection(coll, rc.kv_filter)).strip())
        if rc.keys:
            keys_coll = KEYS.get(rc.coll)
            for i in keys_coll:
                print(f'{i}: {keys_coll[i]}')
        return
