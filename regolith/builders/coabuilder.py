"""Builder for Recent Collaborators."""

import datetime as dt
import os
import sys
import openpyxl
from copy import copy
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from nameparser import HumanName

from regolith.builders.basebuilder import BuilderBase
from regolith.dates import month_to_int
from regolith.sorters import doc_date_key, ene_date_key, position_key
from regolith.tools import all_docs_from_collection, filter_publications, \
    month_and_year, fuzzy_retrieval, is_since


NUM_MONTHS = 48

def mdy_date(month, day, year, **kwargs):
    if isinstance(month, str):
        month = month_to_int(month)
    return dt.date(year, month, day)


def mdy(month, day, year, **kwargs):
    return "{}/{}/{}".format(
        str(month_to_int(month)).zfill(2), str(day).zfill(2), str(year)[-2:]
    )


class RecentCollaboratorsBuilder(BuilderBase):
    """Build recent collaborators from database entries"""

    btype = "recent-collabs"
    needed_dbs = ['citations', 'people', 'contacts', 'institutions']

    def __init__(self, rc):
        super().__init__(rc)
        self.template = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "templates", "coa_template_nsf.xlsx"
        )
        self.template2 = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "templates", "coa_template_doe.xlsx"
        )
        self.cmds = ["excel"]

    def construct_global_ctx(self):
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
        gtx["institutions"] = all_docs_from_collection(rc.client,
                                                       "institutions")
        gtx["citations"] = all_docs_from_collection(rc.client, "citations")
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def excel(self):
        rc = self.rc
        gtx = self.gtx
        # if --to is provided:
        # use self.rc.to_date as the endpoint and find every publications within
        # NUM_MONTHS months of the to_date date
        # Otherwise: find every publication within NUM_MONTHS months from today.
        if isinstance(self.rc.to_date, str):
            since_date = dt.datetime.strptime(self.rc.to_date, '%Y-%m-%d').date() - relativedelta(months=NUM_MONTHS)
        else:
            since_date = dt.date.today() - relativedelta(months=NUM_MONTHS)
        if isinstance(self.rc.people, str):
            self.rc.people = [self.rc.people]
        person = fuzzy_retrieval(all_docs_from_collection(rc.client, "people"),
                                 ['aka', 'name', '_id'], self.rc.people[0],
                                 case_sensitive=False)
        if not person:
            sys.exit("please rerun specifying --people PERSON")
        person_inst = person.get("employment")[0]["organization"]
        person_inst = fuzzy_retrieval(all_docs_from_collection(
            rc.client, "institutions"), ["name", "aka", "_id"],
            person_inst)
        person_inst_name = person_inst.get("name")

        for p in self.gtx["people"]:
            if p["_id"] == person["_id"]:
                my_names = frozenset(p.get("aka", []) + [p["name"]])
                pubs = filter_publications(self.gtx["citations"], my_names,
                                           reverse=True, bold=False)
                my_collabs = []
                for pub in pubs:
                    if is_since(pub.get("year"), since_date.year,
                                pub.get("month", 1), since_date.month):
                        if not pub.get("month"):
                            print("WARNING: {} is missing month".format(
                                pub["_id"]))
                        if pub.get("month") == "tbd".casefold():
                            print("WARNING: month in {} is tbd".format(
                                pub["_id"]))

                        my_collabs.extend([collabs for collabs in
                                           [names for names in
                                            pub.get('author', [])]])
                people, institutions = [], []
                for collab in my_collabs:
                    collab_person = fuzzy_retrieval(all_docs_from_collection(
                        rc.client, "people"),
                        ["name", "aka", "_id"],
                        collab)
                    if not collab_person:
                        collab_person = fuzzy_retrieval(all_docs_from_collection(
                            rc.client, "contacts"),
                            ["name", "aka", "_id"], collab)
                        if not collab_person:
                            print(
                                "WARNING: {} not found in contacts. Check aka".format(
                                   collab))
                        else:
                            people.append(collab_person)
                            inst = fuzzy_retrieval(all_docs_from_collection(
                                rc.client, "institutions"),
                                ["name", "aka", "_id"],
                                collab_person["institution"])
                            if inst:
                                institutions.append(inst["name"])
                            else:
                                institutions.append(collab_person.get("institution", "missing"))
                                print("WARNING: {} missing from institutions".format(
                                       collab_person["institution"]))
                    else:
                        people.append(collab_person)
                        pinst = collab_person.get("employment",
                                           [{"organization": "missing"}])[
                            0]["organization"]
                        inst = fuzzy_retrieval(all_docs_from_collection(
                            rc.client, "institutions"), ["name", "aka", "_id"],
                            pinst)
                        if inst:
                            institutions.append(inst["name"])
                        else:
                            institutions.append(pinst)
                            print(
                                "WARNING: {} missing from institutions".format(
                                    pinst))
                ppl_names = [(collab_person["name"], i) for
                             collab_person, i in zip(people, institutions) if
                             collab_person]
                ppl = []
                # reformatting the name in last name, first name
                for idx in range(len(ppl_names)):
                    names = ppl_names[idx][0].split()
                    last_name = names[-1]
                    first_name = ' '.join(names[:-1])
                    name_reformatted = ', '.join([last_name, first_name])
                    ppl.append((name_reformatted, ppl_names[idx][1]))
                ppl = list(set(ppl))
                # sorting the ppl list
                ppl_sorted = sorted(ppl, key=itemgetter(0))
            emp = p.get("employment", [{"organization": "missing",
                                        "begin_year": 2019}])
            emp.sort(key=ene_date_key, reverse=True)

        def apply_cell_style(cell, style):
            cell.font = style["font"]
            cell.border = style["border"]
            cell.fill = style["fill"]
            cell.alignment = style["alignment"]

        template = self.template
        num_rows = len(ppl)  # number of rows to add to the excel file
        wb = openpyxl.load_workbook(template)
        ws = wb.worksheets[0]
        ws.delete_rows(52, amount=3) # removing the example rows
        ws.move_range("A52:E66", rows=num_rows, cols=0, translate=True)
        style_ref_cell = ws["B51"]
        template_cell_style = {}
        template_cell_style["font"] = copy(style_ref_cell.font)
        template_cell_style["border"] = copy(style_ref_cell.border)
        template_cell_style["fill"] = copy(style_ref_cell.fill)
        template_cell_style["alignment"] = copy(style_ref_cell.alignment)
        col_idx = ["A", "B", "C", "D", "E"]
        for row in range(1, num_rows + 1):
            try:
                ws.unmerge_cells("A{}:E{}".format(row + 51, row + 51))
            except:
                pass
            for idx in range(len(col_idx)):
                apply_cell_style(ws["{}{}".format(col_idx[idx], row + 51)], template_cell_style)
            ws["A{}".format(row + 51)].value = "A:"
            ws["B{}".format(row + 51)].value = ppl_sorted[row - 1][0]
            ws["C{}".format((row + 51))].value = ppl_sorted[row - 1][1]
        ws.delete_rows(51)  # deleting the reference row
        wb.save(os.path.join(self.bldir, "{}_nsf.xlsx".format(person["_id"])))

        template2 = self.template2
        ppl = []
        for t in ppl_names:
            inst = fuzzy_retrieval(
                all_docs_from_collection(rc.client, "institutions"),
                ['aka', 'name', '_id'], t[1],
                case_sensitive=False)
            if inst:
                inst_name = inst.get("name","")
            else:
                inst_name = t[1]
            # remove all people who are in the institution of the person
            if inst_name != person_inst_name:
                name = HumanName(t[0])
                ppl.append((name.last, name.first, t[1]))
        ppl = list(set(ppl))
        ppl.sort(key = lambda x: x[0])
        num_rows = len(ppl)  # number of rows to add to the excel file
        wb = openpyxl.load_workbook(template2)
        ws = wb.worksheets[0]
        for row in range(num_rows):
            ws["A{}".format(row + 8)].value = ppl[row][0]
            ws["B{}".format(row + 8)].value = ppl[row][1]
            ws["C{}".format((row + 8))].value = ppl[row][2]
        wb.save(os.path.join(self.bldir, "{}_doe.xlsx".format(person["_id"])))