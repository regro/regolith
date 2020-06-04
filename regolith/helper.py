"""Generic builder."""

from regolith.helpers import hellohelper as hello
from regolith.helpers import a_proprevhelper as a_proprev
from regolith.helpers import a_grppub_readlisthelper as a_gprl
from regolith.helpers import a_projectumhelper as a_projectum
from regolith.helpers import l_milestoneshelper as l_milestone
from regolith.helpers import l_projectahelper as l_projecta
from regolith.helpers import l_grantshelper as l_grants
from regolith.helpers import l_membershelper as l_members
from regolith.helpers import l_contactshelper as l_contacts

from regolith.helpers import u_contacthelper as u_contact
HELPERS = {
    "hello": (hello.HelloHelper, hello.subparser),
    "a_proprev": (a_proprev.PropRevAdderHelper, a_proprev.subparser),
    "a_grppub_readlist": (a_gprl.GrpPubReadListAdderHelper, a_gprl.subparser),
    "a_projectum": (a_projectum.ProjectumAdderHelper, a_projectum.subparser),
    "l_milestones": (l_milestone.MilestonesListerHelper, l_milestone.subparser),
    "l_projecta": (l_projecta.ProjectaListerHelper, l_projecta.subparser),
    "l_grants": (l_grants.GrantsListerHelper, l_grants.subparser),
    "l_members": (l_members.MembersListerHelper, l_members.subparser),
    "l_contacts": (l_contacts.ContactsListerHelper, l_contacts.subparser),
    "u_contact": (u_contact.ContactUpdaterHelper, u_contact.subparser)
}


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype][0](rc)
