"""Generic builder."""

from regolith.helpers import hellohelper as hello
from regolith.helpers import a_manurevhelper as a_manurev
from regolith.helpers import a_proprevhelper as a_proprev
from regolith.helpers import a_grppub_readlisthelper as a_gprl
from regolith.helpers import a_projectumhelper as a_projectum
from regolith.helpers import a_proposalhelper as a_proposal
from regolith.helpers import a_expensehelper as a_expense
from regolith.helpers import l_milestoneshelper as l_milestone
from regolith.helpers import l_projectahelper as l_projecta
from regolith.helpers import l_grantshelper as l_grants
from regolith.helpers import l_membershelper as l_members
from regolith.helpers import l_contactshelper as l_contacts
from regolith.helpers import u_logurlhelper as u_logurl
from regolith.helpers import u_milestonehelper as u_milestone
from regolith.helpers import makeappointmentshelper as makeappointments
from regolith.helpers import u_contacthelper as u_contact
from regolith.helpers import l_todohelper as l_todo
from regolith.helpers import u_finishprumhelper as u_finishprum
from regolith.helpers import l_generalhelper as l_general
from regolith.helpers import u_institutionshelper as u_institutions
from regolith.helpers import a_todohelper as a_todo
from regolith.helpers import v_meetingshelper as v_meetings

HELPERS = {
    "hello": (hello.HelloHelper, hello.subparser),
    "a_proprev": (a_proprev.PropRevAdderHelper, a_proprev.subparser),
    "a_manurev": (a_manurev.ManuRevAdderHelper, a_manurev.subparser),
    "a_grppub_readlist": (a_gprl.GrpPubReadListAdderHelper, a_gprl.subparser),
    "a_projectum": (a_projectum.ProjectumAdderHelper, a_projectum.subparser),
    "a_proposal": (a_proposal.ProposalAdderHelper, a_proposal.subparser),
    "a_expense": (a_expense.ExpenseAdderHelper, a_expense.subparser),
    "l_milestones": (l_milestone.MilestonesListerHelper, l_milestone.subparser),
    "l_projecta": (l_projecta.ProjectaListerHelper, l_projecta.subparser),
    "l_grants": (l_grants.GrantsListerHelper, l_grants.subparser),
    "l_members": (l_members.MembersListerHelper, l_members.subparser),
    "l_contacts": (l_contacts.ContactsListerHelper, l_contacts.subparser),
    "u_logurl": (u_logurl.LogUrlUpdaterHelper, u_logurl.subparser),
    "u_contact": (u_contact.ContactUpdaterHelper, u_contact.subparser),
    "u_milestone": (u_milestone.MilestoneUpdaterHelper, u_milestone.subparser),
    "l_todo": (l_todo.TodoListerHelper, l_todo.subparser),
    "finish_prum": (u_finishprum.FinishprumUpdaterHelper, u_finishprum.subparser),
    "lister": (l_general.GeneralListerHelper, l_general.subparser),
    "u_institution": (u_institutions.InstitutionsUpdaterHelper, u_institutions.subparser),
    "a_todo": (a_todo.TodoAdderHelper, a_todo.subparser),
    "makeappointments": (makeappointments.MakeAppointmentsHelper, makeappointments.subparser),
    "v_meetings": (v_meetings.MeetingsValidatorHelper, v_meetings.subparser)
}


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype][0](rc)
