"""Builder for Recent Collaborators."""

import datetime as dt
import os
import sys
from copy import copy
from operator import itemgetter

import openpyxl
from dateutil.relativedelta import relativedelta
from nameparser import HumanName

from regolith.builders.basebuilder import BuilderBase
from regolith.dates import month_to_int
from regolith.sorters import position_key
from regolith.tools import all_docs_from_collection, filter_publications, \
    fuzzy_retrieval, is_since

NUM_MONTHS = 48


def mdy_date(month, day, year, **kwargs):
    """Make a date object."""
    if isinstance(month, str):
        month = month_to_int(month)
    return dt.date(year, month, day)


def mdy(month, day, year, **kwargs):
    """Format the date to a string mm/dd/yy."""
    return "{}/{}/{}".format(
        str(month_to_int(month)).zfill(2), str(day).zfill(2), str(year)[-2:]
    )


def filter_since_date(pubs, since_date):
    """Filter the publications after the since_date."""
    for pub in pubs:
        if is_since(pub.get("year"), since_date.year,
                    pub.get("month", 1), since_date.month):
            if not pub.get("month"):
                print("WARNING: {} is missing month".format(
                    pub["_id"]))
            if pub.get("month") == "tbd".casefold():
                print("WARNING: month in {} is tbd".format(
                    pub["_id"]))
            yield pub


def get_since_date(rc):
    """Get the since_date from command."""
    if isinstance(rc, str):
        since_date = dt.datetime.strptime(rc, '%Y-%m-%d').date() - relativedelta(months=NUM_MONTHS)
    else:
        since_date = dt.date.today() - relativedelta(months=NUM_MONTHS)
    return since_date


def get_coauthors_from_pubs(pubs):
    """Get co-authors' names from the publication."""
    my_collabs = []
    for pub in pubs:
        my_collabs.extend(
            [
                collabs for collabs in
                (names for names in pub.get('author', []))
            ]
        )
    return my_collabs


def get_recent_org(person_info):
    if "employment" in person_info:
        employment = person_info["employment"]
        # sort by end_year
        employment = sorted(
            employment,
            key=lambda d: d.get("end_year", float('inf')),
            reverse=True)
        organization = employment[0].get('organization', 'missing')
    else:
        organization = "missing"
    return organization


def query_people_and_instituions(rc, names):
    """Get the people and institutions names."""
    people, institutions = [], []
    for person_name in names:
        person_found = fuzzy_retrieval(all_docs_from_collection(
            rc.client, "people"),
            ["name", "aka", "_id"],
            person_name)
        if not person_found:
            person_found = fuzzy_retrieval(all_docs_from_collection(
                rc.client, "contacts"),
                ["name", "aka", "_id"], person_name)
            if not person_found:
                print(
                    "WARNING: {} not found in contacts or people. Check aka".format(
                        person_name))
            else:
                people.append(person_found['name'])
                inst = fuzzy_retrieval(all_docs_from_collection(
                    rc.client, "institutions"),
                    ["name", "aka", "_id"],
                    person_found["institution"])
                if inst:
                    institutions.append(inst["name"])
                else:
                    institutions.append(person_found.get("institution", "missing"))
                    print("WARNING: {} missing from institutions".format(
                        person_found["institution"]))
        else:
            people.append(person_found['name'])
            pinst = get_recent_org(person_found)
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
    return people, institutions


def format_last_first_instutition_names(rc, ppl_names, excluded_inst_name=None):
    """Get the last name, first name and institution name."""
    ppl = []
    for ppl_tup in ppl_names:
        inst = fuzzy_retrieval(
            all_docs_from_collection(rc.client, "institutions"),
            ['aka', 'name', '_id'], ppl_tup[1],
            case_sensitive=False)
        if inst:
            inst_name = inst.get("name", "")
        else:
            inst_name = ppl_tup[1]
        # remove all people who are in the institution of the person
        if inst_name != excluded_inst_name:
            name = HumanName(ppl_tup[0])
            ppl.append((name.last, name.first, ppl_tup[1]))
    ppl = list(set(ppl))
    ppl.sort(key=lambda x: x[0])
    return ppl


def format_people_name(ppl_names):
    """Format people name to be first name, last name."""
    ppl = []
    # reformatting the name in last name, first name
    for idx in range(len(ppl_names)):
        names = ppl_names[idx][0].split()
        last_name = names[-1]
        first_name = ' '.join(names[:-1])
        name_reformatted = ', '.join([last_name, first_name])
        ppl.append((name_reformatted, ppl_names[idx][1]))
    return list(set(ppl))


def apply_cell_style(*cells, style):
    """Apply the format to cells."""
    for cell in cells:
        cell.font = style["font"]
        cell.border = style["border"]
        cell.fill = style["fill"]
        cell.alignment = style["alignment"]
    return


def copy_cell_style(style_ref_cell):
    """Copy the cell format to a dictionary."""
    template_cell_style = {
        "font": copy(style_ref_cell.font),
        "border": copy(style_ref_cell.border),
        "fill": copy(style_ref_cell.fill),
        "alignment": copy(style_ref_cell.alignment)
    }
    return template_cell_style


def is_merged(cell):
    """Whether the cell is merged."""
    return True if type(cell).__name__ == 'MergedCell' else False


def find_merged_cell(cells):
    """Find the index of all merged cells."""
    i, j = 0, 0
    lst = []
    while i < len(cells):
        if is_merged(cells[i]):
            while j < len(cells):
                if is_merged(cells[j]):
                    j += 1
                else:
                    i = j
                    break
            lst.append((i, j - 1))
        else:
            i += 1
    return lst


def unmerge(ws, cells):
    """Unmerge the cells."""
    lst = find_merged_cell(cells)
    for start, end in lst:
        ws.unmerge_cells("{}:{}").format(cells[start].coordinate, cells[end].coordinate)
    return


class RecentCollaboratorsBuilder(BuilderBase):
    """Build recent collaborators from database entries"""
    btype = "recent-collabs"
    needed_dbs = ['citations', 'people', 'contacts', 'institutions']

    def __init__(self, rc):
        """Initiate the class instance."""
        super().__init__(rc)
        self.template = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "templates", "coa_template_nsf.xlsx"
        )
        self.template2 = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "templates", "coa_template_doe.xlsx"
        )
        self.cmds = ["excel"]

    def construct_global_ctx(self):
        """Construct the global ctx including database and methods."""
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

    def query_ppl(self, target, **filters):
        """Query the data base for the target's collaborators' information."""
        person = fuzzy_retrieval(all_docs_from_collection(self.rc.client, "people"),
                                 ['aka', 'name', '_id'], target,
                                 case_sensitive=False)
        if not person:
            sys.exit("please rerun specifying --people PERSON")
        person_inst_abbr = person.get("employment")[0]["organization"]
        person_inst = fuzzy_retrieval(all_docs_from_collection(
            self.rc.client, "institutions"), ["name", "aka", "_id"],
            person_inst_abbr)
        if person_inst is not None:
            person_inst_name = person_inst.get("name")
        else:
            person_inst_name = person_inst_abbr
            print(f"WARNING: {person_inst_abbr} is not found in institutions.")
        for p in self.gtx["people"]:
            if p["_id"] == person["_id"]:
                my_names = frozenset(p.get("aka", []) + [p["name"]])
                pubs = filter_publications(
                    self.gtx["citations"],
                    my_names,
                    reverse=True,
                    bold=False
                )
                if 'since_date' in filters:
                    since_date = filters.get('since_date')
                    pubs = filter_since_date(pubs, since_date)
                my_collabs = get_coauthors_from_pubs(pubs)
                people, institutions = query_people_and_instituions(self.rc, my_collabs)
                ppl_names = list(zip(people, institutions))
                ppl = format_people_name(ppl_names)
                # sorting the ppl list
                ppl_sorted = sorted(ppl, key=itemgetter(0))
                ppl_names2 = format_last_first_instutition_names(self.rc, ppl_names)
                break
        else:
            print("Warning: No such person in people: {}".format(person['_id']))
            ppl_sorted = []
            ppl_names2 = []
        results = {
            'person_info': person,
            'person_institution_name': person_inst_name,
            'ppl_2tups': ppl_sorted,
            'ppl_3tups': ppl_names2,
        }
        return results

    @staticmethod
    def add_ppl_2tups(ws, ppl_2tups, start_row=37, row_to_merge=40, format_ref_cell='B37', cols='ABCDE'):
        """Add the information in person, institution pairs into the table 4 in nsf table."""
        template_cell_style = copy_cell_style(ws[format_ref_cell])
        ws.unmerge_cells("A40:E40")
        more_rows = len(ppl_2tups) - 2
        if more_rows > 0:
            ws.insert_rows(start_row, amount=more_rows)
        for row, tup in enumerate(ppl_2tups, start=start_row):
            cells = [ws['{}{}'.format(col, row)] for col in cols]
            apply_cell_style(*cells, style=template_cell_style)
            cells[0].value = "A:"
            cells[1].value = tup[0]
            cells[2].value = tup[1]
        header_row = row_to_merge + more_rows - 1
        ws.merge_cells("A{}:E{}".format(header_row, header_row))
        return

    def render_template1(self, person_info, ppl_2tups, **kwargs):
        """Render the nsf template."""
        template = self.template
        wb = openpyxl.load_workbook(template)
        ws = wb.worksheets[0]
        self.add_ppl_2tups(ws, ppl_2tups)
        wb.save(os.path.join(self.bldir, "{}_nsf.xlsx".format(person_info["_id"])))

    def render_template2(self, person_info, ppl_3tups, **kwargs):
        """Render the doe template."""
        template2 = self.template2
        num_rows = len(ppl_3tups)
        wb = openpyxl.load_workbook(template2)
        ws = wb.worksheets[0]
        for row in range(num_rows):
            ws["A{}".format(row + 8)].value = ppl_3tups[row][0]
            ws["B{}".format(row + 8)].value = ppl_3tups[row][1]
            ws["C{}".format((row + 8))].value = ppl_3tups[row][2]
        wb.save(os.path.join(self.bldir, "{}_doe.xlsx".format(person_info["_id"])))

    def excel(self):
        """Query data base and build nsf and doe excels."""
        rc = self.rc
        if isinstance(rc, str):
            rc.people = [rc.people]
        since_date = get_since_date(rc)
        target = rc.people[0]
        query_results = self.query_ppl(target, since_date=since_date)
        self.render_template1(**query_results)
        self.render_template2(**query_results)
