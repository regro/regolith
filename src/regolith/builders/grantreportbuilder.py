"""Builder for Grant Reports."""

from datetime import date

import dateutil.parser as date_parser

# from habanero import Crossref
from nameparser import HumanName

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import get_dates, is_current
from regolith.fsclient import _id_key
from regolith.tools import all_docs_from_collection, filter_presentations, fuzzy_retrieval


class GrantReportBuilder(LatexBuilderBase):
    """Build a proposal review from database entries."""

    btype = "grant-report"
    needed_dbs = [
        "presentations",
        "projecta",
        "people",
        "grants",
        "institutions",
        "expenses",
        "citations",
        "contacts",
    ]

    #    def __init__(self, rc):
    #        super().__init__(rc)
    #        self.needed_dbs = needed_dbs

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        for dbs in self.needed_dbs:
            gtx[dbs] = sorted(all_docs_from_collection(rc.client, dbs), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template."""
        rc = self.rc

        if not rc.grants:
            raise RuntimeError("Error: no grant specified. Please rerun specifying a grant")
        if isinstance(rc.grants, str):
            rc.grants = [rc.grants]
        if len(rc.grants) > 1:
            raise RuntimeError("Error: more than one grant specified. Please rerun with" "only a single grant.")
        grant_id = rc.grants[0]
        grant = fuzzy_retrieval(self.gtx["grants"], ["_id", "alias", "name"], grant_id)
        if grant is None:
            raise NameError(f"Grant {grant_id} given but not found. Please check grant name")
        grant_dates = get_dates(grant)

        # Convert Date Strings to Datetime Objects
        if rc.from_date:
            rp_start_date = date_parser.parse(rc.from_date).date()
        else:
            rp_start_date = grant_dates.get("begin_date")
            print(
                f"INFO: no begin-date specified.  running report from the beginning "
                f"of the grant period ({rp_start_date})"
            )
        if rc.to_date:
            rp_end_date = date_parser.parse(rc.to_date).date()
        else:
            rp_end_date = min([date.today(), grant_dates.get("end_date")])
            print(
                "INFO: no end-date specified for the reporting period.  Running "
                "report up to the earlier of the end of the grant, or today "
                f"({rp_end_date})."
            )
        report_dates = {"begin_date": rp_start_date, "end_date": rp_end_date}
        print(
            f"INFO: generating report for grant {grant_id} for the period"
            f"from {rp_start_date} to {rp_end_date})"
        )

        # Get prum associated to grant and active during reporting period
        #        institutions_coll = [inst for inst in self.gtx["institutions"]]
        institutions_coll = self.gtx["institutions"]
        grant_prums = [
            prum
            for prum in self.gtx["projecta"]
            if grant_id in prum.get("grants", [])
            and "checklist" not in prum.get("deliverable").get("scope")
            and "cancelled" not in prum.get("status")
        ]

        grant_prums_finished_this_period = [
            prum for prum in grant_prums if is_current(report_dates, get_dates(prum).get("end_date"))
        ]
        grant_prum_leads = list(set([prum["lead"] for prum in grant_prums]))
        grant_prum_collaborators = list(
            set([collab for prum in grant_prums for collab in prum.get("collaborators", [])])
        )
        list(set([grp_mbr for prum in grant_prums for grp_mbr in prum.get("group_members", [])]))
        grant_people = grant_prum_leads
        # Accomplishments
        major_activities = []
        significant_results = []
        for prum in grant_prums:
            if prum["status"] == "finished":
                continue
            else:
                major_activities.append(prum)
        for prum in grant_prums_finished_this_period:
            significant_results.append(prum)

        # Opportunities for Training and Professional Development
        training_and_professional_development = []
        # presentations
        for id in grant_people:
            training_and_professional_development.extend(
                filter_presentations(
                    self.gtx["people"],
                    self.gtx["presentations"],
                    institutions_coll,
                    id,
                    types=["all"],
                    since=rp_start_date,
                    before=rp_end_date,
                    statuses=["accepted"],
                )
            )
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
        #                if 'phd' in education['degree'].lower() and 'columbia' in \
        #                education['institution'].lower() and rp_start_date.year <= edu_dates.get(\
        #                'end_date', edu_dates['date']).year <= rp_end_date.year:
        #                    defended_theses.append(id)

        # Products
        # need rg-db-public's citation.yml
        #        publications = filter_publications(self.gtx["citations"],
        #                                           set(grant_people),
        #                                           since=rp_start_date,
        #                                          before=rp_end_date)
        publications = [publ for publ in self.gtx["citations"] if grant_id in publ.get("grant", "")]
        publ_ids = []
        for publ in publications:
            publ_ids.append(publ.get("_id"))
            formatted_authors = [f" {HumanName(name).full_name}" for name in publ.get("authors", [])]
            publ["authors"] = formatted_authors
        # Participants/Organizations
        publication_id_string = ", ".join(publ_ids)
        participants = []
        for person in self.gtx["people"]:
            months_on_grant, months_left = self.months_on(grant_id, person, rp_start_date, rp_end_date)
            if months_on_grant > 0:
                participants.append(
                    {
                        "name": person.get("name"),
                        "email": person.get("email"),
                        "position": person.get("position"),
                        "months_on_grant": int(round(months_on_grant, 0)),
                    }
                )

        collaborators = {}
        missing_contacts = []
        for id in grant_prum_collaborators:
            for contact in self.gtx["contacts"]:
                if contact["_id"] == id:
                    name = contact.get("name")
                    aka = contact.get("aka")
                    institution_id = contact.get("institution")
                    institution = fuzzy_retrieval(institutions_coll, ["name", "aka", "_id"], institution_id)
                    if institution:
                        inst_name = institution.get("name")
                    else:
                        print(f"WARNING: institution {institution_id} not found " f"in institutions collection")
                        inst_name = institution_id
                    collaborators[id] = {"aka": aka, "name": name, "institution": inst_name}
        missing_contacts = [id for id in grant_prum_collaborators if not collaborators.get(id)]
        missing_contacts = list(set(missing_contacts))
        for person_id in missing_contacts:
            print(f"WARNING: contact {person_id} not found in contacts collection")

        # Impacts
        begin_date_str = rp_start_date.isoformat()
        end_date_str = rp_end_date.isoformat()
        self.render(
            "grantreport.txt",
            f"{grant_id}_report_{begin_date_str}_{end_date_str}.txt",
            grant=grant,
            begin_date=begin_date_str,
            newline="\n",
            end_date=end_date_str,
            majorActivities=major_activities,
            significantResults=significant_results,
            trainingAndProfessionalDevelopment=training_and_professional_development,
            #            defendedTheses=defended_theses,
            products=publications,
            grantPeople=grant_people,
            participants=participants,
            collaborators=collaborators,
            publication_id_string=publication_id_string,
            hline="------------------------------------------------------------------------------",
        )

    def months_on(self, grant, person, since=date(1970, 1, 1), before=date.today()):
        #    print('Looking at months on grant {} in period since {} until {}'.format(
        #        grant, since, before), )
        total_months = 0
        appts = person.get("appointments")
        if appts:
            months = 0
            for k1, v1 in appts.items():
                if grant in v1.get("grant"):
                    appt_dates = get_dates(v1)
                    overlap_start = max([appt_dates.get("begin_date"), since])
                    overlap_end = min([appt_dates.get("end_date"), before])
                    if overlap_end >= overlap_start:
                        months = months + (overlap_end - overlap_start).days * v1.get("loading") / 30.4
                    # appt_startdate = dates.get('begin_date')
                    # appt_enddate = dates.get('end_date')
                    # loading = v1.get('loading')
                    # if appt_enddate >= since and appt_startdate <= before:
                    #    months = months + (
                    #            app_enddate - appt_startdate).days * loading / 30.4
                    # elif startdate >= since and enddate > before:
                    #    months = months + (
                    #            before - startdate).days * loading / 30.4
                    # elif startdate < since and enddate <= before:
                    #    months = months + (
                    #            enddate - since).days * loading / 30.4
                    # elif startdate < since and enddate > before:
                    #    months = months + (before - since).days * loading / 30.4
            if months > 0:
                total_months = total_months + months
        months_left = before - date.today()
        return total_months, months_left
