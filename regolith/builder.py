"""Generic builder."""

from regolith.cvbuilder import CVBuilder
from regolith.htmlbuilder import HtmlBuilder
from regolith.gradebuilder import GradeReportBuilder

BUILDERS = {
    'cv': CVBuilder,
    'html': HtmlBuilder,
    'grade': GradeReportBuilder,
    }

def builder(btype, rc):
    """Returns builder of the approriate type."""
    return BUILDERS[btype](rc)
