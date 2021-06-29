"""Helper for adding a presentation to the presentation collection.
"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
)
from argparse import ArgumentParser

TARGET_COLL = "presentations"
ALLOWED_TYPES = ["award", "keynote", "plenary", "invited", "contributed_oral",
                 "poster", "colloquium", "seminar","other"]
ALLOWED_STATI = ["in-prep", "submitted", "accepted", "declined",
                         "cancelled"]


def subparser(subpi):

    subpi.add_argument("place", help="the place of the presentation, location if conference,"
                                     "institution for seminars"
                       )
    subpi.add_argument("name", help="name of the presentation, meeting name if meeting,"
                                    "department if seminar",
                       )
    subpi.add_argument("-p", "--person",
                       help="the person submitting the presentation, used for presentation name,"
                            " defaults to name in user.config",
                       )
    subpi.add_argument("-t", "--title",
                       help="the title of the presentation, default is tbd",
                       default='tbd'
                       )
    subpi.add_argument("-a", "--abstract",
                       help="abstract of the presentation, defaults to tbd",
                       default='tbd'
                       )
    subpi.add_argument("-s", "--status",
                       choices=ALLOWED_STATI,
                       help=f"status, from {ALLOWED_STATI}, default is accepted",
                       default="accepted"
                       )
    subpi.add_argument("-y", "--type",
                       choices=ALLOWED_TYPES,
                       help=f"types, from {ALLOWED_TYPES}. Default",
                       default="invited"
                       )
    subpi.add_argument("-w", "--webinar", help=f"true if the presentation was a "
                                               f"webinar. Default False",
                       action="store_true"
                       )
    subpi.add_argument("-u", "--authors", nargs="+",
                       help="specify the authors of this presentation, "
                            "defaults to person submitting the presentation",
                       )
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file."
                       )
    if isinstance(subpi, ArgumentParser):
        subpi.add_argument("begin_date",
                           help="Input begin date for this presentation "
                                "in YYYY-MM-DD format",
                           )
        subpi.add_argument("end_date",
                           help="Input end date for this presentation"
                                "in YYYY-MM-DD format",
                           )
    else:
        subpi.add_argument("begin_date",
                           help="Input begin date for this presentation ",
                           widget='DateChooser'
                           )
        subpi.add_argument("end_date",
                           help="Input end date for this presentation",
                           widget='DateChooser'
                           )
    return subpi



class PresentationAdderHelper(DbHelperBase):
    """Helper for adding presentations"
    """
    # btype must be the same as helper target in helper.py
    btype = "a_presentation"
    needed_dbs = [f'{TARGET_COLL}', 'groups', 'people']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(
            all_docs_from_collection(rc.client, rc.coll), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        gtx = self.gtx
        rc = self.rc
        # dates

        begin_date = date_parser.parse(rc.begin_date).date()
        end_date = date_parser.parse(rc.end_date).date()

        # User specifies person in CL or in config.json
        if not rc.person:
            try:
                rc.person = rc.default_user_id
            except AttributeError:
                raise RuntimeError(
                    "WARNING: no person been set. please rerun specifying authors,"
                    "or add your id, e.g., sbillinge, to the config.json file in ~/.config/regolith"
                )

        key = f"{str(begin_date.year)[2:]}{str(begin_date.strftime('%m'))}{rc.person[0:2]}_{''.join(rc.place.casefold().split()).strip()}"
        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError(
                "This entry appears to already exist in the collection")
        else:
            pdoc = {}


        if not rc.authors:
            authors = [rc.person]
        else:
            authors = rc.authors

        pdoc.update({'_id': key,
                     'abstract': rc.abstract,
                     'authors': authors,
                     'begin_date': begin_date,
                     'end_date': end_date,
                     })
        if rc.webinar:
            pdoc.update({"webinar": True})
        if rc.type in ['seminar', 'colloquium']:
            pdoc.update({"institution": rc.place,
                        "department": rc.name})
        else:
            pdoc.update({"location": rc.place,
                        "meeting_name": rc.name})
        pdoc.update({"project": ['all'],
                     "status": rc.status,
                     "title": rc.title,
                     "type": rc.type,
                     })

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return
