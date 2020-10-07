"""Builder for Proposal Reviews."""
from datetime import datetime
import time
from nameparser import HumanName
import dateutil.parser as date_parser

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import (month_to_int,
                            get_dates,
                            get_due_date,
                            is_current,
                            is_after,
                            is_before)
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    filter_grants,
    filter_presentations,
    fuzzy_retrieval,
    filter_publications
)

#def subparser(subpi):
#    subpi.add_argument("authorFullName", help="full name of the author of this grant report")
#    subpi.add_argument("start_date", help="start date of the reporting period, formatted as YYYY-MM-DD",
#                       default=None)
#    subpi.add_argument("end_date", help="end date of the reporting period, formatted as YYYY-MM-DD")
#    return subpi


class GrantReportBuilder(LatexBuilderBase):
    """Build a proposal review from database entries"""
    btype = "grantreport"
    needed_dbs = ['presentations', 'projecta', 'people', 'grants',
                  'institutions', 'expenses', 'citations', 'contacts']

#    def __init__(self, rc):
#        super().__init__(rc)
#        self.needed_dbs = needed_dbs

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        for dbs in self.needed_dbs:
            gtx[dbs] = sorted(
                all_docs_from_collection(rc.client, dbs), key=_id_key
            )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        rc = self.rc

        # Convert Date Strings to Datetime Objects
        rp_start_date = date_parser.parse(rc.from_date).date()
        rp_end_date = date_parser.parse(rc.to_date).date()

        # NSF Grant _id
        if isinstance(rc.grants, str):
            rc.grants = [rc.grants]
        grant_name = rc.grants[0]

        # Get prum associated to grant and active during reporting period
        institutions_coll = [inst for inst in self.gtx["institutions"]]
        grant_prums = []
        for prum in self.gtx['projecta']:
            if grant_name in prum['grants']:
                begin_date = get_dates(prum).get('begin_date')
                due_date = get_due_date(prum['deliverable'])
                # if projectum was finished during reporting period or is still current
                # some projectum don't have an "end date", but all projecta have a deliverable
                # due_date
                if (rp_start_date <= due_date <= rp_end_date and prum['status'] is "finished") or is_current(prum):
                    grant_prums.append(prum)
        # Get people associated with grant
        grant_people = list(set([prum['lead'] for prum in grant_prums]))

        # Accomplishments
        major_activities = []
        significant_results = []
        for prum in grant_prums:
            if prum['status'] is "finished":
                significant_results.append(prum)
            else:
                major_activities.append(prum)

        # Opportunities for Training and Professional Development
        training_and_professional_development = []
        # presentations
        for id in grant_people:
            training_and_professional_development.extend(
                filter_presentations(self.gtx["people"], self.gtx["presentations"], institutions_coll, id,
                                     types=["all"], since=rp_start_date, before=rp_end_date, statuses=["accepted"]))
        # thesis defendings
        # how do i access people.yml in rg-db-public vs the people.yml file in rg-db-group?
#        defended_theses = []
#        for id in grant_people:
#            for prsn in self.gtx['people']:
#                if prsn["_id"] != id:
#                    continue
#                else:
#                    person = prsn
#            for education in person['education']:
#                edu_dates = get_dates(education)
#                if 'phd' in education['degree'].lower() and 'columbia' in education['institution'].lower() and \
#                        rp_start_date.year <= edu_dates.get('end_date', edu_dates['date']).year <= rp_end_date.year:
#                    defended_theses.append(id)

        # Products
        # need rg-db-public's citation.yml
        publications = filter_publications(self.gtx["citations"], set(grant_people), since=rp_start_date, before=rp_end_date)

        # Participants/Organizations
        participants = {}
        for id in grant_people:
            for person in self.gtx["people"]:
                if person.get(id) != id:
                    continue
                else:
                    months_on_grant, months_left = self.months_on(grant_name, person, rp_start_date, rp_end_date)
                    participants[id] = [person.get('position'), months_on_grant]

        # Other Collaborators
        collaborator_ids = []
        for prum in grant_prums:
            collabs = prum.get("collaborators")
            if collabs:
                for id in collabs:
                    collaborator_ids.append(id)
        collaborator_ids = set(collaborator_ids)

        collaborators = {}
        for id in collaborator_ids:
            for contact in self.gtx["contacts"]:
                if contact["_id"] == id:
                    name = contact.get("name")
                    aka = contact.get("aka")
                    institution_id = contact.get("institution")
                    institution = fuzzy_retrieval(institutions_coll,
                                                  ["name","aka", "_id"],
                                                  institution_id)
                    if institution:
                        inst_name = institution.get("name")
                    else:
                        print(f"WARNING: institution {institution_id} not found "
                              f"in institutions collection")
                        inst_name = institution_id
                    collaborators[id] = {
                "aka": aka, "name": name,
                "institution": inst_name
            }
        for person in self.gtx["people"]:
            if isinstance(rc.people,str):
                rc.people = [rc.people]
            if person["_id"] == rc.people[0]:
                authorFullName = HumanName(person["name"]).full_name

        # Impacts
        self.render(
            "grantreport.txt",
            "billinge_grant_report.txt",
            authorFullName=authorFullName,
            beginYear=rp_start_date.year,
            endYear=rp_end_date.year,
            majorActivities=major_activities,
            significantResults=significant_results,
            trainingAndProfessionalDevelopment=training_and_professional_development,
#            defendedTheses=defended_theses,
            products=publications,
            grantPeople=grant_people,
            participants=participants,
            collaborators=collaborators
        )

    def months_on(self, grant, person, since=datetime(1970, 1, 1), before=datetime.today()):
        #    print('Looking at months on grant {} in period since {} until {}'.format(
        #        grant, since, before), )
        total_months = 0
        appts = person.get('appointments')
        if appts:
            months = 0
            for k1, v1 in appts.items():
                if grant in v1.get('grant'):
                    dates = get_dates(v1)
                    startdate = dates.get('begin_date')
                    enddate = dates.get('end_date')
                    loading = v1.get('loading')
                    if startdate >= since and enddate <= before:
                        months = months + (
                                enddate - startdate).days * loading / 30.4
                    elif startdate >= since and enddate > before:
                        months = months + (
                                before - startdate).days * loading / 30.4
                    elif startdate < since and enddate <= before:
                        months = months + (
                                enddate - since).days * loading / 30.4
                    elif startdate < since and enddate > before:
                        months = months + (before - since).days * loading / 30.4
            if months > 0:
                total_months = total_months + months
        months_left = (before - datetime.today().date())
        return total_months, months_left
