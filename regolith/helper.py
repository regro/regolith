"""Generic builder."""

from regolith.helpers import hellohelper as hello
from regolith.helpers import a_proprevhelper as a_proprev
from regolith.helpers import a_grppub_readlisthelper as a_gprl
from regolith.helpers import a_projectumhelper as a_projectum


HELPERS = {
    "hello": (hello.HelloHelper, hello.subparser),
    "a_proprev": (a_proprev.PropRevAdderHelper, a_proprev.subparser),
    "a_grppub_readlist": (a_gprl.GrpPubReadListAdderHelper, a_gprl.subparser),
    "a_projectum": (a_projectum.ProjectumAdderHelper, a_projectum.subparser)
}


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype][0](rc)
