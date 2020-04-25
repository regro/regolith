"""Generic builder."""

from regolith.helpers import hellohelper as hello
from regolith.helpers import a_proprevhelper as a_proprev
from regolith.helpers import a_grppub_readlisthelper as a_gprl


HELPERS = {
    "hello": (hello.HelloHelper, hello.subparser),
    "a_proprev": (a_proprev.PropRevAdderHelper, a_proprev.subparser),
    "a_grppub_readlist": (a_gprl.GrpPubReadListAdderHelper, a_gprl.subparser)
}


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype][0](rc)
