"""Helper for listing group members."""

from regolith.dates import get_dates, is_current
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    collection_str,
    fuzzy_retrieval,
    get_pi_id,
    key_value_pair_filter,
    strip_str,
)

TARGET_COLL = "people"
HELPER_TARGET = "l_members"
ALLOWED_STATI = ["proposed", "started", "finished", "back_burner", "paused", "cancelled"]


def subparser(subpi):
    subpi.add_argument("-c", "--current", action="store_true", help="get only current group members ")
    subpi.add_argument("-p", "--prior", action="store_true", help="get only former group members ")
    subpi.add_argument("-v", "--verbose", action="store_true", help="increase verbosity of output")
    subpi.add_argument(
        "-f", "--filter", nargs="+", help="Search this collection by giving key element pairs", type=strip_str
    )
    subpi.add_argument(
        "-k",
        "--keys",
        nargs="+",
        help="Specify what keys to return values from when running "
        "--filter. If no argument is given the default is just the id.",
        type=strip_str,
    )

    return subpi


class MembersListerHelper(SoutHelperBase):
    """Helper for listing group members."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "institutions", "groups"]

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
        gtx = self.gtx
        rc = self.rc
        if rc.filter:
            collection = key_value_pair_filter(self.gtx["people"], rc.filter)
        else:
            collection = self.gtx["people"]
        people = []
        group = fuzzy_retrieval(gtx["groups"], ["_id", "aka", "name"], rc.groupname)
        group_id = group.get("_id")

        if rc.filter:
            if not rc.verbose:
                results = collection_str(collection, rc.keys)
                print(results, end="")
                return
            else:
                for person in collection:
                    print(
                        "{}, {} | group_id: {}".format(
                            person.get("name"), person.get("position"), person.get("_id")
                        )
                    )
                    print("    orcid: {} | github_id: {}".format(person.get("orcid_id"), person.get("github_id")))
                pass
            # code to print verbosely on filtering
        if not rc.filter:
            for person in gtx["people"]:
                if rc.current:
                    if not person.get("active"):
                        continue
                    people.append(person)
                elif rc.prior:
                    if person.get("active"):
                        continue
                    people.append(person)
                else:
                    people.append(person)

        cleaned_people = []
        for person in people:
            not_current_positions = [emp for emp in person.get("employment") if not is_current(emp)]
            not_current_positions.sort(key=lambda x: get_dates(x)["end_date"])
            current_positions = [emp for emp in person.get("employment") if is_current(emp)]
            current_positions.sort(key=lambda x: get_dates(x)["begin_date"])
            positions = not_current_positions + current_positions
            position_keys = [
                position_key(position) for position in positions if position.get("group", "") == group_id
            ]
            if position_keys:
                person["position_key"] = max(position_keys)[0]
                cleaned_people.append(person)
            else:
                print(f"Person {person['name']} has no positions in group {group_id}")
        cleaned_people.sort(key=lambda k: k["position_key"], reverse=True)
        position_names = {
            1: "Undergrads",
            2.5: "Masters Students",
            2: "Visiting Students",
            3: "Graduate Students",
            4: "Post Docs",
            5: "Visitors",
            8: "Assistant Scientists",
            9: "Associate Scientists",
            10: "Scientists",
            11: "PI",
        }
        accounting = 12
        for person in cleaned_people:
            if person.get("position_key") < accounting:
                accounting = person.get("position_key")
                print(f"    -- {position_names.get(accounting, position_names.get(5))} --")
            if rc.verbose:
                print("{}, {}".format(person.get("name"), person.get("position")))
                print("    email: {} | group_id: {}".format(person.get("email"), person.get("_id")))
                print("    github_id: {} | orcid: {}".format(person.get("github_id"), person.get("orcid_id")))
                for position in positions:
                    if is_current(position):
                        inst = fuzzy_retrieval(
                            gtx["institutions"], ["aka", "name", "_id"], position.get("organization")
                        )
                        if inst:
                            instname = inst.get("name")
                        else:
                            print(f"WARNING: {position.get('organization')} not in institutions collection")
                        print("    current organization: {}".format(instname))
                        print(
                            "    current position: {}".format(
                                position.get("full_position", position.get("position").title())
                            )
                        )
                    if not person.get("active"):
                        if position.get("group") == "bg":
                            print("    billinge group position: {}".format(position.get("position")))
            else:
                print("{}".format(person.get("name")))
        return
