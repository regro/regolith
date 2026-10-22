"""Give every service entry in the people collection a uuid.

A builder picks out particular service entries, such as the ones listed
as synergistic activities, by their uuid.  Entries that already have one
keep it, so the helper can be rerun whenever entries have been added by
hand.
"""

from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection, get_uuid

TARGET_COLL = "people"
HELPER_TARGET = "u-service-uuids"


def subparser(subpi):
    subpi.add_argument(
        "people",
        nargs="*",
        help="The ids of the people whose service entries are given uuids. Defaults to everyone.",
    )
    return subpi


def add_missing_uuids(service):
    """Give a uuid to each service entry that lacks one.

    Parameters
    ----------
    service : list of dict
        The service entries of one person, changed in place.

    Returns
    -------
    list of dict
        The entries that were given a uuid.
    """
    given = [entry for entry in service if not entry.get("uuid")]
    for entry in given:
        entry["uuid"] = get_uuid()
    return given


class ServiceUuidsUpdaterHelper(DbHelperBase):
    """Give a uuid to every service entry that lacks one."""

    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        self.rc.coll = f"{TARGET_COLL}"

    def db_updater(self):
        rc = self.rc
        person_ids = rc.people or [person["_id"] for person in all_docs_from_collection(rc.client, rc.coll)]
        dbnames = {person_id: self.where_stored(rc.coll, person_id) for person_id in person_ids}
        unknown = [person_id for person_id, dbname in dbnames.items() if dbname is None]
        if unknown:
            raise ValueError(
                f"These people are not in the people collection: {', '.join(unknown)}. "
                f"Nothing was changed. Please check the ids, which 'regolith helper l_members' will list."
            )
        updated = 0
        for person_id, dbname in dbnames.items():
            person = rc.client.find_one(dbname, rc.coll, {"_id": person_id})
            service = person.get("service", [])
            given = add_missing_uuids(service)
            if not given:
                continue
            rc.client.update_one(dbname, rc.coll, {"_id": person_id}, {"service": service})
            updated += len(given)
            print(f"{person_id}:")
            for entry in given:
                print(f"    {entry['uuid']}  {entry['name']}")
        if updated == 0:
            print("Every service entry already has a uuid.")
        return
