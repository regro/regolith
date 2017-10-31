"""Generic builder."""

from regolith.cvbuilder import CVBuilder
from regolith.htmlbuilder import HtmlBuilder
from regolith.publistbuilder import PubListBuilder
from regolith.gradebuilder import GradeReportBuilder


BUILDERS = {
    'cv': CVBuilder,
    'html': HtmlBuilder,
    'publist': PubListBuilder,
    'grade': GradeReportBuilder,
    'grades': GradeReportBuilder,
    }


def builder(btype, rc):
    """Returns builder of the approriate type."""
    return BUILDERS[btype](rc)
