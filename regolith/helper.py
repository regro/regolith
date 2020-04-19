"""Generic builder."""

from regolith.helpers import hellohelper as hello
from regolith.helpers import a_proprevhelper as a_proprev

HELPERS = {
    "hello": (hello.HelloHelper, hello.subparser),
    "a_proprev": (a_proprev.PropRevAdderHelper, a_proprev.subparser)
}


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype][0](rc)
