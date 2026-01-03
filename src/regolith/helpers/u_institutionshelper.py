"""Helper for updating/adding  to the projecta collection."""

import datetime as dt
import uuid

from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection, fragment_retrieval

TARGET_COLL = "institutions"


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument(
        "institution_id",
        help="id of the institution, e.g., columbiau. "
        "If an index is not specified, this will return "
        "a numbered list of all institutions that contain this id "
        "fragment.  Specify -i # to update institution number # "
        "in the list. #1 is always used for a new institution.",
    )
    subpi.add_argument("-i", "--index", help="Index of the item in the enumerated list to update.", type=int)
    subpi.add_argument("-n", "--name", help="Full name of the institution")
    subpi.add_argument("--city", help="The city where the institution is. " "Required for a new institution.")
    subpi.add_argument(
        "--state",
        help="The state where the institution is. "
        "Required for a new institution if institution's country is US.",
    )
    subpi.add_argument(
        "--zip",
        help="zipcode of the institution. " "Required for a new institution if institution's country is US.",
    )
    subpi.add_argument("--country", help="The country where the institution is. " "Required for a new institution")
    subpi.add_argument(
        "-a", "--aka", nargs="+", help="List of all the different names this " "institution is known by."
    )
    subpi.add_argument("--dept-id", help="dept_id, e.g. physics.")
    subpi.add_argument(
        "--dept-name",
        help="Department canonical name, e.g., Department of Physics. "
        "Required if --dept-id supplied and it is a new department",
    )
    subpi.add_argument("--dept-aka", nargs="+", help="Department aliases, e.g., Physics Dept.")
    subpi.add_argument("--school-id", help="id for the school, e.g., SEAS.")
    subpi.add_argument(
        "--school-name",
        help="Full canonical name, e.g., School of Engineering and Applied Science. "
        "Required if --school-id supplied and it is a new school",
    )
    subpi.add_argument("--school-aka", nargs="+", help="School aliases.")
    # Do not delete --database arg
    subpi.add_argument(
        "--database",
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
    )
    # Do not delete --date arg
    subpi.add_argument(
        "--date", help="The date when the institution was created. " "Defaults to today's date.", **date_kwargs
    )
    return subpi


class InstitutionsUpdaterHelper(DbHelperBase):
    """Helper for updating/adding  to the projecta collection."""

    # btype must be the same as helper target in helper.py
    btype = "u_institution"
    needed_colls = [f"{TARGET_COLL}"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        key = rc.institution_id
        filterid = {"_id": key}
        target_inst = rc.client.find_one(rc.database, rc.coll, filterid)
        now = dt.datetime.today()
        pdoc = {}
        departments = {}
        schools = {}
        if target_inst:
            if rc.aka:
                current_aka = target_inst.get("aka")
                current_aka.extend(rc.aka)
                pdoc.update({"aka": current_aka})
            departments = target_inst.get("departments", {})
            schools = target_inst.get("schools", {})
        else:
            inst = fragment_retrieval(self.gtx["institutions"], ["_id", "name", "aka"], rc.institution_id)
            inst.sort(key=lambda x: x["_id"], reverse=False)
            if not rc.index:
                print("Please rerun the helper specifying '-n list-index' to update item number 'list-index':")
                print(f"1. {key} as a new institution.")
                for i in range(len(inst)):
                    print(f"{i+2}. {inst[i].get('_id')}      {inst[i].get('name')}.")
                return
            if rc.index < 1 or rc.index > len(inst) + 1:
                raise RuntimeError("Sorry, you picked an invalid number.")
            if rc.index == 1:
                if not rc.name or not rc.city or not rc.country:
                    raise RuntimeError("Name, city, and country are required for a new institution.")
                if rc.country == "US":
                    if not rc.zip or not rc.state:
                        raise RuntimeError(
                            "Zip and state are required for a new institution " "if institutions is in the US."
                        )
                pdoc.update({"name": rc.name, "uuid": str(uuid.uuid4())})
                if rc.aka:
                    pdoc.update({"aka": rc.aka})
                if rc.date:
                    pdoc.update({"date": rc.date})
                else:
                    pdoc.update({"date": now.date()})
            else:
                chosen_inst = inst[rc.index - 2]
                key = chosen_inst.get("_id")
                if rc.aka:
                    current_aka = chosen_inst.get("aka")
                    current_aka.extend(rc.aka)
                    pdoc.update({"aka": current_aka})
                current_departments = chosen_inst.get("departments")
                for k, v in current_departments.items():
                    info_department = {"name": v.get("name"), "aka": v.get("aka")}
                    departments.update({k: info_department})
                current_schools = chosen_inst.get("schools")
                for k, v in current_schools.items():
                    info_school = {"name": v.get("name"), "aka": v.get("aka")}
                    schools.update({k: info_school})
        if rc.city:
            pdoc.update({"city": rc.city})
        if rc.state:
            pdoc.update({"state": rc.state})
        if rc.country:
            pdoc.update({"country": rc.country})
        if rc.zip:
            pdoc.update({"zip": rc.zip})
        if rc.date:
            pdoc.update({"updated": rc.date})
        else:
            pdoc.update({"updated": now})
        # departments:
        if rc.dept_id:
            dep = {}
            if rc.dept_id in departments:
                doc = departments.get(rc.dept_id)
                current_dept_aka = doc.get("aka")
                if rc.dept_name:
                    dep.update({"name": rc.dept_name})
                if rc.dept_aka:
                    current_dept_aka.extend(rc.dept_aka)
                    doc.update({"aka": current_dept_aka})
                departments.update({rc.dept_id: doc})
            else:
                if not rc.dept_name:
                    raise RuntimeError("Name is required for a new department.")
                dep.update({"name": rc.dept_name})
                if rc.dept_aka:
                    dep.update({"aka": rc.dept_aka})
                departments[rc.dept_id] = dep
            pdoc.update({"departments": departments})
        # schools
        if rc.school_id:
            school = {}
            if rc.school_id in schools:
                doc = schools.get(rc.school_id)
                if rc.school_name:
                    doc.update({"name": rc.school_name})
                current_sc_aka = doc.get("aka")
                if rc.dept_aka:
                    current_sc_aka.extend(rc.school_aka)
                    doc.update({"aka": current_sc_aka})
                schools.update({rc.school_id: doc})
            else:
                if not rc.school_name:
                    raise RuntimeError("Name is required for a new school.")
                school.update({"name": rc.school_name})
                if rc.school_aka:
                    school.update({"aka": rc.school_aka})
                schools[rc.school_id] = school
                pdoc.update({"schools": schools})
        rc.client.update_one(rc.database, rc.coll, {"_id": key}, pdoc)
        print(f"{key} has been updated/added in institutions")
        return
