"""Generic helper."""

from regolith.lazy import LazyRegistry

# The import path of each helper and its subparser rather than the objects
# themselves, so that running one helper imports only that one.  See
# regolith.lazy for why.
#
# The order here is the order the helper GUI shows them in, so they are grouped
# by what they do and sorted within each group: the listers first, then the
# adders, the finishers and the updaters.  Targets are spelled with hyphens,
# the way argparse spells an argument; the underscored spelling of any of them
# still works, which regolith.lazy takes care of.

# Helpers that print and do not write.  These open every database.
LISTER_HELPER_SPECS = {
    # list what a collection holds
    "l-abstract": (
        "regolith.helpers.l_abstracthelper:AbstractListerHelper",
        "regolith.helpers.l_abstracthelper:subparser",
    ),
    "l-contacts": (
        "regolith.helpers.l_contactshelper:ContactsListerHelper",
        "regolith.helpers.l_contactshelper:subparser",
    ),
    "l-currentappointments": (
        "regolith.helpers.l_currentappointmentshelper:CurrentAppointmentsListerHelper",
        "regolith.helpers.l_currentappointmentshelper:subparser",
    ),
    "l-grants": (
        "regolith.helpers.l_grantshelper:GrantsListerHelper",
        "regolith.helpers.l_grantshelper:subparser",
    ),
    "l-mcgoals": (
        "regolith.helpers.l_mcgoalshelper:MCGoalsListerHelper",
        "regolith.helpers.l_mcgoalshelper:subparser",
    ),
    "l-mcprojects": (
        "regolith.helpers.l_mcprojectshelper:MCProjectsListerHelper",
        "regolith.helpers.l_mcprojectshelper:subparser",
    ),
    "l-members": (
        "regolith.helpers.l_membershelper:MembersListerHelper",
        "regolith.helpers.l_membershelper:subparser",
    ),
    "l-milestones": (
        "regolith.helpers.l_milestoneshelper:MilestonesListerHelper",
        "regolith.helpers.l_milestoneshelper:subparser",
    ),
    "l-progress": (
        "regolith.helpers.l_progressreporthelper:ProgressReportHelper",
        "regolith.helpers.l_progressreporthelper:subparser",
    ),
    "l-projecta": (
        "regolith.helpers.l_projectahelper:ProjectaListerHelper",
        "regolith.helpers.l_projectahelper:subparser",
    ),
    "l-reimbstatus": (
        "regolith.helpers.reimbstatushelper:ReimbstatusHelper",
        "regolith.helpers.reimbstatushelper:subparser",
    ),
    "l-slides": (
        "regolith.helpers.l_slideshelper:SlidesListerHelper",
        "regolith.helpers.l_slideshelper:subparser",
    ),
    "l-talks": (
        "regolith.helpers.l_talkshelper:TalksListerHelper",
        "regolith.helpers.l_talkshelper:subparser",
    ),
    "l-todo": (
        "regolith.helpers.l_todohelper:TodoListerHelper",
        "regolith.helpers.l_todohelper:subparser",
    ),
    # the rest of the reading helpers, which have no prefix of their own
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
    "v-meetings": (
        "regolith.helpers.v_meetingshelper:MeetingsValidatorHelper",
        "regolith.helpers.v_meetingshelper:subparser",
    ),
}

# Helpers that write.  These open only the database named in rc.database.
UPDATER_HELPER_SPECS = {
    # add something to a collection
    "a-expense": (
        "regolith.helpers.a_expensehelper:ExpenseAdderHelper",
        "regolith.helpers.a_expensehelper:subparser",
    ),
    "a-grppub-readlist": (
        "regolith.helpers.a_grppub_readlisthelper:GrpPubReadListAdderHelper",
        "regolith.helpers.a_grppub_readlisthelper:subparser",
    ),
    "a-manurev": (
        "regolith.helpers.a_manurevhelper:ManuRevAdderHelper",
        "regolith.helpers.a_manurevhelper:subparser",
    ),
    "a-mcproject": (
        "regolith.helpers.a_mcprojecthelper:MCProjectAdderHelper",
        "regolith.helpers.a_mcprojecthelper:subparser",
    ),
    "a-presentation": (
        "regolith.helpers.a_presentationhelper:PresentationAdderHelper",
        "regolith.helpers.a_presentationhelper:subparser",
    ),
    "a-projectum": (
        "regolith.helpers.a_projectumhelper:ProjectumAdderHelper",
        "regolith.helpers.a_projectumhelper:subparser",
    ),
    "a-proposal": (
        "regolith.helpers.a_proposalhelper:ProposalAdderHelper",
        "regolith.helpers.a_proposalhelper:subparser",
    ),
    "a-proprev": (
        "regolith.helpers.a_proprevhelper:PropRevAdderHelper",
        "regolith.helpers.a_proprevhelper:subparser",
    ),
    "a-todo": (
        "regolith.helpers.a_todohelper:TodoAdderHelper",
        "regolith.helpers.a_todohelper:subparser",
    ),
    # mark something finished
    "f-mcproject": (
        "regolith.helpers.f_mcprojecthelper:MCProjectFinisherHelper",
        "regolith.helpers.f_mcprojecthelper:subparser",
    ),
    "f-prum": (
        "regolith.helpers.u_finishprumhelper:FinishprumUpdaterHelper",
        "regolith.helpers.u_finishprumhelper:subparser",
    ),
    "f-todo": (
        "regolith.helpers.f_todohelper:TodoFinisherHelper",
        "regolith.helpers.f_todohelper:subparser",
    ),
    # change something that is there
    "u-contact": (
        "regolith.helpers.u_contacthelper:ContactUpdaterHelper",
        "regolith.helpers.u_contacthelper:subparser",
    ),
    "u-institution": (
        "regolith.helpers.u_institutionshelper:InstitutionsUpdaterHelper",
        "regolith.helpers.u_institutionshelper:subparser",
    ),
    "u-logurl": (
        "regolith.helpers.u_logurlhelper:LogUrlUpdaterHelper",
        "regolith.helpers.u_logurlhelper:subparser",
    ),
    "u-mcproject": (
        "regolith.helpers.u_mcprojecthelper:MCProjectUpdaterHelper",
        "regolith.helpers.u_mcprojecthelper:subparser",
    ),
    "u-mcsync": (
        "regolith.helpers.mcsynchelper:MCSyncHelper",
        "regolith.helpers.mcsynchelper:subparser",
    ),
    "u-milestone": (
        "regolith.helpers.u_milestonehelper:MilestoneUpdaterHelper",
        "regolith.helpers.u_milestonehelper:subparser",
    ),
    "u-todo": (
        "regolith.helpers.u_todohelper:TodoUpdaterHelper",
        "regolith.helpers.u_todohelper:subparser",
    ),
}


UPDATER_HELPERS = LazyRegistry(UPDATER_HELPER_SPECS)
LISTER_HELPERS = LazyRegistry(LISTER_HELPER_SPECS)
HELPERS = LazyRegistry({**LISTER_HELPER_SPECS, **UPDATER_HELPER_SPECS})

# fast_updater updaters only connects to the one requested db, not to all
# dbs in rc.databases which is the default behavior
FAST_UPDATER_WHITELIST = ["u-milestone", "f-prum"]


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype][0](rc)
