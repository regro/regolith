"""Generic builder."""

from regolith.helpers.hellohelper import HelloHelper, subparser
from regolith.helpers import hellohelper as hello

HELPERS = {
    "hello": (hello.HelloHelper, hello.subparser)
#    "helper": HelperBuilder,
}


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype][0](rc)
