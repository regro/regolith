"""Generic builder."""


from regolith.cvbuilder import CVBuilder
from regolith.htmlbuilder import HtmlBuilder

BUILDERS = {
    'cv': CVBuilder,
    'html': HtmlBuilder,
    }

def builder(btype, rc):
    """Returns builder of the approriate type."""
    return BUILDERS[btype](rc)
