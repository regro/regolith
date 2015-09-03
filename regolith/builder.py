"""Generic builder."""


from regolith.htmlbuilder import HtmlBuilder

BUILDERS = {
    'html': HtmlBuilder,
    }

def builder(btype, rc):
    """Returns builder of the approriate type."""
    return BUILDERS[btype](rc)
