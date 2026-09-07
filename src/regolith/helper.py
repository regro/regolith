"""Generic helper."""

from regolith.lazy import LazyRegistry

# The import path of each helper and its subparser rather than the objects
# themselves, so that running one helper imports only that one.  See
# regolith.lazy for why.
# Updater helpers will update the db and should not load all databases but
# only the one specified in rc.database for updating.
UPDATER_HELPER_SPECS = {
    "a_expense": (
        "regolith.helpers.a_expensehelper:ExpenseAdderHelper",
        "regolith.helpers.a_expensehelper:subparser",
    ),
    "mc_sync": (
        "regolith.helpers.mcsynchelper:MCSyncHelper",
        "regolith.helpers.mcsynchelper:subparser",
    ),
    "a_mcproject": (
        "regolith.helpers.a_mcprojecthelper:MCProjectAdderHelper",
        "regolith.helpers.a_mcprojecthelper:subparser",
    ),
    "a_grppub_readlist": (
        "regolith.helpers.a_grppub_readlisthelper:GrpPubReadListAdderHelper",
        "regolith.helpers.a_grppub_readlisthelper:subparser",
    ),
    "a_manurev": (
        "regolith.helpers.a_manurevhelper:ManuRevAdderHelper",
        "regolith.helpers.a_manurevhelper:subparser",
    ),
    "a_presentation": (
        "regolith.helpers.a_presentationhelper:PresentationAdderHelper",
        "regolith.helpers.a_presentationhelper:subparser",
    ),
    "a_projectum": (
        "regolith.helpers.a_projectumhelper:ProjectumAdderHelper",
        "regolith.helpers.a_projectumhelper:subparser",
    ),
    "a_proposal": (
        "regolith.helpers.a_proposalhelper:ProposalAdderHelper",
        "regolith.helpers.a_proposalhelper:subparser",
    ),
    "a_proprev": (
        "regolith.helpers.a_proprevhelper:PropRevAdderHelper",
        "regolith.helpers.a_proprevhelper:subparser",
    ),
    "a_todo": (
        "regolith.helpers.a_todohelper:TodoAdderHelper",
        "regolith.helpers.a_todohelper:subparser",
    ),
    "f_prum": (
        "regolith.helpers.u_finishprumhelper:FinishprumUpdaterHelper",
        "regolith.helpers.u_finishprumhelper:subparser",
    ),
    "f_todo": (
        "regolith.helpers.f_todohelper:TodoFinisherHelper",
        "regolith.helpers.f_todohelper:subparser",
    ),
    "u_contact": (
        "regolith.helpers.u_contacthelper:ContactUpdaterHelper",
        "regolith.helpers.u_contacthelper:subparser",
    ),
    "u_institution": (
        "regolith.helpers.u_institutionshelper:InstitutionsUpdaterHelper",
        "regolith.helpers.u_institutionshelper:subparser",
    ),
    "u_logurl": (
        "regolith.helpers.u_logurlhelper:LogUrlUpdaterHelper",
        "regolith.helpers.u_logurlhelper:subparser",
    ),
    "u_milestone": (
        "regolith.helpers.u_milestonehelper:MilestoneUpdaterHelper",
        "regolith.helpers.u_milestonehelper:subparser",
    ),
    "u_todo": (
        "regolith.helpers.u_todohelper:TodoUpdaterHelper",
        "regolith.helpers.u_todohelper:subparser",
    ),
}

# Lister helpers need to load collections across all the databases to show
# everything
LISTER_HELPER_SPECS = {
    "l_abstract": (
        "regolith.helpers.l_abstracthelper:AbstractListerHelper",
        "regolith.helpers.l_abstracthelper:subparser",
    ),
    "l_contacts": (
        "regolith.helpers.l_contactshelper:ContactsListerHelper",
        "regolith.helpers.l_contactshelper:subparser",
    ),
    "l_currentappointments": (
        "regolith.helpers.l_currentappointmentshelper:CurrentAppointmentsListerHelper",
        "regolith.helpers.l_currentappointmentshelper:subparser",
    ),
    "l_grants": (
        "regolith.helpers.l_grantshelper:GrantsListerHelper",
        "regolith.helpers.l_grantshelper:subparser",
    ),
    "u_mcproject": (
        "regolith.helpers.u_mcprojecthelper:MCProjectUpdaterHelper",
        "regolith.helpers.u_mcprojecthelper:subparser",
    ),
    "l_mcgoals": (
        "regolith.helpers.l_mcgoalshelper:MCGoalsListerHelper",
        "regolith.helpers.l_mcgoalshelper:subparser",
    ),
    "l_mcprojects": (
        "regolith.helpers.l_mcprojectshelper:MCProjectsListerHelper",
        "regolith.helpers.l_mcprojectshelper:subparser",
    ),
    "l_members": (
        "regolith.helpers.l_membershelper:MembersListerHelper",
        "regolith.helpers.l_membershelper:subparser",
    ),
    "l_milestones": (
        "regolith.helpers.l_milestoneshelper:MilestonesListerHelper",
        "regolith.helpers.l_milestoneshelper:subparser",
    ),
    "l_progress": (
        "regolith.helpers.l_progressreporthelper:ProgressReportHelper",
        "regolith.helpers.l_progressreporthelper:subparser",
    ),
    "l_projecta": (
        "regolith.helpers.l_projectahelper:ProjectaListerHelper",
        "regolith.helpers.l_projectahelper:subparser",
    ),
    "l_reimbstatus": (
        "regolith.helpers.reimbstatushelper:ReimbstatusHelper",
        "regolith.helpers.reimbstatushelper:subparser",
    ),
    "l_slides": (
        "regolith.helpers.l_slideshelper:SlidesListerHelper",
        "regolith.helpers.l_slideshelper:subparser",
    ),
    "l_talks": (
        "regolith.helpers.l_talkshelper:TalksListerHelper",
        "regolith.helpers.l_talkshelper:subparser",
    ),
    "l_todo": (
        "regolith.helpers.l_todohelper:TodoListerHelper",
        "regolith.helpers.l_todohelper:subparser",
    ),
    "v_meetings": (
        "regolith.helpers.v_meetingshelper:MeetingsValidatorHelper",
        "regolith.helpers.v_meetingshelper:subparser",
    ),
    "attestations": (
        "regolith.helpers.attestationshelper:AttestationsHelper",
        "regolith.helpers.attestationshelper:subparser",
    ),
    "lister": (
        "regolith.helpers.l_generalhelper:GeneralListerHelper",
        "regolith.helpers.l_generalhelper:subparser",
    ),
    "makeappointments": (
        "regolith.helpers.makeappointmentshelper:MakeAppointmentsHelper",
        "regolith.helpers.makeappointmentshelper:subparser",
    ),
}

UPDATER_HELPERS = LazyRegistry(UPDATER_HELPER_SPECS)
LISTER_HELPERS = LazyRegistry(LISTER_HELPER_SPECS)
HELPERS = LazyRegistry({**LISTER_HELPER_SPECS, **UPDATER_HELPER_SPECS})

# fast_updater updaters only connects to the one requested db, not to all
# dbs in rc.databases which is the default behavior
FAST_UPDATER_WHITELIST = ["u_milestone", "f_prum"]


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype][0](rc)
