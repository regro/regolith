"""Generic builder."""

from copy import copy

from regolith.helpers import a_expensehelper as a_expense
from regolith.helpers import a_grppub_readlisthelper as a_gprl
from regolith.helpers import a_manurevhelper as a_manurev
from regolith.helpers import a_presentationhelper as a_presentation
from regolith.helpers import a_projectumhelper as a_projectum
from regolith.helpers import a_proposalhelper as a_proposal
from regolith.helpers import a_proprevhelper as a_proprev
from regolith.helpers import a_todohelper as a_todo
from regolith.helpers import attestationshelper as attestations
from regolith.helpers import f_todohelper as f_todo
from regolith.helpers import l_abstracthelper as l_abstract
from regolith.helpers import l_contactshelper as l_contacts
from regolith.helpers import l_currentappointmentshelper as l_currentappointments
from regolith.helpers import l_generalhelper as l_general
from regolith.helpers import l_grantshelper as l_grants
from regolith.helpers import l_membershelper as l_members
from regolith.helpers import l_milestoneshelper as l_milestone
from regolith.helpers import l_progressreporthelper as l_progress
from regolith.helpers import l_projectahelper as l_projecta
from regolith.helpers import l_todohelper as l_todo
from regolith.helpers import makeappointmentshelper as makeappointments
from regolith.helpers import reimbstatushelper as reimbstatus
from regolith.helpers import u_contacthelper as u_contact
from regolith.helpers import u_finishprumhelper as u_finishprum
from regolith.helpers import u_institutionshelper as u_institutions
from regolith.helpers import u_logurlhelper as u_logurl
from regolith.helpers import u_milestonehelper as u_milestone
from regolith.helpers import u_todohelper as u_todo
from regolith.helpers import v_meetingshelper as v_meetings

# Updtaer helpers will update the db and should not load all databases but only
# the one specified in rc.database for updating.
UPDATER_HELPERS = {
    "a_expense": (a_expense.ExpenseAdderHelper, a_expense.subparser),
    "a_grppub_readlist": (a_gprl.GrpPubReadListAdderHelper, a_gprl.subparser),
    "a_manurev": (a_manurev.ManuRevAdderHelper, a_manurev.subparser),
    "a_presentation": (a_presentation.PresentationAdderHelper, a_presentation.subparser),
    "a_projectum": (a_projectum.ProjectumAdderHelper, a_projectum.subparser),
    "a_proposal": (a_proposal.ProposalAdderHelper, a_proposal.subparser),
    "a_proprev": (a_proprev.PropRevAdderHelper, a_proprev.subparser),
    "a_todo": (a_todo.TodoAdderHelper, a_todo.subparser),
    "f_prum": (u_finishprum.FinishprumUpdaterHelper, u_finishprum.subparser),
    "f_todo": (f_todo.TodoFinisherHelper, f_todo.subparser),
    "u_contact": (u_contact.ContactUpdaterHelper, u_contact.subparser),
    "u_institution": (u_institutions.InstitutionsUpdaterHelper, u_institutions.subparser),
    "u_logurl": (u_logurl.LogUrlUpdaterHelper, u_logurl.subparser),
    "u_milestone": (u_milestone.MilestoneUpdaterHelper, u_milestone.subparser),
    "u_todo": (u_todo.TodoUpdaterHelper, u_todo.subparser),
}

# Lister helpers need to load collections across all the databases to show everything
LISTER_HELPERS = {
    "l_abstract": (l_abstract.AbstractListerHelper, l_abstract.subparser),
    "l_contacts": (l_contacts.ContactsListerHelper, l_contacts.subparser),
    "l_currentappointments": (
        l_currentappointments.CurrentAppointmentsListerHelper,
        l_currentappointments.subparser,
    ),
    "l_grants": (l_grants.GrantsListerHelper, l_grants.subparser),
    "l_members": (l_members.MembersListerHelper, l_members.subparser),
    "l_milestones": (l_milestone.MilestonesListerHelper, l_milestone.subparser),
    "l_progress": (l_progress.ProgressReportHelper, l_progress.subparser),
    "l_projecta": (l_projecta.ProjectaListerHelper, l_projecta.subparser),
    "l_reimbstatus": (reimbstatus.ReimbstatusHelper, reimbstatus.subparser),
    "l_todo": (l_todo.TodoListerHelper, l_todo.subparser),
    "v_meetings": (v_meetings.MeetingsValidatorHelper, v_meetings.subparser),
    "attestations": (attestations.AttestationsHelper, attestations.subparser),
    "lister": (l_general.GeneralListerHelper, l_general.subparser),
    "makeappointments": (makeappointments.MakeAppointmentsHelper, makeappointments.subparser),
}

HELPERS = copy(LISTER_HELPERS)
HELPERS.update(UPDATER_HELPERS)
# fast_updater updaters only connects to the one requested db, not to all dbs
# in rc.databases which is the default behavior
FAST_UPDATER_WHITELIST = ["u_milestone", "f_prum"]


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype][0](rc)
