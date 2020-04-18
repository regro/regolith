"""Generic builder."""

from regolith.helpers.testhelper import TestHelper

HELPERS = {
    "test": TestHelper,
#    "helper": HelperBuilder,
}


def helpr(btype, rc):
    """Returns helper of the appropriate type."""
    return HELPERS[btype](rc)
