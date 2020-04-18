"""Generic builder."""

from regolith.helpers.hellohelper import HelloHelper

HELPERS = {
    "hello": HelloHelper,
#    "helper": HelperBuilder,
}


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype](rc)
